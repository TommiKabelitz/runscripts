"""
Module for managing of the parameters.yml input file.

The parameters can be simply loaded by calling Load from this module. Rather
than having to load with the yaml module every time.
Also takes care of making a copy of the parameters file for the specific job.

The parameters.yml file must be located one directory above this file
"""

# standard library modules
import os  # environmental vars
import pathlib
import subprocess  # for running commands

import yaml  # yaml importing

# local modules
from colarunscripts import directories as dirs
from colarunscripts.utilities import pp


def Load(parametersFile="", writeOut=False, *args, **kwargs):
    """
    Loads the parameters from parameters.yml.

    Arguments:
    parametersFile -- str: The parameters file to read
    writeOut       -- bool: Whether to write out the parameters dictionary
                           to the console when reading.
                           (for testing purposes)
    """

    # Opening and loading the yamml
    with open(parametersFile, "r") as f:
        parameters = yaml.safe_load(f)

    # Writing the details to the screen if specified
    if writeOut is True:
        pp(parameters)

    return parameters


def CopyParamsFile(oldFile, jobID, testing=None, *args, **kwargs):
    """
    Makes a copy of the parameters file to use for this specific job.

    Arguments:
    baseFile -- str: The base parameters.yml file to copy
    jobID    -- int: Job identification number for new filename

    """
    parameters = Load(parametersFile=oldFile)
    # File to make
    copyFile = (
        dirs.FullDirectories(parameters, directory="parameters")["parameters"]
        + f"{jobID}_parameters.yml"
    )

    if testing == "dryrun":
        ModifyExecutables(parameters)

    print(f"Making copy of parameters file at: {copyFile}")
    print()
    yaml.dump(parameters, open(copyFile, "w"))


def ModifyExecutables(parameters, *args, **kwargs):

    # Check we have actually been passed a dictionary
    if type(parameters) is not dict:
        raise TypeError("parameters must be of type dictionary")

    # Loop through the keys in dictionary looking for executables
    for key in parameters:
        # May have nested dictionaries, so recursively call function
        # in that case
        if type(parameters[key]) is dict:
            ModifyExecutables(parameters[key])

        # Otherwise, change the executable value if we find one
        elif "executable" in key.lower():
            parameters[key] = "dryRun"
