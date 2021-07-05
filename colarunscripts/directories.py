'''
Module for constructing the required directory and file paths.

Main functions:
  GetBaseDirectories   -- Constructs the directory paths without replacement of
                          value placeholders
  FullDirectories      -- Replaces the placeholders and makes the directories


'''

import os.path                        #For getting directories from filepaths
import pathlib                        #For making directories
import pprint                         #For nice printing of dictionaries
from argparse import Namespace        #For converting dictionaries to namespaces

from colarunscripts import configIDs as cfg
from colarunscripts import parameters as params
from colarunscripts.utilities import GetEnvironmentVar

#Just for nice printing of dictionaries. print -> pp
pp = pprint.PrettyPrinter(indent=4).pprint 


def GetBaseDirectories(directory=None,*args,**kwargs):
    '''
    Constructs the file paths with placeholder names still present.
    
    Key-word arguments:
    directory -- string, string list: Optional argument to specify specific
                                      file paths to return 
    Returns:
    directories -- dictionary:        The full file paths.
    '''

    #Initialising empty output directory
    directories = {}

    #Reading in parameters from parameters.yml
    parameters = params.Load()
    baseDirectories = parameters['directories']
    tempStorage = parameters['tempStorage']


    #Scanning for and replacing any environment variables
    tempDir = GetEnvironmentVar(tempStorage['tempFS']) + '/'

    #Converting baseDirectories dictionary to a namespace.
    #Enables easier access via base.variable_name
    base = Namespace(**baseDirectories)

    #Constructing directory tree
    outputDir = base.baseOutputDir + base.runIdentifier + base.outputTree

    #Directory for holding run specific files
    runFileDir = base.runscriptDir + 'runFiles/'

    #Appending output file names and saving to directories dictionary
    directories['propReport'] = outputDir + 'reports/' +  base.propFileBase + '.proprep'
    directories['cfunReport'] = outputDir +'reports/' + base.cfunFileBase + 'CONFIGID_STRUCTURE.cfunrep'    
    directories['cfun'] = outputDir + 'cfuns/' + base.cfunFileBase
    
    ##Saving other file paths and directories to directories dictionary
    #Configuration Files
    directories['configFile'] = base.configDir + base.configFilename
    #Landau file
    directories['landau'] = base.landauDir + base.landauFile

    #Runscript directory
    directories['script'] = runFileDir + 'scripts/'
    #scheduler_output directory
    directories['stdout'] = runFileDir + 'stdout/'
    #parameter file copies
    directories['parameters'] = runFileDir + 'parameters/'
    
    
    if tempDir != 'NONE/':
        runFileDir = tempDir
        if tempStorage['props'] is True:
            outputDir = tempDir + 'props/BFKD/'

    #Propagator output file
    directories['prop'] = outputDir +  base.propFileBase

    #COLA input directories
    directories['propInput'] = runFileDir + 'propInput/'
    directories['cfunInput'] = runFileDir + 'cfunInput/'

    #Returning only the specified directory(ies). Default behaviour is all.
    if directory is None:
        return directories
    elif type(directory) == str:
        #Make directory a list of one string
        directory = [directory]
    elif type(directory) != list:
        raise TypeError
    #return directories that are common to the full dictionary and directory
    return {key:directories[key] for key in directory if key in directories.keys()}  


def FullDirectories(directory=None,kappa=0,kd=0,shift='',sourceType='',sinkType='',sweeps_smsrc=0,nModes_lpsrc=0,sweeps_smsnk=[0],nModes_lpsnk=0,cfgID='',structure=[],kH=0,*args,**kwargs):
    '''
    Replaces placeholders in paths, makes directories and returns file paths.
    
    Key-word arguments:
    directory -- string, string list: Optional argument to specify specific
                                      file paths to make and return 
    Other key-word arguments: See their default value for their proper type.
                              Are all used for replacement of placeholders
    '''
    #Get a dictionary of directory(ies) before replacement of placeholders
    directories = GetBaseDirectories(directory)
    
    parameters = params.Load()

    #Setting up which value will be included in the filename with the 
    #source and sink types
    sourceVal = 0
    sinkVal = 0
    if sourceType in ['sm','lpsm','lpxyz','xyz']:
        sourceVal = sweeps_smsrc
    else:
        sourceVal = nModes_lpsrc
    
    if sinkType in ['smeared']:
        sinkVal = sweeps_smsnk[0]
        sinkType = 'sm'
    elif sinkType in ['laplacian']:
        sinkVal = nModes_lpsnk
        sinkType = 'lp'
    
    #Replace all possible placeholders
    for filetype in directories.keys():
        replaced = directories[filetype].replace('KAPPA',str(kappa))
        replaced = replaced.replace('KD',str(kd))
        replaced = replaced.replace('SHIFT',shift)
        replaced = replaced.replace('SOURCE',sourceType+str(sourceVal))
        replaced = replaced.replace('SINK',sinkType+str(sinkVal))
        replaced = replaced.replace('CONFIGID',cfgID)
        replaced = replaced.replace('STRUCTURE',''.join(structure))        
        replaced = replaced.replace('KH',str(kH))
        replaced = replaced.replace('NX',str(parameters['lattice']['extent'][0]))
        replaced = replaced.replace('NY',str(parameters['lattice']['extent'][1]))
        directories[filetype] = replaced

    #Create directories that do not exist
    for key in directories:
        #Extracting just the directory path
        path = os.path.dirname(directories[key])
        if pathlib.Path(path).is_dir() is False:
            print(f'Making directory {path}')
            try:
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            except PermissionError:
                print(f'Permission to create {directory} denied')
   
    return directories
    


def LapModeFiles(kappa=0,kd=0,cfgID='',quark=None,*args,**kwargs):
    '''
    Returns dictionary of Laplacian eigenmode files.

    If quark is not specified, the quark list in parameters.yml
    is used.
    Arguments:
    kappa -- int: Kappa value for the eigenmodes
    kd    -- int: The field strength
    cfgID -- str: The configuration identifier
    quark -- str or list of str: The quark, or list of quarks to 
                  return

    Returns:
    lapModeFiles -- dict: Dictionary of eigenmode file paths.
                          Quarks as keys.
    '''

    #Loading the parameters files
    parameters = params.Load()

    if parameters['tempStorage']['lapmodes'] is True:
        tempDir = GetEnvironmentVar(tempStorage['tempFS'])
    else:
        tempDir = ''

    #Grabbing the base eigenmode filepath
    baseModeDir = parameters['directories']['lapModeDir']
    baseModeFile = parameters['directories']['lapModeFile']
    baseModePath = tempDir+baseModeDir+baseModeFile

    #Setting up the quark list depending on quark input
    if quark is None:
        #Full list from parameters.yml
        quarkList = parameters['propcfun']['quarkList']
    elif type(quark) is list:
        #Using passed list
        quarkList = quark
    elif type(quark) is str:
        #Converting string to list
        quarkList = [quark]
    else:
        raise TypeError('Expected "quark" to be of type str or list')
        
    #Initialising output dict
    lapModeFiles = {}

    #Will need to adjust field strength for neutral quarks, so saving
    #field strength so that it can be reset
    temp = kd
    #Looping through quarks
    for quark in quarkList:
        
        #Setting field strength to zero for neutral quarks
        if 'n' in quark:
            kd=0

        #Replacing kappa,configID, field strength and saving to dict
        modeFile = baseModePath.replace('KAPPA',str(kappa))
        modeFile = modeFile.replace('CONFIGID',cfgID)
        lapModeFiles[quark] = modeFile.replace('KD',str(kd)) 
    
        #Resetting field strength
        kd = temp
    return lapModeFiles
