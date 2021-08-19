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
from colarunscripts.makePropagator import CallMPI
from colarunscripts.particles import QuarkCharge
from colarunscripts.propFiles import FieldCode, MakeLatticeFile
from colarunscripts.utilities import SchedulerParams


def main(parameters,kd,shift,jobValues,timer):

    
    

    inputs = {}
    inputs['configFile'] = dirs.FullDirectories(parameters,kd=kd,directory='configFile',**jobValues)['configFile']
    inputs['configFormat'] = parameters['directories']['configFormat']
    inputs['outputFormat'] = parameters['directories']['lapModeFormat']
    inputs['shift'] = shifts.FormatShift(shift)
    inputs['tolerance'] = parameters['propcfun']['tolerance']
    
    schedulerParams = SchedulerParams(parameters,jobValues['scheduler'])

    fullFileList = []
    for structure in parameters['runValues']['structureList']:
        modeFiles = dirs.LapModeFiles(parameters,kd=kd,quark=structure,**jobValues,withExtension=False)
        for quark in structure:

            filestub = dirs.FullDirectories(parameters,directory='lapmodeInput')['lapmodeInput'] + jobValues['jobID'] + '_' + str(jobValues['nthConfig']) + f'.{quark}'
            MakeLatticeFile(filestub,**parameters['lattice'])

            fullFile = modeFiles[quark] + '.' + parameters['directories']['lapModeFormat']
            print()
            print(5*'-'+f'Doing {quark} quark'+5*'-')
            if pathlib.Path(fullFile).is_file():
                print(f'Skipping {fullFile} eigenmode file. File already exists')
                fullFileList.append(fullFile)
                continue
            print(f'Eigenmode to make is: {fullFile}')

            inputs['U1FieldCode'] = FieldCode(kd=kd*QuarkCharge(quark),**parameters['propcfun'],**jobValues)
            inputs['outputPrefix'] = modeFiles[quark]
            MakeLap2ModesFile(filestub,**inputs,**parameters['laplacianEigenmodes'])

            scheduler = jobValues['scheduler'].lower()
            numGPUs = parameters[scheduler+'Params']['NUMGPUS']
            
            reportFile = dirs.FullDirectories(parameters,directory='lapmodeReport',kd=kd,shift=shift,**jobValues)['lapmodeReport'].replace('QUARK',quark)

            timer.startTimer('Eigenmodes')
            CallMPI(parameters['laplacianEigenmodes']['lapmodeExecutable'],reportFile,filestub=filestub,numGPUs=numGPUs)
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
