import pathlib

def CreateDirectory(Input):

    def create(fullFilepath):
        index = fullFilepath.rfind('/')
        directory = fullFilepath[:index]
        
        path = pathlib.Path(directory)
        if path.exists() is False:
            path.mkdir(parents=True, exist_ok=True)
            print(f'Making directory {directory}')

    inputType = type(Input)
    if inputType is str:
        create(Input)
    elif inputType is list:
        for directory in Input:
            create(directory)
    elif inputType is dict:
        for key,directory in Input.values():
            create(directory)
    else:
        raise TypeError()



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
