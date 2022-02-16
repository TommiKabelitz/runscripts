"""
Functions to make the files required by quarkprop.

All functions require the input filestub and the relevant
parameters which they print to file.

"""
from colarunscripts import directories as dirs
from colarunscripts import parameters as params
from colarunscripts import shifts
from colarunscripts import sources as src
from colarunscripts.utilities import VariablePrinter


def MakeLatticeFile(filestub, logFile, extent):
    """
    Make the .lat input file for cfungenGPU.x.

    Arguments:
    filestub -- string: The filename, without the .lat extension
                         to write lattice details to.
    extent -- int list: number of lattice points in each
                         direction. Order is [nx,ny,nz,nt].
    """
    extension = ".lat"

    # Writing to the file
    with open(filestub + extension, "w") as f:
        f.write("\n".join(str(dim) for dim in extent))
        f.write("\n")

    # Writing to the log file
    with open(logFile, "a") as f:
        f.write(f"\n{extension=}\n")
        f.write(
            "\n".join(
                f"{dim:20}= {val}" for dim, val in zip(["x", "y", "z", "t"], extent)
            )
        )
        f.write("\n")


def MakeCloverFile(filestub, logFile, bcx, bcy, bcz, bct, u0, C_SW, *args, **kwargs):
    """
    Make the .fm_clover input file for qpropGPU.x.

    Arguments:
    filename -- string: The filename to write lattice details to.
    """
    extension = ".fm_clover"

    # Writing to file
    with open(filestub + extension, "w") as f:
        f.write(f"{bcx}\n")
        f.write(f"{bcy}\n")
        f.write(f"{bcz}\n")
        f.write(f"{bct}\n")
        f.write(f"{u0}\n")
        f.write(f"{C_SW}\n")

    # Writing to log file
    with open(logFile, "a") as f:
        f.write(f"\n{extension=}\n")
        VariablePrinter(f"{bcx=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{bcy=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{bcz=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{bct=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{u0=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{C_SW=}\n", fileObject=f, nameWidth=20)


def MakeSourceFile(
    parameters, filestub, logFile, kd, shift, quarkValues, *args, **kwargs
):

    sourceVals = parameters["sourcesink"]

    # Getting the eigenmode file. Only used for some sources.
    lapmodefile = dirs.LapModeFiles(
        parameters, kd=kd, shift=shift, quark=None, **quarkValues
    )
    sourceVals["lapmodefile"] = lapmodefile["quark"]

    # Writing the actual source file using the appropriate function
    # in sources.py. sourcetype_num is required for .qprop input file
    FileWriter = getattr(src, quarkValues["sourceType"])
    sourcetype_num = FileWriter(filestub, logFile, **sourceVals)

    return sourcetype_num


def MakePropFile(
    filestub,
    logFile,
    quarkLabel,
    configFile,
    configFormat,
    quarkPrefix,
    propFormat,
    parallelIO,
    fermionAction,
    kappa,
    strangeKappa,
    shift,
    U1FieldType,
    U1FieldQuanta,
    kd,
    tolerance,
    sourcetype_num,
    *args,
    **kwargs,
):
    """ """
    extension = ".quarkprop"

    if quarkLabel == "h":
        kappa = strangeKappa
    kappa = shifts.FormatKappa(kappa)
    shift = shifts.FormatShift(shift, fullShift="full")
    U1FieldCode = FieldCode(U1FieldType, U1FieldQuanta, kd)

    # Writing to file
    with open(filestub + extension, "w") as f:
        f.write(f"{configFile}\n")
        f.write(f"{configFormat}\n")
        f.write(f"{quarkPrefix}\n")
        f.write(f"{propFormat}\n")
        f.write(f"{parallelIO}\n")
        f.write(f"{fermionAction}\n")
        f.write(f"{kappa}\n")
        f.write(f"{shift}\n")
        f.write(f"{U1FieldCode}\n")
        f.write(f"{tolerance}\n")
        f.write(f"{sourcetype_num}\n")

    # Writing to log file
    with open(logFile, "a") as f:
        f.write(f"\n{extension=}\n")
        VariablePrinter(f"{configFile=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{configFormat=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{quarkPrefix=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{propFormat=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{parallelIO=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{fermionAction=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{kappa=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{shift=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{U1FieldCode=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{tolerance=}\n", fileObject=f, nameWidth=20)
        VariablePrinter(f"{sourcetype_num=}\n", fileObject=f, nameWidth=20)


def FieldCode(U1FieldType, U1FieldQuanta, kd, *args, **kwargs):
    """
    Returns the formatted field code for the quarkprop input file

    Arguments:
    U1FieldType -- String: The type of field here, ie B
    U1FieldQuanta -- String: The label used in the quantisation condition
                             ie. k
    kd -- int: The field strength

    Should at some stage be impoved so that it can deal with more flexible
    input.
    """
    return "[" + U1FieldType + ":" + U1FieldQuanta + "=" + str(kd) + "]"
