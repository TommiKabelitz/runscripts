'''
Module for making propagators by calling quarkpropGPU.x.

'main()' function is called by manageJob.py which passes the job specific
details to this function.

This script is not intended to be called from the command line.

'''

#standard library modules
import copy                         #deep copying of dictionaries
import pathlib                      #for checking existence of files
import pprint                       #nice dictionary printing (for debugging)
import subprocess                   #for calling quarkpropGPU.x
from datetime import datetime       #for writing out the time

#local modules
from colarunscripts import configIDs as cfg
from colarunscripts import directories as dirs
from colarunscripts import parameters as params
from colarunscripts import propFiles as files
from colarunscripts import shifts

#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 



def main(jobValues,*args,**kwargs):
        '''
        Main function. Begins propagator production process.

        Loops over the different quarks in the structure list, calling 
        MakePropagator for each.

        Arguments:
        jobValues -- dict: Dictionary containing the job specific values such as
                           kd, shift, SLURM_ARRAY_TASK_ID, etc...

        '''
        
        #Grabbing parameters from parameters.yml
        parameters = params.Load()

        #File stub for propagator input files. QUARK to be autoreplaced
        filestub = 'prop' + jobValues['jobID'] + '_' + str(jobValues['nthConfig'])+'.QUARK'
        
        #Compiling the full configuration file
        jobValues['configFile'] = dirs.FullDirectories(directory='configFile',**jobValues)['configFile']

        #Initialising list of propagator paths
        propPaths = []

        #Looping over structures and quarks in structures
        for structure in parameters['runValues']['structureList']: 
                
                print()
                print(f'Making propagators for structure set: {structure}')

                for quark in structure:

                        print()
                        print(5*'-'+f'Doing {quark} quark'+5*'-')
                        
                        #Making the propagator
                        propPath = MakePropagator(quark,jobValues,filestub,parameters)
                        propPaths.append(propPath)
        return propPaths



def MakePropagator(quark,jobValues,filestub,parameters,*args,**kwargs):
        '''
        Prepares the input files for making propagators using quarkpropGPU.x.

        Arguments
        quark      --  str: The flavour of quark to make
        jobValues  -- dict: Dictionary containing job specific values
        filestub   --  str: Base filestub to pass to quarkpropGPU.x
        parameters -- dict: Dictionary of all of the run parameters.
                            From parameters.yml
        
        '''
        #Copying jobValues dictionary. Deepcopy so that we can change items for
        #this quark only.
        quarkValues = copy.deepcopy(jobValues)

        #Reducing the number of propagators we make as some propagators are
        #effectively duplicates. quarkLabel will always be u,d,s and goes into
        #the propagator filename
        if quark == 'nl':
                #use zero field d quark in place of neutral quark
                quarkLabel = 'd'
                quarkValues['kd'] = 0
        elif quark == 'nh':
                #use zero field s quark in place of neutral s quark
                quarkLabel = 's'
                quarkValues['kd'] = 0
        elif quark == 'u' and quarkValues['kd'] == 0:
                #print statement says it all
                quarkLabel = 'd'
                print('At zero field strength, u and d quarks are the same. So just use the d quark.')
        else:
                quarkLabel = quark

        #Grabbing all the directories we could need into a dictionary 
        directories = dirs.FullDirectories(**quarkValues,**parameters['sourcesink'])

        #Adding prop filename to quarkValues dictionary
        quarkValues['quarkPrefix'] = directories['prop'].replace('QUARK',quarkLabel)
        
        #Labelling the filestub with the relevant quark
        filestub = directories['propInput'] + filestub.replace('QUARK',quarkLabel)

        #Making input files
        MakePropInputFiles(filestub,quark,quarkLabel,directories,quarkValues,parameters)

        #Checking whether propagator exists before calling executable.
        #Cannot be done earlier as need adjustment of kappa value for s
        #quark which happens in MakePropInputFiles()
        fullQuarkPath = f'{quarkValues["quarkPrefix"]}k{quarkValues["kappa"]}.{parameters["directories"]["propFormat"]}'

        print(f'Quark to make is: \n{fullQuarkPath}')

        if pathlib.Path(fullQuarkPath).is_file():
                print(f'Skipping {quark} quark. Propagator already exists')
                return fullQuarkPath

        #Get propagator report file and call the MPI
        reportFile = directories['propReport'].replace('QUARK',quarkLabel)
        CallMPI(parameters['propcfun']['qpropExecutable'],reportFile,arguments=['--solver="CGNE+S"','--itermax=1000000'],filestub=filestub,**parameters['slurmParams'])
        
        return fullQuarkPath


def MakePropInputFiles(filestub,quark,quarkLabel,directories,quarkValues,parameters,*args,**kwargs):
        '''
        Makes the input files for quarkpropGPU.x.

        Arguments:
        filestub    --  str: Base filestub to pass to quarkpropGPU.x 
        quark       --  str: The quark flavour to make, includes n,ns
        quarkLabel  --  str: The quark flavour to save the prop as. u,d or s
        directories -- dict: Dictionary of directories and filenames
        quarkValues -- dict: Job specific values to go into input files
        parameters  -- dict: To go into input files. From parameters.yml

        '''
       
        #Making input files
        files.MakeLatticeFile(filestub,**parameters['lattice'])
        files.MakeCloverFile(filestub,**parameters['propcfun']['clover'])

        #Source file needs to be made before u and s adjustments due to the 
        #Laplacian Eigenmode file. quark is passed to get the correct modefile.
        #Needs to be the actual flavour, not the label.
        quarkValues['sourcetype_num'] = files.MakeSourceFile(filestub,quark,quarkValues)
                
        #Adjusting for u and s quarks
        if quark == 'u':
                quarkValues['kd']*=-2
        elif quark in ['s','nh']:
                quarkValues['kappa'] = parameters['propcfun']['strangeKappa']

        #Can now make the .quarkprop input file
        files.MakePropFile(filestub,**quarkValues,**parameters['directories'],**parameters['propcfun'])
        
        #end MakePropInputFiles


def CallMPI(executable,reportFile,numGPUs=0,arguments=[],filestub='',**kwargs):
        '''
        Calls the executable using mpirun now that input files are made.

        Arguments:
        filestub   -- str: Filestub of the input files to pass to the executable
        executable -- str: The  exeutable to call
        reportFile -- str: The  reportfile to write the output of the executable to
        numGPUs    -- int: The  number of GPUs available to run on

        '''
        print(f'Time is {datetime.now()}')
        print('mpi-running "' + ' '.join([executable]+arguments) + '"')
        print(f'On {numGPUs} GPUs')
        print(f'The input filestub is "{filestub}"')

        #Running the executable. text=True means input and output are decoded
        runDetails = subprocess.run(['mpirun','-np',str(numGPUs),executable]+arguments,input=filestub+'\n',text=True,capture_output=True)

        #Writing output to report file
        with open(reportFile,'w') as f:
               f.write(runDetails.stdout)
               #Write the returned error to the file if there is one
               if runDetails.stderr is not None:
                       f.write(runDetails.stderr)
        print(f'Report file is: {reportFile}')
        print(f'Time is {datetime.now()}')
        
        #end CallMPI
