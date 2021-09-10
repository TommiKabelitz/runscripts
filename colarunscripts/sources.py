'''
Module containing the different sources that can be used.

- Recommend input from expanded dictionaries, though not 
required.
- All sources have a sourcetype number which identifies them in
COLA. Hard coded into the functions.
- The functions return the sourcetype number in addition to making
the file.

Current sources available:
point(pt),smeared(sm),Laplacian(lp),lpsm,lpxyz,xyz

All function arguments:

filestub         -- str: Input filestub
sourceLocation   -- int list: x,y,z,t location of the source
lapmodefile      -- str: Path to Laplacian eigenmode file
nDim_lpsrc       -- int: Number of dimensions for Laplacian projection
nModes_lpsrc     -- int: Number of modes to truncate Laplacian operator at
preSmear_lpsmsrc -- char: Whether to smear Laplacian source first
sweeps_smsrc     -- int: Sweeps of source smearing
alpha_smsrc      -- float: Alpha value for source smearing
useUzero_smsrc   -- char: Whether to use U0 smeared source
u0_smsrc         -- float: u0 value for smeared source
useStout_lnk     -- char: Whether to do stout link smearing
alphaFat_lnk     -- float: Alpha value for link smearing
swpsFat_lnk      -- int: Number of link smearing sweeps

'''

from colarunscripts.utilities import VariablePrinter

def pt(filestub,logFile,sourceLocation, *args, **kwargs):

    sourcetype_num = 1
    extension = '.qpsrc_pt'

    #Writing to file
    with open(filestub+extension,'w') as f:
        for dim in sourceLocation:
            f.write(f'{dim}\n')
    
    #Writing to log file
    with open(logFile,'a') as f:
        f.write(f'{extension=}\n')
        for dim,loc in zip(sourceLocation,['x','y','z','t']):
            f.write(f'{loc:20}= {dim}\n')

    return sourcetype_num




def sm(filestub,logFile,sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):

    sourcetype_num = 3
    extension = '.qpsrc_sm'

    #Writing to file
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

    #Writing to log file
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        for dim,loc in zip(sourceLocation,['x','y','z','t']):
            f.write(f'{loc:20}= {dim}\n')
        VariablePrinter(f'{sweeps_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{alpha_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{useUzero_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{u0_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{useStout_lnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{alphaFat_lnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{swpsFat_lnk=}\n',fileObject=f,nameWidth=20)

    return sourcetype_num



def lp(filestub,logFile,lapmodefile, nDim_lpsrc, nModes_lpsrc, sourceLocation, *args, **kwargs):

    sourcetype_num = 7
    extension = '.qpsrc_lp'

    #Writing to file
    with open(filestub+extension,'w') as f:
        f.write(f'{lapmodefile}\n')
        f.write(f'{nDim_lpsrc}\n')
        f.write(f'{nModes_lpsrc}')
        for dim in sourceLocation:
            f.write(f'{dim}\n')

    #Writing to log file
    with open(logFile,'a') as f:
        VariablePrinter(f'\n{extension=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{lapmodefile=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{nDim_lpsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{nModes_lpsrc=}',fileObject=f,nameWidth=20)
        for dim,loc in zip(sourceLocation,['x','y','z','t']):
            f.write(f'{loc:20}= {dim}\n')

            
    return sourcetype_num



def xyz(filestub,logFile,sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):

    sourcetype_num = 8
    extension = '.qpsrc_xyz'

    smearcode = 'xy'
    #Writing to file
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

    #Writing to log file
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        VariablePrinter(f'{smearcode=}\n',fileObject=f,nameWidth=20)
        for dim,loc in zip(sourceLocation,['x','y','z','t']):
            f.write(f'{loc:20}= {dim}\n')
        VariablePrinter(f'{sweeps_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{alpha_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{useUzero_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{u0_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{useStout_lnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{alphaFat_lnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{swpsFat_lnk=}\n',fileObject=f,nameWidth=20)

    return sourcetype_num



def lpsm(filestub,logFile,lapmodefile, nDim_lpsrc, nModes_lpsrc, preSmear_lpsmsrc, sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):

    sourcetype_num = 9
    extension = '.qpsrc_lpsm'

    #Writing to file
    with open(filestub+extension,'w') as f:
        f.write(f'{lapmodefile}\n')
        f.write(f'{nDim_lpsrc}\n')
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

    #Writing to log file
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        VariablePrinter(f'{lapmodefile=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{nDim_lpsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{nModes_lpsrc=}',fileObject=f,nameWidth=20)
        VariablePrinter(f'{preSmear_lpsmsrc=}',fileObject=f,nameWidth=20)
        for dim,loc in zip(sourceLocation,['x','y','z','t']):
            f.write(f'{loc:20}= {dim}\n')
        VariablePrinter(f'{sweeps_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{alpha_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{useUzero_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{u0_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{useStout_lnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{alphaFat_lnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{swpsFat_lnk=}\n',fileObject=f,nameWidth=20)

    return sourcetype_num




def lpxyz(filestub,logFile,lapmodefile, nDim_lpsrc, nModes_lpsrc, preSmear_lpsmsrc, sourceLocation, sweeps_smsrc, alpha_smsrc, useUzero_smsrc, u0_smsrc, useStout_lnk, alphaFat_lnk, swpsFat_lnk, *args, **kwargs):

    sourcetype_num = 10
    extension = '.qpsrc_lpxyz'

    smearcode = 'z'
    #Writing to file
    with open(filestub+extension,'w') as f:
        f.write(f'{smearcode}\n')
        f.write(f'{lapmodefile}\n')
        f.write(f'{nDim_lpsrc}\n')
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

    #Writing to log file
    with open(logFile,'a') as f:
        f.write(f'\n{extension=}\n')
        VariablePrinter('{smearcode=}\n',fileObject=f,nameWidth=20)
        VariablePrinter('{lapmodefile=}\n',fileObject=f,nameWidth=20)
        VariablePrinter('{nDim_lpsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter('{nModes_lpsrc=}',fileObject=f,nameWidth=20)
        VariablePrinter(f'{preSmear_lpsmsrc=}',fileObject=f,nameWidth=20)
        for dim,loc in zip(sourceLocation,['x','y','z','t']):
            f.write(f'{loc:20}= {dim}\n')
        VariablePrinter(f'{sweeps_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{alpha_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{useUzero_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{u0_smsrc=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{useStout_lnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{alphaFat_lnk=}\n',fileObject=f,nameWidth=20)
        VariablePrinter(f'{swpsFat_lnk=}\n',fileObject=f,nameWidth=20)

    return sourcetype_num
