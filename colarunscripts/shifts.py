'''
Module for parsing the field shift string into its components.

Also contains a function for formatting the kappa value.

'''

import re


def FormatShift(shift,*args,**kwargs):
    '''
    Returns the x and t shift from a string of form x08y16z24t32.

    Arguments:
    shift -- string: The shift to be formatted. Must be in order
                     x y z t. If a direction is left out, eg.
                     x08y24t32, the missing coordinate will be 
                     filled by the x value, or if x is missing.
    Example Output: 8 16 24 32
    Requires regex module.
    '''

    #Pattern to grab the letters and numbers from the string
    letters = re.compile('[xyzt]')
    numbers = re.compile(r'\d+')

    #Extracting numbers and letters
    #Place in dictionary of coordinate:shift amount
    shifts = dict(zip(letters.findall(shift),numbers.findall(shift)))

    #If all four directions are present, we can return 
    if len(shifts) == 4:
        #Casting to int to remove leading zeros
        #i.e 00->0,01->1
        return ' '.join([str(int(x)) for x in shifts.values()])

    #If we don't have all directions present, need to fill the gaps
    default = ['x','y','z','t']
    output = []
    for direction in default:
        #If direction present, use given value
        if direction in shifts.keys():
            output.append(shifts[direction])
        #If not present, use x value unless missing
        else:
            try:
                output.append(shifts['x'])
            except KeyError:
                output.append('0')
                
    #Casting again for leading zeros
    return ' '.join([str(int(x)) for x in output])



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
