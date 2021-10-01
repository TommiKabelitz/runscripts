#standard library modules
import argparse
from datetime import datetime
import os
import pathlib
import subprocess
import sys

from colarunscripts import configIDs as cfg
from colarunscripts import directories as dirs
from colarunscripts import makeCfun
from colarunscripts import makeEmodes
from colarunscripts import makePropagator
from colarunscripts import parameters as params
from colarunscripts.shifts import CompareShifts
from colarunscripts import simpleTime 
from colarunscripts import submit
from colarunscripts.utilities import GetJobID,pp


def main(newParametersFile,kappa,nthConfig,numSimultaneousJobs,ncon,testing,*args,**kwargs):

    parameters = params.Load(parametersFile=newParametersFile)
    jobValues = parameters['runValues']

    if ncon != 0:
        start,_ = cfg.ConfigDetails(kappa,jobValues['runPrefix'])
    else:
        start,ncon = cfg.ConfigDetails(kappa,jobValues['runPrefix'])

    jobValues['nthConfig'] = nthConfig
    jobValues['cfgID'] = cfg.ConfigID(nthConfig,jobValues['runPrefix'],start)
    jobValues['jobID'] = GetJobID(os.environ)
    jobValues['kappa'] = kappa
    
    print()
    PrintJobValues(jobValues)

    JobLoops(parameters,jobValues['shifts'],jobValues['kds'],jobValues)
    SubmitNext(parameters,jobValues,nthConfig,start,numSimultaneousJobs,testing,newParametersFile,ncon)



def JobLoops(parameters,shifts,kds,jobValues,*args,**kwargs):

    timer = simpleTime.Timer('Overall')
    timer.initialiseCheckpoints()
    timer.initialiseTimer('Eigenmodes')
    timer.initialiseTimer('Propagators')
    timer.initialiseTimer('Correlation functions')

    if jobValues['sourceType'] == 'lp' and jobValues['makeProps']:
        jobValues['makeEmodes'] = True
    if jobValues['sinkType'] == 'laplacian' and jobValues['makeCfuns'] is True:
        jobValues['makeEmodes'] = True

  
    inputSummaries = []
    for shift,nextShift in zip(shifts,[*shifts[1:],None]):
        for kd in kds:
            
            if CfunsExist(parameters,jobValues,kd,shift) is True:
                print(f'Correlation functions for {kd=}, {shift=} already exist, skipping.')
                continue
            
            print()                  
            paths = doJobSet(parameters,kd,shift,jobValues,timer)
            inputSummaries += list( jobValues['inputSummary'].values() )
            
        #removing the propagators
        if jobValues['keepProps'] is False and jobValues['makeProps'] is True:
            print('All field strengths done, new shift, deleting propagators')
            for prop in paths['props']:
                print(f'Deleting {prop}')
                path = pathlib.Path(prop)
                path.unlink(missing_ok=True)
            print()    
            
        if jobValues['makeEmodes'] is not jobValues['keepEmodes'] is CompareShifts(shift,nextShift) is False:
            print('Shifting in more than time, deleting eigenmodes')
            for eigenMode in paths['eigenmodes']:
                print(f'Deleting {eigenMode}')
                path = pathlib.Path(eigenMode)
                path.unlink(missing_ok=True)
            print()

        print('Input file summaries located at:')
        for report in inputSummaries:
            print(report)
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
    
    #That's it for preparation of job values. Now start making stuff

    jobValues['inputSummary'] = {}
    
    #Making eigenmodes
    if jobValues['makeEmodes'] is True:
        print(50*'_')
        print()
        print('Making eigenmodes')
        print(f'Time is {datetime.now()}')
        jobValues['inputSummary']['emode'] = PrepareInputReportFile(parameters,'emode',kd,shift,jobValues)
        eigenmodePaths = makeEmodes.main(parameters,kd,shift,jobValues,timer)
        print("\nEigenmodes done")
        print(f'Time is {datetime.now()}')
        print()
    else:
        eigenmodePath = []


    #Making propagators
    if jobValues['makeProps'] is True:
        print(50*'_')
        print()
        print('Making propagators')
        print(f'Time is {datetime.now()}')
        jobValues['inputSummary']['prop'] = PrepareInputReportFile(parameters,'prop',kd,shift,jobValues)
        propPaths = makePropagator.main(parameters,kd,shift,jobValues,timer)
        print("\nPropagators done")
        print(f'Time is {datetime.now()}')
        print(50*'_')
    else:
        propPaths = []

    #Making cfuns
    if jobValues['makeCfuns'] is True:
        print()        
        print('Making correlation functions')
        print(f'Time is {datetime.now()}')    
        jobValues['inputSummary']['cfun'] = PrepareInputReportFile(parameters,'cfun',kd,shift,jobValues)
        jobValues['inputSummary']['interp'] = PrepareInputReportFile(parameters,'interp',kd,shift,jobValues)
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

def PrepareInputReportFile(parameters,report,kd,shift,jobValues):

    reportFile = dirs.FullDirectories(parameters,directory='inputReport',kd=kd,shift=shift,**jobValues,**parameters['sourcesink'])['inputReport']
    reportFile = reportFile.replace('TYPE',report)

    with open(reportFile,'w') as f:
        f.write(f'Summary of {report} input files.\n')
        f.write('\nValues for this config, field strength and shift\n')
        PrintJobValues(jobValues,stream=f)
        f.write(50*'_'+'\n')

    return reportFile


def PrintJobValues(jobValues,stream=sys.stdout):
    """
    Prints the values specific to the current job to the screen.

    Allows easy checking of run values in the job output file.
    
    Arguments:
    jobValues -- dict: Dictionary containing the variables to print out

    """

    #A list of the variables to print
    #(some variables in jobValues there are a waste of time)
    valuesToPrint = ['kappa',
                     'runPrefix',
                     'cfgID',
                     'kds',
                     'shifts',
                     'sourceType',
                     'sinkType',
                     'structureList',
                     'particleList']
    
    print('Job Values:',file=stream)
    #Printing the values
    for key in valuesToPrint:
        try:
            #Printing list across lines for readability
            if type(jobValues[key]) is list:
                print(f'{key}:',file=stream)
                pp(jobValues[key],stream=stream)
            else:
                print(f'{key}: {jobValues[key]}',file=stream)
        #just in case the key is not present (shouldn't happen)
        except KeyError:
            if stream == sys.stdout:
                print(key)


def SubmitNext(parameters,jobValues,nthConfig,start,numSimultaneousJobs,testing,oldParametersFile,ncon):
    
    nextConfig = int(nthConfig) + int(numSimultaneousJobs)
    
    jobValues['cfgID'] = cfg.ConfigID(nextConfig,jobValues['runPrefix'],start)

    inputArgs = {}
    inputArgs['numjobs'] = numSimultaneousJobs
    inputArgs['parametersfile'] = oldParametersFile
    inputArgs['testing'] = testing

    if nextConfig <= ncon and CfunsExist(parameters,jobValues):
        print(f'Submitting configuration {nextConfig}')
        submit.main(nextConfig,inputArgs)
    else:
        print('No new configurations to submit')

def Input():

    parser = argparse.ArgumentParser()
    parser.add_argument('parametersDir',type=str)
    parser.add_argument('kappa',type=int)
    parser.add_argument('nthConfig',type=int)
    parser.add_argument('numSimultaneousJobs',type=int)
    parser.add_argument('ncon',type=int)
    parser.add_argument('testing')

    args = parser.parse_args()
    return vars(args)



def CfunsExist(parameters,jobValues,kd=None,shift=None,*args,**kwargs):
    """
    Checks whether all cfuns for a parameter set exist.

    Arguments:
    parameters -- dict: Dictionary of all parameters from yml
    jobValues  -- dict: Dictionary of parameters relevant to this job
    kd         -- int: field strength for current set (optional)(default: all)
    shift      -- string: Cshift for current ser (optional)(default:all)

    """

    #Note: As soon as we find something is missing, we can return false as
    #all cfuns are made in one call. (Structure exempt, on todo list)
    
    #Recursively calling function for all shifts/kd if not specified
    if kd is None:
        for kd in jobValues['kds']:
            if CfunsExist(parameters,jobValues,kd,shift) is False:
                return False
    if shift is None:
        for shift in jobValues['shifts']:
            if CfunsExist(parameters,jobValues,kd,shift) is False:
                return False

    #Grabbing appropriate sink values
    if 'laplacian' == jobValues['sinkType']:
        sinkVals = parameters['sourcesink']['nModes_lpsnk']
    elif 'smeared' == jobValues['sinkType']:
        sinkVals = parameters['sourcesink']['sweeps_smsnk']

    #Looping through everything we need
    for sinkVal in sinkVals:
        cfunFilename = dirs.GetCfunFile(parameters,kd=kd,shift=shift,sinkVal=sinkVal,**jobValues)

        for chi,chibar in jobValues['particleList']:
            for structure in jobValues['structureList']:
                #Structure in jobValues['structureList'] is a list
                formattedStructure = ''.join(structure)
                cfun = cfunFilename.replace('CHICHIBAR_STRUCTURE',f'{chi}{chibar}_{formattedStructure}')
                
                if pathlib.Path(cfun).is_file() is False:
                    return False

    return True
                    
        


    
    

if __name__ == '__main__':

    inputArgs = Input()
    jobID = GetJobID(os.environ)    
    inputArgs['newParametersFile'] = f'{inputArgs["parametersDir"]}{jobID}_parameters.yml'
    print(f'Parameters file to use: {inputArgs["newParametersFile"]}')
    
    main(**inputArgs)
