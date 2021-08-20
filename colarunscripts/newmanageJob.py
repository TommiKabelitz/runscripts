#The execution of this file is not done (I think)
#Need to deal with how it gets called now.

import argparse
from datetime import datetime
import os
import pathlib
import pprint
import subprocess

from colarunscripts import configIDs as cfg
from colarunscripts import makeCfun
from colarunscripts import makeEmodes
from colarunscripts import makePropagator
from colarunscripts import parameters as params
from colarunscripts.shifts import CompareShifts
from colarunscripts import simpleTime 
from colarunscripts import submit
from colarunscripts.utilities import GetJobID


#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 


def main(originalParametersFile,newParametersFile,kappa,nthConfig,numSimultaneousJobs,testing,*args,**kwargs):

    parameters = params.Load(parametersFile=newParametersFile)
    jobValues = parameters['runValues']

    start,ncon = cfg.ConfigDetails(kappa,jobValues['runPrefix'])
    jobValues['nthConfig'] = nthConfig
    jobValues['cfgID'] = cfg.ConfigID(nthConfig,jobValues['runPrefix'],start)
    jobValues['jobID'] = GetJobID(os.environ)
    jobValues['kappa'] = kappa
    pp(jobValues)
    JobLoops(parameters,jobValues['shifts'],jobValues['kds'],jobValues)

    SubmitNext(nthConfig,numSimultaneousJobs,testing,newParametersFile,ncon)



def JobLoops(parameters,shifts,kds,jobValues,*args,**kwargs):

    timer = simpleTime.Timer('Overall')
    timer.initialiseCheckpoints()
    timer.initialiseTimer('Eigenmodes')
    timer.initialiseTimer('Propagators')
    timer.initialiseTimer('Correlation functions')
    
    for shift,nextShift in zip(shifts,[*shifts[1:],None]):
        for kd in kds:
            
            paths = doJobSet(parameters,kd,shift,jobValues,timer)
            

        #removing the propagators
        if jobValues['keepProps'] is False:
            print('All field strengths done, new shift, deleting propagators')
            for prop in paths['props']:
                print(f'Deleting {prop}')
                path = pathlib.Path(prop)
                path.unlink(missing_ok=True)
            print()    
    
        if jobValues['keepEmodes'] is CompareShifts(shift,nextShift) is False:
            print('Shifting in more than time, deleting eigenmodes')
            for eigenMode in paths['eigenmodes']:
                print(f'Deleting {eigenMode}')
                path = pathlib.Path(eigenMode)
                path.unlink(missing_ok=True)
            print()

        timer.writeFullReport(final=True)
        print()
        print(50*'_')    
        print()
        
def doJobSet(parameters,kd,shift,jobValues,timer,*args,**kwargs):
    """
    Runs eigenmode, propagator and cfun code for the one configuration.

    Arguments:
    jobValues -- dict: Dictionary containing the job specific values such as
                           kd, shift, SLURM_ARRAY_TASK_ID, etc...
    timer     -- Timer: Timer object to manage timing of correlation function
                           calculation time.

    """

    print(50*'_')
    print()

    #Creating a checkpoint as the configuration starts
    checkpointName = f'Set (kd,shift): ({kd},{shift})'
    timer.createCheckpoint(checkpointName)
    
    #That's it for preparation of job values. Now start making propagators
    #and correlation functions

    if jobValues['sinkType'] == 'laplacian' or jobValues['sourceType'] == 'lp':
        print(50*'_')
        print()
        print('Making eigenmodes')
        print(f'Time is {datetime.now()}')
        eigenmodePaths = makeEmodes.main(parameters,kd,shift,jobValues,timer)
        print("\nEigenmodes done")
        print(f'Time is {datetime.now()}')
        print()
    else:
        eigenmodePath = []
        
    print(50*'_')
    print()
    print('Making propagators')
    print(f'Time is {datetime.now()}')
    propPaths = makePropagator.main(parameters,kd,shift,jobValues,timer)
    print("\nPropagators done")
    print(f'Time is {datetime.now()}')
    print(50*'_')

    print()        
    print('Making correlation functions')
    print(f'Time is {datetime.now()}')    
    makeCfun.main(parameters,kd,shift,jobValues,timer)
    print("Correlation functions done")
    print(f'Time is {datetime.now()}')
    print(50*'_')
    print()

    #Writing out how much time has elapsed since the checkpoint.
    #No longer need the checkpoint, so remove it.
    timer.writeCheckpoint(removeCheckpoint=True)
    print()
    
    paths = {'eigenmodes':eigenmodePaths,'props':propPaths}
    return paths

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


def SubmitNext(nthConfig,numSimultaneousJobs,testing,oldParametersFile,ncon):
    
    nextConfig = int(nthConfig) + int(numSimultaneousJobs)
    print(f'Submitting configuration {nextConfig}')
    
    inputArgs = {}
    inputArgs['numjobs'] = numSimultaneousJobs
    inputArgs['parametersfile'] = oldParametersFile
    inputArgs['testing'] = testing

    if nextConfig <= ncon:
        submit.main(nextConfig,inputArgs)


def Input():

    parser = argparse.ArgumentParser()
    parser.add_argument('originalParametersFile',type=str)
    parser.add_argument('parametersDir',type=str)
    parser.add_argument('kappa',type=int)
    parser.add_argument('nthConfig',type=int)
    parser.add_argument('numSimultaneousJobs',type=int)
    parser.add_argument('testing')

    args = parser.parse_args()
    return vars(args)


    

if __name__ == '__main__':

    inputArgs = Input()
    jobID = GetJobID(os.environ)    
    inputArgs['newParametersFile'] = f'{inputArgs["parametersDir"]}{jobID}_parameters.yml'

    main(**inputArgs)
