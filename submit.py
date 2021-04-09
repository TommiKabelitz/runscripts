import os
import pathlib
import subprocess

import configIDs as cfg
import directories as dirs
import runparams as rp

def runvals():
    kappa_vals = [13770]
    kds = [1]   #field strengths
    shifts = ['x00t00']
    run_prefix = 'a'
    source_type = 'sm'
    sink_type = 'sm'
    return locals()



def submit_jobs(kappa_vals,kds,shifts,run_prefix,source_type,sink_type,**kwargs):
    
    #Creating directory for the runscript to go in
    directory = dirs.FullDirectories(directory='script')['script']

    #Looping over list of parameters to submit
    for kappa in kappa_vals:
        for kd in kds:        
            for shift in shifts:

                print('kappa: ',str(kappa))
                print('kd: ',str(kd))
                print('shift: ',shift)
                print('run_prefix: ',run_prefix)

                #sbatch runscript file
                filename = directory + run_prefix + str(kappa) + str(kd) + shift

                #Getting first ID eg. 1880 and num configurations eg. 400 for gauge fields
                start, ncon = cfg.configDetails(kappa,run_prefix)
                print(f'(start,ncon):({start},{ncon})\n')

                #Runscript to run with sbatch
                make_runscript(filename,kappa,kd,shift,run_prefix,start,ncon,source_type,sink_type)
                subprocess.run(['chmod','+x',filename])
                
                #Submitting jobs
                #runDetails = subprocess.run(['sbatch',f'--array=0-{ncon}',filename3])
                runDetails = subprocess.run(['sbatch',f'--array=1-1',filename3])
                
                #Checking whether slurm threw an error
                runDetails.check_returncode()



def make_runscript(filename,kappa,kd,shift,run_prefix,start,ncon,source_type,sink_type):

    
    with open(filename,'w') as f:

        slurm_details = rp.slurm_params()
        write_slurm_details(f,**slurm_details)
        set_memory_params(f)

        f.write(f'python /home/a1724542/PhD/runscripts/make_propagators.py {kappa} {kd} {shift} {run_prefix} {start} {ncon} {source_type} {sink_type} $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID\n')



def write_slurm_details(f,partition,nodes,ntasks,time,numGPUs,memory,qos,**kwargs):
    f.write(f'#!/bin/bash\n')
    f.write(f'#SBATCH --partition={partition}\n')
    f.write(f'#SBATCH --nodes={nodes}\n')
    f.write(f'#SBATCH --ntasks={ntasks}\n')
    f.write(f'#SBATCH --time={time}\n')
    f.write(f'#SBATCH --gres=gpu:{numGPUs}\n')
    f.write(f'#SBATCH --mem={memory}GB\n')
    #f.write(f'#SBATCH --qos={qos}\n')

def set_memory_params(f):
    
    f.write('echo Running on host `hostname`\n')
    f.write('echo Time is `date`\n')
    f.write('source /home/a1724542/pho_modules.sh\n')
    f.write('ulimit -s unlimited\n')
    f.write('ulimit -c 0\n')
    f.write('ulimit -a\n')
        
if __name__ == '__main__':

    os.chdir(dirs.FullDirectories(directory='slurm')['slurm'])
    values = runvals()

    submit_jobs(**values)
