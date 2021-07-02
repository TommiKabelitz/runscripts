#Standard library modules
import os

import colarunscripts.parameters as params

'''
Some utility functions.

'''

def WriteListLengthnList(fileObject,listToWrite):
    '''
    Writes the length of a list and then the contents to a file.

    Arguments:
    fileObject  -- fileObject: the file to write to
    listToWrite -- list: The list to write to the file
    '''

    length = len(listToWrite)
    fileObject.write(f'{length}\n')
    for element in listToWrite:
        fileObject.write(f'{element}\n')


def PrintDictToFile(filename,dictionary,order=None):
        '''
        Prints the values of dictionary to a file, 1 value per line
        
        Warning: If order is not provided, the default order of the dictionary
                 is used. This is the insertion order from python 3.7, before
                 which that order cannot be guaranteed

        Arguments:
        filename   -- string: The file to print to
        dictionary -- dict: The dict to print
        order      -- list/tuple: List/tuple of keys in the order they should 
                                  be printed
        '''

        #If order is unspecified, use default ordering
        if order is None:
                order = dictionary.keys()

        with open(filename,'w') as f:
                for key in order:
                        f.write(str(dictionary[key])+'\n')



def Parent(path,levels=1,*args,**kwargs):
    '''
    Returns the nth level, parent directory.

    Arguments:
    path --  str: The base path
    level -- int: The level of parent directory, defaults to one level
    '''
    for i in range(levels):
        path = os.path.dirname(path)

    return path



def GetEnvironmentVar(variable,*args,**kwargs):
    '''
    Exchanges names of environmental variables with their value.

    Scans an inputted dictionary of values for strings beginning
    with a dollar sign (used to represent environmental variables. 
    Then exchanges the variable for the value in the environment.
    
    Arguments:
    inputDict -- dict: Dictionary to be scanned
    '''
    
    try:
        if '$' == variable[0]:
            #Removing dollar sign from variable name
            variableName = variable.replace('$','')
            #Returning actual value
            value = os.environ[variableName]
            return value
    except KeyError:
        return ''


def SchedulerParams(scheduler,*args,**kwargs):

    parameters = params.Load()
    if scheduler == 'slurm':
        return parameters['slurmParams']
    elif scheduler == 'PBS':
        return parameters['pbsParams']
