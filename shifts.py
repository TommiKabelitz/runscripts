import re


def formatShift(entry):
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

    entrytype = type(entry)
    if entrytype is str:
        shift = entry
    elif entrytype is dict:
        shift = entry['shift']
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

    if entrytype is str:
        return output
    else:
        entry['shift'] = output
        return None


def formatKappa(entry):
    
    entrytype = type(entry)
    if entrytype is int:
        return '0.'+str(kappa)
    elif entrytype is dict:
        kappa = entry['kappa']
        entry['kappa'] = '0.'+str(kappa)
        return None
    else:
        raise TypeError

    
