import argparse
import os
import pathlib
import subprocess
from datetime import datetime

import configIDs as cfg
import directories as dirs
import parameters as params

script = '/home/a1724542/PhD/runscripts/manageJob.py'

def SubmitJobs(kappaValues,kds,shifts,runPrefix,sourceType,sinkType,testing,**kwargs):

    #Creating directory for the runscript to go in
    directory = dirs.FullDirectories(directory='script')['script']

    #Looping over list of parameters to submit
    for kappa in kappaValues:
        for kd in kds:        
            for shift in shifts:

                print('\nkappa: ',str(kappa))
                print('kd: ',str(kd))
                print('shift: ',shift)
                print('runPrefix: ',runPrefix)

                #sbatch runscript file
                filename =f'{directory}{runPrefix}{kappa}BF{kd}{shift}'

                #Getting first ID eg. 1880 and num configurations eg. 400 for gauge fields
                start, ncon = cfg.ConfigDetails(kappa,runPrefix)
                print(f'(start,ncon):({start},{ncon})')

                #Runscript to run with sbatch
                MakeRunscript(filename,kappa,kd,shift,runPrefix,start,ncon,sourceType,sinkType,testing)
                subprocess.run(['chmod','+x',filename])
            
                #Submitting jobs
                if testing != 'headnode':
                    #subprocess.run(['sbatch',f'--array=1-{ncon}',filename])
                    subprocess.run(['sbatch',f'--array=1-1',filename])
                else:
                    subprocess.run([filename])
                




def MakeRunscript(filename,kappa,kd,shift,runPrefix,start,ncon,sourceType,sinkType,testing):

    partition = None
    if testing =='testqueue':
        partition = 'test'

    #Open the runscript
    with open(filename,'w') as f:

        #Getting slurm request details, ie. partition, num nodes, gpus etc.
        slurm_details = params.params()['slurmParams']
        
        output = dirs.FullDirectories(directory='slurm')['slurm']+'slurm-%A_%a.out'

        WriteSlurmDetails(f,testing,output=output,**slurm_details)
        WriteMemoryParams(f)
        
        #Simulating Slurm values for running on head node
        if testing == 'headnode':
            f.write('SLURM_ARRAY_JOB_ID=1\n')
            f.write('SLURM_ARRAY_TASK_ID=1\n')

        #Write the propagator execution line
        f.write(f'python {script} {kappa} {kd} {shift} $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID\n')
        #f.write(f'python {script} {kappa} {kd} {shift} {runPrefix} {start} {ncon} {sourceType} {sinkType} $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID\n')



def WriteSlurmDetails(f,testing,partition,nodes,numCPUs,time,numGPUs,memory,output,**kwargs):

    print( f'Partition: {partition}\n'
          +f'Nodes: {nodes}\n'
          +f'Time: {time}\n')

    f.write(f'#!/bin/bash\n')
    f.write(f'#SBATCH --partition={partition}\n')
    f.write(f'#SBATCH --nodes={nodes}\n')
    f.write(f'#SBATCH --ntasks={numCPUs}\n')
    f.write(f'#SBATCH --time={time}\n')
    f.write(f'#SBATCH --mem={memory}GB\n')
    f.write(f'#SBATCH --output={output}\n')
    if testing is None:
        f.write(f'#SBATCH --gres=gpu:{numGPUs}\n')
    


def WriteMemoryParams(f):
    f.write('echo Running on host `hostname`\n')
    f.write('source /home/a1724542/pho_modules.sh\n')
    f.write('ulimit -s unlimited\n')
    f.write('ulimit -c 0\n')
    f.write('ulimit -a\n')
    

    
def Input():
    
    parser = argparse.ArgumentParser(description='Submits jobs to the queue. Produces propagators and correlation functions.')

    parser.add_argument('-t','--testing',help='run in testing mode, either on head node, or to test queue',choices=['headnode','testqueue'])
    args = parser.parse_args()
    return vars(args)
    


if __name__ == '__main__':

    print(f'Time is {datetime.now()}')

    values = {**params.params()['runValues'],**Input()}

    SubmitJobs(**values)
    

