import re


def getShiftDetails(shift):
    """
    Returns the x and t shift from a string of form x24t36.

    Arguments:
    shift -- string: Examples of possible input. x00t00, 
                     x16t8, x0t36. Will have a problem if
                     either the t or x shift is missing. 
                     Number of digits does not matter, 1,
                     2, or 3 are all fine.

    Requires regex module.
    """
    #Pattern to grab the numbers from the string
    pattern = re.compile(r'\d+')

    #Extracting all numbers according to the pattern
    xshift,tshift = pattern.findall(shift)
    
    #Extraction returns string, ints preferable
    xshift = int(xshift)
    tshift = int(tshift)
    
    return xshift,tshift
