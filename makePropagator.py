import copy
import pathlib
import pprint
import subprocess
from datetime import datetime

import configIDs as cfg
import directories as dirs
import parameters as params
import shifts
#import smearing as sm
import sources as src
from utilities import PrintDictToFile

#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 

cfgFormat = 'ildg' 
#cfgFormat = 'U=1'   #Uncomment for free field (for testing)
                     #Should otherwise be commented out

propFormat = 'prop'  #file extension without .
parallelIO = 'F'
tolerance = '1.0d-5'
fermionAction = 'clover'
U1FieldType = 'B'
U1FieldQuanta = 'k'

Ns = 32
Nt = 64
c_sw = 1.715
#c_sw = 1.0    #Uncomment for free field (for testing)
               #Should otherwise be commented out

kappa_strange = 13665

executable = '/home/a1724542/PhD/cola/trunk/cuda/quarkpropGPU.x'
#executable = '/home/a1724542/PhD/cola/trunk/bin/noisegen.x'

def FieldCode(U1FieldType,U1FieldQuanta,kd,**kwargs):
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



def MakeLatticeInputFile(filename):
        '''
        Make the .lat input file for qpropGPU.x.

        Note: Ns,Nt are global variables. Located at the top of the file.
        Arguments:
        filename -- string: The filename to write lattice details to.
        '''

        lattice = [Ns,Ns,Ns,Nt]
        with open(filename,'w') as f:
                f.write('\n'.join(str(dim) for dim in lattice))
                f.write('\n')



def MakeCloverInputFile(filename):
        '''
        Make the .fm_clover input file for qpropGPU.x.

        Note: c_sw, the clover coefficient is a global variable. Located at
              the top of this file.
        Arguments:
        filename -- string: The filename to write lattice details to.
        '''

        #       #[bcx,bcy,bcz,bct, u0,c_sw]
        values = [1.0,1.0,1.0,0.0,1.0,c_sw]
        with open(filename,'w') as f:
                f.write('\n'.join(str(val) for val in values))
                f.write('\n')



def MakeSourceInputFile(filename,quark,sourceType,kappa,kd,cfgID,*args,**kwargs):
        
        parameters = params.params()['sourcesink']

        #Getting the eigenmode file. Only used for some sources.
        #kwargs should provide kappa,kd,cfgID
        lapmodefile = dirs.LapModeFiles(kappa=kappa,kd=kd,cfgID=cfgID,quark=quark)[quark]

        #merging dictionaries
        smearing_values = {**parameters,'lapmodefile':lapmodefile}  

        #Calling functions in sources.py
        FormatFunction = getattr(src,sourceType)
        formatted_values = FormatFunction(**smearing_values)

        #Extracting sourcetype_num
        sourcetype_num = formatted_values.pop('sourcetype_num')


        #Writing lists to file
        with open(filename,'w') as f:
                #Convert to string and write to newline, elements of values
                f.write('\n'.join(str(line) for line in formatted_values['values']))
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




def CallMPI(inputFileBase,reportFile,numGPUs,**kwargs):

        print(f'Time is {datetime.now()}')
        print('mpi-running "' + ' '.join([executable,'--solver="CGNE+S"','--itermax=1000000']) + '"')
        print(f'On {numGPUs} GPUs')
        print(f'The input filestub is "{inputFileBase}"')


        runDetails = subprocess.run(['mpirun','-np',str(numGPUs),executable,'--solver=CGNE+S','--itermax=1000000'],input=inputFileBase+'\n',text=True,capture_output=True)
        with open(reportFile,'w') as f:
               f.write(runDetails.stdout)
               if runDetails.stderr is not None:
                       f.write(runDetails.stderr)
        print(f'Report file is: {reportFile}')
        print(f'Time is {datetime.now()}')


def MakePropagator(quark,values,directories,filename,src_extension,qprop_extension):

        #Copying values dictionary. Deepcopy so that we can change items for
        #this quark only.
        quarkValues = copy.deepcopy(values)

        #Adding prop filename to quarkValue dictionary
        quarkValues['quarkPrefix'] = directories['prop'].replace('QUARK',quark)

        ##Constructing Input file paths files
        #Filestub to pass to quarkpropgpu.x
        inputFileBase = directories['propInput'] + filename.replace('QUARK',quark)
        #The actual input filenames
        lat_file = inputFileBase + '.lat'
        clover_file = inputFileBase + '.fm_clover'
        src_file = inputFileBase + src_extension
        qprop_file = inputFileBase + qprop_extension
        #Prop report file
        reportFile = directories['propReport'].replace('QUARK',quark)

        
        #Making input files - Source files need to be made before u and s
        #adjustments due to the lapmodefiles
        MakeLatticeInputFile(lat_file)
        MakeCloverInputFile(clover_file)

        quarkValues['sourcetype_num'] = MakeSourceInputFile(src_file,quark,**quarkValues)

                
        #Adjusting for u and s quarks
        if quark == 'u':
                quarkValues['kd']*=-2
        if quark == 's':
                quarkValues['kappa'] = kappa_strange

        #Propagator input file needs to be made after adjustments due to u and s
        MakePropInputFile(qprop_file,quarkValues)

        #Checking whether propagator exists before calling quarkpropGPU
        fullQuarkPath = f'{quarkValues["quarkPrefix"]}k{quarkValues["kappa"]}.{propFormat}'
        if pathlib.Path(fullQuarkPath).is_file():
                print(f'Skipping {quark} quark. Propagator already exists')
                return 


        print()
        print(f'Doing {quark} quark')

        CallMPI(inputFileBase,reportFile,**rp.SlurmParams())


def main(jobValues,*args,**kwargs):

        parameters = params.params()

        directories = dirs.FullDirectories(**jobValues,**parameters['sourcesink'])

        #prop input files
        filestub = 'prop' + jobValues['SLURM_ARRAY_JOB_ID'] + '_' + jobValues['SLURM_ARRAY_TASK_ID']+'.QUARK'
        src_extension = '.qpsrc_' + jobValues['sourceType']
        qprop_extension = '.quarkprop'

        
        jobValues['cfgFile'] = directories['cfgFile']


        for quark in ['u','d','s']: #Don't need neutral props, just use zero field d and s props
        
                MakePropagator(quark,jobValues,directories,filestub,src_extension,qprop_extension)

