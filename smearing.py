"""
Returns dictionaries containing values pertaining to smearing.

Defines a function, smearing_vals, which returns a dictionary 
of values based on type of smearing (source,link,sink). With
the supplementation of information such as lapmodefile (if
required), the dictionary can be passed to the functions in 
sources.py to be prepared for final output to the COLA input
files.

Global variables here are the ones which will be passed. If
you want to change them for all sinks/sources then change them
here. Otherwise, specify them in the pertinent if statement.
Consider the global values as 'default values.'
"""
from sys import exit

##Global variables
source_location = [1,1,1,16]

#Smeared source related parameters
alpha_smsrc = 0.7
useUzero = 'f'
u0_smsrc = 1.0
src_smearing = [alpha_smsrc,useUzero,u0_smsrc] #src_sm
#Laplacian projection related parameters
numdim = 2   #nd
source_value = 16  #so_val
presmear = 't'
lapsmear = 100
#Link smearing related parameters - Stout link smearing
use_stout = 't'
alpha_fat = 0.1
swps_fat = 10

#Sink smearing related parameters
sink_smearcode = 'xyz'
sink_value = 100

def SmearingVals(smear_type,**kwargs):
    """
    Returns appropriate smearing values in a dictionary

    Arguments:
    smear_type -- string: options are source_smearing
                                      link_smearing
                                      sink_smearing
    Kwargs:
    The source_type or sink_type must be passed as a key
    word argument with the smear_type for the code to run
    """

    #Local function definition
    #one for each type of smearing
    def SourceSmearing(source_type,**kwargs):
        """
        Returns dictionary of values related to source smearing.

        Works by declaring the variables we want as the proper
        value, deleting the extrenuous variables, then returning
        all that is defined through locals().
        See sources.py for details on all variables.
        Arguments:
        source_type -- string: the type of source
        """


        if 'source_type' not in locals():#Checking source_type was passed
            raise TypeError("SourceSmearing() missing 1 required positional argument: 'source_type'")

        #Setting all of the relevant variables to the 
        #desired value. By default from the global 
        #variable defined above.
        elif source_type == 'pt':
            src_loc = source_location            
        elif source_type == 'sm':
            src_loc = source_location   
            so_val = source_value
            src_sm = src_smearing
        elif source_type == 'lp':
            src_loc = source_location
            nd = numdim
            so_val = source_value
        elif source_type == 'xyz':
            lp_sm = ['xy'] 
            src_loc = source_location
            so_val = source_value
            src_sm = src_smearing
        elif source_type == 'lpsm':
            nd = numdim
            so_val = source_value
            lp_sm = ['',presmear,lapsmear]
            src_loc = source_location
            src_sm = src_smearing
        elif source_type == 'lpxyz':
            lp_sm = ['z',presmear,lapsmear]
            nd = numdim
            so_val = source_value
            src_loc = source_location
            src_sm = src_smearing
        else:
            raise ValueError("SourceSmearing() received an unexpected 'source_type'")

        #Deleting the local variables we do not wish to
        #return.
        del kwargs, source_type
        return locals()
                 


    def LinkSmearing(**kwargs):
        """
        Returns dictionary of values related to link smearing.

        Works in the same manner as SourceSmearing, but requires
        no input as we only use stout link smearing presently.
        
        Arguments:
        Nothing need be passed. **kwargs required in definition
        as the function will be passed an empty dictionary.
        """
        
        link_sm = [use_stout,alpha_fat,swps_fat]

        del kwargs
        return locals()



    def SinkSmearing(sink_type,**kwargs):
        """
        Returns dictionary of values related to sink smearing.

        Works in the same manner as source_smearing and sink_smearing.
        
        Arguments:
        sink_type -- string: The type of sink
        """


        if 'sink_type' not in locals():#checking sink_type was passed
            raise TypeError("SinkSmearing() missing 1 required positional argument: 'source_type'")
        
        #Setting all of the relevant variables to the 
        #desired value. By default from the global 
        #variable defined above.

        if sink_type == 'sm':
            smearcode = sink_smearcode
            sink_smear = 't'
            sink_val = sink_value
        elif sink_type == 'lp':
            sink_smear = 'f'
        else:
            raise ValueError("SinkSmearing() received an unexpected 'sink_type'")

        #Deleting the local variables we do not wish to
        #return.        
        del kwargs,sink_type
        return locals()




    #Grabbing the appropriate function (source/link/sink)
    #to use based on the variable smear_type which was passed
    #from the locals() dictionary
    Function = locals()[smear_type]

    #The kwargs dictionary here contains the key-word
    #arguments passed to smearing_vals. Should contain
    #the sink or source type variable required by the
    #relevant function.
    return Function(**kwargs)
