import os

directories = {}
#Base directory information                                                                                                                                             

#Base output directory                                                                                                                                                  
directories['BaseOutputDir'] = '/hpcfs/users/a1724542/WorkingStorage/'
#Run Specific directory                                                                                                                                                 
directories['rundir'] = 'firstrun/'
#Gauge config directory - probably get made as the first job
directories['ConfigDir'] = 'str'
#Laplacian e-mode directory - same as above                                                                                                           
directories['LapModeDir'] = 'str'
#COLA input directory
directories['inputs'] = os.getcwd() + '/inputs/'

def GetDirectories(kappa):
    
    directories['cfuns'] = directories['BaseOutputDir'] + directories['rundir'] + 'cfuns/'
    directories['props'] = directories['BaseOutputDir'] + directories['rundir'] + 'props/'
    directories['reports'] = directories['BaseOutputDir'] + directories['rundir'] + 'reports/'
    directories['tagfiles'] = directories['cfuns'] + 'tagfiles/'

    return directories
