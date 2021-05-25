import directories as dirs
import parameters as params
import shifts
import sources as src

def MakeLatticeFile(filestub,extent,*args,**kwargs):
    '''
    Make the .lat input file for quarkpropGPU.x.
    
    Arguments:
    filestub -- string: The filename, without the .lat extension
                         to write lattice details to.
    extent -- int list: number of lattice point in each 
                         direction. Order is [nx,ny,nz,nt].
    '''
    extension = '.lat'

    with open(filestub+extension,'w') as f:
        for dim in extent:
            f.write(f'{dim}\n')



def MakeCloverFile(filestub,bcx,bcy,bcz,bct,u0,C_SW,*args,**kwargs):
        '''
        Make the .fm_clover input file for qpropGPU.x.

        Arguments:
        filename -- string: The filename to write lattice details to.
        '''
        extension = 'fm_clover'

        with open(filestub+extension,'w') as f:
                f.write(f'{bcx}\n')
                f.write(f'{bcy}\n')
                f.write(f'{bcz}\n')
                f.write(f'{bct}\n')
                f.write(f'{u0}\n')
                f.write(f'{C_SW}\n')



def MakeSourceFile(filestub,quark,quarkValues,*args,**kwargs):
        
        sourceVals = params.params()['sourcesink']

        #Getting the eigenmode file. Only used for some sources.
        lapmodefile = dirs.LapModeFiles(quark=quark,**quarkValues)[quark]
        sourceVals['lapmodefile'] = lapmodefile

        #Writing the actual source file using the appropriate function
        #in sources.py. sourcetype_num is required for .qprop input file
        FileWriter = getattr(src,quarkValues['sourceType'])
        sourcetype_num = FileWriter(filestub,**sourceVals)

        return sourcetype_num



def MakePropFile(filestub,configFile,configFormat,quarkPrefix,propFormat,parallelIO,fermionAction,kappa,shift,U1FieldType,U1FieldQuanta,kd,tolerance,sourcetype_num,*args,**kwargs):
    '''

    '''
    extension = '.quarkprop'

    shift = shifts.FormatShift(shift)
    kappa = shifts.FormatKappa(kappa)
    U1FieldCode = FieldCode(U1FieldType,U1FieldQuanta,kd)
    
    with open(filestub+extension,'w') as f:
        f.write(f'{configFile}\n')
        f.write(f'{configFormat}\n')
        f.write(f'{quarkPrefix}\n')
        f.write(f'{propFormat}\n')
        f.write(f'{parallelIO}\n')
        f.write(f'{fermionAction}\n')
        f.write(f'{kappa}\n')
        f.write(f'{shift}\n')
        f.write(f'{U1FieldCode}\n')
        f.write(f'{tolerance}\n')
        f.write(f'{sourcetype_num}\n')



def FieldCode(U1FieldType,U1FieldQuanta,kd,*args,**kwargs):
        '''
        Returns the formatted field code for the quarkprop input file

        Arguments:
        U1FieldType -- String: The type of field here, ie B
        U1FieldQuanta -- String: The label used in the quantisation condition
                                 ie. k
        kd -- int: The field strength
        
        Should at some stage be impoved so that it can deal with more flexible
        input.
        '''
        return '['+U1FieldType+':'+U1FieldQuanta+'='+str(kd)+']'
