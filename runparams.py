
def SlurmParams():
    partition = 'batch'
    nodes = 1
    ntasks = 4 #num CPUs
    time = '2:00:00'
    numGPUs = 2
    memory = 64 #in GB
    qos = 'gxl'
    return locals()
