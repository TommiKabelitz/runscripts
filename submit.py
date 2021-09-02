import argparse

from colarunscripts.submit import main


def Input():
    '''
    Parses input from the command line.

    Returns:
    inputDict -- dict: Dictionary of input given. testing key will have
                       value None or one of the choices given below.
                       submitmissing is False by default

    '''

    #Setting up the parser
    parser = argparse.ArgumentParser(description='Submits jobs to the queue. Produces propagators and correlation functions.')

    parser.add_argument('-p','--parametersfile',help='The parameters file to use. Default is ./parameters.yml.',default='./parameters.yml')
    parser.add_argument('-c','--firstconfig',help='The first config to submit. Default is 1.',default=1,type=int)
    parser.add_argument('-s','--simjobs',help='Number of jobs to run simultaneously for each kappa value. Default is 1.',default=1,type=int)
    parser.add_argument('-n','--nconfigurations',help='Number of total configurations to run. Default is all available',default=0,type=int)
    parser.add_argument('-t','--testing',help='Run in testing mode. Runs on head node (no GPUs). Else submits only 1 configuration to either the test queue (no GPUs) or the full queue.',choices=['headnode','testqueue','fullqueue','interactive','interactivetestqueue'])
    parser.add_argument('-m','--submitmissing',help='Checks for missing correlation functions, then submits only those configurations. (BROKEN)',action='store_true')

    #Parsing the arguments from the command line
    args = parser.parse_args()
    #Turning the namespace into a dictionary
    inputDict = vars(args)
    return inputDict



if __name__ == '__main__':

    inputArgs = Input()
    
    firstconfig = inputArgs['firstconfig']
    simJobs = inputArgs['simjobs']

    for nthConfig in range(int(firstconfig),int(firstconfig)+int(simJobs)):
        main(nthConfig,inputArgs)

