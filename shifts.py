import re


def FormatShift(shift,*args,**kwargs):
    '''
    Returns the x and t shift from a string of form x24t36.

    Arguments:
    shift -- string: Examples of possible input. x00t00, 
                     x16t8, x0t36. Will have a problem if
                     either the t or x shift is missing. 
                     Number of digits does not matter, 1,
                     2, or 3 are all fine.
                     Shift may also be a dictionary 
                     containing a shift with the key "shift"
    Example Output: 24 24 24 36
    Requires regex module.
    '''

    #Pattern to grab the numbers from the string
    pattern = re.compile(r'\d+')

    #extracting shift from input
    inputType = type(shifts)
    if inputType is str:
        shift = shifts
    elif inputType is dict:
        shift = shifts['shift']
    else:
        raise TypeError('FormatShift expects input of type str or dict')

    #Extracting all numbers according to the pattern
    xshift,tshift = pattern.findall(shift)

    #Casting to int to remove leading zeros
    #i.e 00->0,01->1
    xshift = int(xshift)
    tshift = int(tshift)
    
    #Formatting as 'x y z t'
    output = 3*(str(xshift)+' ')+str(tshift)

    #returning output
    if inputType is str:
        return output
    else:
        shifts['shift'] = output
        return None


def FormatKappa(kappa,*args,**kwargs):
    '''
    Formats a kappa value into the form 0.kappa .

    Arguments:
    kappa -- int,str: kappa value
          -- dict:    dictionary containing kappa value
                      with key "kappa" - modifies in place
                      returns, None in this case.
    '''
    inputType = type(kappa)
    if inputType in [int, str]:
        return f'0.{kappa}'
    elif inputType is dict:
        value = kappa['kappa']
        kappa['kappa'] = f'0.{value}'
        return None
    else:
        raise TypeError
