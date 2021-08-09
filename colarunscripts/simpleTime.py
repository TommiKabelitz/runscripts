from time import perf_counter
from datetime import timedelta
class Timer:
    """

    """

    #Time is calculated using finish - start. Hence when timers start
    #they are set to -start
    def __init__(self,timerName):
        """Initialise class variables"""

        self.timerName = timerName                        #Overall timer name
        self.totalTime = -1*perf_counter()                #
        self.timerDict = {self.timerName:[self.totalTime,True]}  #Dictionary of timers
            

    def initialiseTimer(self,timerName):
        """Initialise, but don't start the timer called 'timeName'."""
        #Add entry to dictionary of timers, timerName is label for timer.
        #List is [amount of time,isTimerRunning]
        self.timerDict[timerName] = [0,False]

    def startTimer(self,timerName):
        self.timerDict[timerName][0] -= perf_counter()
        self.timerDict[timerName][1] = True
        
    def endTimer(self,timerName):
        self.timerDict[timerName][0] += perf_counter()
        self.timerDict[timerName][1] = False

    def initialiseCheckpoints(self):
        self.checkpoints = {}

        
    def createCheckpoint(self,checkpointName,timerName=None):

        timerList = ParseKeyInput(timerName,self.timerDict,'timerName')
        self.checkpoints[checkpointName] = {}
        
        for timer in timerList:
            time = UpdateTimer(self.timerDict[timer],inplace=False)
            self.checkpoints[checkpointName][timer] = time

        print(f'Checkpoint "{checkpointName}" created')


        
    def writeCheckpoint(self,checkpointName=None,timerName=None,printTotal=True,removeCheckpoint=False):

        checkpointList = ParseKeyInput(checkpointName,self.checkpoints,'checkpointName')
        timerList = ParseKeyInput(timerName,self.timerDict,'timerName')
        
        WriteReport([self.timerName],self.timerDict)
        for i,name in enumerate(checkpointList):

            print(f'Time since checkpoint "{name}"')
            for timer in timerList:

                time = self.timerDict[timer][0] + self.timerDict[timer][1]*perf_counter() - self.checkpoints[name][timer] 
                
                self.checkpoints[name][timer] = time
                        
            WriteReport(timerName,self.checkpoints[name],self.timerName,self.totalTime,printTotal=False)

            if removeCheckpoint is True:
                del self.checkpoints[name]
                

        
    def writeFullReport(self,timerName=None,final=False):

        if final is True:
            print('Final report: ')
        WriteReport(timerName,self.timerDict)

                
def UpdateTimer(timerInfo,inplace=True):

    try:
        time = timerInfo[0] + timerInfo[1]*perf_counter()
    except TypeError:
        time = timerInfo
    if inplace is True:
        timerInfo = [time,False]
    else:
        return time



def PrintTimeData(timerName,timerInfo,maxNameLength):

    time = UpdateTimer(timerInfo,inplace=False)
    
    fieldWidth = maxNameLength + 1

    timerName += ':'
    print(f'{timerName:{fieldWidth}}\t {timedelta(seconds=time)}')

    

def WriteReport(names,timerDict,totalName='',totalTime=0,printTotal=False):
    nameList = ParseKeyInput(names,timerDict,'timerName')
    
    maxNameLength = printTotal*len(totalName)
    for timerName in nameList:
        if len(str(timerName)) > maxNameLength:
            maxNameLength = len(str(timerName))
                
    if printTotal is True:
        timerInfo = [totalTime,True]
        PrintTimeData(totalName,timerInfo,maxNameLength)
                
    for timerName in nameList:
        timerInfo = timerDict[timerName]
        PrintTimeData(timerName,timerInfo,maxNameLength)
    

def ParseKeyInput(key,dictionary,variableName):
    if  key is None:
        keyList = [x for x in dictionary.keys()]
    elif type(key) is list:
        keyList = key
    elif type(key) is str:
        keyList = [key]
    else:
        raise TypeError(f'Expected {variableName} to be string or list of strings')

    return keyList

