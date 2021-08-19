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
from pathlib import Path                                     
#local modules
import colarunscripts.configIDs as cfg
import colarunscripts.directories as dirs
import colarunscripts.parameters as params


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

    #Getting the directory for the runscript
    directory = dirs.FullDirectories(parameters,directory='script')['script']
    
    #If tempstorage for eigenmodes is False and keepEmodes is False
    #confirm the user wishes to delete permanently stored emodes
    if values['keepEmodes'] is parameters['tempStorage']['lapmodes'] is False:
        print('WARNING: proceeding will result in the deletion of locally stored eigenmodes.')
        if input('Enter y to proceed: ') != 'y':
            print('exiting')
            exit()

    #Looping over parameters to submit
    for kappa in values['kappaValues']:
              
        print()
        print('kappa: ',kappa)
        print('kds: ',values['kds'])
        print('shifts: ',values['shifts'])
        print('runPrefix: ',values['runPrefix'])

        # #REWRITE NEEDED
        # if inputArgs['submitmissing'] is True:
        #     print()
        #     # print('This is broken at the moment')
        #     # exit()
        #     # print('Checking for missing correlation functions')
        #     # #All of these not currently in the scope
        #     # jobList = MissingCfunList(kappa,kd,shift,runPrefix,start,ncon,sinkType)
        #     # print(f'{len(jobList)} jobs need to be re-run.')
        #     # if input('Enter y to submit:\n') != 'y':
        #     #     continue
        # elif inputArgs['testing'] in ['fullqueue','testqueue']:
        #     jobList = ['1']
        # else:
        jobList = [str(i) for i in range(1,401)]


        #Compiling the runscript filename
        filename =f'{directory}{values["runPrefix"]}{kappa}conf{nthConfig}'

        #Making the runscript
        if values['scheduler'] == 'slurm':
            MakeSlurmRunscript(parameters,filename,inputArgs['parametersfile'],kappa,values['doArrayJobs'],nthConfig=nthConfig,**inputArgs)
        elif values['scheduler'] == 'PBS':
            MakePBSRunscript(parameters,filename,inputArgs['parametersfile'],kappa,values['doArrayJobs'],nthConfig=nthConfig,**inputArgs)
        else:
            raise ValueError('Unknown scheduler specified')
        subprocess.run(['chmod','+x',filename]) #executable permission

        ScheduleJobs(filename,jobList,values['scheduler'],values['doArrayJobs'],inputArgs)


                
def ScheduleJobs(filename,jobList,scheduler,doArrayJobs,inputArgs):

    command = []
    capture_output = True

    print()
    print(f'Running {filename}')

    if inputArgs['testing'] == 'headnode':
        params.CopyParamsFile(inputArgs['parametersfile'],jobID=1)
        subprocess.run([filename])
        return

    if scheduler == 'PBS':
        command.append('qsub')
    elif scheduler == 'slurm':
        command.append('sbatch')

    if inputArgs['testing'] in ['interactive', 'interactivetestqueue']:
            command.append('-I')
            capture_output = False
    elif doArrayJobs is True or len(jobList) == 1:

        formattedList = ','.join(jobList)
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


def MakeSlurmRunscript(parameters,filename,originalParametersFile,kappa,doArrayJobs,nthConfig=1,numjobs=1,testing=None,*args,**kwargs):
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
    schedulerDetails = parameters['slurmParams']

    #Adjusting parameters based on the test run type. Also checking if a test
    #queue exists
    if testing == 'testqueue':
        out = subprocess.run('sinfo',text=True,capture_output=True,shell=True)
        if 'test' not in out.stdout:
            raise ValueError('Test queue does not exist on your machine. Try "-t headnode" or "-t interactive".')
        else:
            schedulerDetails['queue'] = 'test'
            schedulerDetails['time'] = '00:05:00'
            schedulerDetails['memory'] = 16    
    elif testing == 'fullqueue':
        schedulerDetails['time'] = '02:00:00'
    elif testing == 'interactive':
        raise ValueError('Interactive jobs not presently supported by slurm. Try "-t headnode".')


    
    template = Path(schedulerDetails['runscriptTemplate'])
    runscript = Path(filename)
    text = template.read_text()
    for key,value in schedulerDetails.items():
        text = text.replace(key,str(value))
    text = text.replace('ORIGINALPARAMETERSFILE',originalParametersFile)
    text = text.replace('PARAMETERSDIR',dirs.FullDirectories(parameters,directory='parameters')['parameters'])
    text = text.replace('KAPPA',str(kappa))
    text = text.replace('NTHCONFIG',str(nthConfig))
    text = text.replace('NUMJOBS',str(numjobs))
    text = text.replace('TESTING',str(testing))
    
    runscript.write_text(text)


def MakePBSRunscript(parameters,filename,originalParametersFile,kappa,doArrayJobs,nthConfig=1,numjobs=1,testing=None,*args,**kwargs):
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
        
    if testing in ['testqueue','interactivetestqueue']:
        out = subprocess.run('qstat -Q',text=True,capture_output=True,shell=True)
        #Gadi test queue is called express
        if 'express' not in out.stdout:
            raise ValueError('Test queue does not exist on your machine. Try "-t headnode" or "-t interactive".')
        else:
            schedulerDetails['queue'] = 'express'
            schedulerDetails['time'] = '01:00:00'
            schedulerDetails['memory'] = 16
            schedulerDetails['numCPUs'] = 4
    elif testing == 'fullqueue':
        schedulerDetails['time'] = '02:00:00'


        
    template = Path(schedulerDetails['runscriptTemplate'])
    runscript = Path(filename)
    text = template.read_text()
    for key,value in schedulerDetails.items():
        text = text.replace(key,str(value))
    text = text.replace('ORIGINALPARAMETERSFILE',originalParametersFile)
    text = text.replace('PARAMETERSDIR',dirs.FullDirectories(parameters,directory='parameters')['parameters'])
    text = text.replace('KAPPA',str(kappa))
    text = text.replace('NTHCONFIG',str(nthConfig))
    text = text.replace('NUMJOBS',str(numjobs))
    text = text.replace('TESTING',str(testing))
    
    runscript.write_text(text)

    
# def MissingCfunList(kappa,kd,shift,runPrefix,start,ncon,sinkType,*args,**kwargs):
#     '''
#     Returns a list of configurations for which cfuns are missing.

#     Returned list is comma separated string of integers. Integers are not
#     configuration IDs, the i'th integer is the i'th missing configuration.

#     Arguments:
#     kappa     -- int: kappa value of the particular job
#     kd        -- int: field strength of the particular job
#     shift     -- str: lattice shift of the particular job
#     runPrefix -- char: PACS-CS configuration label
#     start     -- int: The first configuration number. Eg 1880
#     ncon      -- int: The total number of configurations
#     sinkType  -- str: The sink type

#     Returns:
#     missingCfuns -- str list: str list of integers labelling missing configurations.
#     '''

#     #Loading parameters
#     parameters = params.Load()

#     #Getting base cfun directory
#     cfunPrefix = dirs.FullDirectories(directory='cfun',kappa=kappa,kd=kd,shift=shift,**parameters['runValues'],**parameters['sourcesink'])['cfun']

#     #COLA is dumb in the way it puts information about the sink into the
#     #cfun name, we have to simulate that behaviour here
#     if sinkType == 'smeared':
#         sinkLabel = 'sismVAL'    #Hard coded into COLA
#         sinkVals = parameters['sourcesink']['sweeps_smsnk']
#     if sinkType == 'laplacian':
#         #Changing modes to val to simplify things later
#         sinkLabel = parameters['sourcesink']['baseSinkCode'].replace('MODES','VAL')
#         sinkVals = parameters['sourcesink']['nModes_lpsnk']
    
#     #initialising output list
#     missing = []
#     #Looping through structures and particles
#     for structure in parameters['runValues']['structureList']:
#         for particlePair in parameters['runValues']['particleList']:
            
#             #Compiling cfun filename and path
#             particleName = ''.join(particlePair)
#             structureString = ''.join(structure)
#             baseCfunPath = f'{cfunPrefix}CONFIGIDSINKLABEL.{particleName}_{structureString}.u.2cf'

#             #Looping through the sink values desired
#             for sinkVal in sinkVals:
#                 label = sinkLabel.replace('VAL',str(sinkVal))
#                 cfunPath = baseCfunPath.replace('SINKLABEL',label)
#                 #Looping through configurations
#                 for i in range(1,ncon+1):
#                     #If configuration is already seen to be missing, don't need to check again
#                     if str(i) in missing:
#                         continue
#                     #Replacing base path with specific config ID
#                     ID = cfg.ConfigID(i,runPrefix,start)
#                     finalPath = cfunPath.replace('CONFIGID',ID)
            
#                     #Checking cfun existence
#                     if os.path.isfile(finalPath) is False:
#                         missing.append(str(i))

#     return missing



    
def main(nthConfig,inputArgs):
    print(f'Time is {datetime.now()}')

    parametersFile = inputArgs['parametersfile']
    parameters = params.Load(parametersFile=parametersFile)

    SubmitJobs(parameters,nthConfig,inputArgs,parameters['runValues'])

