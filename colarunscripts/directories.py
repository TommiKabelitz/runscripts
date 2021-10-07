"""
Module for constructing the required directory and file paths.

Main functions:
  GetBaseDirectories   -- Constructs the directory paths without replacement of
                          value placeholders
  FullDirectories      -- Replaces the placeholders and makes the directories


"""

import os.path                        #For getting directories from filepaths
import pathlib                        #For making directories
import pprint                         #For nice printing of dictionaries
from argparse import Namespace        #For converting dictionaries to namespaces

from colarunscripts import configIDs as cfg
from colarunscripts.particles import QuarkCharge
from colarunscripts.shifts import FormatShift
from colarunscripts.utilities import GetEnvironmentVar

#Just for nice printing of dictionaries. print -> pp
pp = pprint.PrettyPrinter(indent=4).pprint 


def GetBaseDirectories(parameters,directory=None,*args,**kwargs):
    """
    Constructs the file paths with placeholder names still present.
    
    Key-word arguments:
    directory -- string, string list: Optional argument to specify specific
                                      file paths to return 
    Returns:
    directories -- dictionary:        The full file paths.
    """

    #Initialising empty output directory
    directories = {}

    #Reading in parameters from parameters.yml
    baseDirectories = parameters['directories']
    tempStorage = parameters['tempStorage']

    #Scanning for and replacing any environment variables
    tempDir = GetEnvironmentVar(tempStorage['tempFS']) + '/'

    #Converting baseDirectories dictionary to a namespace.
    #Enables easier access via base.variable_name
    base = Namespace(**baseDirectories)

    #Constructing directory tree
    outputDir = base.baseOutputDir + base.runIdentifier + base.outputTree

    #Directory for holding report files
    reportDir = outputDir + 'reports/'
    
    #Appending output file names and saving to directories dictionary
    directories['cfun'] = outputDir + 'cfuns/' + base.cfunFileBase
    directories['propReport'] = reportDir +  base.propFileBase + '.proprep'
    directories['cfunReport'] = reportDir + base.cfunFileBase + 'CONFIGIDsiSINK_STRUCTURE.cfunrep'
    directories['lapmodeReport'] = reportDir + base.lapModeReport + '.lapmoderep'
    directories['inputReport'] = reportDir + base.inputReport + '.TYPEinputrep'
    
    ##Saving other file paths and directories to directories dictionary
    #Configuration Files
    directories['configFile'] = base.configDir + base.configFilename
    #Landau file
    directories['landau'] = base.landauDir + base.landauFile

    #Directory for holding run specific files
    runFileDir = base.runscriptDir + 'runFiles/'

    #Runscript directory
    directories['script'] = runFileDir + 'scripts/'
    #scheduler_output directory
    directories['stdout'] = runFileDir + 'stdout/' + base.runIdentifier
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
    directories['lapmodeInput'] = runFileDir + 'lapmodeInput/'
    
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


def FullDirectories(parameters,directory=None,kappa=0,kd=0,shift='',sourceType='',sinkType='',sweeps_smsrc=0,nModes_lpsrc=0,sweeps_smsnk=[0],nModes_lpsnk=[0],cfgID='',structure=[],kH=0,*args,**kwargs):
    """
    Replaces placeholders in paths, makes directories and returns file paths.
    
    Key-word arguments:
    directory -- string, string list: Optional argument to specify specific
                                      file paths to make and return 
    Other key-word arguments: See their default value for their proper type.
                              Are all used for replacement of placeholders
    """
    #Get a dictionary of directory(ies) before replacement of placeholders
    directories = GetBaseDirectories(parameters,directory)
    
    #Setting up which value will be included in the filename with the 
    #source and sink types
    sourceVal = ''
    sinkVal = ''
    if sourceType in ['sm','lpsm','lpxyz','xyz']:
        sourceVal = sweeps_smsrc
    elif sourceType == 'lp':
        sourceVal = nModes_lpsrc

    if type(sinkType) is list:
        sinkType = '-'.join(sinkType)
    elif sinkType in ['smeared']:
        sinkVal = '-'.join([str(x) for x in sweeps_smsnk])
        sinkType = 'sm'
    elif sinkType in ['laplacian']:
        sinkVal = '-'.join([str(x) for x in nModes_lpsnk])
        sinkType = 'lp'
    
    #Replace all possible placeholders
    for filetype in directories.keys():
        replaced = directories[filetype].replace('KAPPA',str(kappa))
        replaced = replaced.replace('KD',str(kd))
        replaced = replaced.replace('SHIFT',shift)
        replaced = replaced.replace('SOURCE',f'{sourceType}{str(sourceVal)}')
        replaced = replaced.replace('SINK',f'{sinkType}{str(sinkVal)}')
        replaced = replaced.replace('SOSI_','_')
        replaced = replaced.replace('SI_','_')
        replaced = replaced.replace('CONFIGID',cfgID)
        replaced = replaced.replace('STRUCTURE',''.join(structure))        
        replaced = replaced.replace('KH',str(kH))
        replaced = replaced.replace('NX',str(parameters['lattice']['extent'][0]))
        replaced = replaced.replace('NY',str(parameters['lattice']['extent'][1]))
        directories[filetype] = replaced

    #Create directories that do not exist
    for directory in directories.values():
        #Extracting just the directory path
        path = os.path.dirname(directory)
        if pathlib.Path(path).is_dir() is False:
            print(f'Making directory {path}')
            try:
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            except PermissionError:
                print(f'Permission to create {directory} denied')
   
    return directories
    


def LapModeFiles(parameters,kappa=0,kd=0,cfgID='',shift='',quark=None,withExtension=True,*args,**kwargs):
    """
    Returns dictionary of Laplacian eigenmode files.

    If quark is not specified, the charge passed is not adjusted for
    flavour. It is assumed that is already done
    Arguments:
    kappa -- int: Kappa value for the eigenmodes
    kd    -- int: The field strength
    cfgID -- str: The configuration identifier
    quark -- str or list of str: The quark, or list of quarks to 
                  return

    Returns:
    lapModeFiles -- dict: Dictionary of eigenmode file paths.
                          Quarks as keys.
    """

    tempStorage = parameters['tempStorage']
    extension = '.' + parameters['directories']['lapModeFormat']
    #Are we storing eigenmodes on temporary job storage?
    if parameters['tempStorage']['lapmodes'] is True:
        baseModeDir = GetEnvironmentVar(tempStorage['tempFS'])
    else:
        baseModeDir = parameters['directories']['lapModeDir']

    #Grabbing the base eigenmode filepath
    baseModeFile = parameters['directories']['lapModeFile']
    baseModePath = baseModeDir+baseModeFile

    if withExtension is True:
        baseModePath += extension

    baseModePath = baseModePath.replace('KAPPA',str(kappa))
    baseModePath = baseModePath.replace('CONFIGID',cfgID)
    formattedShift = FormatShift(shift,form='label',fullShift='emode')
    baseModePath = baseModePath.replace('SHIFT',formattedShift)

        
    #Setting up the quark list depending on quark input
    if quark is None:
        adjustkd = False
        quarkList = ['quark']
    elif type(quark) is list:
        #Using passed list
        quarkList = quark
        adjustkd = True
    elif type(quark) is str:
        #Converting string to list
        quarkList = [quark]
        adjustkd = True
    else:
        raise TypeError('Expected "quark" to be of type str or list')
        
    #Initialising output dict
    lapModeFiles = {}

    #Should we need to adjust the field strength based on quark
    #flavour, we have the true value saved
    temp = kd

    #Looping through quarks
    for quark in quarkList:
        #Adjusting strength based on charge
        if adjustkd is True:
            kd *= QuarkCharge(quark)

        #Can now replace kd
        lapModeFiles[quark] = baseModePath.replace('KD',str(kd)) 

        #Making directory if it doesn't exist
        path = os.path.dirname(lapModeFiles[quark])
        if pathlib.Path(path).is_dir() is False:
            print(f'Making directory {path}')
            try:
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            except PermissionError:
                print(f'Permission to create {directory} denied')

        
        #Resetting field strength
        kd = temp
    return lapModeFiles



def GetCfunFile(parameters,kappa,kd,shift,sourceType,sinkType,sinkVal,cfgID,*args,**kwargs):

    cfunBase = FullDirectories(parameters,directory='cfun',kappa=kappa,kd=kd,shift=shift,sourceType=sourceType,**parameters['sourcesink'])['cfun']

    if sinkType == 'laplacian':
        sinkLabel = f'lp{sinkVal}'
    elif sinkType == 'smeared':
        sinkLabel = f'sm{sinkVal}'

    cfunFilename = f'{cfunBase}{cfgID}si{sinkLabel}.CHICHIBAR_STRUCTURE.u.2cf'
    return cfunFilename
