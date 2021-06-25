'''
Module for managing of the parameters.yml input file.

The parameters can be simply loaded by calling Load from this module. Rather
than having to load with the yaml module every time.
Also takes care of making a copy of the parameters file for the specific job.

The parameters.yml file must be located one directory above this file
'''

#standard library modules
import os                             #environmental vars
import pathlib
import pprint                         #for nice directory printing
import subprocess                     #for running commands
import yaml                           #yaml importing

#local modules
from colarunscripts import directories as dirs
from colarunscripts.utilities import Parent

#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 

def Load(writeOut=False,*args,**kwargs):
    '''
    Loads the parameters from parameters.yml.

    If SLURM_ARRAY_JOB_ID exists as an environment variable then the 
    copy of the parameters file will exist. Use of the ordinary 
    version is required by submit.py.
    
    Arguments:
    writeOut -- bool: Whether to write out the parameters dictionary
                      to the console when reading.
                      (for testing purposes)

    '''
    
    runscriptDir = Parent(__file__,2)

    #Trying to grab the job ID
    try:
        jobID = os.environ['SLURM_JOB_ID']
    except KeyError:
        pass
    try:
        jobID = os.environ['PBS_JOB_ID']
    except KeyError:
        pass

    try:
        #If it exists using the copied params file in the parameters dir.
        paramsDir = runscriptDir + '/runFiles/parameters'
        parametersFile = paramsDir + f'/{jobID}_parameters.yml'
    
    #Using the original parameters file if the job id is unset.
    #Should only happen when being called in submit.py
    except NameError:
        parametersFile = runscriptDir + '/parameters.yml'

    #Opening and loading the yamml
    with open(parametersFile,'r') as f:
        parameters = yaml.safe_load(f)

    #Writing the details to the screen if specified
    if writeOut is True:
        pp(parameters)

    return(parameters)



def CopyParamsFile(jobID,*args,**kwargs):
    '''
    Makes a copy of the parameters file to use for this specific job.

    Arguments:
    jobID -- int: Job identification number

    '''

    #File to copy
    originalFile = Parent(__file__,2) + '/parameters.yml'
    #File to make
    copyFile = dirs.FullDirectories(directory='parameters')['parameters'] + f'{jobID}_parameters.yml'
    
    #Copying file
    subprocess.run(['cp',originalFile,copyFile])
