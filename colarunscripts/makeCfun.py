"""
Module for making correlation function by calling cfungenGPU.x

'main()' function is called by  manageJob.py which passes the job specific
details to this function.

This script is not intended to  be called fromthe command line

"""

#standard library modules
import pprint                       #nice dictionary printing (for debugging)
import subprocess                   #for calling cfungenGPU.x
from datetime import datetime       #for writing out the time

#local modules
from colarunscripts import configIDs as cfg
from colarunscripts import directories as dirs
from colarunscripts import cfgenFiles as files
from colarunscripts import particles as part
from colarunscripts.makePropagator import CallMPI
from colarunscripts.particles import QuarkCharge
from colarunscripts.shifts import FormatShift
#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 



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
    
    with open(logFile,'a') as f:
        f.write('\nInput files not dependent on structure:\n')
        
    #Making files which are reused for all structures
    MakeReusableFiles(parameters,filestub,logFile,kd,shift,jobValues)
    
    with open(logFile,'a') as f:
        f.write('\nInput files dependent on structure:\n')

    #Looping over different structures
    for structure in parameters['runValues']['structureList']:

        with open(logFile,'a') as f,open(jobValues['inputSummary']['interp'],'a') as g:

            print(f'\nDoing structure set: {structure}\n')
            f.write(f'\nDoing structure set: {structure}\n')
            g.write(f'\nDoing structure set: {structure}\n')
                
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

        #Calling cfungen
        timer.startTimer('Correlation functions')
        CallMPI(executable,reportFile,filestub=filestub,numGPUs=numGPUs)
        timer.stopTimer('Correlation functions')

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
        if quark in ['s','nh']:
            quarkLabel = 'h'
            jobValues['kappa'] = parameters['propcfun']['strangeKappa']
        else:
            quarkLabel = 'l'
        
        #Getting the base propagator file
        propFile = dirs.FullDirectories(parameters,directory='prop',kd=kd,shift=shift,**jobValues,**parameters['sourcesink'])['prop']
        
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
    files.MakePartStubsFile(filestub,logFile,particleList)

    

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
    modeFiles = dirs.LapModeFiles(parameters,kd=kd,quark=structure,**jobValues)   #(dict)
    lapModeFiles = [modeFiles[quark] for quark in structure]   #(above as list) 
    files.MakeLPSinkFile(filestub,logFile,shift=FormatShift(shift,fullShift='lpsink'),lapModeFiles=lapModeFiles,**parameters['sourcesink'])

    #Setting isospin symmetry based on field strength
    if kd == 0:
        isospinSym = 't'
    else:
        isospinSym = 'f'
        
    #Correlation function filepath
    cfunPrefix = dirs.FullDirectories(parameters,directory='cfun',kd=kd,shift=shift,**jobValues,**parameters['sourcesink'])['cfun']
    
    #Looping over operator pairs
    for chi,chibar in jobValues['particleList']:
        #compiling the particle stub ie. 5319732_4protonprotonbar
        partstub = filestub + chi + chibar
        
        #Making the interpolator file using that stub
        files.MakeInterpFile(partstub,jobValues['inputSummary']['interp'],chi,chibar,structure,cfunPrefix,isospinSym,**parameters['propcfun'])

        #Getting the details regarding the hadronic projection (fourier vs landau, etc...)
        hadronicProjection = HadronicProjection(parameters,kd,chi,structure)

        #Making the files which hold the paths to the propagators in the u,d,s 
        #spots. Returns the paths to those files. Apparently must be fed in
        #order u,s,d. I don't know why - apparently because u,s often degenerate
        propList = files.MakePropPathFiles(filestub,logFile,propDict,structure)
        propList[1],propList[2] = propList[2],propList[1]

        files.MakePropCfunInfoFile(filestub,logFile,propList,**parameters['directories'],**parameters['propcfun'],**parameters['runValues'],**hadronicProjection)


def HadronicProjection(parameters,kd,particle,structure,*args,**kwargs):
    """
    Returns the details for the hadronic projection.

    Arguments:
    parameters -- dict: Dictionary of all of the run parameters.
                        From parameters.yml
    kd         -- int: The field strength
    particle   -- str: The hadron in question
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
