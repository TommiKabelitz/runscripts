import os
import pathlib
import configIDs as cfg
directories = {}
#Base directory information                                                                                                                                             

#Base output directory
baseOutputDir = '/hpcfs/groups/cssm-hpc-users/a1724542/WorkingStorage/'
#Run Specific directory                                                                                                                                                 
runIdentifier = 'firstrun/'
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
#Laplacian e-mode directory - probably get made early      
lapModeDir = '/dir/'
lapModeFile = 'file'


def GetBaseDirectories(directory=None):

    outputDir = baseOutputDir + runIdentifier + outputTree

    directories['cfun'] = outputDir + 'cfuns/' + fileBase + cfunExt
    directories['prop'] = outputDir + 'props/' +  fileBase + propExt
    directories['report'] = outputDir + 'reports/' +  fileBase + reportExt
    directories['tagfile'] = outputDir + 'tagfiles/' +  fileBase + tagfileExt

    #Configuration Files
    directories['cfgFile'] = configDir + configFile

    #Laplacian e-modes
    directories['lapmode'] = lapModeDir + lapModeFile
    
    #COLA input directory
    directories['input'] = os.getcwd() + '/inputs/'

    if directory is None:
        return directories
    else:
        return directories[directory]


def FullDirectories(kappa,kd,shift,source_type,so_val,sink_type,sink_val,cfgID,**kwargs):

    directories = GetBaseDirectories()

    for filetype in ['cfun','prop','report','tagfile']:

        replaced = directories[filetype].replace('KAPPA',str(kappa))
        replaced = replaced.replace('KD',str(kd))
        replaced = replaced.replace('SHIFT',shift)
        replaced = replaced.replace('SOURCE',source_type+str(so_val))
        replaced = replaced.replace('SINK',sink_type+str(sink_val))
        replaced = replaced.replace('CONFIGID',cfgID)
        directories[filetype] = replaced

    replaced = directories['cfgFile'].replace('KAPPA',str(kappa))
    replaced = replaced.replace('CONFIGID',cfgID)
    directories['cfgFile'] = replaced

    for key in directories:
        print("Making directory")
        print(directories[key])
        #CreateDirectory(directories[key])
    
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
        


