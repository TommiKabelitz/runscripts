import argparse
from datetime import datetime

import configIDs as cfg
import makePropagator
import makeCfun
import parameters as params


def main():

    inputValues = Input()
    
    jobValues = {**inputValues,**params.params()['runValues']}
    jobValues['start'],jobValues['ncon'] = cfg.ConfigDetails(**jobValues)
    jobValues['nthCon'] = int(jobValues['SLURM_ARRAY_TASK_ID'])
    jobValues['cfgID'] = cfg.ConfigID(**jobValues) #must happen before kappa -> kappa_strange
        
    
    print()        
    print('Making propagators')
    print(f'Time is {datetime.now()}')
    makePropagator.main(jobValues)
    print("Propagators done")
    print(f'Time is {datetime.now()}')

    print()        
    print('Making correlationfunctions')
    print(f'Time is {datetime.now()}')    
    makeCfun.main(jobValues)
    print("Correlation functions done")
    print(f'Time is {datetime.now()}')
    print()

    

def Input():

        parser = argparse.ArgumentParser()

        parser.add_argument('kappa',type=int)
        parser.add_argument('kd',type=int)
        parser.add_argument('shift',type=str)
        parser.add_argument('SLURM_ARRAY_JOB_ID',type=str)
        parser.add_argument('SLURM_ARRAY_TASK_ID',type=str)
        
        args = parser.parse_args()
        values = vars(args)
        return values




if __name__ == '__main__':

    main()
