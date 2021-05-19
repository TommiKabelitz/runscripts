import os
import pprint
import yaml


def params(writeOut=False):

    #nice printing for dictionaries, replace print with pp
    pp = pprint.PrettyPrinter(indent=4).pprint 

    parametersFile = os.path.dirname(__file__) + '/parameters.yml'

    with open(parametersFile,'r') as f:
        parameters = yaml.safe_load(f)

    if writeOut is True:
        pp(parameters)

    return(parameters)
