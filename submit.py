
import configIDs as cfg
import subprocess
import os
import runparams as rp

def runvals():
    kappa_vals = [13770]
    kds = [-1,0,1]
    shifts = ['x00t00','x16t8']
    run_prefix = 'a'
    source_type = 'sm'
    sink_type = 'sm'
    return locals()


def submit_jobs(kappa_vals,kds,shifts,run_prefix,source_type,sink_type,**kwargs):
    filename = os.getcwd()+'/scripts/'+run_prefix 
    for kappa in kappa_vals:
        filename1 = filename + str(kappa)

        for kd in kds:
            filename2 = filename1 + str(kd)

            for shift in shifts:
                filename3 = filename2 + shift

                print('kappa: ',str(kappa))
                print('kd: ',str(kd))
                print('shift: ',shift)
                print('run_prefix: ',run_prefix)

                start, ncon = cfg.configDetails(kappa,run_prefix)
                make_runscript(filename3,kappa,kd,shift,run_prefix,start,ncon,source_type,sink_type)
                subprocess.call(['chmod','+x',filename3])
                errorcode = subprocess.call(['sbatch',f'--array=0-{ncon}',filename3])
                #print(f"sbatch --array=0-{ncon} {filename3}")
                if errorcode != 0:
                    print(errorcode)
                
def make_runscript(filename,kappa,kd,shift,run_prefix,start,ncon,source_type,sink_type):

    with open(filename,'w') as f:

        slurm_details = rp.slurm_params()
        write_slurm_details(f,**slurm_details)

        f.write(f'python ../make_propagators.py {kappa} {kd} {shift} {run_prefix} {start} {ncon} {source_type} {sink_type} $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID\n')


def write_slurm_details(f,partition,nodes,ntasks,time,numGPUs,memory,qos,**kwargs):
    f.write(f'#!/bin/bash\n')
    f.write(f'#SBATCH --partition={partition}\n')
    f.write(f'#SBATCH --nodes={nodes}\n')
    f.write(f'#SBATCH --ntasks={ntasks}\n')
    f.write(f'#SBATCH --time={time}\n')
    f.write(f'#SBATCH --gres=gpu:{numGPUs}\n')
    f.write(f'#SBATCH --mem={memory}GB\n')
    f.write(f'#SBATCH --qos={qos}\n')


def submit_jobs(kappa_vals,kd,shifts,run_prefix,**kwargs):
    
    for kappa in kapp_vals:
        for kd in kds:
            for shift in shifts:
                print('kappa: ',str(kappa))
                print('run_prefix: ',run_prefix)
                print('kd: ',str(kd))
                print('shift: ',shift)


    
if __name__ == '__main__':


    values = runvals()

    submit_jobs(**values)
    
    return locals()

                
    



