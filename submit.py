'''
Submits jobs to the queue. Making propagators then correlation functions.

Based on the parameters set in the jobValues section of the parameters.yml 
file, creates bash scripts to be called by the scheduler to make propagators
and correlation functions. 

The bash scripts will call manageJob.py which manages the running of the 
job on the node.

Optional command line arguments are available for testing purposes.

'''

#standard library modules
import argparse                      #input parsing
import subprocess                    #for running scripts
from datetime import datetime        #for writing out the time

#local modules
import configIDs as cfg
import directories as dirs
import parameters as params


def SubmitJobs(kappaValues,kds,shifts,runPrefix,testing=None,*args,**kwargs):
    '''
    Submits jobs to the queue.

    kappaValues, kds, shifts are looped over. 

    Arguments:
    kappaValues -- int list: kappa values to loop over
    kds         -- int list: field strength to loop over
    shifts      -- str list: lattice shifts to loop over
    runPrefix   -- char:     PACS-CS configuration label
    testing     -- str:      what type of testing submission to do
    '''

    #Getting the directory for the runscript
    directory = dirs.FullDirectories(directory='script')['script']

    #Looping over parameters to submit
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

                #Making the runscript
                MakeRunscript(filename,kappa,kd,shift,testing)
                subprocess.run(['chmod','+x',filename]) #executable permission
            
                #Submitting jobs
                if testing is None: #normal array submission
                    subprocess.run(['sbatch',f'--array=1-{ncon}',filename])
                elif testing in ['fullqueue','testqueue']:
                    #submitting only 1 configuration
                    subprocess.run(['sbatch',f'--array=2-2',filename])
                elif testing == 'headnode':
                    #just running on the head node
                    subprocess.run([filename])
                




def MakeRunscript(filename,kappa,kd,shift,testing=None,*args,**kwargs):
    '''
    Makes the runscript to be called by the scheduler.
    
    The runscript does the basic submission before calling manageJob.py
    which manages the rest of the job.

    Arguments:
    filename -- str: the name of the file to make
    kappa    -- int: kappa value of the particular job
    kd       -- int: field strength of the particular job
    shift    -- str: lattice shift of the particular job
    testing  -- str: type of test submission

    '''
    #Getting slurm request details, ie. partition, num nodes, gpus etc.
    slurmDetails = params.params()['slurmParams']
    
    #Job management script
    script = params.params()['directories']['runscriptDir'] + 'manageJob.py'
    #Script to load modules
    modules = params.params()['directories']['modules']

    #adjusting some slurm parameters for submission to the test queue
    if testing =='testqueue':
        slurmDetails['partition'] = 'test'
        slurmDetails['time'] = '00:30:00'
        slurmDetails['memory'] = 16
    
    #The location for the slurm output files to be dumped
    output = dirs.FullDirectories(directory='slurm')['slurm']+'slurm-%A_%a.out'

    #Open the runscript
    with open(filename,'w') as f:
        #Writing the slurm details to the script
        WriteSlurmDetails(f,output=output,**slurmDetails)
        
        #Writing other stuff to the script.
        WriteOtherDetails(f,modules)
        
        #Simulating Slurm values for running on head node
        #The scheduler assigns the TASK and JOB ids to each job
        #so we need to simulate their existence
        if testing == 'headnode':
            f.write('SLURM_ARRAY_JOB_ID=1\n')
            f.write('SLURM_ARRAY_TASK_ID=1\n')

        #Write the line which calls the python job script
        f.write(f'python {script} {kappa} {kd} {shift} $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID\n')




def WriteSlurmDetails(fileObject,partition,time,output,nodes,numCPUs,numGPUs,memory,*args,**kwargs):
    '''
    Writes the parameters for the slurm scheduler to the runscript.

    Arguments:
    fileObject -- file object: an open file to write to
    partition  -- str: the partition to submit to
    time       -- str: the time allowed for the run in format D-HH:MM:SS
    output     -- str: the location for the slurm output files to be placed
    nodes      -- int: the number of nodes to request 
    numCPUs    -- int: the number of CPUs to request
    numGPUs    -- int: the number of GPUs to request
    memory     -- int: the amount of in job memory to request
    
    '''

    #Printing a couple of relevant details to the screen for checking
    print( f'Partition: {partition}\n'
          +f'Nodes: {nodes}\n'
          +f'Time: {time}\n')

    #Writing everything to the file
    fileObject.write(f'#!/bin/bash\n')
    fileObject.write(f'#SBATCH --partition={partition}\n')
    fileObject.write(f'#SBATCH --nodes={nodes}\n')
    fileObject.write(f'#SBATCH --ntasks={numCPUs}\n')
    fileObject.write(f'#SBATCH --time={time}\n')
    fileObject.write(f'#SBATCH --mem={memory}GB\n')
    fileObject.write(f'#SBATCH --output={output}\n')
    if partition != 'test':
        fileObject.write(f'#SBATCH --gres=gpu:{numGPUs}\n')
    


def WriteOtherDetails(fileObject,modules,*args,**kwargs):
    '''
    Writes non-scheduler related details to the runscript.

    Arguments:
    fileObject -- fileObject: an open file to write to
    modules    -- str: the path to a script to load the required modules

    '''

    fileObject.write('echo Running on host `hostname`\n')
    fileObject.write(f'source {modules}\n')
    #Unlimiting stack size
    fileObject.write('ulimit -s unlimited\n')
    #Limiting the size of core dump files such that cannot be made.
    #If not limited, code crashing while running will very quickly do a lot of
    #damage
    fileObject.write('ulimit -c 0\n')
    #Showing status of stack and core dump limits
    fileObject.write('ulimit -a\n')
    

    
def Input():
    '''
    Parses input from the command line.

    Only needed for testing purposes.
    Returns:
    inputDict -- dict: Contains only one pair. Key is testing. Value is None or
                       one of the choices given below.

    '''

    #Setting up the parser
    parser = argparse.ArgumentParser(description='Submits jobs to the queue. Produces propagators and correlation functions.')

    #Adding the testing argument
    parser.add_argument('-t','--testing',help='run in testing mode. Runs on head node (no GPUs). Else submits only 1 configuration to either the test queue (no GPUs) or the full queue.',choices=['headnode','testqueue','fullqueue'])

    #Parsing the arguments from the command line
    args = parser.parse_args()
    #Turning the namespace into a dictionary
    inputDict = vars(args)
    return inputDict
    

if __name__ == '__main__':

    print(f'Time is {datetime.now()}')

    #Combining the run parameters from the parameters.yml file with
    #the input specifications from the command line
    values = {**params.params()['runValues'],**Input()}


    SubmitJobs(**values)
    

