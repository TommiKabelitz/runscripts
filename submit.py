import argparse
import os
import pathlib
import subprocess
from datetime import datetime

import configIDs as cfg
import directories as dirs
import parameters as params

#Script to be called within the job
script = '/home/a1724542/PhD/runscripts/manageJob.py'



def SubmitJobs(kappaValues,kds,shifts,runPrefix,testing,*args,**kwargs):
    '''
    Submits jobs to the queue.

    kappaValues, kds, shifts are looped over
    Arguments:
    kappaValues -- int list: kappa values to loop over
    '''
    #Getting the directory for the runscript
    directory = dirs.FullDirectories(directory='script')['script']

    #Looping over list of parameters to submit
    for kappa in kappaValues:
        for kd in kds:        
            for shift in shifts:

                print()
                print('kappa: ',str(kappa))
                print('kd: ',str(kd))
                print('shift: ',shift)
                print('runPrefix: ',runPrefix)

                #Compiling the runscript filename
                filename =f'{directory}{runPrefix}{kappa}BF{kd}{shift}'

                #Getting first ID eg. 1880 and num configurations eg. 400 for gauge fields
                start, ncon = cfg.ConfigDetails(kappa,runPrefix)
                print(f'(start,ncon):({start},{ncon})')

                #Runscript to run with sbatch
                MakeRunscript(filename,kappa,kd,shift,testing)
                subprocess.run(['chmod','+x',filename])
            
                #Submitting jobs
                if testing is None:
                    subprocess.run(['sbatch',f'--array=1-{ncon}',filename])
                elif testing in ['fullqueue','testqueue']:
                    subprocess.run(['sbatch',f'--array=1-1',filename])
                elif testing == 'headnode':
                    subprocess.run([filename])
                




def MakeRunscript(filename,kappa,kd,shift,testing):

    #Getting slurm request details, ie. partition, num nodes, gpus etc.
    slurmDetails = params.params()['slurmParams']

    if testing =='testqueue':
        slurmDetails['partition'] = 'test'
        slurmDetails['time'] = '00:30:00'
        slurmDetails['memory'] = 16

    #Open the runscript
    with open(filename,'w') as f:
        
        output = dirs.FullDirectories(directory='slurm')['slurm']+'slurm-%A_%a.out'
        WriteSlurmDetails(f,output=output,**slurmDetails)
        WriteMemoryParams(f)
        
        #Simulating Slurm values for running on head node
        if testing == 'headnode':
            f.write('SLURM_ARRAY_JOB_ID=1\n')
            f.write('SLURM_ARRAY_TASK_ID=1\n')

        #Write the line which calls the python job script
        f.write(f'python {script} {kappa} {kd} {shift} $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID\n')




def WriteSlurmDetails(f,partition,nodes,numCPUs,time,numGPUs,memory,output,**kwargs):

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
    if partition != 'test':
        f.write(f'#SBATCH --gres=gpu:{numGPUs}\n')
    


def WriteMemoryParams(f):
    f.write('echo Running on host `hostname`\n')
    f.write('source /home/a1724542/pho_modules.sh\n')
    f.write('ulimit -s unlimited\n')
    f.write('ulimit -c 0\n')
    f.write('ulimit -a\n')
    

    
def Input():
    
    parser = argparse.ArgumentParser(description='Submits jobs to the queue. Produces propagators and correlation functions.')

    parser.add_argument('-t','--testing',help='run in testing mode. Runs on head node (no GPUs). Else submits only 1 configuration to either the test queue (no GPUs) or the full queue.',choices=['headnode','testqueue','fullqueue'])
    args = parser.parse_args()
    return vars(args)
    


if __name__ == '__main__':

    print(f'Time is {datetime.now()}')

    values = {**params.params()['runValues'],**Input()}

    SubmitJobs(**values)
    

