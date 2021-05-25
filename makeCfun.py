import os
import subprocess
import yaml
from datetime import datetime

import configIDs as cfg
import directories as dirs
import cfgenFiles as files
import parameters as params
import particles as part
import utilities as ut



def MakeCorrelationFunctions(filestub,jobValues):
    
    parameters = params.params()
    
    propDict = CompilePropPaths(jobValues,parameters)

    particleList = parameters['runValues']['particleList']
    MakeReusableFiles(filestub,parameters,jobValues)
    
    for structure in parameters['runValues']['structureList']:

        print(f'\nDoing structure set: {structure}\n')

        print(f'Quark paths are: ')
        for quark in structure:
            print(f'{quark}: {propDict[quark]}')

        print('Making structure specific files')
        MakeSpecificFiles(filestub,structure,particleList,propDict,jobValues,parameters)
        
        executable = parameters['propcfun']['cfgenExecutable']
        numGPUs = parameters['slurmParams']['numGPUs']
        reportFile = dirs.FullDirectories(directory='cfunReport',structure=structure,**jobValues,**parameters['sourcesink'])['cfunReport']
        CallMPI(filestub,executable,reportFile,numGPUs)
        

def CompilePropPaths(jobValues,parameters):
    
    kd_original = jobValues['kd']

    propDict = {}

    for quark in parameters['propcfun']['quarkList']:
        if quark == 'n':
            kappa = jobValues['kappa']
            jobValues['kd'] = 0
            quarkProp = 'd'
            
        elif quark == 'ns':
            jobValues['kd'] = 0
            quarkProp = 's'
            kappa = parameters['propcfun']['strangeKappa']

        elif quark == 's':
            kappa = parameters['propcfun']['strangeKappa']
            quarkProp = quark

        elif quark == 'u' and kd_original == 0:
            kappa = jobValues['kappa']
            quarkProp = 'd'
        else:
            kappa = jobValues['kappa']
            quarkProp = quark
            
        propFile = dirs.FullDirectories(directory='prop',**jobValues,**parameters['sourcesink'])['prop']
        
        propFormat = parameters["directories"]["propFormat"]
        propFile = propFile.replace('QUARK',quarkProp)
        propFile += f'k{kappa}.{propFormat}'
        
        propDict[quark] = propFile


    jobValues['kd'] = kd_original
    
    return propDict




def MakeReusableFiles(filestub,parameters,jobValues):

    files.MakeLatticeFile(filestub,**parameters['lattice'])
        
    files.MakeConfigIDsFile(filestub,**jobValues)

    configFile = dirs.FullDirectories(directory='configFile',**jobValues)['configFile']
    files.MakeGFSFile(filestub,parameters['directories']['configFormat'],configFile)

    files.MakePropSmearingFile(filestub,**parameters['sourcesink'],**jobValues)





def MakeSpecificFiles(filestub,structure,particleList,propDict,jobValues,parameters):
    #Making Laplacian Sink File
    modeFiles = dirs.LapModeFiles(**jobValues)
    lapModeFiles = [modeFiles[quark] for quark in structure]
    files.MakeLPSinkFile(filestub,lapModeFiles=lapModeFiles,**parameters['sourcesink'])

    if jobValues['kd'] == 0:
        isospinSym = 't'
    else:
        isospinSym = 'f'
        
    #Correlation function filepath
    cfunPrefix = dirs.FullDirectories(directory='cfun',**jobValues,**parameters['sourcesink'])['cfun']
    
    #Writing number of operator pairs to the particle_stubs file
    files.AppendPartStub( filestub,numParticlePairs=len(particleList) )
    #Looping over operator pairs
    for chi,chibar in particleList:
        partstub = filestub + chi + chibar
        
        files.MakeInterpFile(partstub,chi,chibar,structure,cfunPrefix,isospinSym,**parameters['propcfun'])

        files.AppendPartStub(filestub,partstub=partstub)


        hadronicProjection = HadronicProjection(jobValues['kd'],parameters,chi,structure)

        propList = files.MakePropPathFiles(filestub,propDict,structure)
        propList[1],propList[2] = propList[2],propList[1]



        ##THIS FILESTUB WILL NEED TO CHANGE ONCE CFGEN IS UPDATED TO WORK WITH
        ##DIFFERENT LANDAU FILES FOR EACH OPERATOR - AT THE MOMENT, THE PARTICLE
        ##PAIR LAST IN THE PAIR LIST IS USED - AND I THINK IT IS BROKEN FOR 
        ##CORRELATION MATRICES
        files.MakePropCfunInfoFile(filestub,cfunPrefix,propList,**parameters['directories'],**parameters['propcfun'],**parameters['runValues'],**hadronicProjection)


def HadronicProjection(kd,parameters,particle,structure,*args,**kwargs):

    if kd == 0:
        return parameters['hadronicProjection']['fourier']
    else:
        details = parameters['hadronicProjection']['landau']
        
        kH = part.HadronicCharge(kd,particle,structure)
        details['nLandauModes'] = abs(kH)
        details['pmax'] = abs(kH) + 1
        details['fullLandauFile'] = dirs.FullDirectories(directory='landau',kH=kH)['landau']
        return details
    


def CallMPI(filestub,executable,reportFile,numGPUs,*args,**kwargs):

    print()
    print(f'mpi-running "{executable}"')
    print(f'On {numGPUs} GPUs')
    print(f'The input filestub is "{filestub}"')
    
    runDetails = subprocess.run(['mpirun','-np',str(numGPUs),executable],input=filestub+'\n2\n',text=True,capture_output=True)
    
    with open(reportFile,'w') as f:
        f.write(runDetails.stdout)
        if runDetails.stderr is not None:
            f.write(runDetails.stderr)
    print(f'Report file is: {reportFile}')



def main(jobValues,*args,**kwargs):

    filestub = dirs.FullDirectories(directory='cfunInput')['cfunInput'] + jobValues['SLURM_ARRAY_JOB_ID'] + '_' + jobValues['SLURM_ARRAY_TASK_ID']
    
    MakeCorrelationFunctions(filestub,jobValues)


    

if __name__ == '__main__':
    
    main()
