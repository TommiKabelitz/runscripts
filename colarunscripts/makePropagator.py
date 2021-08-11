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
from colarunscripts.particles import QuarkCharge
#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 



def main(jobValues,timer,*args,**kwargs):
        '''
        Main function. Begins propagator production process.

        Loops over the different quarks in the structure list, calling 
        MakePropagator for each.

        Arguments:
        jobValues -- dict: Dictionary containing the job specific values such as
                           kd, shift, SLURM_ARRAY_TASK_ID, etc...
        timer     -- Timer: Timer object to manage timing of correlation function
                           calculation time.

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
                        propPath = MakePropagator(quark,jobValues,filestub,parameters,timer)
                        propPaths.append(propPath)
        return propPaths



def MakePropagator(quark,jobValues,filestub,parameters,timer,*args,**kwargs):
        '''
        Prepares the input files for making propagators using quarkpropGPU.x.

        Arguments
        quark      --  str: The flavour of quark to make
        jobValues  -- dict: Dictionary containing job specific values
        filestub   --  str: Base filestub to pass to quarkpropGPU.x
        parameters -- dict: Dictionary of all of the run parameters.
                            From parameters.yml
        timer      -- Timer: Timer object to manage timing of correlation function
                            calculation time.

        '''
        #Copying jobValues dictionary. Deepcopy so that we can change items for
        #this quark only.
        quarkValues = copy.deepcopy(jobValues)
        print(quark, quarkValues['kd'],quarkValues['kappa'])
     
        #Labelling the filestub with the relevant quark
        filestub = dirs.FullDirectories(directory='propInput')['propInput'] + filestub.replace('QUARK',quark)

        #Making input files
        fullQuarkPath = MakePropInputFiles(filestub,quark,quarkValues,parameters)

        #Checking whether the quark already exists
        print(f'Quark to make is: \n{fullQuarkPath}')
        if pathlib.Path(fullQuarkPath).is_file():
                print(f'Skipping {quark} quark. Propagator already exists')
                return fullQuarkPath
        
        
        #Get propagator report file and call the MPI
        reportFile = dirs.FullDirectories(directory='propReport',**quarkValues,**parameters['sourcesink'])['propReport'].replace('QUARK',quark)
        timer.startTimer('Propagators')
        CallMPI(parameters['propcfun']['qpropExecutable'],reportFile,arguments=['--solver=CGNE+S','--itermax=1000000'],filestub=filestub,**parameters['slurmParams'])
        timer.stopTimer('Propagators')        
        return fullQuarkPath


def MakePropInputFiles(filestub,quark,quarkValues,parameters,*args,**kwargs):
        '''
        Makes the input files for quarkpropGPU.x.

        Arguments:
        filestub    --  str: Base filestub to pass to quarkpropGPU.x 
        quark       --  str: The quark flavour to make, includes n,ns
        quarkLabel  --  str: The quark flavour to save the prop as. u,d or s
        directories -- dict: Dictionary of directories and filenames
        quarkValues -- dict: Job specific values to go into input files
        parameters  -- dict: To go into input files. From parameters.yml

        Returns:
        fullQuarkPath -- str: The full path to the quark to be made
        '''
       
        #Making input files
        files.MakeLatticeFile(filestub,**parameters['lattice'])
        files.MakeCloverFile(filestub,**parameters['propcfun']['clover'])

        #Source file needs to be made before u and s adjustments due to the 
        #Laplacian Eigenmode file. quark is passed to get the correct modefile.
        #Needs to be the actual flavour, not the label.
        quarkValues['sourcetype_num'] = files.MakeSourceFile(filestub,quark,quarkValues)

        #Reducing the number of propagators we make as some propagators are
        #effectively duplicates. ie. u props are d props with -2*kd, nl props
        #are neutral d props
        #quarkLabel will always be d or s and goes into
        #the propagator filename
        quarkValues['kd'] *= QuarkCharge(quark)
        if quark in ['s','nh']:
                quarkLabel = 's'
        else:
                quarkLabel = 'd'
                
        #Adjusting for u and s quarks, can't be done earlier, see above
        if quark in ['s','nh']:
                quarkValues['kappa'] = parameters['propcfun']['strangeKappa']

        #Assembling the quark prefix
        quarkPrefix = dirs.FullDirectories(directory='prop',**quarkValues,**parameters['sourcesink'])['prop']
        quarkValues['quarkPrefix'] = quarkPrefix.replace('QUARK',quarkLabel)
        #Compiling full prop path
        fullQuarkPath = f'{quarkValues["quarkPrefix"]}k{quarkValues["kappa"]}.{parameters["directories"]["propFormat"]}'
                
        #Can now make the .quarkprop input file
        files.MakePropFile(filestub,**quarkValues,**parameters['directories'],**parameters['propcfun'])

        return fullQuarkPath


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
