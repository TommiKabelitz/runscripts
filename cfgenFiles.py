from configIDs import ConfigID
import particles
import utilities as ut


def MakePropPathFiles(filestub,propDict,structure,*args,**kwargs):
    extension = '.QUARK.propinfo'
    
    propList = []
    for trueQuark,quarkPosition in zip(structure,['u','d','s']):
        quarkPath = propDict[trueQuark]
        ext = extension.replace('QUARK',quarkPosition)
        with open(filestub+ext,'w') as f:
            f.write(f'{quarkPath}\n')
        propList.append(filestub+ext)

    return propList


def AppendPartStub(filestub,partstub=None,numParticlePairs=None,*args,**kwargs):
    extension = '.part_stubs'
    
    
    if numParticlePairs is not None:
        with open(filestub+extension,'w') as f:    
            f.write(f'{numParticlePairs}\n')
        
    if partstub is not None:
        with open(filestub+extension,'a') as f:
            f.write(f'{partstub}\n')


def MakeInterpFile(part_stub,chi,chibar,structure,cfunPrefix,isospinSym,su3FlavLimit,*args,**kwargs):
    extension = '.interp'
    
    cfunName = f'{chi}{chibar}_{"".join(structure)}'

    particle_details = getattr(particles,chi)()
    with open(part_stub+extension,'w') as f:
        f.write(f'{cfunName}\n')
        f.write(f'{cfunPrefix}\n')
        ut.WriteListLengthnList(f,particle_details['lorentz_indices'])
        ut.WriteListLengthnList(f,particle_details['gamma_matrices'])
        ut.WriteListLengthnList(f,particle_details['levi_civita_indices'])
        ut.WriteListLengthnList(f,particle_details['cfun_terms'])
        
    particle_details = getattr(particles,chibar)()
    with open(part_stub+extension,'a') as f:
        ut.WriteListLengthnList(f,particle_details['gamma_matrices'])
        ut.WriteListLengthnList(f,particle_details['levi_civita_indices'])
        ut.WriteListLengthnList(f,particle_details['cfun_terms'])
        f.write(f'{isospinSym}\n')
        f.write(f'{su3FlavLimit}\n')




def MakeConfigIDsFile(filestub,cfgID,**kwargs):
    extension = '.cfg_ids'

    with open(filestub+extension,'w') as f:
        f.write(f'{cfgID}\n')
    


def MakePropCfunInfoFile(filestub,cfunPrefix,propList,propFormat,cfunFormat,parallelIO,gmaRep,gellMannRep,pmin,pmax,doUstar,sinkType,useLandau,fullLandauFile='',nLandauModes=0,*args,**kwargs):
    extension = '.prop_cfun_info'

    if sinkType in ['smeared']:
        doSinkSmear = 't'
    else:
        doSinkSmear = 'f'

    with open(filestub+extension,'w') as f:
        f.write(f'{1}\n')   
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
    lextent -- int list: number of lattice point in each 
                         direction. Order is [nx,ny,nz,nt].
    '''
    extension = '.lat'

    with open(filestub+extension,'w') as f:
        f.write('\n'.join(str(dim) for dim in extent))
        f.write('\n')



def MakeGFSFile(filestub,configFormat,configFile,*args,**kwargs):
    extension = '.gfs'

    with open(filestub+extension,'w') as f:
        f.write(f'1\n')  
        f.write(f'{configFormat}\n')
        f.write(f'{configFile}\n')
        

def MakeLPSinkFile(filestub,nDim_lpsnk,lapModeFiles,sinkCode,nModes_lpsnk,*args,**kwargs):
    extension = '.qpsnk_lp'

    nSnk_lp = 1
    with open(filestub+extension,'w') as f:
        f.write(f'{nDim_lpsnk}\n')
        for modeFile in lapModeFiles:
            f.write(f'{modeFile}\n')
        f.write(f'{nSnk_lp}\n')
        f.write(f'{sinkCode}\n')
        f.write(3*f'{nModes_lpsnk} '+'\n')
        


def MakePropSmearingFile(filestub,sinkSmearcode,alpha_smsnk,u0_smsnk,kd,swpsFat_lnk,useStout_lnk,alphaFat_lnk,sweeps_smsnk,*args,**kwargs):
    extension = '.prop_sm_params'

    nsnk = len(sweeps_smsnk)

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



def MakeParticlesFile(filestub='',particlestubs=[],*args,**kwargs):
    extension = '.partstubs'

    num_particles = len(particlestubs)

    with(filestub+extension,'w') as f:
        f.write(f'{num_particles}\n')
        for stub in particlestubs:
            f.write(f'{stub}\n')




#if __name__ == '__main__':
    
    
