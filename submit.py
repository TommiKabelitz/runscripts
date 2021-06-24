'''
Submits jobs to the queue. Making propagators then correlation functions.

Based on the parameters set in the jobValues section of the parameters.yml 
file, creates bash scripts to be called by the scheduler to make propagators
and correlation functions. 

The bash scripts will call manageJob.py which manages the running of the 
job on the node.

Optional command line arguments are available for testing purposes and 
re-submitting jobs where correlation functions are missing.

'''

#standard library modules
import argparse                       #input parsing
import os                             #for checking file existence
import re                             #for integer extraction
import subprocess                     #for running scripts
from datetime import datetime         #for writing out the time
from os.path import dirname, realpath #for grabbing the directory of this script
                                     
#local modules
import colarunscripts.configIDs as cfg
import colarunscripts.directories as dirs
import colarunscripts.parameters as params


def SubmitJobs(kappaValues,kds,shifts,runPrefix,scheduler,doArrayJobs,submitmissing,testing=None,*args,**kwargs):
    '''
    Submits jobs to the queue.

    kappaValues, kds, shifts are looped over. 

    Arguments:
    kappaValues   -- int list: kappa values to loop over
    kds           -- int list: field strength to loop over
    shifts        -- str list: lattice shifts to loop over
    runPrefix     -- char: PACS-CS configuration label
    submitmissing -- bool: Whether we are submitting only the subset of 
                           missing correlation functions
    testing       -- str: what type of testing submission to do
    '''

    #Getting the directory for the runscript
    directory = dirs.FullDirectories(directory='script')['script']

    #Looping over parameters to submit
    for kappa in kappaValues:
        #Getting first ID eg. 1880 and num configurations eg. 400 for gauge fields
        start, ncon = cfg.ConfigDetails(kappa,runPrefix)

        for kd in kds:        
            for shift in shifts:

                print()
                print('kappa: ',str(kappa))
                print('kd: ',str(kd))
                print('shift: ',shift)
                print('runPrefix: ',runPrefix)
                print(f'(start,ncon):({start},{ncon})')

                if submitmissing is True:
                    print('Checking for missing correlation functions')
                    jobList = MissingCfunList(kappa,kd,shift,runPrefix,start,ncon)
                    print(f'{len(jobList)} jobs need to be re-run.')
                    if input('Enter y to submit:\n') != 'y':
                        continue
                elif testing in ['fullqueue','testqueue']:
                    jobList = ['1']
                else:
                    jobList = [str(i) for i in range(1,ncon+1)]

                #Compiling the runscript filename
                filename =f'{directory}{runPrefix}{kappa}BF{kd}{shift}'
                
                #Making the runscript
                if scheduler == 'slurm':
                    MakeSlurmRunscript(filename,kappa,kd,shift,doArrayJobs,testing)
                elif scheduler == 'PBS':
                    MakePBSRunscript(filename,kappa,kd,shift,doArrayJobs,testing)
                else:
                    raise ValueError('Unknown scheduler specified')
                subprocess.run(['chmod','+x',filename]) #executable permission

                ScheduleJobs(filename,jobList,scheduler,doArrayJobs,testing)

def ScheduleJobs(filename,jobList,scheduler,doArrayJobs,testing):

    command = []
    
    if testing == 'headnode':
        subprocess.run([filename])
        return

    if scheduler == 'PBS':
        command.append('qsub')
    elif scheduler == 'slurm':
        command.append('sbatch')

    if testing == 'interactive':
            command.append('-I')
    elif doArrayJobs is True or len(jobList) == 1:

        formattedList = ','.join(jobList)
        if scheduler == 'PBS':
            command.append(f'-J {formattedList}')
        elif scheduler == 'slurm':
            command.append(f'--array={formattedList}')
        
    command.append(filename)

    out = subprocess.run(command,text=True,capture_output=True)

    try:
        print(out.stdout)
        print(out.stderr)
        pattern = re.compile(r'\d+')
        jobID = pattern.findall(out.stdout)[0]
    except NameError:
        jobID = ''

    params.CopyParamsFile(jobID)



def MakeSlurmRunscript(filename,kappa,kd,shift,doArrayJobs,testing=None,*args,**kwargs):
    '''
    Makes the runscript to be called by the scheduler.
    
    The runscript does the basic submission before calling manageJob.py
    which manages the rest of the job.

    Arguments:
    filename -- str: the name of the file to make
    kappa    -- int: kappa value of the particular job
    kd       -- int: field strength of the particular job
    shift    -- str: lattice shift of the particular job
    testing  -- str: type of test submission

    '''
    if testing == 'testqueue':
        out = subprocess.run('sinfo',text=True,capture_output=True,shell=True)
        if 'test' not in out.stdout:
            raise ValueError('Test queue does not exist on your machine. Try "-t headnode" or "-t interactive".')
    elif testing == 'interactive':
        raise ValueError('Interactive jobs not presently supported by slurm. Try "-t headnode".')

    parameters = params.Load()
    #Getting slurm request details, ie. queue, num nodes, gpus etc.
    schedulerDetails = parameters['slurmParams']
    
    #Job management script
    script = parameters['directories']['runscriptDir'] + 'colarunscripts/manageJob.py'
    #Script to load modules
    modules = parameters['directories']['modules']

    #Adjusting some slurm parameters for submission to the test queue
    if testing == 'testqueue':
        schedulerDetails['queue'] = 'test'
        schedulerDetails['time'] = '00:05:00'
        schedulerDetails['memory'] = 16
    
    #The location for the scheduler output files to be dumped
    output = dirs.FullDirectories(directory='stdout')['stdout']

    #Preparing the correct terms based on whether we are using array jobs
    jobID = '$SLURM_JOB_ID'
    if doArrayJobs is True:
        arrayID = '$SLURM_ARRAY_TASK_ID'
        output += 'slurm-%A_%a.out'
    else:
        arrayID = 0     #Arbitrary
        output += 'slurm-%A.out'

    #Simulating Slurm values for running on head node
    #The scheduler assigns the TASK and JOB ids to each job
    #so we need to simulate their existence
    if testing == 'headnode':
        jobID = 1
        arrayID = 1

    #Open the runscript
    with open(filename,'w') as f:
        #Writing the slurm details to the script
        WriteSlurmDetails(f,output=output,**schedulerDetails)
        
        #Writing other stuff to the script. Output directory is made here
        WriteOtherDetails(f,modules)
        
        #Write the line which calls the python job script
        f.write(f'python {script} {kappa} {kd} {shift} {jobID} {arrayID}\n')



def MakePBSRunscript(filename,kappa,kd,shift,doArrayJobs,testing=None,*args,**kwargs):
    '''
    Makes the runscript to be called by the scheduler.
    
    The runscript does the basic submission before calling manageJob.py
    which manages the rest of the job.

    Arguments:
    filename -- str: the name of the file to make
    kappa    -- int: kappa value of the particular job
    kd       -- int: field strength of the particular job
    shift    -- str: lattice shift of the particular job
    testing  -- str: type of test submission

    '''

    if testing == 'testqueue':
        out = subprocess.run('qstat -Q',text=True,capture_output=True,shell=True)
        if 'test' not in out.stdout:
            raise ValueError('Test queue does not exist on your machine. Try "-t headnode" or "-t interactive".')
    

    parameters = params.Load()
    #Getting slurm request details, ie. queue, num nodes, gpus etc.
    schedulerDetails = parameters['pbsParams']
    
    #Job management script
    script = parameters['directories']['runscriptDir'] + 'colarunscripts/manageJob.py'
    #Script to load modules
    modules = parameters['directories']['modules']

    #The location for the scheduler output files to be dumped
    output = dirs.FullDirectories(directory='stdout')['stdout']
    
    jobID = '$PBS_JOBID'
    if doArrayJobs is True:
        arrayID = '$PBS_ARRAY_INDEX'
    else:
        arrayID = 1      #Arbitrary

    #Simulating scheduler variables for running on head node
    #The scheduler assigns the TASK and JOB ids to each job
    #so we need to simulate their existence
    if testing == 'headnode':
        jobID = 1
        arrayID = 1

    #Open the runscript
    with open(filename,'w') as f:
        #Writing the slurm details to the script
        WritePBSDetails(f,output=output,**schedulerDetails)
        
        #Writing other stuff to the script
        WriteOtherDetails(f,modules)
        
        #Write the line which calls the python job script 1 at the end
        #is the array number which is not used for PBS
        f.write(f'python {script} {kappa} {kd} {shift} {jobID} {arrayID}\n')




def WriteSlurmDetails(fileObject,queue,time,output,nodes,numCPUs,numGPUs,memory,jobStorage,*args,**kwargs):
    '''
    Writes the parameters for the slurm scheduler to the runscript.

    Arguments:
    fileObject -- file object: an open file to write to
    queue      -- str: queue to submit to
    time       -- str: the time allowed for the run in format D-HH:MM:SS
    output     -- str: the location for the slurm output files to be placed
    nodes      -- int: the number of nodes to request 
    numCPUs    -- int: the number of CPUs to request
    numGPUs    -- int: the number of GPUs to request
    memory     -- int: the amount of in job memory to request
    jobStorage -- int: the amount of temporary job storage to request
    '''

    #Printing a couple of relevant details to the screen for checking
    print('\n'+ f'Queue: {queue}\n'
              + f'Nodes: {nodes}\n'
              + f'Time: {time}\n')

    #Writing everything to the file
    fileObject.write(f'#!/bin/bash\n')
    fileObject.write(f'#SBATCH --partition={queue}\n')
    fileObject.write(f'#SBATCH --nodes={nodes}\n')
    fileObject.write(f'#SBATCH --ntasks={numCPUs}\n')
    fileObject.write(f'#SBATCH --time={time}\n')
    fileObject.write(f'#SBATCH --mem={memory}GB\n')
    fileObject.write(f'#SBATCH --output={output}\n')
    fileObject.write(f'#SBATCH --gres=tmpfs:{jobStorage}G\n')
    if queue != 'test':
        fileObject.write(f'#SBATCH --gres=gpu:{numGPUs}\n')



def WritePBSDetails(fileObject,project,queue,numCPUs,numGPUs,time,memory,jobStorage,linkStorage,output,*args,**kwargs):
    '''
    Writes the parameters for the slurm scheduler to the runscript.

    Arguments:
    fileObject -- file object: an open file to write to
    queue      -- str: queue to submit to
    time       -- str: the time allowed for the run in format D-HH:MM:SS
    output     -- str: the location for the slurm output files to be placed
    nodes      -- int: the number of nodes to request 
    numCPUs    -- int: the number of CPUs to request
    numGPUs    -- int: the number of GPUs to request
    memory     -- int: the amount of in job memory to request
    
    '''

    #Printing a couple of relevant details to the screen for checking
    print('\n'+ f'Queue: {queue}\n'
              + f'CPUs: {numCPUs}\n'
              + f'GPUs: {numGPUs}\n'
              + f'Time: {time}\n')

    #Writing everything to the file
    fileObject.write(f'#!/bin/bash\n')
    fileObject.write(f'#PBS -q {queue}\n')
    fileObject.write(f'#PBS -P {project}\n')
    fileObject.write(f'#PBS -l ncpus={numCPUs}\n')
    fileObject.write(f'#PBS -l ngpus={numGPUs}\n')
    fileObject.write(f'#PBS -l walltime={time}\n')
    fileObject.write(f'#PBS -l mem={memory}GB\n')
    fileObject.write(f'#PBS -l jobfs={jobStorage}GB\n')
    fileObject.write(f'#PBS -lstorage {linkStorage}\n')
    fileObject.write(f'#PBS -j oe\n')
    fileObject.write(f'#PBS -l wd\n')
    fileObject.write(f'#PBS -o {output}\n')
    


def WriteOtherDetails(fileObject,modules,*args,**kwargs):
    '''
    Writes non-scheduler related details to the runscript.

    Arguments:
    fileObject -- fileObject: an open file to write to
    modules    -- str: the path to a script to load the required modules

    '''

    fileObject.write('echo Running on host `hostname`\n')
    fileObject.write(f'source {modules}\n')
    #Unlimiting stack size
    fileObject.write('ulimit -s unlimited\n')
    #Limiting the size of core dump files such that cannot be made.
    #If not limited, code crashing while running will very quickly do a lot of
    #damage
    fileObject.write('ulimit -c 0\n')
    #Showing status of stack and core dump limits
    fileObject.write('ulimit -a\n')



def MissingCfunList(kappa,kd,shift,runPrefix,start,ncon,*args,**kwargs):
    '''
    Returns a list of configurations for which cfuns are missing.

    Returned list is comma separated string of integers. Integers are not
    configuration IDs, the i'th integer is the i'th missing configuration.

    Arguments:
    kappa     -- int: kappa value of the particular job
    kd        -- int: field strength of the particular job
    shift     -- str: lattice shift of the particular job
    runPrefix -- char: PACS-CS configuration label
    start     -- int: The first configuration number. Eg 1880
    ncon      -- int: The total number of configurations

    Returns:
    missingCfuns -- str list: str list of integers labelling missing configurations.
    '''

    #Loading parameters
    parameters = params.Load()

    #Getting base cfun directory
    cfunPrefix = dirs.FullDirectories(directory='cfun',kappa=kappa,kd=kd,shift=shift,**parameters['runValues'],**parameters['sourcesink'])['cfun']

    #initialising output list
    missing = []
    #Looping through structures and particles
    for structure in parameters['runValues']['structureList']:
        for particlePair in parameters['runValues']['particleList']:
            
            #Compiling cfun filename and path
            particleName = ''.join(particlePair)
            structureString = ''.join(structure)
            baseCfunPath = f'{cfunPrefix}CONFIGID.{particleName}_{structureString}.u.2cf'
            
            #Looping through configurations
            for i in range(1,ncon+1):
                #If configuration is already seen to be missing, don't need to check again
                if i in missing:
                    continue
                #Replacing base path with specific config ID
                ID = cfg.ConfigID(i,runPrefix,start)
                cfunPath = baseCfunPath.replace('CONFIGID',ID)
                #Checking cfun existence
                if os.path.isfile(cfunPath) is False:
                    missing.append(str(i))

    return missing



def Input():
    '''
    Parses input from the command line.

    Returns:
    inputDict -- dict: Dictionary of input given. testing key will have
                       value None or one of the choices given below.
                       submitmissing is False by default

    '''

    #Setting up the parser
    parser = argparse.ArgumentParser(description='Submits jobs to the queue. Produces propagators and correlation functions.')

    #Adding the testing argument
    parser.add_argument('-t','--testing',help='run in testing mode. Runs on head node (no GPUs). Else submits only 1 configuration to either the test queue (no GPUs) or the full queue.',choices=['headnode','testqueue','fullqueue','interactive'])
    
    #Adding the argument for submitting only missing jobs
    parser.add_argument('-m','--submitmissing',help='checks for missing correlation functions, then submits only those configurations.',action='store_true')

    #Parsing the arguments from the command line
    args = parser.parse_args()
    #Turning the namespace into a dictionary
    inputDict = vars(args)
    return inputDict
    

if __name__ == '__main__':

    print(f'Time is {datetime.now()}')

    #Combining the run parameters from the parameters.yml file with
    #the input specifications from the command line
    values = {**params.Load()['runValues'],**Input()}


    SubmitJobs(**values)
    

