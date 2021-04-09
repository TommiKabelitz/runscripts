import argparse
import copy
import pathlib
import pprint
import subprocess

import configIDs as cfg
import directories as dirs
import runparams as rp
import shifts
import smearing as sm
import sources as src




#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 

cfgFormat = 'ildg' 
cfgFormat = 'U=1'   #Uncomment for free field (for testing)
                    #Should otherwise be commented out

propFormat = 'prop' #file extension without .
parallelIO = 'F'
tolerance = '1.0d-5'
fermionAction = 'clover'
U1FieldType = 'B'
U1FieldQuanta = 'k'

Ns = 32
Nt = 64
c_sw = 1.715

kappa_strange = 13665

executable = '/home/a1724542/PhD/cola/trunk/cuda/quarkpropGPU.x'


def FieldCode(U1FieldType,U1FieldQuanta,kd,**kwargs):
        return '['+U1FieldType+':'+U1FieldQuanta+'='+str(kd)+']'



def PrintDictToFile(filename,dictionary,order):
    
    with open(filename,'w') as f:
        for key in order:
            f.write(str(dictionary[key])+'\n')
        f.write('\n')
def MakeLatticeInputFile(filename):
        
        lattice = [Ns,Ns,Ns,Nt]
        with open(filename,'w') as f:
                f.write('\n'.join(str(dim) for dim in lattice))
                f.write('\n')

def MakeCloverInputFile(filename):
        #[bcx,bcy,bcz,bct,u0,c_sw]
        values = [1.0,1.0,1.0,0.0,1.0,c_sw]
        with open(filename,'w') as f:
                f.write('\n'.join(str(val) for val in values))
                f.write('\n')

def MakeSourceInputFile(filename,source_type,lapmodefile=None,**kwargs):

    src_vals = sm.SmearingVals(smear_type='SourceSmearing',source_type=source_type)
    link_vals = sm.SmearingVals(smear_type='LinkSmearing')

    smearing_values = {**src_vals,**link_vals}  #merging dictionaries

    #Adding in extras
    if lapmodefile is not None:
        smearing_values['lapmodefile'] = lapmodefile

    #Calling functions in sources.py
    FormatFunction = getattr(src,source_type)
    formatted_values = FormatFunction(**smearing_values)

    #Extracting sourcetype_num
    sourcetype_num = formatted_values.pop('sourcetype_num')


    #Writing lists to file
    for quark,values in formatted_values.items():
        #Each set of values are in a list
        quarkfile = filename.replace('QUARK',quark)
        with open(quarkfile,'w') as f:
            #Convert to string and write to newline, elements of values
            f.write('\n'.join(str(line) for line in values))
            f.write('\n')

    return sourcetype_num




def MakePropInputFile(filename,prop_input_dict):

    order = ['cfgFile',
             'cfgFormat',
             'quarkPrefix',
             'propFormat',
             'parallelIO',
             'fermionAction',
             'kappa', 
             'shift', 
             'U1FieldCode',
             'tolerance',
             'sourcetype_num']

    #grabbing the variables we care about from the global scope
    globalvals = {key:globals()[key] for key in set(order).intersection(globals().keys())}
    into_file = {**prop_input_dict,**globalvals}

    into_file['U1FieldCode'] = FieldCode(U1FieldType,U1FieldQuanta,**prop_input_dict)
    shifts.FormatShift(into_file)
    shifts.FormatKappa(into_file)

    PrintDictToFile(filename,into_file,order)

#end function



def MakePropagator(inputFileBase,reportFile,numGPUs,**kwargs):
        
        print('mpi-running "' + ' '.join([executable,'--solver="CGNE+S"','--itermax=1000000']) + '"')
        print(f'On {numGPUs} GPUs')
        print(f'The input filestub is "{inputFileBase}"')
        print()

        runDetails = subprocess.run(['mpirun','-np',str(numGPUs),executable,'--solver=CGNE+S'+' --itermax=1000000'],text=True,input=inputFileBase+'\n',capture_output=True)

        with open(reportFile,'w') as f:
               f.write(runDetails.stdout)
               if runDetails.stderr is not None:
                       f.write(runDetails.stderr)
        print(f'Report file is: {reportFile}')



def Input():

        parser = argparse.ArgumentParser()

        parser.add_argument('kappa',type=int)
        parser.add_argument('kd',type=int)
        parser.add_argument('shift',type=str)
        parser.add_argument('run_prefix',type=str)
        parser.add_argument('start',type=int)
        parser.add_argument('ncon',type=int)
        parser.add_argument('source_type',type=str)
        parser.add_argument('sink_type',type=str)
        parser.add_argument('SLURM_ARRAY_JOB_ID',type=str)
        parser.add_argument('SLURM_ARRAY_TASK_ID',type=int)
        
        args = parser.parse_args()
        values = vars(args)
        return values
                
if __name__ == '__main__':

        values = Input()
        values['nth_con'] = values['SLURM_ARRAY_TASK_ID']

        #need soval,sinkval - going to hack a solution right now
        stuff = sm.SmearingVals('SourceSmearing',source_type=values['source_type'])
        stuff2 = sm.SmearingVals('SinkSmearing',sink_type=values['sink_type'])
        
        values['cfgID'] = cfg.ConfigID(**values) #must happen before kappa -> kappa_strange
        
        directories = dirs.FullDirectories(**values,**stuff,**stuff2)


        #prop input files
        filename = values['SLURM_ARRAY_JOB_ID'] + '_' + str(values['nth_con'])+'.QUARK'
        src_extension = '.qpsrc_' + values['source_type']
        src_file = directories['input'] + filename + src_extension
        qprop_extension = '.quarkprop'

        #Making .qpsrc file, return sourcetype_num also
        values['sourcetype_num'] = MakeSourceInputFile(src_file,**values)

        values['cfgFile'] = directories['cfgFile']

        
        for quark in ['u','d','s']: #Don't need neutral props, just use zero field d and s props

                values['quarkPrefix'] = directories['prop'].replace('QUARK',quark)
                if pathlib.Path(values['quarkPrefix']).is_file():
                        continue #skip existing props
                
                quarkValues = copy.deepcopy(values)
                
                if quark == 'u':
                        quarkValues['kd']*=-2

                if quark == 's':
                        quarkValues['kappa'] = kappa_strange

                inputFileBase = directories['input'] + filename.replace('QUARK',quark)
                reportFile = directories['report'].replace('QUARK',quark)
                lat_file = inputFileBase + '.lat'
                clover_file = inputFileBase + '.fm_clover'
                qprop_file = inputFileBase + qprop_extension
                
                MakeLatticeInputFile(lat_file)
                MakeCloverInputFile(clover_file)
                MakePropInputFile(qprop_file,quarkValues)

                print(f'Doing {quark} quark')
                
                MakePropagator(inputFileBase,reportFile,**rp.SlurmParams())
                exit()

