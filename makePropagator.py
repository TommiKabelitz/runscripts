import copy
import pathlib
import pprint
import subprocess
from datetime import datetime

import configIDs as cfg
import directories as dirs
import parameters as params
import propFiles as files
import shifts
import sources as src
from utilities import PrintDictToFile

#nice printing for dictionaries, replace print with pp
pp = pprint.PrettyPrinter(indent=4).pprint 


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



def MakePropagator(quark,jobValues,filestub,parameters,*args,**kwargs):

        #Copying values dictionary. Deepcopy so that we can change items for
        #this quark only.
        quarkValues = copy.deepcopy(jobValues)

        if quark == 'n':
                quarkLabel = 'd'
                quarkValues['kd'] = 0
        elif quark == 'ns':
                quarkLabel = 's'
                quarkValues['kd'] = 0
        elif quark == 'u' and quarkValues['kd'] == 0:
                quarkLabel = 'd'
                print('At zero field strength, u and d quarks are the same. So just use the d quark.')
        else:
                quarkLabel = quark


        directories = dirs.FullDirectories(**quarkValues,**parameters['sourcesink'])

        #Adding prop filename to quarkValue dictionary
        quarkValues['quarkPrefix'] = directories['prop'].replace('QUARK',quarkLabel)

        ##Constructing Input file paths files
        #Filestub to pass to quarkpropgpu.x
        filestub = directories['propInput'] + filestub.replace('QUARK',quarkLabel)
        
        #Prop report file
        reportFile = directories['propReport'].replace('QUARK',quarkLabel)

        
        #Making input files - Source files need to be made before u and s
        #adjustments due to the lapmodefiles
        files.MakeLatticeFile(filestub,**parameters['lattice'])
        files.MakeCloverFile(filestub,**parameters['propcfun']['clover'])

        #Quark is for the Laplacian Eigenmode file, so needs to be the actual quark
        #not just the label.
        quarkValues['sourcetype_num'] = files.MakeSourceFile(filestub,quark,quarkValues)
                

        #Adjusting for u and s quarks
        if quark == 'u':
                quarkValues['kd']*=-2
        elif quark in ['s','ns']:
                quarkValues['kappa'] = parameters['propcfun']['strangeKappa']

        #Propagator input file needs to be made after adjustments due to u and s
        files.MakePropFile(filestub,**quarkValues,**parameters['directories'],**parameters['propcfun'])

        print()
        print(f'Doing {quark} quark')
        #Checking whether propagator exists before calling quarkpropGPU
        fullQuarkPath = f'{quarkValues["quarkPrefix"]}k{quarkValues["kappa"]}.{parameters["directories"]["propFormat"]}'
        print(f'Quark to make is: \n{fullQuarkPath}')

        if pathlib.Path(fullQuarkPath).is_file():
                print(f'Skipping {quark} quark. Propagator already exists')
                return 

        CallMPI(inputFileBase,reportFile,**parameters['slurmParams'])


def main(jobValues,*args,**kwargs):

        parameters = params.params()

        #File stub for propagator input files. QUARK to be autoreplaced
        filestub = 'prop' + jobValues['SLURM_ARRAY_JOB_ID'] + '_' + jobValues['SLURM_ARRAY_TASK_ID']+'.QUARK'

        #Compiling the full configuration file
        jobValues['configFile'] = dirs.FullDirectories(directory='configFile',**jobValues)['configFile']

        #Looping over structures and quarks in structures
        for structure in parameters['runValues']['structureList']: 
                
                print()
                print(f'Making propagators for structure set: {structure}')

                for quark in structure:

                        MakePropagator(quark,jobValues,filestub,parameters)

