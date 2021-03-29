import configIDs as cfg
import subprocess

def runvals():
    kappa_vals = [13770]
    kds = [-1,0,1]
    shifts = ['x00t00','x16t8']
    run_prefix = 'a'
    return locals()


def submit_jobs(kappa_vals,kds,shifts,run_prefix,**kwargs):
    filename = './scripts/'+run_prefix 
    for kappa in kappa_vals:
        filename1 = filename + str(kappa)

        for kd in kds:
            filename2 = filename1 + str(kd)

            for shift in shifts:
                filename3 = filename2 + shift

                print('kappa: ',str(kappa))
                print('run_prefix: ',run_prefix)
                print('kd: ',str(kd))
                print('shift: ',shift)

                start, ncon = cfg.configIDs(kappa,run_prefix)
                make_runscript(filename,kappa,kd,shift,run_prefix,start,ncon)
                errorcode = subprocess.call(['sbatch',f'--array=0-{ncon}',filename3)
                #print(f"sbatch --array=0-{ncon} {filename3}")
                if errorcode != 0:
                    print(errorcode)
                
def make_runscript(filename,kappa,kd,shift,run_prefix,start,ncon):

    with open(filename,'w') as f:
        f.write('#!/bin/tcsh\n')
        f.write('#SBATCH -p batch\n')
        f.write('#SBATCH -N 1\n')
        f.write('#SBATCH -n 4\n')
        f.write('#SBATCH --time=5:00:00\n')
        f.write('#SBATCH --gres=gpu:4\n')
        f.write('#SBATCH --mem=64GB\n')
        f.write('#SBATCH --qos=gxl\n')

        f.write(f'kappa = {kappa}\n')
        f.write(f'kd = {kd}\n')
        f.write(f'shift = {shift}\n')
        f.write(f'run_prefix = {run_prefix}\n')
        f.write(f'start = {start}\n')
        f.write(f'ncon = {ncon}\n')

        f.write('python make_propagators.py\n')



                    

if __name__ == '__main__':

    print('yeet')
    values = runvals()

    submit_jobs(**values)
    


