import pathlib

def WriteListLengthnList(fileObject,listToWrite):
    length = len(listToWrite)
    fileObject.write(f'{length}\n')
    for element in listToWrite:
        fileObject.write(f'{element}\n')


def CreateDirectory(paths,*args,**kwargs):
    '''
    Given a path including the file, makes the parent directory.

    Arguments:
    paths -- string: the path to the file or directory to create.
                     Create multiple at once by passing a list or
                     dict of paths.
    '''
    def create(fullFilePath):
        '''
        Sub-function to actually create the directory
        '''
        directory = IsolateDirectory(fullFilePath)
        #Creating the directory if it does not exist
        path = pathlib.Path(directory)
        if path.exists() is False:
            print(f'Making directory {directory}')
            try:
                path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                print(f'Permission to create {directory} denied')


    #Dealing with input type
    inputType = type(paths)
    if inputType is str:
        create(paths)
    elif inputType is list:
        for directory in paths:
            create(directory)
    elif inputType is dict:
        for key,directory in paths.values():
            create(directory)
    else:
        raise TypeError()


def IsolateDirectory(fullFilePath,*args,**kwargs):
    '''
    Takes a file path and returns only the directory in which the file is located.
    '''
    #Find the last / in the path
    index = fullFilePath.rfind('/')
    #Slicing the string to isolate the directory
    return fullFilePath[:index]



def PrintDictToFile(filename,dictionary,order=None):
        '''
        Prints the values of dictionary to a file, 1 value per line
        
        Warning: If order is not provided, the default order of the dictionary
                 is used. This is the insertion order from python 3.7, before
                 which that order cannot be guaranteed
        Arguments:
        filename -- string: The file to print to
        dictionary -- dict: The dict to print
        order -- List/tuple: List/tuple of keys in the order they should be printed
        '''

        #If order is unspecified, use default ordering
        if order is None:
                order = dictionary.keys()

        with open(filename,'w') as f:
                for key in order:
                        f.write(str(dictionary[key])+'\n')

