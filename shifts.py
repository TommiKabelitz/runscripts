import re


def FormatShift(arg):
    """
    Returns the x and t shift from a string of form x24t36.

    Arguments:
    shift -- string: Examples of possible input. x00t00, 
                     x16t8, x0t36. Will have a problem if
                     either the t or x shift is missing. 
                     Number of digits does not matter, 1,
                     2, or 3 are all fine.
    
    Example Output: 24 24 24 36
    Requires regex module.
    """
    #Pattern to grab the numbers from the string
    pattern = re.compile(r'\d+')

    inputType = type(arg)
    if inputType is str:
        shift = arg
    elif inputType is dict:
        shift = arg['shift']
    else:
        raise TypeError

    #Extracting all numbers according to the pattern
    xshift,tshift = pattern.findall(shift)

    #Casting to int removes zeros from start of shift
    #i.e 00->0,01->1
    xshift = int(xshift)
    tshift = int(tshift)
    
    #Formatting as x y z t
    output = 3*(str(xshift)+' ')+str(tshift)

    if inputType is str:
        return output
    else:
        arg['shift'] = output
        return None


def FormatKappa(arg):
    
    inputType = type(arg)
    if inputType is int:
        return '0.'+str(kappa)
    elif inputType is dict:
        kappa = arg['kappa']
        arg['kappa'] = '0.'+str(kappa)
        return None
    else:
        raise TypeError

    
