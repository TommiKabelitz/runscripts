'''
Manages the job, calling makePropagator.py and makeCfun.py.

Is called by the basic slurm runscript in ./scripts after modules are loaded 
and memory requirements are dealt with.

Should not be called manually from the command line.

Input arguments pass the job specific values in so that they can be fed to 
makePropagator.py and makeCfun.py.

'''

#standard library modules
import argparse                      #input parsing
from datetime import datetime        #for writing out the time
import pathlib                       #for deleting props

#local modules
from colarunscripts import configIDs as cfg
from colarunscripts import makePropagator
from colarunscripts import makeCfun
from colarunscripts import parameters as params


def main():

    #Getting job specific values from command line
    inputValues = Input()
  
    #Combining job specific values with the runValues from parameters.yml
    jobValues = {**inputValues,**params.Load()['runValues']}
    
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

        doConfiguration(jobValues)



def doConfiguration(jobValues,*args,**kwargs):

    #Compiling the full configuration identification number
    jobValues['cfgID'] = cfg.ConfigID(**jobValues)
        
    print(50*'_')
    print()

    #That's it for preparation of job values. Now start making propagators
    #and correlation functions

    print(50*'_')
    print()
    print('Making propagators')
    print(f'Time is {datetime.now()}')
    propPaths = makePropagator.main(jobValues)
    print("\nPropagators done")
    print(f'Time is {datetime.now()}')
    print(50*'_')

    print()        
    print('Making correlation functions')
    print(f'Time is {datetime.now()}')    
    makeCfun.main(jobValues)
    print("Correlation functions done")
    print(f'Time is {datetime.now()}')
    print(50*'_')
    print()

    #removing the propagator
    if jobValues['keepProps'] is False:
        print('Deleting Propagators')
        for prop in propPaths:
            path = pathlib.Path(prop)
            pathlib.unlink(path,missing_ok=True)



def PrintJobValues(jobValues):
    '''
    Prints the values specific to the current job to the screen.

    Allows easy checking of run values in the job output file.
    
    Arguments:
    jobValues -- dict: Dictionary containing the variables to print out

    '''
    
    #A list of the variables to print
    #(some variables in there are a waste of time)
    valuesToPrint = ['cfgID',
                     'kappa',
                     'kd',
                     'shift',
                     'sinkType',
                     'sourceType',
                     'structureList']

    print('JobValues:')
    #Printing the values
    for key in valuesToPrint:
        try:
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
