'''
Manages the job, calling makePropagator.py, makeCfun.py makeEmodes.py.

Is called by the basic slurm runscript in ./scripts after modules are loaded 
and memory requirements are dealt with.

Should not be called manually from the command line.

Input arguments pass the job specific values in so that they can be fed to 
makePropagator.py, makeCfun.py makeEmodes.py.

'''

#standard library modules
import argparse                      #input parsing
from datetime import datetime        #for writing out the time
import pathlib                       #for deleting props
import pprint                        #nice dictionary printing (for debugging)

#local modules
from colarunscripts import configIDs as cfg
from colarunscripts import makeCfun
from colarunscripts import makeEmodes
from colarunscripts import makePropagator
from colarunscripts import parameters as params
from colarunscripts import simpleTime

#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 

def main():

    #Initialising the timer
    timer = simpleTime.Timer('Overall')
    timer.initialiseTimer('Eigenmodes')
    timer.initialiseTimer('Propagators')
    timer.initialiseTimer('Correlation functions')
    timer.initialiseCheckpoints()
    
    #Getting job specific values from command line
    inputValues = Input()
  
    #Combining job specific values with the runValues from parameters.yml
    jobValues = {**inputValues,**params.Load()['runValues']}

    print()
    PrintJobValues(jobValues)
    ##Getting details about the configurations to use
    #Starting number and total number of configurations for the specified 
    #kappa and configuration label (runPrefix)
    jobValues['start'],jobValues['ncon'] = cfg.ConfigDetails(**jobValues)

    #if we are not using array jobs, we need to loop over 
    #all configurations. 
    #The ncon we set here is local, just for the loop. Value in jobValues is
    #used by prop and cfun routines so left untouched
    if jobValues['doArrayJobs'] is False:
        ncon = jobValues['ncon']
    else:
        ncon = 1
    
    for nthConfig in range(1,ncon+1):
        
        jobValues['nthConfig'] = nthConfig

        doConfiguration(jobValues,timer)
    
    print(50*'_')
    print()
    #Writing report for how long everything took
    timer.writeFullReport(final=True)

def doConfiguration(jobValues,timer,*args,**kwargs):
    """
    Runs eigenmode, propagator and cfun code for the one configuration.

    Arguments:
    jobValues -- dict: Dictionary containing the job specific values such as
                           kd, shift, SLURM_ARRAY_TASK_ID, etc...
    timer     -- Timer: Timer object to manage timing of correlation function
                           calculation time.

    """

    #Compiling the full configuration identification number
    jobValues['cfgID'] = cfg.ConfigID(**jobValues)

    print(50*'_')
    print()

    #Creating a checkpoint as the configuration starts
    timer.createCheckpoint(f'Configuration {jobValues["cfgID"]}')
    
    #That's it for preparation of job values. Now start making propagators
    #and correlation functions

    if jobValues['sinkType'] == 'laplacian' or jobValues['sourceType'] == 'lp':
        print(50*'_')
        print()
        print('Making eigenmodes')
        print(f'Time is {datetime.now()}')
        eigenmodePaths = makeEmodes.main(jobValues,timer)
        print("\nEigenmodes done")
        print(f'Time is {datetime.now()}')
        print()
    else:
        eigenmodePath = []
        
    print(50*'_')
    print()
    print('Making propagators')
    print(f'Time is {datetime.now()}')
    propPaths = makePropagator.main(jobValues,timer)
    print("\nPropagators done")
    print(f'Time is {datetime.now()}')
    print(50*'_')

    print()        
    print('Making correlation functions')
    print(f'Time is {datetime.now()}')    
    makeCfun.main(jobValues,timer)
    print("Correlation functions done")
    print(f'Time is {datetime.now()}')
    print(50*'_')
    print()

    #Writing out how much time has elapsed since the checkpoint.
    #No longer need the checkpoint, so remove it.
    timer.writeCheckpoint(removeCheckpoint=True)
    print()
    
    #removing the propagator
    if jobValues['keepProps'] is False:
        print('Deleting Propagators')
        for prop in propPaths:
            path = pathlib.Path(prop)
            path.unlink(missing_ok=True)
    
    if jobValues['keepEmodes'] is False and eigenmodePaths != []:
        print('Deleting Eigenmodes')
        for eigenMode in eigenmodePaths:
            path = pathlib.Path(eigenMode)
            path.unlink(missing_ok=True)
    

def PrintJobValues(jobValues):
    '''
    Prints the values specific to the current job to the screen.

    Allows easy checking of run values in the job output file.
    
    Arguments:
    jobValues -- dict: Dictionary containing the variables to print out

    '''
    
    #A list of the variables to print
    #(some variables in there are a waste of time)
    valuesToPrint = ['kappa',
                     'kd',
                     'shift',
                     'sinkType',
                     'sourceType',
                     'structureList',
                     'particleList']
    
    print('Job Values:')
    #Printing the values
    for key in valuesToPrint:
        try:
            if type(jobValues[key]) is list:
                print(f'{key}:')
                pp(jobValues[key])
            else:
                print(f'{key}: {jobValues[key]}')
        #just in case the key is not present (shouldn't happen)
        except KeyError:
            print(f'{key} not in JobValues')

def Input():
    '''
    Parses input from the command line.

    Parses the job specific values which are originally specified in 
    the loops of submit.py
    
    Returns:
    values -- dict: dictionary containing the values from the command line
    '''

    #Initialising the parser
    parser = argparse.ArgumentParser()

    #Adding the arguments to the parser
    parser.add_argument('kappa',type=int)
    parser.add_argument('kd',type=int)
    parser.add_argument('shift',type=str)
    parser.add_argument('jobID',type=str)
    parser.add_argument('nthConfig',type=str)
    
    #Actually parsing the command line input
    args = parser.parse_args()
    #Converting the input to a dictionary
    values = vars(args)
    return values




if __name__ == '__main__':
     
    main()
