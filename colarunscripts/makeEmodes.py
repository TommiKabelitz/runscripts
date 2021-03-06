"""
Module for making Laplacian Eigenmodes by calling lap2modesGPU.x.

'main()' function is called by manageJob.py which passes the job specific
details to this function.

This script is not intended to be called from the command line.

"""

# standard library modules
import pathlib  # for checking existence of files
import subprocess  # for calling lap2dmodes.x
from datetime import datetime  # for writing out the time

from colarunscripts import directories as dirs
from colarunscripts import shifts
from colarunscripts.makePropagator import CallMPI
from colarunscripts.particles import QuarkCharge
from colarunscripts.propFiles import FieldCode, MakeLatticeFile
from colarunscripts.utilities import SchedulerParams, VariablePrinter


def main(parameters, kd, shift, jobValues, timer):

    inputs = {}
    inputs["configFile"] = dirs.FullDirectories(
        parameters, kd=kd, directory="configFile", **jobValues
    )["configFile"]
    inputs["configFormat"] = parameters["directories"]["configFormat"]
    inputs["outputFormat"] = parameters["directories"]["lapModeFormat"]
    inputs["shift"] = shifts.FormatShift(shift, fullShift="emode")

    schedulerParams = SchedulerParams(parameters, jobValues["scheduler"])

    logFile = jobValues["inputSummary"]["emode"]

    fullFileList = []
    for structure in parameters["runValues"]["structureList"]:
        modeFiles = dirs.LapModeFiles(
            parameters,
            kd=kd,
            shift=shift,
            quark=structure,
            **jobValues,
            withExtension=False,
        )

        print()
        print(f"Making eigenmodes for structure set: {structure}")
        with open(logFile, "a") as f:
            f.write(f"\n\n\n{structure=}")

        for quark in structure:

            with open(logFile, "a") as f:
                f.write(f"\n{quark=}\n")

            # Full name of the eigenmode file (including file extension)
            fullFile = (
                modeFiles[quark] + "." + parameters["directories"]["lapModeFormat"]
            )
            print()
            print(5 * "-" + f"Doing {quark} quark" + 5 * "-")
            print(f"Eigenmode to make is: {fullFile}")

            # Checking for eigenmode existence
            if pathlib.Path(fullFile).is_file():
                print("Skipping eigenmode file. File already exists")
                fullFileList.append(fullFile)

                with open(logFile, "a") as f:
                    f.write(
                        f"\nSkipping {quark=}.\n{fullFile}\n File already exists.\n\n"
                    )
                continue

            # Constructing the input filestub
            filestub = (
                dirs.FullDirectories(parameters, directory="lapmodeInput")[
                    "lapmodeInput"
                ]
                + jobValues["jobID"]
                + "_"
                + str(jobValues["nthConfig"])
                + f".{quark}"
            )

            # Adding required quantities to the inputs dictionary
            inputs["U1FieldCode"] = FieldCode(
                kd=kd * QuarkCharge(quark), **parameters["propcfun"], **jobValues
            )
            inputs["outputPrefix"] = modeFiles[quark]

            # Making the input files
            MakeLatticeFile(filestub, logFile, **parameters["lattice"])
            MakeLap2ModesFile(
                filestub, logFile, **inputs, **parameters["laplacianEigenmodes"]
            )

            # In parameters file, scheduler params are lowercase, eg. pbsParams
            scheduler = jobValues["scheduler"].lower()
            numGPUs = parameters[scheduler + "Params"]["NUMGPUS"]
            numCPUs = numGPUs
            if numCPUs < parameters[scheduler + "Params"]["NUMGPUS"]:
                print(
                    f"WARNING: {numCPUs=}, {numGPUs=}, BUT lap2dmodes generally requires equal numbers of CPUs and GPUs. This may cause issues."
                )

            timeout = parameters["laplacianEigenmodes"]["timeout"]

            # For the output from the binaries
            reportFile = dirs.FullDirectories(
                parameters, directory="lapmodeReport", kd=kd, shift=shift, **jobValues
            )["lapmodeReport"].replace("QUARK", quark)

            timerLabel = "Eigenmodes"
            # Calling the mpi
            CallMPI(
                parameters["laplacianEigenmodes"]["lapmodeExecutable"],
                reportFile,
                jobValues["runFunction"],
                filestub=filestub,
                numGPUs=numGPUs,
                numCPUs=numCPUs,
                timeout=timeout,
                timerLabel=timerLabel,
                timer=timer,
            )

            # Compiling the list of files created
            fullFileList.append(fullFile)

    return fullFileList


def MakeLap2ModesFile(
    filestub,
    logFile,
    configFile,
    configFormat,
    outputPrefix,
    outputFormat,
    alpha_smearing,
    smearing_sweeps,
    shift,
    U1FieldCode,
    numEvectors,
    numAuxEvectors,
    tolerance,
    doRandomInitial,
    inputModeFile,
    *args,
    **kwargs,
):

    extension = ".lap2dmodes"
    # Writing to file
    with open(filestub + extension, "w") as f:
        f.write(f"{configFile}\n")
        f.write(f"{configFormat}\n")
        f.write(f"{outputPrefix}\n")
        f.write(f"{outputFormat}\n")
        f.write(f"{alpha_smearing}\n")
        f.write(f"{smearing_sweeps}\n")
        f.write(f"{shift}\n")
        f.write(f"{U1FieldCode}\n")
        f.write(f"{numEvectors}\n")
        f.write(f"{numAuxEvectors}\n")
        f.write(f"{tolerance}\n")
        f.write(f"{doRandomInitial}\n")
        f.write(f"{inputModeFile}\n")

    # Writing to log file. Variable printer allows aligning of all values
    with open(logFile, "a") as f:
        f.write(f"\n{extension=}\n")
        VariablePrinter(f"{configFile=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{configFormat=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{outputPrefix=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{outputFormat=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{alpha_smearing=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{smearing_sweeps=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{shift=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{U1FieldCode=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{numEvectors=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{numAuxEvectors=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{tolerance=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{doRandomInitial=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{inputModeFile=}\n", fileObject=f, nameWidth=20)
