from configIDs import ConfigID
import particles
import utilities as ut


def MakePropPathFiles(filestub,propDict,structure,*args,**kwargs):
    '''
    Make the files containing paths to propagators.

    These are 3, one for each of the u,d,s quarks, files. Each file contains
    only one line, the path to the propagator that will be taking the place
    of that respective quark.

    Arguments:
    filestub  -- str: The base filename without extension to write to
    propDict  -- dict: Dictionary containing paths to all of the propagators
    structure -- str list: The specific quark structure we want to make

    Return:
    propList -- str list: List of files we make. Get written to .prop_cfun_info
                          file
    '''
    #File extension, QUARK to be replaced to differentiate the files
    extension = '.QUARK.propinfo'
    
    #Initialising list of filenames
    propList = []

    #Looping through quark flavours. trueQuark is the flavour actually being 
    #passed. quarkPosition is where in the traditional u,d,s structure the quark
    #is being passed
    for trueQuark,quarkPosition in zip(structure,['u','d','s']):
        #Grabbing the quark path
        quarkPath = propDict[trueQuark]
        #Replacing the extension for the write file
        ext = extension.replace('QUARK',quarkPosition)
        #Writing to the file
        with open(filestub+ext,'w') as f:
            f.write(f'{quarkPath}\n')
        #Adding the file to the filename list
        propList.append(filestub+ext)

    return propList


def AppendPartStub(filestub,partstub=None,numParticlePairs=None,*args,**kwargs):
    '''
    Creates the particle stubs file. Appending where necessary.

    Top of file should be the number of particle pairs with the 
    particle stubs listed underneath it.
    
    Arguments:
    numParticlePairs -- str: The number of pairs of particles we are making
    partsub          -- str: The particle specific filestub which is used for 
                             the interpolator file. Particle stubs should be
                             passed one at a time

    '''
    #File extension
    extension = '.part_stubs'
    
    #In both cases, we check if something is passed, if so it is written
    if numParticlePairs is not None:
        with open(filestub+extension,'w') as f:    
            f.write(f'{numParticlePairs}\n')
        
    if partstub is not None:
        with open(filestub+extension,'a') as f:
            f.write(f'{partstub}\n')



def MakeInterpFile(partstub,chi,chibar,structure,cfunPrefix,isospinSym,su3FlavLimit,*args,**kwargs):
    '''
    Makes the interpolator file containing particle specific information.

    chi and chibar are seperate in the case that we want to do different source 
    and sink operators.

    Arguments:
    partstub     -- str: The file stub for the specific particle
    chi          -- str: The source particle
    chibar       -- str: The sink particle
    structure    -- str list: The particle structure we are using
    cfunPrefix   -- str: The base correlation function name
    isospinSym   -- char: Boolean for isospin symmetry
    su3FlavLimit -- char: Boolean for SU(3) flavour limit

    '''

    #File extension
    extension = '.interp'
    
    #The name of the correlation function
    cfunName = f'{chi}{chibar}_{"".join(structure)}'

    #Getting the particle details from the particles module
    particle_details = getattr(particles,chi)()
    #Writing the source details to the file
    #WriteListLengthnList writes first the length of the list, then the elements
    #of the list if it is not empty.
    with open(partstub+extension,'w') as f:
        f.write(f'{cfunName}\n')
        f.write(f'{cfunPrefix}\n')
        ut.WriteListLengthnList(f,particle_details['lorentz_indices'])
        ut.WriteListLengthnList(f,particle_details['gamma_matrices'])
        ut.WriteListLengthnList(f,particle_details['levi_civita_indices'])
        ut.WriteListLengthnList(f,particle_details['cfun_terms'])
        
    #Getting the anti-particle details from the particles module
    particle_details = getattr(particles,chibar)()
    #Writing the sink details to the file
    with open(partstub+extension,'a') as f:
        ut.WriteListLengthnList(f,particle_details['gamma_matrices'])
        ut.WriteListLengthnList(f,particle_details['levi_civita_indices'])
        ut.WriteListLengthnList(f,particle_details['cfun_terms'])
        f.write(f'{isospinSym}\n')
        f.write(f'{su3FlavLimit}\n')



def MakeConfigIDsFile(filestub,cfgID,*args,**kwargs):
    '''
    Makes the configuration ID file.

    In the current implementation, only writing the current config ID to the
    file. COLA can handle multiple configurations at once though.
    
    Arguments:
    filestub -- str: The base file to write the ID to
    cfgID    -- str: The ID to write
    '''

    #File extension
    extension = '.cfg_ids'

    #Writing the ID to file
    with open(filestub+extension,'w') as f:
        f.write(f'{cfgID}\n')
    


def MakePropCfunInfoFile(filestub,cfunPrefix,propList,propFormat,cfunFormat,parallelIO,gmaRep,gellMannRep,pmin,pmax,doUstar,sinkType,useLandau,fullLandauFile='',nLandauModes=0,*args,**kwargs):
    '''
    Makes the file containing information relevant to props and cfuns.

    This is a busy file. It contains firstly information about the propagators
    and correlation functions. Then information about the sink. If there is a
    hadronic projection to be done, then the appropriate (Landau) information 
    is passed.
    Finally, the paths to the files containing the paths to the propagators are 
    appended on the end.

    Arguments:
    filestub       -- str: Base filename to write information to
    cfunPrefix     -- str: Base correlation function filename (no cfgID,particles)
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

    '''

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
            f.write(f'{nLandauModes}\n')
        for propFile in propList:
            f.write(f'{propFile}\n')
     

def MakeLatticeFile(filestub,extent):
    '''
    Make the .lat input file for cfungenGPU.x.
    
    Arguments:
    filestub -- string: The filename, without the .lat extension
                         to write lattice details to.
    extent -- int list: number of lattice point in each 
                         direction. Order is [nx,ny,nz,nt].
    '''
    extension = '.lat'

    with open(filestub+extension,'w') as f:
        f.write('\n'.join(str(dim) for dim in extent))
        f.write('\n')



def MakeGFSFile(filestub,configFormat,configFile,*args,**kwargs):
    '''
    Makes that gauge field input file.

    Arguments:
    filestub     -- str: The base filename to write to
    configFormat -- str: The file extension of the gauge field files
    configFile   -- str: The path of the configuration file (no extension)

    '''

    #File extension
    extension = '.gfs'

    #Writing to the file
    with open(filestub+extension,'w') as f:
        f.write(f'1\n')       #Number of configurations we are doing at once    
        f.write(f'{configFormat}\n')
        f.write(f'{configFile}\n')
        

def MakeLPSinkFile(filestub,nDim_lpsnk,lapModeFiles,sinkCode,nModes_lpsnk,*args,**kwargs):
    '''
    Makes the Laplacian sink file.

    Arguments:
    filestub     -- str: Base filename to write details to
    nDim_lpSnk   -- int: Number of dimensions that we project
                         the Laplacian sink to
    lapModeFiles -- str list: List containing paths to eigenmode
                         files. In order u,d,s
    sinkCode     -- str: Label inserted into the correlation 
                         function filename. Can be used to store
                         sink information
    nModes_lpsnk -- int: Number of modes to truncate the Laplacian
                         at.
    
    '''
    
    #File extension
    extension = '.qpsnk_lp'
    
    #Number of distinct nModes_lpsnk values to use
    nSnk_lp = 1
    #Writing to the file
    with open(filestub+extension,'w') as f:
        f.write(f'{nDim_lpsnk}\n')
        for modeFile in lapModeFiles:
            f.write(f'{modeFile}\n')
        f.write(f'{nSnk_lp}\n')
        f.write(f'{sinkCode}\n')
        #COLA requires nModes in x,y,z dirs
        f.write(3*f'{nModes_lpsnk} '+'\n')
        


def MakePropSmearingFile(filestub,sinkSmearcode,alpha_smsnk,u0_smsnk,kd,swpsFat_lnk,useStout_lnk,alphaFat_lnk,sweeps_smsnk,*args,**kwargs):
    '''
    Makes the input file related to smearing (sink and link).

    Arguments:
    filestub      -- str: Base filename to write details to
    sinkSmearCode -- str: Which dimensions to smear
    alpha_smsnk   -- float: Sink smearing intensity
    u0_smsnk      -- float: Mean-field improvement factor
    kd            -- int: Field strength
    swpsFat_lnk   -- int: Number of fat link smearing sweeps
    useStout_lnk  -- char: Whether to do stout link smearing
    alphaFat_lnk  -- float: Link smearing intensity
    sweeps_smsnk  -- int: Number of sink smearing sweeps
    '''

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

