import os
import pprint

import shifts
import smearing as sm
import sources as src

pp = pprint.PrettyPrinter(indent=4).pprint

propFormat = 'prop' #file extension without .
parallelIO = 'F'
tolerance = '1.0d-5'
fermionAction = 'clover'
U1FieldType = 'B'
U1FieldQuanta = 'k'



def FieldCode(U1FieldType,U1FieldQuanta,kd,**kwargs):
        return '['+U1FieldType+':'+U1FieldQuanta+'='+str(kd)+']'



def print_dict_to_file(filename,dictionary,order):
    
    with open(filename,'w') as f:
        for key in order:
            f.write(str(dictionary[key])+'\n')


def make_source_input_file(filename,source_type,so_val=None,lapmodefile=None):

    src_vals = sm.smearing_vals(smear_type='source_smearing',source_type=source_type)
    link_vals = sm.smearing_vals(smear_type='link_smearing')

    smearing_values = {**src_vals,**link_vals}  #merging dictionaries

    #Adding in extras
    if so_val is not None:
        smearing_values['so_val'] = so_val
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


def make_propagators(quark,params):
        cfgfile = configuration_file(kappa,


#testing source_input_file
source_type = 'smeared'
lapmodefile = ['0','1','2','3','4']
so_val = 2
filename = os.getcwd()+'/Inputs/QUARK.qpsrc_'+source_type
sourcetype_num = make_source_input_file(filename,source_type,so_val,lapmodefile)


#testing prop_input_file
d = {}
d['cfgFile'] = 'I am the config file'
d['cfgFormat'] = 'ildg'
d['quarkPrefix'] = 'I am a quark name'
d['kappa'] = 13770
d['shift'] = 'x16t8'
d['kd'] = 2
d['sourcetype_num'] = sourcetype_num
make_prop_input_file(os.getcwd()+'/Inputs/prop.quarkprop',d)



    #cfgfile
    #dquarkprefix
    ##propfmt
    ##parallel io (t/f)
    ##clover
    #kappa
    #shift
    #U1fieldcode - Just needs k_d
    ##tolerance
    #sourcetype_num

    #So stuff to pass
    #cfgfile
    #quarkprefix (filename)
    #kappa
    #shift
    #k_d
    #sourcetype_num



#def make_propagator(source_type,so_val=None,lapmodefile=None):






#make_propagator('smeared',1,['1','2','3','4','5'])


#quarkprop
