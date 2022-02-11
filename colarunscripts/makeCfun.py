"""
Module for making correlation function by calling cfungenGPU.x

'main()' function is called by  manageJob.py which passes the job specific
details to this function.

This script is not intended to  be called fromthe command line

"""

#standard library modules
import glob                         #for globbing created cfuns
import pathlib                      #for various path related operations
import random                       #for avoiding race conditions with tars
import re                           #for extracting tar file path
import tarfile                      #for managing the cfun tars
import time                         #for time.sleep
import traceback                    #allows printing of the full traceback
from datetime import datetime       #for writing out the time


#local modules
from colarunscripts import configIDs as cfg
from colarunscripts import directories as dirs
from colarunscripts import cfgenFiles as files
from colarunscripts import particles as part
from colarunscripts.makePropagator import CallMPI
from colarunscripts.particles import QuarkCharge
from colarunscripts.shifts import FormatShift
from colarunscripts.utilities import pp



def main(parameters,kd,shift,jobValues,timer,*args,**kwargs):
    """
    Main function. Begins correlation function production process

    Arguments:
    jobValues -- dict: Dictionary containing the job specific values such as
                       kd, shift, nthConfig, etc...
    timer     -- Timer: Timer object to manage timing of correlation function
                       calculation time.
    """

    #compiling the filestub for the input files to feed to cfungen
    filestub = dirs.FullDirectories(parameters,directory='cfunInput')['cfunInput'] + jobValues['jobID'] + '_' + str(jobValues['nthConfig'])
    
    #Calling the function that does all the work
    MakeCorrelationFunctions(parameters,filestub,kd,shift,jobValues,timer)



def MakeCorrelationFunctions(parameters,filestub,kd,shift,jobValues,timer,*args,**kwargs):
    """
    Makes the input files and then the actual correlation functions.

    Arguments:
    filestub  -- str: Base input filestub to pass to cfungenGPU.x
    jobValues -- dict: Dictionary containing the job specific values such as
                      kd, shift, nthConfig, etc...
    timer     -- Timer: Timer object to manage timing of correlation function
                      calculation time.


    """
   
    #Getting a dictionary of paths to all possible props
    #(props don't necessarily exist unless required)
    propDict = CompilePropPaths(parameters,kd,shift,jobValues)

    logFile = jobValues['inputSummary']['cfun']

    for sinkType in jobValues['sinkTypes']:
        jobValues['sinkType'] = sinkType
        
        with open(logFile,'a') as f:
            f.write(f'\nSink type: {sinkType}\n')
            f.write('\nInput files not dependent on structure:\n')

        #Making files which are reused for all structures
        MakeReusableFiles(parameters,filestub,logFile,kd,shift,jobValues)

        with open(logFile,'a') as f:
            f.write('\nInput files dependent on structure:\n')

        #Looping over different structures
        for structure in parameters['runValues']['structureList']:

            if structure != ['u','d','s'] and sinkType == 'smeared':
                print(f'\nskipping combination of {structure=} and {sinkType=}')
                continue
            
            with open(logFile,'a') as f,open(jobValues['inputSummary']['interp'],'a') as g:

                print(f'\nDoing structure set: {structure}\n')
                f.write(f'\n\nDoing structure set: {structure}\n\n')
                g.write(f'\n\nDoing structure set: {structure}\n\n')

                #Just printing quark paths for reference
                print(f'Quark paths are: ')
                f.write(f'Quark paths are:\n')
                for quark in structure:
                    print(f'{quark}: {propDict[quark]}')
                    f.write(f'{quark}: {propDict[quark]}\n')

            print('Making structure specific files')
            MakeSpecificFiles(parameters,filestub,logFile,kd,shift,structure,propDict,jobValues)

            #Preparing final variables for call to cfungen
            executable = parameters['propcfun']['cfgenExecutable']

            scheduler = jobValues['scheduler'].lower()
            numGPUs = parameters[scheduler+'Params']['NUMGPUS']
            reportFile = dirs.FullDirectories(parameters,directory='cfunReport',kd=kd,shift=shift,structure=structure,**jobValues,**parameters['sourcesink'])['cfunReport']

            timerLabel = 'Correlation functions'
            CallMPI(executable,reportFile,jobValues['runFunction'],filestub=filestub,numGPUs=numGPUs,timerLabel=timerLabel)

            if jobValues['tarCfuns'] is True:
                #Tar new correlation functions together
                TarCfuns(parameters,kd,shift,structure,sinkType,jobValues)

        #End structure loop
    #End sinktype loop

                
def CompilePropPaths(parameters,kd,shift,jobValues,*args,**kwargs):
    """
    Creates a dictionary of propagator paths for all quarks in the quarkList.

    Arguments:
    jobValues  -- dict: Dictionary containing job specific values
    parameters -- dict: Dictionary of all of the run parameters.
                        From parameters.yml

    """

    #Will change the kd value in jobvalues so saving it to fix at the end
    kd_original = kd
    kappa_original = jobValues['kappa']

    #Initialising output dictionary
    propDict = {}
    
    #Looping over quarks in quark list
    for quark in parameters['propcfun']['quarkList']:

        #Effectively only make 2 types of propagator. Light (d) and heavy (s).
        #The rest we get through charge manipulation (u=-2*d,nl=0*d,nh=0*nh).

        kd *= QuarkCharge(quark)
        
        #Getting the base propagator file
        propFile = dirs.FullDirectories(parameters,directory='prop',kd=kd,shift=shift,**jobValues,**parameters['sourcesink'])['prop']

        if quark in ['s','nh']:
            quarkLabel = 'h'
            jobValues['kappa'] = parameters['propcfun']['strangeKappa']
        else:
            quarkLabel = 'l'

        #Adding the kappa value and file extension (propFormat) which are 
        #appended by quarkpropGPU.x
        propFormat = parameters["directories"]["propFormat"]
        propFile = propFile.replace('QUARK',quarkLabel)
        propFile += f'k{jobValues["kappa"]}.{propFormat}'
        
        #Saving the path to the dictionary
        propDict[quark] = propFile

        #returning the field strength to its original value
        kd = kd_original
        jobValues['kappa'] = kappa_original
        #end quark loop
    return propDict




def MakeReusableFiles(parameters,filestub,logFile,kd,shift,jobValues,*args,**kwargs):
    """
    Makes the input files which are structure independent and reusable.

    Arguments:
    filestub   -- str: Base filestub to pass to cfungenGPU.x
    jobValues  -- dict: Dictionary containing job specific values
    parameters -- dict: Dictionary of all of the run parameters.
                        From parameters.yml

    """
    
    print('Making input files independent of structure')

    files.MakeLatticeFile(filestub,logFile,**parameters['lattice'])
        
    files.MakeConfigIDsFile(filestub,logFile,**jobValues)

    #Getting the gauge field configuration file, then making the relevant input 
    #file
    configFile = dirs.FullDirectories(parameters,directory='configFile',**jobValues)['configFile']
    files.MakeGFSFile(filestub,logFile,parameters['directories']['configFormat'],configFile,FormatShift(shift,fullShift='full'))
    
    #Making the smearing file, still read in for Laplacian sink (I think)
    files.MakePropSmearingFile(filestub,logFile,kd=kd,**parameters['sourcesink'],**jobValues)

    #Making the particle stubs file
    particleList = jobValues['particleList']
    files.MakePartStubsFile(filestub,logFile,kd,particleList)

    

def MakeSpecificFiles(parameters,filestub,logFile,kd,shift,structure,propDict,jobValues):
    """
    Makes the files which depend on structure and cannot be reused.

    Arguments:
    filestub   -- str: Base filestub to pass to cfungenGPU.x
    structure  -- str list: Quark structure
    propDict   -- dict: Dictionary containing prop paths
    jobValues  -- dict: Dictionary containing job specific values
    parameters -- dict: Dictionary of all of the run parameters.
                        From parameters.yml
    
    """
    
    #Making Laplacian Sink File
    modeFiles = dirs.LapModeFiles(parameters,kd=kd,shift=shift,quark=structure,**jobValues)   #(dict)
    lapModeFiles = [modeFiles[quark] for quark in structure]   #(above as list) 
    files.MakeLPSinkFile(filestub,logFile,shift=FormatShift(shift,fullShift='lpsink'),lapModeFiles=lapModeFiles,**parameters['sourcesink'])

    #Setting isospin symmetry based on field strength
    if kd == 0:
        isospinSym = 't'
    else:
        isospinSym = 'f'
        
    #Correlation function filepath
    cfunPrefix = dirs.FullDirectories(parameters,directory='cfun',kd=kd,shift=shift,**jobValues,**parameters['sourcesink'])['cfun']
    
    #Getting the details regarding the hadronic projection (fourier vs landau, etc...)
    hadronicProjection = HadronicProjection(parameters,kd,structure)

    #Making the files which hold the paths to the propagators in the u,d,s 
    #spots. Returns the paths to those files.
    propList = files.MakePropPathFiles(filestub,logFile,propDict,structure)
    #Exchange the order as the order to feed props in is u,s,d. COLA reads
    #u and s first, then d if isospin is false.
    propList[1],propList[2] = propList[2],propList[1]

    files.MakePropCfunInfoFile(filestub,logFile,propList,**parameters['directories'],**parameters['propcfun'],**parameters['runValues'],**hadronicProjection)

    #Looping over operator pairs to make interpolator files
    #.interp files are structure dependent as the structure
    #is in the filename of the correlator
    for chi,chibar in jobValues['particleList']:
        #compiling the particle stub ie. 5319732_4protonprotonbar
        partstub = filestub + chi + chibar
        
        #Making the interpolator file using that stub
        files.MakeInterpFile(partstub,jobValues['inputSummary']['interp'],chi,chibar,structure,cfunPrefix,isospinSym,**parameters['propcfun'])


def HadronicProjection(parameters,kd,structure,*args,**kwargs):
    """
    Returns the details for the hadronic projection.

    Arguments:
    parameters -- dict: Dictionary of all of the run parameters.
                        From parameters.yml
    kd         -- int: The field strength
    structure  -- str: list: Quark structure
    

    """

    details = {'pmin':0,
               'pmax':0}
    
    #Projection type depends on field strength
    if kd == 0:
        #Fourier project at zero field strength where Landau levels vanish
        details['useLandau'] = 'f'
        return details
    else:
        #At non-zero field strength, do a projection to the Landau levels.
        details['useLandau'] = 't'

        effectiveQuarkCharge = []
        for quark in structure:
            effectiveQuarkCharge.append(part.QuarkCharge(quark)*kd)

        details['kd_q'] = ' '.join([str(x) for x in effectiveQuarkCharge])
        details['fullLandauFile'] = dirs.FullDirectories(parameters,directory='landau')['landau']
        return details


def TarCfuns(parameters: dict, kd: int, shift: str, structure: list, sinkType: str, jobValues: dict) -> None:
    """
    Tars newly created correlation functions together.

    Arguments:
    parameters -- dict: 
    kd         -- int:
    shift      -- str:
    structure  -- list:
    sinkType   -- str:
    jobValues  -- dict

    Globs to create list of files to tar and determines tarfile name based on 
    what was globbed. Ability to specify what to glob intended for future versions.
    """
    tarPath,cfunBase = GetTarFile(parameters,kd,shift,sinkType,jobValues,structure)

    #Looping through particles (We want a different tar for each)
    for chi,chibar in jobValues['particleList']:
        #Finalising filenames
        tarFile = tarPath.replace('CHICHIBAR',f'{chi}{chibar}')
        cfunFiles = cfunBase.replace('CHICHIBAR',f'{chi}{chibar}')
        cfunList = glob.glob(cfunFiles)        #Doing the glob
     
        #Checking that we actually have cfuns to tar
        if len(cfunList) == 0:
            print(f'No cfuns for {chi}{chibar}. If you are not debugging, something has gone wrong')
            continue

        #Putting everything into the tar
        CreateTar(tarFile,cfunList,shift,jobValues)


def GetTarFile(parameters: dict, kd: int, shift: str, sinkType: str, jobValues: dict, structure: list = None, sinkVal: str = '*', *args, **kwargs):
    """
    Compiles the directory and filename of the tar.

    Leaves particle unreplaced.

    Arguments:
    parameters -- dict: 
    kd         -- int:
    shift      -- str:
    sinkType   -- str:
    jobValues  -- dict
    structure  -- list:
    sinkVal    -- str:
    """

    #Getting the general path to the cfuns. We intentionally pass * for sinkVal so
    #that we can glob for that.
    cfunFiles = dirs.GetCfunFile(parameters,jobValues['kappa'],kd,shift,jobValues['sourceType'],sinkType,sinkVal,jobValues['cfgID'])

    if structure is not None:
        #Replacing structure placeholder
        cfunBase = cfunFiles.replace('STRUCTURE',''.join(structure))
    else:
        cfunBase = cfunFiles
        
    #Removing various parts of the cfun filepath to construct the tar path. Removed
    #things are combined in the tar. Use regex to remove for generality, probably
    #not strictly necessary
    tarPath = re.sub(r'sh(([xyzt]\d+)+|(None))\/','',cfunBase)        #shift
    tarPath = re.sub(r'icfg-([ab]|([ghijk]M)){1}-\d+','',tarPath)     #config id
    tarPath = tarPath.replace('.u.2cf','') + '.tar'                   #file extension
    tarPath = tarPath.replace('*','')                                 #any globs
    #Ensuring the directory for the tar exists
    tarDir = pathlib.PurePath(tarPath).parent
    pathlib.Path(tarDir).mkdir(parents=True,exist_ok=True)

    return tarPath, cfunBase


        
def BreakRaceCondition(filePath: str, maxTries: int = 10, *args, **kwargs) -> str:
    """
    Breaks race condition of file being accessed by different processes.

    Arguments:
    filepath -- str: path to file which is being accessed
    maxTries -- int: number of attempts to access file before giving up.

    Returns:
    statusFile -- str: The path to the status file made showing the file is open.
                       Returns failed if it gives up.

    Creates a status file, demonstrating that this process has the file open. If 
    the status file already exists, waits before trying again. Gives up when 
    maxTries is reached.

    STATUS FILE MUST BE DELETED AFTER CLOSING FILE OF INTEREST.
    """

    #Needs to be a pathlib path for touch
    statusFile = pathlib.Path(filePath+'.status')
    counter = 0                    #Attempt counter
    while True:
        if counter >= maxTries:    #'give up' condition
            print('maxTries exceeded, skipping file. File open by other process')
            return 'failed'
        #Try to create the status file
        try:
            statusFile.touch(exist_ok=False)     #creating own status file
            return statusFile
        except FileExistsError:     #If file exists,
             time.sleep(5)          #wait 5 seconds before trying again
             counter += 1
        print(counter)


def CreateTar(tarPath: str, cfunList: list, shift: str, jobValues: dict, *args,**kwargs) -> None:
    """
    Creates/appends the list of cfuns to the tar.

    Arguments:
    tarPath   -- str: File path to the tar. 
    cfunList  -- list: List of cfuns to add to the tar
    shift     -- str: Shift of cfuns to append. For naming inside tar
    jobValues -- dict: Dictionary of job Values
  
    """

    #Need to break race condition with other jobs if doing different configs in
    #different jobs, otherwise they may try to access the same tar simultaneously
    statusFile = BreakRaceCondition(tarPath)
    if statusFile == 'failed':    #If the race condition cannot be broken
        return

    #try is to ensure statusFile is always deleted, even if something goes wrong here
    try:
        print(f'\nPutting cfuns into tar file:\n{tarPath}')
        #Opening tar in append mode
        with tarfile.open(name=tarPath,mode='a') as t:
            #adding all cfuns with name in archive being arcname
            for cfun in cfunList:
                #PurePath required to use .name (just how pathlib works). method
                #extracts just filename.
                t.add(cfun,arcname=f'/sh{shift}/'+pathlib.PurePosixPath(cfun).name)

        #Deleting cfuns which are in tar. We wait until tar is finalised so we don't
        #delete the cfun if it fails
        for cfun in cfunList:
            path = pathlib.Path(cfun)
            path.unlink(missing_ok=True)
              
        #Writing info files - file containing list of cfgids and list of files
        with open(tarPath+'cfglist','a') as f:
            f.write(jobValues['cfgID']+'\n')
        with open(tarPath+'info','a') as i:
            i.write('\n'.join(cfunList))
            i.write('\n')

        #Deleting status file
        statusFile.unlink(missing_ok=True)
    except:
        #Deleting status file, then raising exception and exiting
        statusFile.unlink(missing_ok=True)
        traceback.print_exc()
        exit()



        
