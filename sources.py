"""
Module containing the different sources that can be used.

Orders the inputs into lists ready to be printed to the 
COLA input files. Actual input values go in smearing.py. 
All functions return dictionary of lists. One list for each
quark. Labelled u,d,s,n,ns. Recommend input from expanded 
dictionaries, though not required.

Current sources available:
point,smeared,lp,lpsm,lpxyz,xyz

Adding sources requires addition here and in smearing.py.

Function arguments:
src_loc -- Integer list: the x,y,z,t coordinates of the source
so_val -- Integer: The 'source value,' ie. 
                   -for smeared sources, the number of smeared
                    sources
                   -for lp, number of emodes projected at 
                    the source
lapmodefile -- String list: List of locations of the eigenmodes
                   for the quarks. Each quark is one index.
                   Order is u,d,s,n,ns.
nd -- Integer: Related to the Laplacian projection. Number of 
                   dimensions.
lp_sm = [smearcode,presmear,lapsmear]
            -- List [str,bool,int]: Parameters related to Laplacian 
                   smearing. In order, smearing directions,
                   presmear (smear before or after projection),
                   number of laplacian smearing sweeps.
src_sm = [alpha_smsrc,useUzero,u0_smsrc]
            -- List [float,bool,float]: Parameters related to the 
                   smearing of the source. See /src/sourcetypes.f90
link_sm = [use_stout,alpha_fat,swps_fat]
            -- List [bool,float,int]: Parameters related to link
                   smearing. In order, whether to do stout
                   link smearing, the alpha value and the
                   number of sweeps. Boolean must be in form
                   of just 'T' or 'F'. Case insensitive.
"""


def point(src_loc, **kwargs):
    """
    Returns key information for a point source.

    Point source is no smearing.
    """

    source = {}
    source['sourcetype_num'] = 1
    source['u'] = src_loc
    source['d'] = source['u']
    source['s'] = source['u']
    source['n'] = source['u']
    source['ns'] = source['u']
    
    return source



def smeared(src_loc, so_val, src_sm, link_sm, **kwargs):
    """
    Returns key information for a normally smeared source.
    """

    source = {}
    source['sourcetype_num'] = 3
    source['u'] = src_loc + [ so_val ] + src_sm + link_sm
    source['d'] = source['u']
    source['s'] = source['u']
    source['n'] = source['u']
    source['ns'] = source['u']
    
    return source



def lp(lapmodefile, nd, so_val, src_loc, **kwargs):
    """
    Returns key information for Laplacian source.

    Laplacian source does no smearing. Instead projects only to
    the Laplacian operator.
    """

    source = {}
    source['sourcetype_num'] = 7
    source['u'] = [ lapmodefile[0],nd,so_val ] + src_loc
    source['d'] = [ lapmodefile[1],nd,so_val ] + src_loc
    source['s'] = [ lapmodefile[2],nd,so_val ] + src_loc
    source['n'] = [ lapmodefile[3],nd,so_val ] + src_loc
    source['ns'] = [ lapmodefile[4],nd,so_val ] + src_loc

    return source

def xyz(lp_sm, src_loc, so_val, src_sm, link_sm, **kwargs):
    """
    Returns key information for the xyz source

    Does no projection and smears only in the direction(s) 
    provided by smearcode in src_sm.
    """
    smearcode = lp_sm[0]     #unpacking
    source = {}
    source['sourcetype_num'] = 8
    source['u'] = [smearcode] + src_loc + [ so_val ] + src_sm + link_sm
    source['d'] = source['u']
    source['s'] = source['u']
    source['n'] = source['u']
    source['ns'] = source['u']

    return source



def lpsm(lapmodefile, nd, so_val, lp_sm, src_loc, src_sm, link_sm, **kwargs):
    """
    Returns key information for the Laplacian, smeared source.

    Does Laplacian projection and smears in all spatial directions (we think).
    Is passed smearcode through src_sm, but ignores it.
    """

    smearcode,presmear,lapsmear=lp_sm     #unpacking
    source = {}
    source['sourcetype_num'] = 9
    source['u'] = [ lapmodefile[0],nd,so_val,presmear ] + src_loc + [ lapsmear ] + src_sm + link_sm
    source['d'] = [ lapmodefile[1],nd,so_val,presmear ] + src_loc + [ lapsmear ] + src_sm + link_sm
    source['s'] = [ lapmodefile[2],nd,so_val,presmear ] + src_loc + [ lapsmear ] + src_sm + link_sm
    source['n'] = [ lapmodefile[3],nd,so_val,presmear ] + src_loc + [ lapsmear ] + src_sm + link_sm
    source['ns'] = [ lapmodefile[4],nd,so_val,presmear ] + src_loc + [ lapsmear ] + src_sm + link_sm
    
    return source




def lpxyz(lp_sm, lapmodefile, nd, so_val, src_loc, src_sm, link_sm, **kwargs):
    """
    Returns key information for the Laplacian, xyz source.

    Laplacian xyz source does Laplacian projection and smearing.
    Smears only in direction provided by smearcode, string in src_sm.
    """

    smearcode,presmear,lapsmear=lp_sm     #unpacking
    source = {}
    source['sourcetype_num'] = 10
    source['u'] = [ smearcode,lapmodefile[0],nd,so_val,presmear ] + src_loc + [ lapsmear ] + src_sm + link_sm
    source['d'] = [ smearcode,lapmodefile[1],nd,so_val,presmear ] + src_loc + [ lapsmear ] + src_sm + link_sm
    source['s'] = [ smearcode,lapmodefile[2],nd,so_val,presmear ] + src_loc + [ lapsmear ] + src_sm + link_sm
    source['n'] = [ smearcode,lapmodefile[3],nd,so_val,presmear ] + src_loc + [ lapsmear ] + src_sm + link_sm
    source['ns'] = [ smearcode,lapmodefile[4],nd,so_val,presmear ] + src_loc + [ lapsmear ] + src_sm + link_sm
    
    return source

