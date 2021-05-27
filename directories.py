'''
Module for constructing the required directory and file paths.

Global variables are intended to be easy access ways of changing relevant 
parameters

Main functions:
  GetBaseDirectories   -- Constructs the directory paths without replacement of
                          value placeholders
  FullDirectories      -- Replaces the placeholders and makes the directories


'''
import pathlib
import parameters as params
import pprint
from argparse import Namespace

import configIDs as cfg
from utilities import CreateDirectory

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

    baseDirectories = params.params()
    base = Namespace(**baseDirectories['directories'])

    #Constructing directory tree
    outputDir = base.baseOutputDir + base.runIdentifier + base.outputTree

    #Appending output file names and saving to directories dictionary
    directories['cfun'] = outputDir + 'cfuns/' + base.cfunFileBase
    directories['prop'] = outputDir + 'props/' +  base.propFileBase
    directories['propReport'] = outputDir + 'reports/' +  base.propFileBase + '.proprep'
    directories['cfunReport'] = outputDir +'reports/' + base.cfunFileBase + 'CONFIGID_STRUCTURE.cfunrep'
    
    ##Saving other file paths and directories to directories dictionary
    #Configuration Files
    directories['configFile'] = base.configDir + base.configFilename
    #COLA input directories
    directories['propInput'] = base.runscriptDir + 'propInput/'
    directories['cfunInput'] = base.runscriptDir + 'cfunInput/'
    #Runscript directory
    directories['script'] = base.runscriptDir + 'scripts/'
    #slurm_output directory
    directories['slurm'] = base.runscriptDir + 'slurm/'
    #landau file
    directories['landau'] = base.landauDir + base.landauFile
    
    
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


def FullDirectories(directory=None,kappa=0,kd=0,shift='',sourceType='',sinkType='',sweeps_smsrc=0,nModes_lpsrc=0,sweeps_smsnk=0,nModes_lpsnk=0,cfgID='',structure=[],kH=0,*args,**kwargs):
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
    
    parameters = params.params()

    sourceVal = 0
    sinkVal = 0
    if sourceType in ['sm','lpsm','lpxyz','xyz']:
        sourceVal = sweeps_smsrc
    else:
        sourceVal = nModes_lpsrc
    
    if sinkType in ['smeared']:
        sinkVal = sweeps_smsnk
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

    #Create directories that do not exist - CreateDirectory in utilities.py
    for key in directories:
        CreateDirectory(directories[key])
    
    return directories
    


def LapModeFiles(kappa=0,kd=0,cfgID='',quark=None,*args,**kwargs):

    parameters = params.params()

    baseModeDir = parameters['directories']['lapModeDir']
    baseModeFile = parameters['directories']['lapModeFile']

    baseModePath = baseModeDir+baseModeFile

    if quark is None:
        quarkList = parameters['propcfun']['quarkList']
    elif type(quark) is list:
        quarkList = quark
    elif type(quark) is str:
        quarkList = [quark]
    else:
        raise TypeError('Expected "quark" to be of type str or list')
        

    lapModeFiles = {}

    temp = kd
    for quark in quarkList:

        if 'n' in quark:
            kd=0

        modeFile = baseModePath.replace('KAPPA',str(kappa))
        modeFile = modeFile.replace('CONFIGID',cfgID)
        lapModeFiles[quark] = modeFile.replace('KD',str(kd)) 
    
        kd = temp
    return lapModeFiles
