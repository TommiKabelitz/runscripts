
def slurm_params():
    partition = 'batch'
    nodes = 1
    ntasks = 4
    time = '5:00:00'
    numGPUs = 4
    memory = 64 #in GB
    qos = 'gxl'
    return locals()
