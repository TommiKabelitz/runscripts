'''
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
'''

#Helper functions for ConfigDetails. Act like select case statement for 
#kappa value. 
#Template for adding new functions should be clear, pairing
#of kappa:function_handle does need to be added in the dictionary 'switch'
#in ConfigDetails.
#Function names are not more explicit because I couldn't think of anything
#better.
#13700
def One(kappa,run_prefix):
    if run_prefix == 'b':
        start = 2510
        ncon = 399
        return start, ncon
    else:
        raise ValueError("Invalid (kappa,prefix) combination. Terminating")

#13727
def Two(kappa,run_prefix):
    if run_prefix == 'b':
        start = 1310
        ncon = 397
        return start, ncon
    else:
        raise ValueError("Invalid (kappa,prefix) combination. Terminating")

#13754
def Three(kappa,run_prefix):
    if run_prefix == 'a':
        start = 2510
        ncon = 200
        return start, ncon
    elif run_prefix == 'b':
        start = 2510
        ncon = 249
        return start, ncon
    else:
        raise ValueError("Invalid (kappa,prefix) combination. Terminating")

#13770
def Four(kappa,run_prefix):
    if run_prefix == 'a':
        start = 1880
        ncon = 400
        return start, ncon
    elif run_prefix == 'b':
        start = 1780
        ncon = 399
        return start, ncon
    else:
        raise ValueError("Invalid (kappa,prefix) combination. Terminating")

#13781
def Five(kappa,run_prefix):
        if run_prefix == 'gM':
            start = 1200
            ncon = 44
            return start, ncon
        elif run_prefix == 'hM':
            start = 1240
            ncon = 22
            return start, ncon
        elif run_prefix == 'iM':
            start = 870
            ncon = 44 
            return start, ncon
        elif run_prefix == 'jM':
            start = 260
            ncon = 44
            return start, ncon
        elif run_prefix == 'kM':
            start = 1090
            ncon = 43
            return start, ncon
        else:
            raise ValueError("Invalid (kappa,prefix) combination. Terminating")

def ConfigDetails(kappa,run_prefix,*args,**kwargs):
    '''
    Returns the starting configuration number and total number of configurations

    Function arguments:
    kappa -- Integer:        The kappa value, relating to the light quark mass 
                             of the configuration
    run_prefix -- Character: The run_prefix or series name within the
                             configuration set.

    Returns:
    start -- Integer:        The first configuration number
    ncon -- Integer:         The total number of configurations
    '''
    switch = {
        13700:One,
        13727:Two,
        13754:Three,
        13770:Four,
        13781:Five
    }
    case = switch[kappa]
    start, ncon = case(kappa,run_prefix)
    
    return start,ncon

def ConfigID(nth_con,run_prefix,start,*args,**kwargs):
    '''
    Returns a formatted configuration ID, eg -a-1880
    
    Function arguments:
    nth_con -- Integer:      The current configuration. Eg the 1st or 10th
                             configuration to be used.
    start -- Integer:        The first configuration number. Eg 1880
    run_prefix -- Character: The run_prefix or series name within the
                             configuration set.
    
    Returns:
    Formatted ID suffix, ie -a-1880.
    '''
    #Different series types (run_prefix) have different gaps between 
    #configuration numbers.
    if run_prefix in ['a','b']:
        gap = 10
    elif run_prefix in ['gM','hM','iM','jM','kM']:
        gap = 20
    else:
        raise ValueError('Invalid run prefix')
    
    ID = start + (nth_con-1)*gap
    return f'-{run_prefix}-00{ID}'
