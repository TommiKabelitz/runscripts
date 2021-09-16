"""
Functions to make the files required by cfungen.

All functions require the input filestub, the log file and the relevant
parameters which they print to file. MakePartStubsFile is the exception.

"""

from colarunscripts.configIDs import ConfigID
from colarunscripts import particles
from colarunscripts.utilities import WriteListLengthnList,VariablePrinter


def MakePropPathFiles(filestub,logFile,propDict,structure,*args,**kwargs):
    """
    Make the files containing paths to propagators.

    These are 3, one for each of the u,d,s quarks, files. Each file contains
    only one line, the path to the propagator that will be taking the place
    of that respective quark.

    Arguments:
    filestub  -- str: The base filename without extension to write to
    logFile   -- str: The input logFile to also write inputs to.
    propDict  -- dict: Dictionary containing paths to all of the propagators
    structure -- str list: The specific quark structure we want to make

    Return:
    propList -- str list: List of files we make. Get written to .prop_cfun_info
                          file
    """

    #File extension, QUARK to be replaced to differentiate the files
    extension = '.QUARK.propinfo'
    
    #Initialising list of filenames
    propList = []

    #Looping through quark flavours. trueQuark is the flavour actually being 
    #passed. quarkPosition is where in the traditional u,d,s structure the quark
    #is being passed
    for trueQuark,quarkPosition in zip(structure,['u','d','s']):

        #Grabbing the quark propagator path
        quarkPath = propDict[trueQuark]
        #Replacing the quark in the extension
        ext = extension.replace('QUARK',quarkPosition)

        #Writing to the file
        with open(filestub+ext,'w') as f:
            f.write(f'{quarkPath}\n')
        #Writing to the log file
        with open(logFile,'a') as f:
            f.write(f'\nextension={ext}\n')
            VariablePrinter(f'{quarkPath=}\n',fileObject=f,nameWidth=20)
            
        #Adding the file to the filename list
        propList.append(filestub+ext)
    
    return propList


def MakePartStubsFile(filestub,logFile,particleList,*args,**kwargs):
    """
    Creates the particle stubs file.

    Top of file should be the number of particle pairs with the 
    particle stubs listed underneath it.
    
    Arguments:
    filestub     -- str: The base filename without extension to write to.
    logFile      -- str: The input logFile to also write inputs to.
    particleList -- list: list of lists containing the chi and chibar
                          pairs to be made. 

    """
    #File extension
    extension = '.part_stubs'

    numParticlePairs = len(particleList)
    with open(filestub+extension,'w') as f, open(logFile,'a') as l:
        l.write(f'\n{extension=}\n')

        #Writing number of operator pairs
        f.write(f'{numParticlePairs}\n')
        VariablePrinter(f'{numParticlePairs=}\n',fileObject=l,nameWidth=20)

        #Writing the particle stubs
        for chi,chibar in particleList:
            partstub = filestub + chi + chibar
            f.write(f'{partstub}\n')
            l.write(f'{partstub}\n')



def MakeInterpFile(partstub,logFile,chi,chibar,structure,cfunPrefix,isospinSym,su3FlavLimit,*args,**kwargs):
    """
    Makes the interpolator file containing particle specific information.

    chi and chibar are seperate in the case that we want to do different source 
    and sink operators.

    Arguments:
    partstub     -- str: The file stub for the specific particle
    logFile      -- str: The input logFile to also write inputs to.
    chi          -- str: The source particle
    chibar       -- str: The sink particle
    structure    -- str list: The particle structure we are using
    cfunPrefix   -- str: The base correlation function name
    isospinSym   -- char: Boolean for isospin symmetry
    su3FlavLimit -- char: Boolean for SU(3) flavour limit

    """

    #File extension
    extension = '.interp'
    
    #The name of the correlation function
    cfunName = f'{chi}{chibar}_{"".join(structure)}'

    #ACTUAL INPUT FILE
    #Getting the particle details from the particles module
    particle_details = getattr(particles,chi)()
    #Writing the source details to the file
    #WriteListLengthnList writes first the length of the list, then the elements
    #of the list if it is not empty.
    with open(partstub+extension,'w') as f:
        f.write(f'{cfunName}\n')
        f.write(f'{cfunPrefix}\n')
        WriteListLengthnList(f,particle_details['lorentz_indices'])
        WriteListLengthnList(f,particle_details['gamma_matrices'])
        WriteListLengthnList(f,particle_details['levi_civita_indices'])
        WriteListLengthnList(f,particle_details['cfun_terms'])
        
    #Getting the anti-particle details from the particles module
    particle_details = getattr(particles,chibar)()
    #Writing the sink details to the file
    with open(partstub+extension,'a') as f:
        WriteListLengthnList(f,particle_details['gamma_matrices'])
        WriteListLengthnList(f,particle_details['levi_civita_indices'])
        WriteListLengthnList(f,particle_details['cfun_terms'])
        f.write(f'{isospinSym}\n')
        f.write(f'{su3FlavLimit}\n')

    
    #LOG FILE
    #Getting the particle details from the particles module
    particle_details = getattr(particles,chi)()
    #Writing the source details to the file
    #WriteListLengthnList writes first the length of the list, then the elements
    #of the list if it is not empty.
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        VariablePrinter(f'{cfunName=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{cfunPrefix=}\n',fileObject=f,nameWidth=20)
        WriteListLengthnList(f,particle_details['lorentz_indices'],label='lorentz_indices')
        WriteListLengthnList(f,particle_details['gamma_matrices'],label='gamma_matrices')
        WriteListLengthnList(f,particle_details['levi_civita_indices'],label='levi_civita_indices')
        WriteListLengthnList(f,particle_details['cfun_terms'],label='cfun_terms')
        
    #Getting the anti-particle details from the particles module
    particle_details = getattr(particles,chibar)()
    #Writing the sink details to the file
    with open(logFile,'a') as f:
        WriteListLengthnList(f,particle_details['gamma_matrices'],label='gamma_matrices')
        WriteListLengthnList(f,particle_details['levi_civita_indices'],label='levi_civita_indices')
        WriteListLengthnList(f,particle_details['cfun_terms'],label='cfun_terms')
        VariablePrinter(f'{isospinSym=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{su3FlavLimit=}\n',fileObject=f,nameWidth=20)



def MakeConfigIDsFile(filestub,logFile,cfgID,*args,**kwargs):
    """
    Makes the configuration ID file.

    In the current implementation, only writing the current config ID to the
    file. COLA can handle multiple configurations at once though.
    
    Arguments:
    filestub -- str: The base file to write the ID to
    logFile  -- str: The input logFile to also write inputs to.
    cfgID    -- str: The ID to write
    """

    #File extension
    extension = '.cfg_ids'

    #Writing the ID to file
    with open(filestub+extension,'w') as f:
        f.write(f'{cfgID}\n')

    #Writing the ID to the log file
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        VariablePrinter(f'{cfgID=}\n',fileObject=f,nameWidth=20)



def MakePropCfunInfoFile(filestub,logFile,propList,propFormat,cfunFormat,parallelIO,gmaRep,gellMannRep,pmin,pmax,doUstar,sinkType,useLandau,fullLandauFile='',nLandauModes=0,kd_q='',*args,**kwargs):
    """
    Makes the file containing information relevant to props and cfuns.

    This is a busy file. It contains firstly information about the propagators
    and correlation functions. Then information about the sink. If there is a
    hadronic projection to be done, then the appropriate (Landau) information 
    is passed.
    Finally, the paths to the files containing the paths to the propagators are 
    appended on the end.

    Arguments:
    filestub       -- str: Base filename to write information to
    logFile      -- str: The input logFile to also write inputs to.
    propList       -- str list: List of propagator filenames containing 
                           propagator file paths
    propFormat     -- str: The propagator file extension
    cfunFormat     -- str: The correlation function file extension
    parallelIO     -- char: Boolean character, whether to do file I/O in parallel
    gmaRep         -- str: Gamma matrix representation
    gellMannRep    -- str: Gell Mann matrix representation
    pmin           -- int: Minimimum hadronic projection momentum
    pmax           -- int: Maximimum hadronic projection momentum
    doUstar        -- char: Boolean character, whether to do the U star trick
    sinkType       -- str: Type of sink
    useLandau      -- char: Whether hadronic landau projection is being used
    fullLandauFile -- str: The full Landau mode file
    nLandauModes   -- int: The number of landau modes to project
    kd_q           -- str: Field strength experienced by each quark (charge*kd)
                           eg. "2 -1 0" for u d n at kd=-1
    """

    #File extension
    extension = '.prop_cfun_info'

    #Setting whether we are doing sink smearing
    if sinkType in ['smeared']:
        doSinkSmear = 't'
    else:
        doSinkSmear = 'f'

    #Writing to the file
    with open(filestub+extension,'w') as f:
        f.write(f'{1}\n')  #Number of configurations we are doing at once   
        f.write(f'{propFormat}\n')
        f.write(f'{cfunFormat}\n')
        f.write(f'{parallelIO}\n')
        f.write(f'{gmaRep}\n')
        f.write(f'{gellMannRep}\n')
        f.write(f'{pmin}\n')
        f.write(f'{pmax}\n')
        f.write(f'{doSinkSmear}\n')
        f.write(f'{doUstar}\n')
        f.write(f'{sinkType}\n')
        f.write(f'{useLandau}\n')
        if useLandau == 't':
            f.write(f'{fullLandauFile}\n')
            f.write(f'{kd_q}\n')
        for propFile in propList:
            f.write(f'{propFile}\n')

    #Writing to the log file
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        f.write(f'{"simultaneousConfigs":20}= 1\n')  #Number of configurations we are doing at once   
        VariablePrinter(f'{propFormat=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{cfunFormat=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{parallelIO=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{gmaRep=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{gellMannRep=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{pmin=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{pmax=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{doSinkSmear=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{doUstar=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{sinkType=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{useLandau=}\n',fileObject=f,nameWidth=20)
        if useLandau == 't':
            VariablePrinter(f'{fullLandauFile=}\n',fileObject=f,nameWidth=20)
            VariablePrinter(f'{kd_q=}\n',fileObject=f,nameWidth=20)
        for propFile in propList:
            VariablePrinter(f'{propFile=}\n',fileObject=f,nameWidth=20)

def MakeLatticeFile(filestub,logFile,extent):
    """
    Make the .lat input file for cfungenGPU.x.
    
    Arguments:
    filestub -- string: The filename, without the .lat extension
                         to write lattice details to.
    logFile  -- str: The input logFile to also write inputs to.
    extent   -- int list: number of lattice point in each 
                         direction. Order is [nx,ny,nz,nt].
    """
    extension = '.lat'
    
    #Writing to the file
    with open(filestub+extension,'w') as f:
        f.write('\n'.join(str(dim) for dim in extent))
        f.write('\n')

    #Writing to the log file
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        f.write('\n'.join(f'{dim:20}= {val}' for dim,val in zip(['x','y','z','t'],extent)))
        f.write('\n')



def MakeGFSFile(filestub,logFile,configFormat,configFile,shift,*args,**kwargs):
    """
    Makes that gauge field input file.

    Arguments:
    filestub     -- str: The base filename to write to
    logFile      -- str: The input logFile to also write inputs to.
    configFormat -- str: The file extension of the gauge field files
    configFile   -- str: The path of the configuration file (no extension)

    """

    #File extension
    extension = '.gfs'

    #Writing to the file
    with open(filestub+extension,'w') as f:
        f.write(f'1\n')       #Number of configurations we are doing at once    
        f.write(f'{configFormat}\n')
        f.write(f'{shift}')
        f.write(f'{configFile}\n')
                
    #Writing to the log file
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        f.write(f'{"simultaneousConfigs":20}= 1\n')       #Number of configurations we are doing at once    
        VariablePrinter(f'{configFormat=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{shift=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{configFile=}\n',fileObject=f,nameWidth=20)

def MakeLPSinkFile(filestub,logFile,nDim_lpsnk,shift,lapModeFiles,baseSinkCode,nModes_lpsnk,*args,**kwargs):
    """
    Makes the Laplacian sink file.

    Arguments:
    filestub     -- str: Base filename to write details to
    logFile      -- str: The input logFile to also write inputs to.
    nDim_lpSnk   -- int: Number of dimensions that we project
                         the Laplacian sink to
    lapModeFiles -- str list: List containing paths to eigenmode
                         files. In order u,d,s
    sinkCode     -- str: Label inserted into the correlation 
                         function filename. Can be used to store
                         sink information
    nModes_lpsnk -- int: Number of modes to truncate the Laplacian
                         at.
    
    """
    
    #File extension
    extension = '.qpsnk_lp'
    
    #Number of distinct nModes_lpsnk values to use
    nSnk_lp = len(nModes_lpsnk)

    #Writing to the file
    with open(filestub+extension,'w') as f:
        f.write(f'{nDim_lpsnk}\n')
        f.write(f'{shift}\n')
        for modeFile in lapModeFiles:
            f.write(f'{modeFile}\n')
        f.write(f'{nSnk_lp}\n')
        for modes in nModes_lpsnk:
            sinkCode = baseSinkCode.replace('MODES',str(modes))
            f.write(f'{sinkCode}\n')
            #COLA requires nModes in x,y,z dirs
            f.write(3*f'{modes} '+'\n')

    #Writing to the log file
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        VariablePrinter(f'{nDim_lpsnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{shift=}\n',fileObject=f,nameWidth=20)
        for modeFile in lapModeFiles:
            VariablePrinter(f'{modeFile=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{nSnk_lp=}\n',fileObject=f,nameWidth=20)
        for modes in nModes_lpsnk:
            sinkCode = baseSinkCode.replace('MODES',str(modes))
            VariablePrinter(f'{sinkCode=}\n',fileObject=f,nameWidth=20)
            #COLA requires nModes in x,y,z dirs
            f.write(f'{"modes":20}= '+3*f'{modes} '+'\n')



def MakePropSmearingFile(filestub,logFile,sinkSmearcode,alpha_smsnk,u0_smsnk,kd,swpsFat_lnk,useStout_lnk,alphaFat_lnk,sweeps_smsnk,*args,**kwargs):
    """
    Makes the input file related to smearing (sink and link).

    Arguments:
    filestub      -- str: Base filename to write details to
    logFile       -- str: The input logFile to also write inputs to.
    sinkSmearCode -- str: Which dimensions to smear
    alpha_smsnk   -- float: Sink smearing intensity
    u0_smsnk      -- float: Mean-field improvement factor
    kd            -- int: Field strength
    swpsFat_lnk   -- int: Number of fat link smearing sweeps
    useStout_lnk  -- char: Whether to do stout link smearing
    alphaFat_lnk  -- float: Link smearing intensity
    sweeps_smsnk  -- int: Number of sink smearing sweeps
    """

    #File extension
    extension = '.prop_sm_params'
    
    #Number of different sweep values
    nsnk = len(sweeps_smsnk)

    #Writing to the file
    with open(filestub+extension,'w') as f:
        f.write(f'{sinkSmearcode}\n')
        f.write(f'{alpha_smsnk}\n')
        f.write(f'{u0_smsnk}\n')
        f.write(f'{kd}\n')
        f.write(f'{nsnk}\n')
        for sweeps in sweeps_smsnk:
            f.write(f'{sweeps}\n')
        f.write(f'{swpsFat_lnk}\n')
        f.write(f'{useStout_lnk}\n')
        f.write(f'{alphaFat_lnk}\n')

    #Writing to the log file
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        VariablePrinter(f'{sinkSmearcode=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{alpha_smsnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{u0_smsnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{kd=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{nsnk=}\n',fileObject=f,nameWidth=20)
        for sweeps in sweeps_smsnk:
            VariablePrinter(f'{sweeps=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{swpsFat_lnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{useStout_lnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{alphaFat_lnk=}\n',fileObject=f,nameWidth=20)

