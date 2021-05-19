'''
Module containing the different sources that can be used.

Orders the inputs into a list ready to be printed to the 
COLA input files. Actual input values go in smearing.py. 
All functions return a dictionary. One entry the 
sourcetype_num. The other the list. 
Recommend input from expanded dictionaries, though not 
required.

Current sources available:
point(pt),smeared(sm),Laplacian(lp),lpsm,lpxyz,xyz


Adding sources requires addition here and in smearing.py.

Function arguments:
sourceLocation -- Integer list: the x,y,z,t coordinates of the source
so_val -- Integer: The 'source value,' ie. 
                   -for smeared sources, the number of smeared
                    sources
                   -for lp, number of emodes projected at 
                    the source
lapmodefile -- String: Location of the eigenmodes for the quark.
nDim_lpsrc -- Integer: Related to the Laplacian projection. Number of 
                   dimensions.
lp_sm = [smearcode,preSmear_lpsmsrc,lapsmear]
            -- List [str,bool,int]: Parameters related to Laplacian 
                   smearing. In order, smearing directions,
                   preSmear_lpsmsrc (smear before or after projection),
                   number of laplacian smearing sweeps.
src_sm = [alpha_smsrc,useUzero,u0_smsrc] 
            -- List [float,bool,float]: Parameters related to the 
                   smearing of the source. See /src/sourcetypes.f90
link_sm = [useStout_lnk,alphaFat_lnk,swpsFat_lnk]
            -- List [bool,float,int]: Parameters related to link
                   smearing. In order, whether to do stout
                   link smearing, the alpha value and the
                   number of sweeps. Boolean must be in form
                   of just 'T' or 'F'. Case insensitive.
'''


def pt(sourceLocation, *args, **kwargs):
    '''
    Returns key information for a point source.

    Point source is no smearing or projection.
    '''

    source = {}
    source['sourcetype_num'] = 1
    source['values'] = sourceLocation
    
    return source




def sm(sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):
    '''
    Returns key information for a normally smeared source.
    '''

    source = {}
    source['sourcetype_num'] = 3
    source['values'] = sourceLocation + [ sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk ]
    
    return source



def lp(lapmodefile, nDim_lpsrc, nModes_lpsrc, sourceLocation, *args, **kwargs):
    '''
    Returns key information for Laplacian source.

    Laplacian source does no smearing. Instead projects only to
    the Laplacian operator.
    '''

    source = {}
    source['sourcetype_num'] = 7
    source['values'] = [ lapmodefile, nDim_lpsrc, nModes_lpsrc ] + sourceLocation

    return source

def xyz(sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):
    '''
    Returns key information for the xyz source

    Does no projection and smears only in the x and y directions
    (Not 100% on smearing directions)
    '''
    smearcode = 'xy'
    source = {}
    source['sourcetype_num'] = 8
    source['values'] = [smearcode] + sourceLocation + [ sweeps_smsrc, alpha_smsrc,useUzero_smsrc,u0_smsrc + useStout_lnk,alphaFat_lnk,swpsFat_lnk ]

    return source



def lpsm(lapmodefile, nDim_lpsrc, nModes_lpsrc, preSmear_lpsmsrc, sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):
    '''
    Returns key information for the Laplacian, smeared source.

    Does Laplacian projection and smears in all spatial directions (we think).
    '''

    source = {}
    source['sourcetype_num'] = 9
    source['values'] = [ lapmodefile, nDim_lpsrc, nModes_lpsrc, preSmear_lpsmsrc ] + sourceLocation + [ sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk]
    
    return source




def lpxyz(lapmodefile, nDim_lpsrc, nModes_lpsrc, preSmear_lpsmsrc, sourceLocation, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):
    '''
    Returns key information for the Laplacian, xyz source.

    Laplacian xyz source does Laplacian projection and smearing.
    Smears only in direction(s) provided by smearcode.
    '''

    smearcode = 'z'

    source = {}
    source['sourcetype_num'] = 10
    source['values'] = [ smearcode,lapmodefile,nDim_lpsrc,nModes_lpsrc,preSmear_lpsmsrc ] + sourceLocation + [ sweeps_smsrc,alpha_smsrc,useUzero_smsrc,u0_smsrc, useStout_lnk,alphaFat_lnk,swpsFat_lnk ]
    
    return source
