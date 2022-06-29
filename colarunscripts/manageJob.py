# standard library modules
import argparse
import os
import pathlib
import re
import sys
import tarfile
from collections import UserDict
from datetime import datetime

from colarunscripts import configIDs as cfg
from colarunscripts import directories as dirs
from colarunscripts import makeCfun, makeEmodes, makePropagator
from colarunscripts import parameters as params
from colarunscripts import particles, simpleTime, submit
from colarunscripts.shifts import CompareShifts
from colarunscripts.utilities import GetJobID, pp


class Paths(UserDict):
    """
    Simple dict extension. Allows psuedo merging through + operator.

    Paths1 + Paths2 creates new entries for distinct keys and does
    Paths1[key] = Paths1[key] + Paths2[key] for common keys. A TypeError
    will be raised if the addition does not make sense.

    Parameters
    ----------
    paths: dict
        Dictionary of values with which to initialise the Paths object.
    """

    def __init__(self, paths: dict = None):
        # Initialialising the dictionary class
        super().__init__()

        if paths is not None:
            self.data = paths

    def __add__(self, paths):
        """
        Adds dictionary or Paths object to this instance.
        Common keys are added with the new object to the right (if
        that is important). Distinct keys either remain or are added
        as with instance[key] = value.

        Parameters
        ----------
        paths: dict or Paths
            The data to add.

        Returns
        ----------
        Resulting Paths object
        """

        for key, value in paths.items():
            try:
                self.data[key] += value
            except KeyError:
                self.data[key] = value
        return self

    def clear(self, key: str = None):
        """Empties dictionary. If key is specified, empties only that key."""
        if key is not None:
            self.data.pop(key)
        else:
            self.data = {}


def main(
    newParametersFile,
    kappa,
    nthConfig,
    numSimultaneousJobs,
    ncon,
    testing,
    *args,
    **kwargs,
):

    parameters = params.Load(parametersFile=newParametersFile)
    jobValues = parameters["runValues"]

    if ncon != 0:
        start, _ = cfg.ConfigDetails(kappa, jobValues["runPrefix"])
    else:
        start, ncon = cfg.ConfigDetails(kappa, jobValues["runPrefix"])

    jobValues["nthConfig"] = nthConfig
    jobValues["cfgID"] = cfg.ConfigID(nthConfig, jobValues["runPrefix"], start)
    jobValues["jobID"] = GetJobID(os.environ)
    jobValues["kappa"] = kappa

    print()
    PrintJobValues(jobValues)

    JobLoops(parameters, jobValues["shifts"], jobValues["kds"], jobValues)
    SubmitNext(
        parameters,
        jobValues,
        nthConfig,
        start,
        numSimultaneousJobs,
        testing,
        newParametersFile,
        ncon,
    )


def JobLoops(parameters, shifts, kds, jobValues, *args, **kwargs):
    """
    Loops over field strengths and shifts
    """
    timer = simpleTime.Timer("Overall")
    timer.initialiseCheckpoints()
    timer.initialiseTimer("Eigenmodes")
    timer.initialiseTimer("Light Propagators")
    timer.initialiseTimer("Heavy Propagators")
    timer.initialiseTimer("Correlation functions")

    # Do we actually need eigenmodes. Does not override makeEmodes = True
    # in parameters file (In case you want to make and not use eigenmodes
    # for some reason).
    if jobValues["sourceType"] == "lp" and jobValues["makeProps"]:
        jobValues["makeEmodes"] = True
    if "laplacian" in jobValues["sinkTypes"] and jobValues["makeCfuns"] is True:
        jobValues["makeEmodes"] = True

    inputSummaries = []
    paths = Paths()  # Stores the created files so they can be deleted

    # The funky zip just ensures we have the current and the next shift
    # easily accessible
    for shift, nextShift in zip(shifts, [*shifts[1:], None]):
        for kd in kds:

            if CfunsExist(parameters, jobValues, kd, shift) is True:
                print(
                    f"Correlation functions for {kd=}, {shift=} already exist, skipping."
                )
                continue
            newpaths = doJobSet(parameters, kd, shift, jobValues, timer)
            paths = paths + newpaths
            inputSummaries += list(jobValues["inputSummary"].values())

        removeProps = (
            jobValues["keepProps"] is False
            and jobValues["makeProps"] is True
            and "props" in paths.keys()
        )

        # Removing the propagators
        if removeProps:
            print("All field strengths done, new shift, deleting propagators")
            for prop in paths["props"]:
                print(f"Deleting {prop}")
                path = pathlib.Path(prop)
                path.unlink(missing_ok=True)
            paths.clear(key="props")
            print()

        removeEmodes = (
            # If we made eigenmodes
            jobValues["makeEmodes"]
            # and don't want to keep them
            is not jobValues["keepEmodes"]
            # and the next shift is such that we is False  # won't re-use them. Then delete
            is CompareShifts(shift, nextShift) is False
            and "eigenmodes" in paths.keys()
        )

        # Removing the eigenmodes
        if removeEmodes:
            print("Shifting in more than time, deleting eigenmodes")
            for eigenMode in paths["eigenmodes"]:
                print(f"Deleting {eigenMode}")
                path = pathlib.Path(eigenMode)
                path.unlink(missing_ok=True)
            paths.clear(key="eigenmodes")
            print()

        print("Input file summaries located at:")
        for report in inputSummaries:
            print(report)
        print()

        timer.writeFullReport(final=True)
        print()
        print(50 * "_")
        print()


def doJobSet(parameters, kd, shift, jobValues, timer, *args, **kwargs) -> Paths:
    """
    Runs eigenmode, propagator and cfun code for the one configuration.

    Loops through field strength and shifts inside through JobLoops function.

    Arguments:
    jobValues -- dict: Dictionary containing the job specific values such as
                           kd, shift, SLURM_ARRAY_TASK_ID, etc...
    timer     -- Timer: Timer object to manage timing of correlation function
                           calculation time.

    """

    print(50 * "_")
    print()

    # Creating a checkpoint as the configuration starts
    checkpointName = f"Set (kd,shift): ({kd},{shift})"
    timer.createCheckpoint(checkpointName)

    # That's it for preparation of job values. Now start making stuff

    jobValues["inputSummary"] = {}

    # Making eigenmodes
    if jobValues["makeEmodes"] is True:
        print(50 * "_")
        print()
        print("Making eigenmodes")
        print(f"Time is {datetime.now()}")
        jobValues["inputSummary"]["emode"] = PrepareInputReportFile(
            parameters, "emode", kd, shift, jobValues
        )
        eigenmodePaths = makeEmodes.main(parameters, kd, shift, jobValues, timer)
        print("\nEigenmodes done")
        print(f"Time is {datetime.now()}")
        print()
    else:
        eigenmodePaths = []

    # Making propagators
    if jobValues["makeProps"] is True:
        print(50 * "_")
        print()
        print("Making propagators")
        print(f"Time is {datetime.now()}")
        jobValues["inputSummary"]["prop"] = PrepareInputReportFile(
            parameters, "prop", kd, shift, jobValues
        )
        propPaths = makePropagator.main(parameters, kd, shift, jobValues, timer)
        print("\nPropagators done")
        print(f"Time is {datetime.now()}")
        print(50 * "_")
    else:
        propPaths = []

    # Making cfuns
    if jobValues["makeCfuns"] is True:
        print()
        print("Making correlation functions")
        print(f"Time is {datetime.now()}")
        jobValues["inputSummary"]["interp"] = PrepareInputReportFile(
            parameters, "interp", kd, shift, jobValues
        )
        jobValues["inputSummary"]["cfun"] = PrepareInputReportFile(
            parameters, "cfun", kd, shift, jobValues
        )
        makeCfun.main(parameters, kd, shift, jobValues, timer)
        print("Correlation functions done")
        print(f"Time is {datetime.now()}")
        print(50 * "_")
        print()

    # Writing out how much time has elapsed since the checkpoint.
    # No longer need the checkpoint, so remove it.
    timer.writeCheckpoint(removeCheckpoint=True)
    print()

    paths = Paths({"eigenmodes": eigenmodePaths, "props": propPaths})
    return paths


def PrepareInputReportFile(parameters, report, kd, shift, jobValues):

    pathArgs = {"kd": kd, "shift": shift, **jobValues, **parameters["sourcesink"]}
    if report in ["prop", "emode"]:
        pathArgs["sinkType"] = ""
    if report == "emode":
        pathArgs["sourceType"] = ""

    reportFile = dirs.FullDirectories(parameters, directory="inputReport", **pathArgs)[
        "inputReport"
    ]
    reportFile = reportFile.replace("TYPE", report)

    with open(reportFile, "w") as f:
        f.write(f"Summary of {report} input files.\n")
        if report == "prop" and "lp" in jobValues["sourceType"]:
            emodeReport = jobValues["inputSummary"].get("emode")
            f.write(f"\nEigenmode summary file is:\n{emodeReport}\n")
        elif report == "cfun":
            emodeReport = jobValues["inputSummary"].get("emode")
            propReport = jobValues["inputSummary"].get("prop")
            interpReport = jobValues["inputSummary"].get("interp")
            f.write(f"\nPropagator summary file is:\n{propReport}\n")
            f.write(f"\nInterpolator summary file is:\n{interpReport}\n")
            if "laplacian" in jobValues["sinkTypes"]:
                f.write(f"\nEigenmode summary file is:\n{emodeReport}\n")

        f.write("\nValues for this config, field strength and shift\n")
        PrintJobValues(jobValues, stream=f)
        f.write(50 * "_" + "\n")

    return reportFile


def PrintJobValues(jobValues, stream=sys.stdout):
    """
    Prints the values specific to the current job to the screen.

    Allows easy checking of run values in the job output file.

    Arguments:
    jobValues -- dict: Dictionary containing the variables to print out

    """

    # A list of the variables to print
    # (some variables in jobValues there are a waste of time)
    valuesToPrint = [
        "kappa",
        "runPrefix",
        "cfgID",
        "kds",
        "shifts",
        "sourceType",
        "sinkTypes",
        "structureList",
        "particleList",
    ]

    print("Job Values:", file=stream)
    # Printing the values
    for key in valuesToPrint:
        try:
            # Printing list across lines for readability
            if type(jobValues[key]) is list:
                print(f"{key}:", file=stream)
                pp(jobValues[key], stream=stream)
            else:
                print(f"{key}: {jobValues[key]}", file=stream)
        # just in case the key is not present (shouldn't happen)
        except KeyError:
            if stream == sys.stdout:
                print(key)


def SubmitNext(
    parameters,
    jobValues,
    nthConfig,
    start,
    numSimultaneousJobs,
    testing,
    oldParametersFile,
    ncon,
):

    print(f"Submitting next. {ncon=} {nthConfig=} {numSimultaneousJobs=}")

    while True:

        nthConfig = int(nthConfig) + int(numSimultaneousJobs)
        jobValues["cfgID"] = cfg.ConfigID(nthConfig, jobValues["runPrefix"], start)

        if nthConfig > ncon:
            print(f"No new configurations to submit")
            return

        if CfunsExist(parameters, jobValues) is False:
            break
        else:
            print(
                f'Correlation functions all exist for config ID: {jobValues["cfgID"]}. Skipping'
            )

    inputArgs = {}
    inputArgs["simjobs"] = numSimultaneousJobs
    inputArgs["parametersfile"] = oldParametersFile
    inputArgs["testing"] = testing
    inputArgs["nconfigurations"] = ncon
    inputArgs["skipDeleteCheck"] = True

    print(f"Submitting configuration {nthConfig}")
    submit.main(nthConfig, inputArgs)


def Input():

    parser = argparse.ArgumentParser()
    parser.add_argument("parametersDir", type=str)
    parser.add_argument("kappa", type=int)
    parser.add_argument("nthConfig", type=int)
    parser.add_argument("numSimultaneousJobs", type=int)
    parser.add_argument("ncon", type=int)
    parser.add_argument("testing")

    args = parser.parse_args()
    return vars(args)


def CfunsExist(parameters, jobValues, kd=None, shift=None, *args, **kwargs):
    """
    Checks whether all cfuns for a parameter set exist.

    Arguments:
    parameters -- dict: Dictionary of all parameters from yml
    jobValues  -- dict: Dictionary of parameters relevant to this job
    kd         -- int: field strength for current set (optional)(default: all)
    shift      -- string: Cshift for current set (optional)(default:all)

    """

    # Note: As soon as we find something is missing, we can return false as
    # all cfuns are made in one call. (Structure exempt, on todo list)

    # Recursively calling function for all shifts/kd if not specified
    if kd is None:
        for kd in jobValues["kds"]:
            if CfunsExist(parameters, jobValues, kd, shift) is False:
                return False
    if shift is None:
        for shift in jobValues["shifts"]:
            if CfunsExist(parameters, jobValues, kd, shift) is False:
                return False

    for sinkType in jobValues["sinkTypes"]:

        # Grabbing appropriate sink values
        if "laplacian" == sinkType:
            sinkVals = parameters["sourcesink"]["nModes_lpsnk"]
        elif "smeared" == sinkType:
            sinkVals = parameters["sourcesink"]["sweeps_smsnk"]

        # Looping through everything we need
        for sinkVal in sinkVals:
            cfunArgs = {"kd": kd, "shift": shift, "sinkVal": sinkVal, **jobValues}
            cfunArgs["sinkType"] = sinkType
            cfunFilename = dirs.GetCfunFile(parameters, **cfunArgs)

            tarArgs = {
                "kd": kd,
                "shift": shift,
                "sinkType": sinkType,
                "sinkVal": "",
                "jobValues": jobValues,
            }
            tarFilename, _ = makeCfun.GetTarFile(parameters, **tarArgs)

            for chi, chibar in jobValues["particleList"]:

                for structure in jobValues["structureList"]:
                    # Not a perfect check for isospin, but close enough
                    if (kd == 0) or (structure[1] == structure[0]):
                        fields = particles.CheckForVanishingFields(
                            isospin_sym=True, chi=chi, chibar=chibar
                        )
                        if len(fields) == 0:
                            continue

                    # Structure in jobValues['structureList'] is a list
                    formattedStructure = "".join(structure)
                    cfun = cfunFilename.replace(
                        "CHICHIBAR_STRUCTURE", f"{chi}{chibar}_{formattedStructure}"
                    )
                    tar = tarFilename.replace(
                        "CHICHIBAR_STRUCTURE", f"{chi}{chibar}_{formattedStructure}"
                    )

                    cfunParts = re.split(r"\/", cfun)
                    prunedCfun = cfunParts[-3] + "/" + cfunParts[-1]
                    try:
                        with tarfile.open(tar, "r") as t:
                            fileList = t.getnames()

                    except FileNotFoundError:
                        fileList = []

                    if (
                        pathlib.Path(cfun).is_file() is False
                        and prunedCfun not in fileList
                    ):
                        return False

        return True


if __name__ == "__main__":

    inputArgs = Input()
    jobID = GetJobID(os.environ)
    inputArgs[
        "newParametersFile"
    ] = f'{inputArgs["parametersDir"]}{jobID}_parameters.yml'
    print(f'Parameters file to use: {inputArgs["newParametersFile"]}')

    main(**inputArgs)
