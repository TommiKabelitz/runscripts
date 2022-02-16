# Standard library modules
import os
import pprint
import re
import sys

"""
Some utility functions.

"""


def WriteListLengthnList(fileObject, listToWrite, label=None):
    """
    Writes the length of a list and then the contents to a file.

    Arguments:
    fileObject  -- fileObject: the file to write to
    listToWrite -- list: The list to write to the file
    label       -- str: Label for the variable in the file if desired.

    """

    length = len(listToWrite)
    if label is None:
        fileObject.write(f"{length}\n")
    else:  # Labling length if desired
        fileObject.write(f"{label:20}= {length}\n")
    # Writing list elements
    for element in listToWrite:
        fileObject.write(f"{element}\n")


def PrintDictToFile(filename, dictionary, order=None):
    """
    Prints the values of dictionary to a file, 1 value per line

    Warning: If order is not provided, the default order of the dictionary
             is used. This is the insertion order from python 3.7, before
             which that order cannot be guaranteed

    Arguments:
    filename   -- string: The file to print to
    dictionary -- dict: The dict to print
    order      -- list/tuple: List/tuple of keys in the order they should
                              be printed
    """

    # If order is unspecified, use default ordering
    if order is None:
        order = dictionary.keys()

    with open(filename, "w") as f:
        for key in order:
            f.write(str(dictionary[key]) + "\n")


def Parent(path, levels=1, *args, **kwargs):
    """
    Returns the nth level, parent directory.

    Arguments:
    path --  str: The base path
    level -- int: The level of parent directory, defaults to one level
    """
    for i in range(levels):
        path = os.path.dirname(path)

    return path


def GetEnvironmentVar(variable, *args, **kwargs):
    """
    Exchanges names of environmental variables with their value.

    Scans an inputted dictionary of values for strings beginning
    with a dollar sign (used to represent environmental variables.
    Then exchanges the variable for the value in the environment.

    Arguments:
    inputDict -- dict: Dictionary to be scanned
    """

    try:
        if "$" == variable[0]:
            # Removing dollar sign from variable name
            variableName = variable.replace("$", "")
            # Returning actual value
            value = os.environ[variableName]
            return value
    except KeyError:
        return "NONE"


def SchedulerParams(parameters, scheduler, *args, **kwargs):

    if scheduler == "slurm":
        return parameters["slurmParams"]
    elif scheduler == "PBS":
        return parameters["pbsParams"]


def GetJobID(environmentVariables):

    jobIDLabels = ["SLURM_ARRAY_JOB_ID", "SLURM_JOB_ID", "PBS_ARRAYID", "PBS_JOBID"]

    for label in jobIDLabels:
        try:
            jobID = environmentVariables[label]
            pattern = re.compile(r"\d+")
            return pattern.findall(jobID)[0]
        except KeyError:
            continue
    else:
        return "1"


def pp(toPrint, indent=4, stream=None):
    """
    Pretty printer, great for dictionaries.

    Arguments:
    toPrint -- object: Object to be printed.
    indent -- int: Distance to indent each new level.
    stream -- fileObject: Where to print to. Default is sys.stdout.
    """

    pprint.PrettyPrinter(indent=indent, stream=stream).pprint(toPrint)


def VariablePrinter(toPrint, fileObject=sys.stdout, nameWidth=10):
    """
    Prints an f-string formatted variable with desired name width.

    Arguments:
    toPrint    -- str: String to print. Must be in form variable=27.4
    fileObject -- openFile: The file to print to. Default prints to stdout.
    nameWidth  -- int: Field width to print variable name in.
    """

    # Splitting the string into variable and value. = sign is lost
    stringParts = toPrint.split("=", maxsplit=1)
    # Recombining string with formatting
    formatted = f"{stringParts[0]:{nameWidth}}= {stringParts[1]}"
    # Writing out the string
    fileObject.write(formatted)
