import directories as dirs
def SlurmParams():
    # partition = 'batch'
    # nodes = 1
    # ntasks = 4 #num CPUs
    # time = '2:00:00'
    # numGPUs = 2
    # memory = 64 #in GB
    qos = 'gxl'
    output = dirs.FullDirectories(directory='slurm')['slurm']+'slurm-%A_%a.out'

    partition = 'test'
    nodes = 1
    ntasks = 1 #num CPUs
    time = '05:00'
    numGPUs = 1
    memory = 16 #in GB

    return locals()
