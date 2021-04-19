import argparse
import os
import pathlib
import subprocess

import configIDs as cfg
import directories as dirs
import runparams as rp

script = '/home/a1724542/PhD/runscripts/make_propagators.py'

def RunValues():
    kappa_vals = [13770]
    kds = [1]   #field strengths
    shifts = ['x00t00']
    run_prefix = 'a'
    source_type = 'sm'
    sink_type = 'sm'
    return locals()



def SubmitJobs(kappa_vals,kds,shifts,run_prefix,source_type,sink_type,testing,**kwargs):
    
    #Creating directory for the runscript to go in
    directory = dirs.FullDirectories(directory='script')['script']

    #Looping over list of parameters to submit
    for kappa in kappa_vals:
        for kd in kds:        
            for shift in shifts:

                print('\nkappa: ',str(kappa))
                print('kd: ',str(kd))
                print('shift: ',shift)
                print('run_prefix: ',run_prefix)

                #sbatch runscript file
                filename = directory + run_prefix + str(kappa) + str(kd) + shift

                #Getting first ID eg. 1880 and num configurations eg. 400 for gauge fields
                start, ncon = cfg.ConfigDetails(kappa,run_prefix)
                print(f'(start,ncon):({start},{ncon})')

                #Runscript to run with sbatch
                MakeRunscript(filename,kappa,kd,shift,run_prefix,start,ncon,source_type,sink_type,testing)
                subprocess.run(['chmod','+x',filename])
                
                #Submitting jobs
                if testing is False:
                    #subprocess.run(['sbatch',f'--array=0-{ncon}',filename])
                    subprocess.run(['sbatch',f'--array=1-1',filename])
                else:
                    subprocess.run([filename])
                




def MakeRunscript(filename,kappa,kd,shift,run_prefix,start,ncon,source_type,sink_type,testing):

    #Open the runscript
    with open(filename,'w') as f:
        #Getting slurm request details, ie. partition, num nodes, gpus etc.
        slurm_details = rp.SlurmParams()
        
        WriteSlurmDetails(f,**slurm_details)
        WriteMemoryParams(f)
        
        if testing is True:
            f.write('SLURM_ARRAY_JOB_ID=1\n')
            f.write('SLURM_ARRAY_TASK_ID=1\n')

        #Write the propagator execution line
        f.write(f'python {script} {kappa} {kd} {shift} {run_prefix} {start} {ncon} {source_type} {sink_type} $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID\n')



def WriteSlurmDetails(f,partition,nodes,ntasks,time,numGPUs,memory,qos,output,**kwargs):
    f.write(f'#!/bin/bash\n')
    f.write(f'#SBATCH --partition={partition}\n')
    f.write(f'#SBATCH --nodes={nodes}\n')
    f.write(f'#SBATCH --ntasks={ntasks}\n')
    f.write(f'#SBATCH --time={time}\n')
    f.write(f'#SBATCH --gres=gpu:{numGPUs}\n')
    f.write(f'#SBATCH --mem={memory}GB\n')
    #f.write(f'#SBATCH --qos={qos}\n')
    f.write(f'#SBATCH --output={output}\n')



def WriteMemoryParams(f):
    f.write('echo Running on host `hostname`\n')
    f.write('echo Time is `date`\n')
    f.write('source /home/a1724542/pho_modules.sh\n')
    f.write('ulimit -s unlimited\n')
    f.write('ulimit -c 0\n')
    f.write('ulimit -a\n')
    

    
def Input():
    
    parser = argparse.ArgumentParser(description='Submits jobs to the queue. Produces propagators and correlation functions')

    parser.add_argument('-t','--testing',help='Skips queue submission, runs on head node',action='store_true')
    args = parser.parse_args()
    return vars(args)
    


if __name__ == '__main__':

    values = {**RunValues(),**Input()}

    SubmitJobs(**values)
    
    subprocess.run('echo Time is `date`',shell=True)
