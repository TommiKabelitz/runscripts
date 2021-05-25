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


def pt(filestub,sourceLocation, *args, **kwargs):
    '''
    
    '''
    sourcetype_num = 1
    extension = '.qpsrc_pt'

    with open(filestub+extension,'w') as f:
        for dim in sourceLocation:
            f.write(f'{dim}\n')
    
    return sourcetype_num




def sm(filestub,sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):
    '''

    '''
    sourcetype_num = 3
    extension = '.qpsrc_pt'

    with open(filestub+extension,'w') as f:
        for dim in sourceLocation:
            f.write(f'{dim}\n')
        f.write(f'{sweeps_smsrc}\n')
        f.write(f'{alpha_smsrc}\n')
        f.write(f'{useUzero_smsrc}\n')
        f.write(f'{u0_smsrc}\n')
        f.write(f'{useStout_lnk}\n')
        f.write(f'{alphaFat_lnk}\n')
        f.write(f'{swpsFat_lnk}\n')

    return sourcetype_num



def lp(filestub,lapmodefile, nDim_lpsrc, nModes_lpsrc, sourceLocation, *args, **kwargs):
    '''

    '''
    sourcetype_num = 7
    extension = 'qpsrc_lp'

    with open(filestub+extension,'w') as f:
        f.write(f'{lapmodefile}\n')
        f.write(f'{ndim_lpsrc}\n')
        f.write(f'{nModes_lpsrc}')
        for dim in sourceLocation:
            f.write(f'{dim}\n')

    return sourcetype_num



def xyz(filestub,sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):
    '''

    '''
    sourcetype_num = 8
    extension = 'qpsrc_xyz'

    smearcode = 'xy'
    with open(filestub+extension,'w') as f:
        f.write(f'{smearcode}\n')
        for dim in sourceLocation:
            f.write(f'{dim}\n')
        f.write(f'{sweeps_smsrc}\n')
        f.write(f'{alpha_smsrc}\n')
        f.write(f'{useUzero_smsrc}\n')
        f.write(f'{u0_smsrc}\n')
        f.write(f'{useStout_lnk}\n')
        f.write(f'{alphaFat_lnk}\n')
        f.write(f'{swpsFat_lnk}\n')

    return sourcetype_num



def lpsm(filestub,lapmodefile, nDim_lpsrc, nModes_lpsrc, preSmear_lpsmsrc, sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):
    '''
    
    '''
    sourcetype_num = 9
    extension = 'qpsrc_lpsm'

    with open(filestub+extension,'w') as f:
        f.write(f'{lapmodefile}\n')
        f.write(f'{ndim_lpsrc}\n')
        f.write(f'{nModes_lpsrc}')
        f.write(f'{preSmear_lpsmsrc}')
        for dim in sourceLocation:
            f.write(f'{dim}\n')
        f.write(f'{sweeps_smsrc}\n')
        f.write(f'{alpha_smsrc}\n')
        f.write(f'{useUzero_smsrc}\n')
        f.write(f'{u0_smsrc}\n')
        f.write(f'{useStout_lnk}\n')
        f.write(f'{alphaFat_lnk}\n')
        f.write(f'{swpsFat_lnk}\n')

    return sourcetype_num




def lpxyz(filestub,lapmodefile, nDim_lpsrc, nModes_lpsrc, preSmear_lpsmsrc, sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):
    '''
    
    '''
    sourcetype_num = 10
    extension = 'qpsrc_lpxyz'

    smearcode = 'z'
    with open(filestub+extension,'w') as f:
        f.write(f'{smearcode}\n')
        f.write(f'{lapmodefile}\n')
        f.write(f'{ndim_lpsrc}\n')
        f.write(f'{nModes_lpsrc}')
        f.write(f'{preSmear_lpsmsrc}')
        for dim in sourceLocation:
            f.write(f'{dim}\n')
        f.write(f'{sweeps_smsrc}\n')
        f.write(f'{alpha_smsrc}\n')
        f.write(f'{useUzero_smsrc}\n')
        f.write(f'{u0_smsrc}\n')
        f.write(f'{useStout_lnk}\n')
        f.write(f'{alphaFat_lnk}\n')
        f.write(f'{swpsFat_lnk}\n')

    return sourcetype_num
