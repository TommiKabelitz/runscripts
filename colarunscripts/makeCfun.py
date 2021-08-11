'''
Module for making correlation function by calling cfungenGPU.x

'main()' function is called by  manageJob.py which passes the job specific
details to this function.

This script is not intended to  be called fromthe command line

'''

#standard library modules
import pprint                       #nice dictionary printing (for debugging)
import subprocess                   #for calling cfungenGPU.x
from datetime import datetime       #for writing out the time

#local modules
from colarunscripts import configIDs as cfg
from colarunscripts import directories as dirs
from colarunscripts import cfgenFiles as files
from colarunscripts import parameters as params
from colarunscripts import particles as part
from colarunscripts.makePropagator import CallMPI
from colarunscripts.particles import QuarkCharge
#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 



def main(jobValues,timer,*args,**kwargs):
    '''
    Main function. Begins correlation function production process

    Arguments:
    jobValues -- dict: Dictionary containing the job specific values such as
                       kd, shift, nthConfig, etc...
    timer     -- Timer: Timer object to manage timing of correlation function
                       calculation time.
    '''

    #compiling the filestub for the input files to feed to cfungen
    filestub = dirs.FullDirectories(directory='cfunInput')['cfunInput'] + jobValues['jobID'] + '_' + str(jobValues['nthConfig'])
    
    #Calling the function that does all the work
    MakeCorrelationFunctions(filestub,jobValues,timer)



def MakeCorrelationFunctions(filestub,jobValues,timer,*args,**kwargs):
    """
    Makes the input files and then the actual correlation functions.

    Arguments:
    filestub  -- str: Base input filestub to pass to cfungenGPU.x
    jobValues -- dict: Dictionary containing the job specific values such as
                      kd, shift, nthConfig, etc...
    timer     -- Timer: Timer object to manage timing of correlation function
                      calculation time.


    """

    #Grabbing the parameters from parameter.yml
    parameters = params.Load()
    
    #Getting a dictionary of paths to all possible props
    #(props don't necessarily exist unless required)
    propDict = CompilePropPaths(jobValues,parameters)

    #Making files which are reused for all structures
    MakeReusableFiles(filestub,jobValues,parameters)
    
    #Looping over different structures
    for structure in parameters['runValues']['structureList']:

        print(f'\nDoing structure set: {structure}\n')

        #Just printing quark paths for reference
        print(f'Quark paths are: ')
        for quark in structure:
            print(f'{quark}: {propDict[quark]}')

        print('Making structure specific files')
        MakeSpecificFiles(filestub,structure,propDict,jobValues,parameters)
      
        #Preparing final variables for call to cfungen
        executable = parameters['propcfun']['cfgenExecutable']
        numGPUs = parameters['slurmParams']['numGPUs']
        reportFile = dirs.FullDirectories(directory='cfunReport',structure=structure,**jobValues,**parameters['sourcesink'])['cfunReport']

        #Calling cfungen
        timer.startTimer('Correlation functions')
        CallMPI(executable,reportFile,filestub=filestub,numGPUs=numGPUs)
        timer.stopTimer('Correlation functions')

def CompilePropPaths(jobValues,parameters,*args,**kwargs):
    '''
    Creates a dictionary of propagator paths for all quarks in the quarkList.

    Arguments:
    jobValues  -- dict: Dictionary containing job specific values
    parameters -- dict: Dictionary of all of the run parameters.
                        From parameters.yml

    '''

    #Will change the kd value in jobvalues so saving it to fix at the end
    kd_original = jobValues['kd']
    kappa_original = jobValues['kappa']

    #Initialising output dictionary
    propDict = {}
    
    #Looping over quarks in quark list
    for quark in parameters['propcfun']['quarkList']:

        #Effectively only make 2 types of propagator. Light (d) and heavy (s).
        #The rest we get through charge manipulation (u=-2*d,nl=0*d,nh=0*nh).
        jobValues['kd'] *= QuarkCharge(quark)
        if quark in ['s','nh']:
            quarkLabel = 's'
            jobValues['kappa'] = parameters['propcfun']['strangeKappa']
        else: #['u','d','nl]
            quarkLabel = 'd'
        
        #Getting the base propagator file
        propFile = dirs.FullDirectories(directory='prop',**jobValues,**parameters['sourcesink'])['prop']
        
        #Adding the kappa value and file extension (propFormat) which are 
        #appended by quarkpropGPU.x
        propFormat = parameters["directories"]["propFormat"]
        propFile = propFile.replace('QUARK',quarkLabel)
        propFile += f'k{jobValues["kappa"]}.{propFormat}'
        
        #Saving the path to the dictionary
        propDict[quark] = propFile
        jobValues['kd'] = kd_original
        jobValues['kappa'] = kappa_original
        #end quark loop

    #returning the field strength to its original value

    return propDict




def MakeReusableFiles(filestub,jobValues,parameters,*args,**kwargs):
    '''
    Makes the input files which are structure independent and reusable.

    Arguments:
    filestub   -- str: Base filestub to pass to cfungenGPU.x
    jobValues  -- dict: Dictionary containing job specific values
    parameters -- dict: Dictionary of all of the run parameters.
                        From parameters.yml

    '''
    
    print('Making input files independent of structure')

    files.MakeLatticeFile(filestub,**parameters['lattice'])
        
    files.MakeConfigIDsFile(filestub,**jobValues)

    #Getting the gauge field configuration file, then making the relevant input 
    #file
    configFile = dirs.FullDirectories(directory='configFile',**jobValues)['configFile']
    files.MakeGFSFile(filestub,parameters['directories']['configFormat'],configFile)
    
    #Making the smearing file, still read in for Laplacian sink (I think)
    files.MakePropSmearingFile(filestub,**parameters['sourcesink'],**jobValues)



def MakeSpecificFiles(filestub,structure,propDict,jobValues,parameters):
    '''
    Makes the files which depend on structure and cannot be reused.

    Arguments:
    filestub   -- str: Base filestub to pass to cfungenGPU.x
    structure  -- str list: Quark structure
    propDict   -- dict: Dictionary containing prop paths
    jobValues  -- dict: Dictionary containing job specific values
    parameters -- dict: Dictionary of all of the run parameters.
                        From parameters.yml
    
    '''

    #Making Laplacian Sink File
    modeFiles = dirs.LapModeFiles(**jobValues)   #(dict)
    lapModeFiles = [modeFiles[quark] for quark in structure]   #(above as list) 
    files.MakeLPSinkFile(filestub,lapModeFiles=lapModeFiles,**parameters['sourcesink'])

    #Setting isospin symmetry based on field strength
    if jobValues['kd'] == 0:
        isospinSym = 't'
    else:
        isospinSym = 'f'
        
    #Correlation function filepath
    cfunPrefix = dirs.FullDirectories(directory='cfun',**jobValues,**parameters['sourcesink'])['cfun']
    
    #Writing number of operator pairs to the particle_stubs file
    particleList = parameters['runValues']['particleList']
    files.AppendPartStub( filestub,numParticlePairs=len(particleList) )

    #Looping over operator pairs
    for chi,chibar in particleList:
        #compiling the particle stub ie. 5319732_4protonprotonbar
        partstub = filestub + chi + chibar
        
        #Making the interpolator file using that stub
        files.MakeInterpFile(partstub,chi,chibar,structure,cfunPrefix,isospinSym,**parameters['propcfun'])

        #appending that stub into the particle stubs file
        files.AppendPartStub(filestub,partstub=partstub)

        #Getting the details regarding the hadronic projection (fourier vs landau, etc...)
        hadronicProjection = HadronicProjection(jobValues['kd'],chi,structure,parameters)

        #Making the files which hold the paths to the propagators in the u,d,s 
        #spots. Returns the paths to those files. Apparently must be fed in
        #order u,s,d. I don't know why - apparently because u,s often degenerate
        propList = files.MakePropPathFiles(filestub,propDict,structure)
        propList[1],propList[2] = propList[2],propList[1]

        files.MakePropCfunInfoFile(filestub,propList,**parameters['directories'],**parameters['propcfun'],**parameters['runValues'],**hadronicProjection)


def HadronicProjection(kd,particle,structure,parameters,*args,**kwargs):
    '''
    Returns the details for the hadronic projection.

    Arguments:
    kd         -- int: The field strength
    particle   -- str: The hadron in question
    structure  -- str: list: Quark structure
    parameters -- dict: Dictionary of all of the run parameters.
                        From parameters.yml

    '''
    
    #Projection type depends on field strength
    if kd == 0:
        #Fourier project at zero field strength where Landau levels vanish
        return parameters['hadronicProjection']['fourier']
    else:
        #At non-zero field strength, do a projection to the Landau levels.
        #First get base details.
        details = parameters['hadronicProjection']['landau']

        effectiveQuarkCharge = []
        for quark in structure:
            effectiveQuarkCharge.append(part.QuarkCharge(quark)*kd)

        details['kd_q'] = ' '.join([str(x) for x in effectiveQuarkCharge])
        details['fullLandauFile'] = dirs.FullDirectories(directory='landau')['landau']
        return details
