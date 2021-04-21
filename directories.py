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
import pprint

import configIDs as cfg
from utilities import CreateDirectory

##Global variables. Intended to be changed as required. Are available to the 
##functions in this module but not to a file which imports this module.

#Base directory information 
#Runscript directory
runscriptDir = '/home/a1724542/PhD/runscripts/'
#Base output directory
baseOutputDir = '/hpcfs/groups/cssm-hpc-users/a1724542/WorkingStorage/'
#Run Specific directory                                                                                                                                                 
runIdentifier = 'testing/'
#Output directory structure - KAPPA,KD,SHIFT to be replaced.
outputTree = 'KAPPA/BFKD/SHIFT/'

#Output base filename - SOURCE,SINK,CONFIGID to be replaced
fileBase = 'SOSOURCE_SISINKCONFIGID'
#Base output file extensions
propExt ='.QUARK'                #COLA appends .propformat to this
cfunExt = '.PARTICLE.2cf'
reportExt = '.QUARKrep'
tagfileExt = '.tag' 

#Gauge config files - KAPPA,CONFIGID to be replaced
configDir = '/hpcfs/groups/cssm-hpc-users/PACS-CS/'
configFile = 'RC32x64_B1900Kud0KAPPA00Ks01364000C1715/RC32x64_B1900Kud0KAPPA00Ks01364000C1715CONFIGID'
#Laplacian e-mode directory - KAPPA,KD,CONFIGID to be replaced
lapModeDir = '/hpcfs/groups/cssm-hpc-users/a1724542/Lap2modes/'
lapModeFile = 'RC32x64_B1900Kud0KAPPA00Ks01364000C1715/as0nsm0/BFKD/KAPPAModess32t64kBKDCONFIGID.l2ev'

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
    
    #Constructing directory tree
    outputDir = baseOutputDir + runIdentifier + outputTree

    #Appending output file names and saving to directories dictionary
    directories['cfun'] = outputDir + 'cfuns/' + fileBase + cfunExt
    directories['prop'] = outputDir + 'props/' +  fileBase + propExt
    directories['report'] = outputDir + 'reports/' +  fileBase + reportExt
    directories['tagfile'] = outputDir + 'tagfiles/' +  fileBase + tagfileExt

    ##Saving other file paths and directories to directories dictionary
    #Configuration Files
    directories['cfgFile'] = configDir + configFile
    #Laplacian e-modes
    directories['lapMode'] = lapModeDir + lapModeFile
    #COLA input directory
    directories['input'] = runscriptDir + 'Inputs/'
    #Runscript directory
    directories['script'] = runscriptDir + 'scripts/'
    #slurm_output directory
    directories['slurm'] = runscriptDir + 'slurm/'

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


def FullDirectories(directory=None,kappa=0,kd=0,shift='',source_type='',so_val=0,sink_type='',sink_val=0,cfgID='',*args,**kwargs):
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
    
    #Replace all possible placeholders
    for filetype in directories.keys():
        replaced = directories[filetype].replace('KAPPA',str(kappa))
        replaced = replaced.replace('KD',str(kd))
        replaced = replaced.replace('SHIFT',shift)
        replaced = replaced.replace('SOURCE',source_type+str(so_val))
        replaced = replaced.replace('SINK',sink_type+str(sink_val))
        replaced = replaced.replace('CONFIGID',cfgID)
        directories[filetype] = replaced

    #Create directories that do not exist - CreateDirectory in utilities.py
    for key in directories:
        CreateDirectory(directories[key])
    
    return directories
    
    
#Pretty sure this function doesn't get used - leaving here for a little longer
#just in case.

# def GetConfigurationFile(filebase,kappa,nth_con,run_prefix,SLURM_ARRAY_TASK_ID,**kwargs):

#     filename = filebase.replace('KAPPA',str(kappa))
#     configID = cfg.configID(nth_con,run_prefix,SLURM_ARRAY_TASK_ID)

#     return filename + configID
