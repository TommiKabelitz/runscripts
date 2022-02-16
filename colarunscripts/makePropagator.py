"""
Module for making propagators by calling quarkpropGPU.x.

'main()' function is called by manageJob.py which passes the job specific
details to this function.

This script is not intended to be called from the command line.

"""

#standard library modules
import copy                         #deep copying of dictionaries
import pathlib                      #for checking existence of files
import pprint                       #nice dictionary printing (for debugging)
import subprocess                   #for calling quarkpropGPU.x
from datetime import datetime       #for writing out the time

#local modules
from colarunscripts import directories as dirs
from colarunscripts import propFiles as files
from colarunscripts import shifts
from colarunscripts.particles import QuarkCharge
from colarunscripts.utilities import pp


def main(parameters,kd,shift,jobValues,timer,*args,**kwargs):
        """
        Main function. Begins propagator production process.

        Loops over the different quarks in the structure list, calling 
        MakePropagator for each.

        Arguments:
        jobValues -- dict: Dictionary containing the job specific values such as
                           kd, shift, SLURM_ARRAY_TASK_ID, etc...
        timer     -- Timer: Timer object to manage timing of correlation function
                           calculation time.

        """
        
        #File stub for propagator input files. QUARK to be autoreplaced
        filestub = 'prop' + jobValues['jobID'] + '_' + str(jobValues['nthConfig'])+'.QUARK'
        
        #Compiling the full configuration file
        jobValues['configFile'] = dirs.FullDirectories(parameters,directory='configFile',kd=kd,**jobValues)['configFile']

        logFile = jobValues['inputSummary']['prop']
        
        #Initialising list of propagator paths
        propPaths = []
       
        #Looping over structures and quarks in structures
        for structure in parameters['runValues']['structureList']: 
                
                print()
                print(f'Making propagators for structure set: {structure}')

                with open(logFile,'a') as f:
                        f.write(f'\n\n\n{structure=}:\n')

                for quark in structure:

                        print()
                        print(5*'-'+f'Doing {quark} quark'+5*'-')

                        with open(logFile,'a') as f:
                                f.write(f'{quark=}:\n')

                        #Making the propagator
                        propPath = MakePropagator(parameters,quark,kd,shift,jobValues,filestub,logFile,timer)
                        propPaths.append(propPath)
        return propPaths



def MakePropagator(parameters,quark,kd,shift,jobValues,filestub,logFile,timer,*args,**kwargs):
        """
        Prepares the input files for making propagators using quarkpropGPU.x.

        Arguments
        quark      --  str: The flavour of quark to make
        jobValues  -- dict: Dictionary containing job specific values
        filestub   --  str: Base filestub to pass to quarkpropGPU.x
        parameters -- dict: Dictionary of all of the run parameters.
                            From parameters.yml
        timer      -- Timer: Timer object to manage timing of correlation function
                            calculation time.
        """

        #Copying jobValues dictionary. Deepcopy so that we can change items for
        #this quark only.
        quarkValues = copy.deepcopy(jobValues)
     
        #First we check if the quark exists - need property adjustment
        #for quark flavour to do so
        kd *= QuarkCharge(quark)
        if quark in ['s','nh']:
                quarkLabel = 'h'
        else:
                quarkLabel = 'l'
        quarkValues['strangeKappa'] = parameters['propcfun']['strangeKappa']

        #Assembling the quark path
        quarkPrefix = dirs.FullDirectories(parameters,directory='prop',kd=kd,shift=shift,**quarkValues,**parameters['sourcesink'])['prop']
        quarkValues['quarkPrefix'] = quarkPrefix.replace('QUARK',quarkLabel)

        fullQuarkPath = f'{quarkValues["quarkPrefix"]}kKAPPA.{parameters["directories"]["propFormat"]}'
        #Kappa in filename is flavour dependent, different for directory, but
        #that should change
        if quarkLabel == 'h':
                fullQuarkPath = fullQuarkPath.replace('KAPPA',str(quarkValues['strangeKappa']))
        else:
                fullQuarkPath = fullQuarkPath.replace('KAPPA',str(quarkValues['kappa']))

        #Checking whether the quark already exists
        print(f'Quark to make is: \n{fullQuarkPath}')
        if pathlib.Path(fullQuarkPath).is_file():
                print(f'Skipping {quark} quark. Propagator already exists')

                with open(logFile,'a') as f:
                    f.write(f'\nSkipping {quark=}.\n{fullQuarkPath} \nFile already exists\n\n')
                return fullQuarkPath

       
        #Labelling the filestub with the relevant quark
        filestub = dirs.FullDirectories(parameters,directory='propInput')['propInput'] + filestub.replace('QUARK',quark)

        #Making input files
        MakePropInputFiles(parameters,filestub,logFile,quarkLabel,kd,shift,quarkValues)
        
        scheduler = jobValues['scheduler'].lower()
        numGPUs = parameters[scheduler+'Params']['NUMGPUS']
        
        #Get propagator report file and call the MPI
        reportFile = dirs.FullDirectories(parameters,directory='propReport',kd=kd,shift=shift,**quarkValues,**parameters['sourcesink'])['propReport'].replace('QUARK',quark)
        if quark in ['s','nh']:
                timerLabel = 'Heavy Propagators'
        else:
                timerLabel = 'Light Propagators'
        CallMPI(parameters['propcfun']['qpropExecutable'],reportFile,jobValues['runFunction'],arguments=['--solver=CGNE+S','--itermax=1000000'],filestub=filestub,numGPUs=numGPUs,timerLabel=timerLabel,timer=timer)
        return fullQuarkPath


def MakePropInputFiles(parameters,filestub,logFile,quarkLabel,kd,shift,quarkValues,*args,**kwargs):
        """
        Makes the input files for quarkpropGPU.x.

        Arguments:
        filestub    --  str: Base filestub to pass to quarkpropGPU.x 
        quark       --  str: The quark flavour to make, includes n,ns
        quarkLabel  --  str: The quark flavour to save the prop as. u,d or s
        directories -- dict: Dictionary of directories and filenames
        quarkValues -- dict: Job specific values to go into input files
        parameters  -- dict: To go into input files. From parameters.yml
        """

        #Making input files
        files.MakeLatticeFile(filestub,logFile,**parameters['lattice'])
        files.MakeCloverFile(filestub,logFile,**parameters['propcfun']['clover'])

        quarkValues['sourcetype_num'] = files.MakeSourceFile(parameters,filestub,logFile,kd,shift,quarkValues)

        quarkValues.pop('strangeKappa')
        #Can now make the .quarkprop input file
        files.MakePropFile(filestub,logFile,quarkLabel,kd=kd,shift=shift,**quarkValues,**parameters['directories'],**parameters['propcfun'])



def CallMPI(executable,reportFile,runFunction,numGPUs=0,arguments=[],filestub='',timerLabel=None,timer=None,*args,**kwargs):
        """
        Calls the executable using mpirun now that input files are made.

        Arguments:
        executable  -- str: The executable to call
        reportFile  -- str: The reportfile to write the output of the executable to
        runFunction -- str: Function call the executable with, ie. mpirun
        numGPUs     -- int: The number of GPUs available to run on
        arguments   -- list: List of arguments to pass to the executable
        filestub    -- str: Filestub of the input files to pass to the executable
        timerLabel  -- str: Specify which, if any timer should record execution time
        timer       -- Timer: Timer object that is tracking the execution time

        """
        
        #Compiling the command based on the different syntax required
        if runFunction == 'mpirun':
                command = [runFunction,'-np',str(numGPUs),executable]+arguments
        elif runFunction == 'srun':
                #Using srun can do weird things with the number of CPUs specified.
                #The propagator code breaks with more than 1 while the others need
                #2. 
                if 'quarkprop' in executable:
                        numTasks = 1
                else:
                        numTasks = 2
                command = [runFunction,'-n',str(numTasks),executable]+arguments
        else:
                raise NotImplementedError(f'{runFunction} is not implemented')

        print(f'Time is {datetime.now()}')
        print(f'Running {" ".join([executable]+arguments)} using{runFunction}')
        print(f'On {numGPUs} GPUs')
        print(f'The input filestub is "{filestub}"')

        #If doing a dry testrun. We do everything except call binaries
        #Print path to reportfile as usual though it may not exist
        if executable == 'dryRun':
                print(f'Report file is: {reportFile}')
                print(f'Time is {datetime.now()}')
                return
        
        if timerLabel is not None:
                timer.startTimer(timerLabel)

        #Running the executable. text=True means input and output are decoded
        runDetails = subprocess.run(command,input=filestub+'\n',text=True,capture_output=True)

        if timerLabel is not None:
                timer.stopTimer(timerLabel)

        #Writing output to report file
        with open(reportFile,'w') as f:
               f.write(runDetails.stdout)
               #Write the returned error to the file if there is one
               if runDetails.stderr is not None:
                       f.write(runDetails.stderr)
        print(f'Report file is: {reportFile}')
        print(f'Time is {datetime.now()}')
        #end CallMPI
