import argparse
import copy
import pathlib
import pprint
import subprocess

import configIDs as cfg
import directories as dir
import runparams as rp
import shifts
import smearing as sm
import sources as src




#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 

cfgFormat = 'ildg' #set to 'U=1' for free field
propFormat = 'prop' #file extension without .
parallelIO = 'F'
tolerance = '1.0d-5'
fermionAction = 'clover'
U1FieldType = 'B'
U1FieldQuanta = 'k'

kappa_strange = 13665

executable = '/home/a1724542/PhD/cola/trunk/cuda/quarkpropGPU.x'
=======

>>>>>>> 309ac3eb5ff744cf3977a91b8e0caaf828388de8


def FieldCode(U1FieldType,U1FieldQuanta,kd,**kwargs):
        return '['+U1FieldType+':'+U1FieldQuanta+'='+str(kd)+']'



def print_dict_to_file(filename,dictionary,order):
    
    with open(filename,'w') as f:
        for key in order:
            f.write(str(dictionary[key])+'\n')



def make_source_input_file(filename,source_type,lapmodefile=None,**kwargs):

    src_vals = sm.smearing_vals(smear_type='source_smearing',source_type=source_type)
    link_vals = sm.smearing_vals(smear_type='link_smearing')

    smearing_values = {**src_vals,**link_vals}  #merging dictionaries

    #Adding in extras
    if lapmodefile is not None:
        smearing_values['lapmodefile'] = lapmodefile

    #Calling functions in sources.py
    format_function = getattr(src,source_type)
    formatted_values = format_function(**smearing_values)

    #Extracting sourcetype_num
    sourcetype_num = formatted_values.pop('sourcetype_num')


    #Writing lists to file
    for quark,values in formatted_values.items():
        #Each set of values are in a list
        quarkfile = filename.replace('QUARK',quark)
        with open(quarkfile,'w') as f:
            #Convert to string and write to newline, elements of values
            f.write('\n'.join(str(line) for line in values))

    return sourcetype_num




def make_prop_input_file(filename,prop_input_dict):


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
    shifts.formatShift(into_file)
    shifts.formatKappa(into_file)

    print_dict_to_file(filename,into_file,order)

#end function



def make_propagator(inputFileBase,reportFile,numGPUs,**kwargs):
        
        #output = subprocess.call(['mpirun','-np',numGPUs,executable,'--solver="CGNE+S"','--itermax=1000000',inputFileBase],stdout=subprocess.PIPE)

        print(' '.join(['mpirun','-np',str(numGPUs),executable,'--solver="CGNE+S"','--itermax=1000000',inputFileBase]))
        
        #convOutput = output.stdout.decode('utf-8')
        #with open(reportFile,'w') as f:
        #        f.write(convOutput)




        

        
        
def input():

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

        values = input()
        values['nth_con'] = values['SLURM_ARRAY_TASK_ID']

        #need soval,sinkval - going to hack a solution right now
        stuff = sm.smearing_vals('source_smearing',source_type=values['source_type'])
        stuff2 = sm.smearing_vals('sink_smearing',sink_type=values['sink_type'])
        
        values['cfgID'] = cfg.configID(**values)
        
        directories = dir.FullDirectories(**values,**stuff,**stuff2)


        #prop input files
        filename = values['SLURM_ARRAY_JOB_ID'] + '_' + str(values['nth_con'])+'.QUARK'
        src_extension = '.qpsrc_' + values['source_type']
        src_file = directories['input'] + filename + src_extension
        qprop_extension = '.qprop'

        #Making .qpsrc file, return sourcetype_num also
        values['sourcetype_num'] = make_source_input_file(src_file,**values)


        values['cfgFile'] = directories['cfgFile']



        
        for quark in ['u','d','s']: #Don't need neutral props, just use zero field d and s props

                values['quarkPrefix'] = directories['prop'].replace('QUARK',quark)
                if pathlib.Path(values['quarkPrefix']).is_file():
                        continue #skip existing props
                
                quarkValues = copy.deepcopy(values)
                
                if quark == 'u':
                        quarkValues['kd']*=-2

                if 's' in quark:
                        quarkValues['kappa'] = kappa_strange

                inputFileBase = directories['input'] + filename.replace('QUARK',quark)
                reportFile = directories['report'].replace('QUARK',quark)
                src_file =  inputFileBase + src_extension
                qprop_file = inputFileBase + qprop_extension
                make_prop_input_file(qprop_file,quarkValues)

                print(quark)
                print(src_file)
                print()
                subprocess.call(['cat',src_file])
                print()
                print(qprop_file)
                subprocess.call(['cat',qprop_file])
                print()


                make_propagator(inputFileBase,reportFile,**rp.slurm_params())


