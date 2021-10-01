'''
Submits jobs to the queue.

Based on the parameters set in the jobValues section of the parameters.yml 
file, creates bash scripts to be called by the scheduler to make propagators
and correlation functions. 

The bash scripts will call manageJob.py which manages the running of the 
job on the node.
'''

#standard library modules
import argparse                       #input parsing
import os                             #for checking file existence
import re                             #for integer extraction
import subprocess                     #for running scripts
from datetime import datetime         #for writing out the time
from os.path import dirname, realpath #for grabbing the directory of this script
from pathlib import Path                                     

#local modules
import colarunscripts.configIDs as cfg
import colarunscripts.directories as dirs
import colarunscripts.parameters as params
from colarunscripts.utilities import GetJobID, pp

def SubmitJobs(parameters,nthConfig,inputArgs,values,*args,**kwargs):
    '''
    Submits jobs to the queue.

    kappaValues, kds, shifts are looped over. 

    Arguments:
    kappaValues   -- int list: kappa values to loop over
    kds           -- int list: field strength to loop over
    shifts        -- str list: lattice shifts to loop over
    runPrefix     -- char: PACS-CS configuration label
    sinkType      -- str: The type of sink being used
    scheduler     -- str: The scheduler of the system (eg. slurm,pbs,etc.)
    doArrayJobs   -- bool: Whether to do jobs in arrays or not
    keepEmodes    -- bool: Whether to delete eigenmodes each run
    submitmissing -- bool: Whether we are submitting only the subset of 
                           missing correlation functions
    testing       -- str: what type of testing submission to do
    '''

    #Getting the directory for the runscripts
    directory = dirs.FullDirectories(parameters,directory='script')['script']
    
    #If tempstorage for eigenmodes is False and keepEmodes is False
    #confirm the user wishes to delete permanently stored emodes
    if values['keepEmodes'] is parameters['tempStorage']['lapmodes'] is False:
        print('WARNING: proceeding will result in the deletion of locally stored eigenmodes.')
        if input('Enter y to proceed: ') != 'y':
            print('exiting')
            exit()

    #Looping over parameters to submit as separate jobs
    for kappa in values['kappaValues']:

        #Printing parameters to be submitted
        print()
        print('kappa: ',kappa)
        print('kds: ',values['kds'])
        print('shifts: ',values['shifts'])
        print('runPrefix: ',values['runPrefix'])

        #Compiling the runscript filename
        filename =f'{directory}{values["runPrefix"]}{kappa}conf{nthConfig}'

        #Making the runscript
        if values['scheduler'] == 'slurm':
            MakeSlurmRunscript(parameters,filename,kappa,values['doArrayJobs'],nthConfig=nthConfig,**inputArgs)
        elif values['scheduler'] == 'PBS':
            MakePBSRunscript(parameters,filename,kappa,values['doArrayJobs'],nthConfig=nthConfig,**inputArgs)
        else:
            raise ValueError('Unknown scheduler specified')
        subprocess.run(['chmod','+x',filename]) #executable permission

        #Need ncon if we are doing array jobs - defines end of array
        _,ncon = cfg.ConfigDetails(kappa,values['runPrefix'])
        #Scheduling jobs
        ScheduleJobs(filename,values['scheduler'],values['doArrayJobs'],ncon,inputArgs)


                
def ScheduleJobs(filename,scheduler,doArrayJobs,ncon,inputArgs):

    command = []
    capture_output = True

    print()
    print(f'Running {filename}')

    if inputArgs['testing'] == 'headnode':
        jobID = GetJobID(os.environ) 
        params.CopyParamsFile(inputArgs['parametersfile'],jobID=jobID)
        subprocess.run([filename])
        return

    if scheduler == 'PBS':
        command.append('qsub')
    elif scheduler == 'slurm':
        command.append('sbatch')

    if inputArgs['testing'] in ['interactive', 'interactivetestqueue']:
            command.append('-I')
            capture_output = False
    elif doArrayJobs is True:
        formattedList = f'1-{ncon}'#Job ids for array jobs
        if scheduler == 'PBS':
            command.append('-J ')
            command.append(f'{formattedList}')
        elif scheduler == 'slurm':
            command.append(f'--array={formattedList}')
        
    command.append(filename)
    
    out = subprocess.run(command,text=True,capture_output=capture_output)

    try:
        print(out.stdout)
        print(out.stderr)
        pattern = re.compile(r'\d+')
        jobID = pattern.findall(out.stdout)[0]
    except NameError:
        jobID = ''

    params.CopyParamsFile(inputArgs['parametersfile'],jobID)


def MakeSlurmRunscript(parameters,filename,kappa,doArrayJobs,nthConfig=1,simjobs=1,nconfigurations=0,testing=None,*args,**kwargs):
    '''
    Makes the runscript to be called by the scheduler.
    
    The runscript does the basic submission before calling manageJob.py
    which manages the rest of the job.

    Arguments:
    parameters      -- dict:
    filename        -- str: the name of the file to make
    kappa           -- int: kappa value of the particular job
    doArrayJobs     -- bool:
    nthConfig       -- int:
    simjobs         -- int:
    nconfigurations -- int:
    testing         -- str: type of test submission

    '''

    #Getting slurm request details, ie. queue, num nodes, gpus etc.
    schedulerDetails = parameters['slurmParams']

    #Adjusting parameters based on the test run type. Also checking if a test
    #queue exists
    if testing == 'testqueue':
        out = subprocess.run('sinfo',text=True,capture_output=True,shell=True)

        if 'test' not in out.stdout:
            raise ValueError('Test queue does not configured on your machine. Try "-t headnode" or "-t interactive".')
        else:
            schedulerDetails['QUEUE'] = 'test'
            schedulerDetails['TIME'] = '00:05:00'
            schedulerDetails['MEMORY'] = 16    
            schedulerDetails['JOBSTORAGE'] = 10
            schedulerDetails['NUMCPUS'] = 0
            schedulerDetails['NUMGPUS'] = 0

    elif testing == 'interactive':
        raise ValueError('Interactive jobs not presently supported by slurm. Try "-t headnode".')
    
    template = Path(schedulerDetails['runscriptTemplate'])
    runscript = Path(filename)
    text = template.read_text()
    for key,value in schedulerDetails.items():
        text = text.replace(key,str(value))
    text = text.replace('PARAMETERSDIR',dirs.FullDirectories(parameters,directory='parameters')['parameters'])
    text = text.replace('KAPPA',str(kappa))
    if doArrayJobs is False:
        text = text.replace('NTHCONFIG',str(nthConfig))
    else:
        text = text.replace('NTHCONFIG','$SLURM_ARRAY_TASK_ID')
    text = text.replace('NUMJOBS',str(simjobs))
    text = text.replace('NCON',str(nconfigurations))
    text = text.replace('TESTING',str(testing))
    
    #Writing runscript text to runscript file
    runscript.write_text(text)


def MakePBSRunscript(parameters,filename,kappa,doArrayJobs,nthConfig=1,simjobs=1,nconfigurations=0,testing=None,*args,**kwargs):
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
    
    #Getting slurm request details, ie. queue, num nodes, gpus etc.
    schedulerDetails = parameters['pbsParams']
    schedulerDetails['OUTPUTDIR'] = dirs.FullDirectories(parameters,directory='stdout')['stdout']
    
    if testing in ['testqueue','interactivetestqueue']:
        out = subprocess.run('qstat -Q',text=True,capture_output=True,shell=True)
        #Gadi test queue is called express
        if 'express' not in out.stdout:
            raise ValueError('Test queue does not exist on your machine. Try "-t headnode" or "-t interactive".')
        else:
            schedulerDetails['QUEUE'] = 'express'
            schedulerDetails['TIME'] = '00:30:00'
            schedulerDetails['MEMORY'] = 16
            schedulerDetails['JOBSTORAGE'] = 10
            schedulerDetails['NUMCPUS'] = 4
            schedulerDetails['NUMGPUS'] = 0        

    template = Path(schedulerDetails['runscriptTemplate'])
    runscript = Path(filename)
    text = template.read_text()
    for key,value in schedulerDetails.items():
        text = text.replace(key,str(value))
    text = text.replace('PARAMETERSDIR',dirs.FullDirectories(parameters,directory='parameters')['parameters'])
    text = text.replace('KAPPA',str(kappa))
    if doArrayJobs is False:
        text = text.replace('NTHCONFIG',str(nthConfig))
    else:
        text = text.replace('NTHCONFIG','$PBS_ARRAY_INDEX')
    text = text.replace('NUMJOBS',str(simjobs))
    text = text.replace('NCON',str(nconfigurations))
    text = text.replace('TESTING',str(testing))
    
    #Writing runscript text to runscript file
    runscript.write_text(text)

   
def main(nthConfig,inputArgs):

    print(f'Time is {datetime.now()}')

    parametersFile = inputArgs['parametersfile']
    parameters = params.Load(parametersFile=parametersFile)

    SubmitJobs(parameters,nthConfig,inputArgs,parameters['runValues'])

