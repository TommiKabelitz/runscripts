import os
import pathlib
import configIDs as cfg

#Base directory information 
#Runscript directory
runscriptDir = '/home/a1724542/PhD/runscripts/'
#Base output directory
baseOutputDir = '/hpcfs/groups/cssm-hpc-users/a1724542/WorkingStorage/'
#Run Specific directory                                                                                                                                                 
runIdentifier = 'testing/'
#Output directory structure
outputTree = 'KAPPA/BFKD/SHIFT/'

fileBase = 'SOSOURCE_SISINKCONFIGID'

#Base prop extension
propExt ='.QUARK'
#Base cfun extension
cfunExt = '.PARTICLE.2cf'
#Base report extension
reportExt = '.QUARKrep'
#Base tagfile extension
tagfileExt = '.tag' 

#Gauge config files
configDir = '/hpcfs/groups/cssm-hpc-users/PACS-CS/'
configFile = 'RC32x64_B1900Kud0KAPPA00Ks01364000C1715/RC32x64_B1900Kud0KAPPA00Ks01364000C1715CONFIGID'
#Laplacian e-mode directory      
lapModeDir = '/hpcfs/groups/cssm-hpc-users/a1724542/Lap2modes/'
lapModeFile = 'RC32x64_B1900Kud0KAPPA00Ks01364000C1715/as0nsm0/BFKD/KAPPAModess32t64kBKDCONFIGID.l2ev'

directories = {}
def GetBaseDirectories(directory=None):

    outputDir = baseOutputDir + runIdentifier + outputTree

    directories['cfun'] = outputDir + 'cfuns/' + fileBase + cfunExt
    directories['prop'] = outputDir + 'props/' +  fileBase + propExt
    directories['report'] = outputDir + 'reports/' +  fileBase + reportExt
    directories['tagfile'] = outputDir + 'tagfiles/' +  fileBase + tagfileExt

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

    if directory is None:
        return directories
    elif type(directory) == str:
        directory = [directory]
    elif type(directory) != list:
        raise TypeError
    return {key:directories[key] for key in directory if key in directories.keys()}  


def FullDirectories(directory=None,kappa=0,kd=0,shift='',source_type='',so_val=0,sink_type='',sink_val=0,cfgID='',**kwargs):

    directories = GetBaseDirectories(directory)

    for filetype in directories.keys():

        replaced = directories[filetype].replace('KAPPA',str(kappa))
        replaced = replaced.replace('KD',str(kd))
        replaced = replaced.replace('SHIFT',shift)
        replaced = replaced.replace('SOURCE',source_type+str(so_val))
        replaced = replaced.replace('SINK',sink_type+str(sink_val))
        replaced = replaced.replace('CONFIGID',cfgID)
        directories[filetype] = replaced

    for key in directories:
        print("Making directory")
        print(directories[key])
        CreateDirectory(directories[key])
    
    return directories
    
    

def GetConfigurationFile(filebase,kappa,nth_con,run_prefix,SLURM_ARRAY_TASK_ID,**kwargs):

    filename = filebase.replace('KAPPA',str(kappa))
    configID = cfg.configID(nth_con,run_prefix,SLURM_ARRAY_TASK_ID)

    return filename + configID



def CreateDirectory(Input):

    def create(fullFilepath):
        index = fullFilepath.rfind('/')
        directory = fullFilepath[:index]
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)


    inputType = type(Input)
    if inputType is str:
        create(Input)
    elif inputType is list:
        for directory in Input:
            create(directory)
    elif inputType is dict:
        for key,directory in Input.values():
            create(directory)
    else:
        raise TypeError()

