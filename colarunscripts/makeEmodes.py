'''
Module for making Laplacian Eigenmodes by calling lap2modesGPU.x.

'main()' function is called by manageJob.py which passes the job specific
details to this function.

This script is not intended to be called from the command line.

'''

#standard library modules
import pathlib                      #for checking existence of files
import subprocess                   #for calling lap2dmodes.x
from datetime import datetime       #for writing out the time

from colarunscripts import directories as dirs
from colarunscripts import shifts
from colarunscripts import parameters as params
from colarunscripts.makePropagator import CallMPI
from colarunscripts.propFiles import FieldCode, MakeLatticeFile
from colarunscripts.utilities import SchedulerParams


def main(jobValues,timer):

    parameters = params.Load()

    filestub = dirs.FullDirectories(directory='lapmodeInput')['lapmodeInput'] + jobValues['jobID'] + '_' + str(jobValues['nthConfig'])
    inputs = {}
    MakeLatticeFile(filestub,**parameters['lattice'])

    modeFiles = dirs.LapModeFiles(**jobValues,withExtension=False)
    
    inputs['configFile'] = dirs.FullDirectories(directory='configFile',**jobValues)['configFile']
    inputs['configFormat'] = parameters['directories']['configFormat']
    inputs['outputFormat'] = parameters['directories']['lapModeFormat']
    inputs['U1FieldCode'] = FieldCode(**parameters['propcfun'],**jobValues)
    inputs['shift'] = shifts.FormatShift(jobValues['shift'])
    inputs['tolerance'] = parameters['propcfun']['tolerance']
    
    schedulerParams = SchedulerParams(jobValues['scheduler'])

    fullFileList = []
    for structure in parameters['runValues']['structureList']:
        for quark in structure:

            fullFile = modeFiles[quark] + '.' + parameters['directories']['lapModeFormat']
            print()
            print(5*'-'+f'Doing {quark} quark'+5*'-')
            if pathlib.Path(fullFile).is_file():
                print(f'Skipping {fullFile} eigenmode file. File already exists')
                fullFileList.append(fullFile)
                continue
            print(f'Eigenmode to make is: {fullFile}')

            inputs['outputPrefix'] = modeFiles[quark]
            MakeLap2ModesFile(filestub,**inputs,**parameters['laplacianEigenmodes'])

            reportFile = dirs.FullDirectories(directory='lapmodeReport',**jobValues)['lapmodeReport'].replace('QUARK',quark)

            timer.startTimer('Eigenmodes')
            CallMPI(parameters['laplacianEigenmodes']['lapmodeExecutable'],reportFile,filestub=filestub,**schedulerParams)
            timer.stopTimer('Eigenmodes')
                    
            fullFileList.append(fullFile)

    return fullFileList



def MakeLap2ModesFile(filestub,configFile,configFormat,outputPrefix,outputFormat,alpha_smearing,smearing_sweeps,shift,U1FieldCode,numEvectors,numAuxEvectors,tolerance,doRandomInitial,inputModeFile,*args,**kwargs):

    extension = '.lap2dmodes'
    with open(filestub+extension,'w') as f:
        f.write(f'{configFile}\n')
        f.write(f'{configFormat}\n')
        f.write(f'{outputPrefix}\n')
        f.write(f'{outputFormat}\n')
        f.write(f'{alpha_smearing}\n')
        f.write(f'{smearing_sweeps}\n')
        f.write(f'{shift}\n')
        f.write(f'{U1FieldCode}\n')
        f.write(f'{numEvectors}\n')
        f.write(f'{numAuxEvectors}\n')
        f.write(f'{tolerance}\n')
        f.write(f'{doRandomInitial}\n')
        f.write(f'{inputModeFile}\n')
