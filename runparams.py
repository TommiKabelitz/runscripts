'''
Module containing the parameters to be passed to the job scheduler.
'''

import directories as dirs

def SlurmParams(partition=None,*args,**kwargs):

    #Default mode
    if partition is None:
        partition = 'batch'
        nodes = 1
        ntasks = 4 #num CPUs
        time = '2:00:00'
        numGPUs = 2
        memory = 64 #in GB

    #Submitting to test queue
    if partition == 'test':
        nodes = 1
        ntasks = 1 #num CPUs
        time = '05:00'
        numGPUs = 1
        memory = 16 #in GB

    qos = 'gxl'
    #Put slurm output files into subdirectory of runscripts file.
    # %A is $SLURM_ARRAY_JOB_ID, %a is $SLURM_ARRAY_TASK_ID
    output = dirs.FullDirectories(directory='slurm')['slurm']+'slurm-%A_%a.out'
    return locals()
