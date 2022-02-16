import argparse
import re

from colarunscripts import configIDs, particles
from colarunscripts.makeCfun import GetTarFile
from colarunscripts.manageJob import CfunsExist
from colarunscripts.parameters import Load


def FullCheck(inputArgs: dict, *args, **kwargs):

    parameters = Load(inputArgs["parametersfile"])
    jobValues = parameters["runValues"]
    for kappa in jobValues["kappaValues"]:
        jobValues["kappa"] = kappa

        start, ncon = configIDs.ConfigDetails(kappa, jobValues["runPrefix"])
        print(start, ncon)
        cfgIDs = [
            configIDs.ConfigID(i, jobValues["runPrefix"], start)
            for i in range(1, ncon + 1)
        ]
        print("Checking IDs")
        missingList = []
        for ID in cfgIDs:
            jobValues["cfgID"] = ID
            if CfunsExist(parameters, jobValues) is True:
                print(f"Correlation functions exist for {ID}")
            else:
                print(f"Correlations functions missing for {ID}")
                missingList.append(ID)

        with open(inputArgs["outputfile"], "w") as f:
            for i, ID in enumerate(cfgIDs):
                if ID in missingList:
                    f.write(f"{ID} {i+1}\n")

        print('output file is {inputArgs["outputfile"]}')


def QuickCheck(inputArgs: dict, *args, **kwargs):

    parameters = Load(inputArgs["parametersfile"])
    jobValues = parameters["runValues"]
    for kappa in jobValues["kappaValues"]:
        jobValues["kappa"] = kappa

        start, ncon = configIDs.ConfigDetails(kappa, jobValues["runPrefix"])
        jobValues["cfgID"] = configIDs.ConfigID(1, jobValues["runPrefix"], start)

        haveIDs = set(f'-{jobValues["runPrefix"]}-00{start+10*i}' for i in range(ncon))
        print("Checking IDs")
        for kd in jobValues["kds"]:
            for structure in jobValues["structureList"]:
                for sinkType in jobValues["sinkTypes"]:
                    tarPath, _ = GetTarFile(
                        parameters,
                        kd,
                        jobValues["shifts"][0],
                        sinkType,
                        jobValues,
                        structure,
                    )
                    for chi, chibar in jobValues["particleList"]:
                        if kd == 0:
                            fields = particles.CheckForVanishingFields(
                                kd, chi=chi, chibar=chibar
                            )
                            if len(fields) == 0:
                                continue

                        cfgFileList = (
                            tarPath.replace("CHICHIBAR", f"{chi}{chibar}") + "cfglist"
                        )
                        with open(cfgFileList, "r") as f:
                            cfgList = f.read().splitlines()
                        haveIDs = haveIDs.intersection(cfgList)
                        if len(set(cfgList)) < 200:
                            print(cfgFileList)

    fullList = [f'-{jobValues["runPrefix"]}-00{start+10*i}' for i in range(ncon)]
    allIDs = set(fullList)
    missingIDs = allIDs - haveIDs

    sortedIDs = sorted_nicely(list(missingIDs))
    with open(inputArgs["outputfile"], "w") as f:
        for i, ID in enumerate(fullList):
            if ID in sortedIDs:
                f.write(f"{ID} {i+1}\n")

    print(f"Number of missing configs is {len(missingIDs)}")
    print(f'output file is {inputArgs["outputfile"]}')


# From https://stackoverflow.com/questions/2669059/how-to-sort-alpha-numeric-set-in-python
def sorted_nicely(l):
    """Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(l, key=alphanum_key)


def Input():

    # Setting up the parser
    parser = argparse.ArgumentParser(
        description="Submits jobs to the queue. Produces propagators and correlation functions."
    )
    parser.add_argument(
        "-f",
        "--fullcheck",
        help="Whether to fully check for file existence or to just check id list",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--parametersfile",
        help="The parameters file to use. Default is ./parameters.yml.",
        default="./parameters.yml",
    )
    parser.add_argument(
        "-o",
        "--outputfile",
        help="The output file to write to. Default is ./missingCfuns.txt.",
        default="./missingCfuns.txt",
    )

    # Parsing the arguments from the command line
    args = parser.parse_args()
    # Turning the namespace into a dictionary
    inputDict = vars(args)
    return inputDict


if __name__ == "__main__":

    inputArgs = Input()
    if inputArgs["fullcheck"] is True:
        FullCheck(inputArgs)
    else:
        QuickCheck(inputArgs)
