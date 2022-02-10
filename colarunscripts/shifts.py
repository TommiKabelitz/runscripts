'''
Module for parsing the field shift string into its components.

Also contains a function for formatting the kappa value.

'''

import re


def FormatShift(shift,form='input',fullShift='full'):
    """
    Formats a specified c-shift into the specified format.

    Arguments:
    shift     -- str: The raw shift to format. Should be of the
                      form xN1yN2zN3tN4 where xyzt are the directions
                      and N1,...,N4 the amount shift in each direction.
                      Missing directions will be assumed to be zero.
    form      -- str: What the shift should be formatted for. Options
                      are 'input' and 'label'. 'input' formats ready to
                      pass to COLA. 'label' formats for in filenames.
    fullShift -- str: Allows the specification of the type of input file
                      the shift is being formatted for as some directions
                      are trivial in these cases. 'emode' for the 
                      .lap2dmodes file and and 'lpsnk' for the laplacian 
                      sink file.
    """
    
    directions = 'xyzt'
    #Pattern to grab the letters and numbers from the string
    letters = re.compile(f'[{directions}]')
    numbers = re.compile(r'\d+')

    #Extracting numbers and letters that are present
    #Place in dictionary of coordinate:shift amount
    present = dict(zip(letters.findall(shift),numbers.findall(shift)))

    #Substituting zero for anything missing
    missing = {key:'0' for key in directions if key not in present.keys()}
    shifts = {**present,**missing}

    #Where eigenmodes are concerned, we don't pass full shift as otherwise
    #end up double shifting gauge fields
    if fullShift == 'emode':
        shifts['t'] = '0'
    elif fullShift == 'lpsink':
        shifts['x'] = '0'
        shifts['y'] = '0'
        shifts['z'] = '0'
    elif fullShift != 'full':
        raise ValueError('fullShift must be "full", "emode", or "lpsink"')
    
    if form == 'input': # ie '0 24 8 6'
        #casting to int to remove trailing zeros
        cleaned = [str(int(shifts[key])) for key in directions]
        return ' '.join(cleaned)
    elif form == 'label': # ie y24z8t6
        nonTrivial = [direction+shifts[direction] for direction in shifts if int(shifts[direction]) != 0]
        if nonTrivial != []:
            return ''.join(nonTrivial)
        else:
            return 'None'
    else:
        raise ValueError('form must be "input" or "label"')


    
def CompareShifts(shift1,shift2,*args,**kwargs):
    """
    Returns True if two shifts only differ in time shift

    Arguments:
    shift1,shift2 -- str: The shifts formatted as defined in 
                          FormatShift.
    """

    #Making sure both are proper shifts
    if None in [shift1,shift2]:
        return False

    shift1 = FormatShift(shift1,form='input').split()
    shift2 = FormatShift(shift2,form='input').split()

    if shift1[0:2] == shift2[0:2]:
        return True
    else:
        return False

    
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
