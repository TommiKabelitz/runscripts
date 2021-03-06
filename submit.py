"""
Parses input and calls the job submission code which sets up the jobs.
"""

# standard library modules
import argparse

# local modules
from colarunscripts.submit import main


def Input():
    """
    Parses input from the command line.

    Returns:
    inputDict -- dict: Dictionary of input given. testing key will have
                       value None or one of the choices given below.
                       submitmissing is False by default

    """

    # Setting up the parser
    parser = argparse.ArgumentParser(
        description="Submits jobs to the queue. Produces propagators and correlation functions."
    )

    parser.add_argument(
        "-p",
        "--parametersfile",
        help="The parameters file to use. Default is ./parameters.yml.",
        default="./parameters.yml",
    )
    parser.add_argument(
        "-c",
        "--firstconfig",
        help="The first config to submit. Default is 1.",
        default=1,
        type=int,
    )
    parser.add_argument(
        "-s",
        "--simjobs",
        help="Number of jobs to run simultaneously for each kappa value. Default is 1.",
        default=1,
        type=int,
    )
    parser.add_argument(
        "-n",
        "--nconfigurations",
        help="Number of total configurations to run. Default is all available",
        default=0,
        type=int,
    )
    parser.add_argument(
        "-t",
        "--testing",
        help='Run in testing mode. \n"headnode": Runs on head node (no GPUs (probably)) calling binaries. \n"dryrun": Runs on head node but skips calls to binaries. \n"testqueue:" Runs in the express queue (probably no GPUs). \n"interactive": Submits an interactive job to the full queue. \n"interactivetestqueue": Submits an interactive job to the express queue',
        choices=[
            "headnode",
            "dryrun",
            "testqueue",
            "interactive",
            "interactivetestqueue",
        ],
    )

    # Parsing the arguments from the command line
    args = parser.parse_args()
    # Turning the namespace into a dictionary
    inputDict = vars(args)
    return inputDict


if __name__ == "__main__":

    inputArgs = Input()

    inputArgs["skipDeleteCheck"] = False

    firstConfig = int(inputArgs["firstconfig"])
    simJobs = int(inputArgs["simjobs"])

    if inputArgs["nconfigurations"] != 0:
        inputArgs["nconfigurations"] = inputArgs["nconfigurations"] + (firstConfig - 1)

    # Looping through jobs to run simultaneously
    for ithJob in range(simJobs):
        nthConfig = ithJob + firstConfig
        main(nthConfig, inputArgs)
