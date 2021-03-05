"""
Module containing the different sources that can be used.

All functions return dictionary of lists. One list for each
quark. Labelled u,d,s,n,ns. Recommend input from expanded 
dictionaries, though not required.

Current sources available:
point_src,smeared_src,lp_src,lpsm_src,lpxyz_src,xyz_src

Function arguments:
src_loc -- Integer list: the x,y,z,t coordinates of the source
so_val -- Integer: The 'source value,' ie. 
                   -for xyz, the number of source smearings
                   -for lp, number of emodes projected at 
                    the source
                   -for ln, is sigma_z
lapmodefile -- String list: List of locations of the eigenmodes
                   for the quarks. Each quark is one index.
                   Order is u,d,s,n,ns.
lp_sm = [smearcode,presmear,lapsmear]
            -- List [str,bool,int]: Parameters related to Laplacian 
                   smearing. In order, smearing directions,
                   presmear (smear before or after projection),
                   number of laplacian smearing sweeps.
link_sm -- List [bool,float,int]: Parameters related to link
                   smearing. In order, whether to do stout
                   link smearing, the alpha value and the
                   number of sweeps. Boolean must be in form
                   of just 'T' or 'F'. Case insensitive.

Global variables:
Variables that are the same for all sources are assigned globally
here. There is no concern about naming clashes as python maintains
namespaces when importing modules in the background.
nd -- Integer: Related to the Laplacian projection. More detail
               required.
src_sm -- List [float,bool,float]: Parameters related to the 
               smearing of the source. In order, smearing coefficient,
               useUzero (t or f), u0_smsrc. See /src/sourcetypes.f90
"""

#Global variables
nd = 2
src_sm = [0.7,'f',1.0]


def point_src(src_loc=[1,1,1,16], **kwargs):
    """
    Returns key information for a point source.

    Point source is no smearing.
    """

    source = {}
    source['sourcetype_num'] = 1
    source['u'] = src_loc
    source['d'] = src_loc
    source['s'] = src_loc
    source['n'] = src_loc
    source['ns'] = src_loc
    
    return source



def smeared_src(src_loc=[1,1,1,16], so_val, link_sm, **kwargs):
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



def lp_src(lapmodefile, so_val, src_loc=[1,1,1,16], **kwargs):
    """
    Returns key information for Laplacian source.

    Laplacian source does no smearing. Instead projects to
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



def lpxyz_src(lp_sm, lapmodefile, so_val, src_loc=[1,1,1,16], link_sm, **kwargs):
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



def lpsm_src(lapmodefile, so_val, lp_sm, src_loc=[1,1,1,16], link_sm, **kwargs):
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



def xyz_src(lp_sm, src_loc=[1,1,1,16], so_val, link_sm, **kwargs):
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
