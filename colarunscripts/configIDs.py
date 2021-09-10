"""
Module for getting configuration IDs and configuration details.

Contains two main functions.
  ConfigDetails -- Returns the starting configuration number and total
                    number of configurations based on the run prefix and 
                    kappa value.
  ConfigIDs     -- Returns the formatted configuration ID, eg -a-1880 
                    based on current (nth) configuration, starting config
                    and the run prefix

Numeric functions (One,Two,...) are helper functions for ConfigDetails.

NOTE: SOME START AND NCON VALUES DIFFER FROM THOSE ON THE PACS-CS SITE.
      THE VALUES HERE ARE MANUALLY GRABBED FROM THE CONFIGURATIONS PRESENT
      ON PHOENIX. - some may be missing on phoenix
"""

#Helper functions for ConfigDetails. Act like select case statement for 
#kappa value. 
#Template for adding new functions should be clear, pairing
#of kappa:function_handle does need to be added in the dictionary 'switch'
#in ConfigDetails.
#Function names are not more explicit because I couldn't think of anything
#better.

#13700
def One(kappa,runPrefix):
    if runPrefix == 'b':
        start = 2510
        ncon = 399
        return start, ncon
    else:
        raise ValueError("Invalid (kappa,prefix) combination. Terminating")

#13727
def Two(kappa,runPrefix):
    if runPrefix == 'b':
        start = 1310
        ncon = 397
        return start, ncon
    else:
        raise ValueError("Invalid (kappa,prefix) combination. Terminating")

#13754
def Three(kappa,runPrefix):
    if runPrefix == 'a':
        start = 2510
        ncon = 200
        return start, ncon
    elif runPrefix == 'b':
        start = 2510
        ncon = 249
        return start, ncon
    else:
        raise ValueError("Invalid (kappa,prefix) combination. Terminating")

#13770
def Four(kappa,runPrefix):
    if runPrefix == 'a':
        start = 1880
        ncon = 400
        return start, ncon
    elif runPrefix == 'b':
        start = 1780
        ncon = 399
        return start, ncon
    else:
        raise ValueError("Invalid (kappa,prefix) combination. Terminating")

#13781
def Five(kappa,runPrefix):
        if runPrefix == 'gM':
            start = 1200
            ncon = 44
            return start, ncon
        elif runPrefix == 'hM':
            start = 1240
            ncon = 22
            return start, ncon
        elif runPrefix == 'iM':
            start = 870
            ncon = 44 
            return start, ncon
        elif runPrefix == 'jM':
            start = 260
            ncon = 44
            return start, ncon
        elif runPrefix == 'kM':
            start = 1090
            ncon = 43
            return start, ncon
        else:
            raise ValueError("Invalid (kappa,prefix) combination. Terminating")


#12400
def Six(kappa,runPrefix):
    """
    This is for free field testing, the start point and number of configurations are arbitrary
    """
    start = 1000
    ncon = 5
    return start,ncon




def ConfigDetails(kappa,runPrefix,*args,**kwargs):
    """
    Returns the starting configuration number and total number of configurations

    Function arguments:
    kappa     -- int: The kappa value, relating to the light quark mass 
                      of the configuration
    runPrefix -- char: The runPrefix or series name within the
                      configuration set.

    Returns:
    start -- int: The first configuration number. Eg 1880
    ncon  -- int: The total number of configurations
    """
    switch = {
        13700:One,
        13727:Two,
        13754:Three,
        13770:Four,
        13781:Five,
        12400:Six
    }
    case = switch[kappa]
    start, ncon = case(kappa,runPrefix)
    
    return start,ncon

def ConfigID(nthConfig,runPrefix,start,*args,**kwargs):
    """
    Returns a formatted configuration ID, eg -a-1880
    
    Function arguments:
    nthConfig -- int: The current configuration. Eg the 1st or 10th
                      configuration to be used.
    start     -- int: The first configuration number. Eg 1880
    runPrefix -- char: The runPrefix or series name within the
                       configuration set.
    
    Returns:
    configID -- str: Formatted ID suffix, ie -a-001880.
    """
    #Different series types (runPrefix) have different gaps between 
    #configuration numbers.
    if runPrefix in ['a','b']:
        gap = 10
    elif runPrefix in ['gM','hM','iM','jM','kM']:
        gap = 20
    else:
        raise ValueError('Invalid run prefix')
    
    ID = start + (nthConfig-1)*gap
    return f'-{runPrefix}-00{ID}'
