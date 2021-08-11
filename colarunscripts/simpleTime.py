from time import perf_counter
from datetime import timedelta
class Timer:
    """
    A class used to time the execution of code.
    
    Attributes:
    timerName -- str: The name of what is being timed

    Methods:
    initialiseTimer       -- Initialises a sub-timer.
    startTimer            -- Starts the specified sub-timer.
    stopTimer             -- Stops the specified sub-timer.
    initialiseCheckpoints -- Enables the use of checkpoints.
    createCheckpoint      -- Creates a checkpoint.
    writeCheckpoint       -- Writes a report of elapsed time since the checkpoint's
                             creation.
    writeFullReport       -- Writes a report of elapsed time for all sub-timers.
    """

    #Time is calculated using finish - start. Hence when timers start
    #they are set to -start
    def __init__(self,timerName):
        self.timerName = timerName           #Overall timer name
        self.totalTime = -1*perf_counter()   #Starting the overall timer
        self.timerDict = {self.timerName:[self.totalTime,True]}  #Dictionary of timers
            

    def initialiseTimer(self,timerName):
        """
        Initialises a sub-timer.

        Arguments:
        timerName -- str: Name of the sub-timer
        """

        #Add entry to dictionary of timers
        #List is [amount of time,isTimerRunning]
        self.timerDict[timerName] = [0,False]


        
    def startTimer(self,timerName):
        """
        Starts the specified sub-timer.

        Arguments:
        timerName -- str: Name of the sub-timer
        """
        
        self.timerDict[timerName][0] -= perf_counter() #Starting timer
        self.timerDict[timerName][1] = True            #Changing state to running


        
    def stopTimer(self,timerName):
        """
        Stops the specified sub-timer.

        Arguments:
        timerName -- str: Name of the sub-timer
        """
        self.timerDict[timerName][0] += perf_counter() #Stopping timer
        self.timerDict[timerName][1] = False           #Changing state to not running


        
    def initialiseCheckpoints(self):
        """Enables the use of checkpoints."""

        #Initialises the dictionary of checkpoints
        self.checkpoints = {}


        
    def createCheckpoint(self,checkpointName,timerName=None):
        """
        Creates a checkpoint.

        Arguments:
        checkpointName -- str: Name of the checkpoint to make
        timerName      -- str: The timer(s) to create a checkpoint for.
                               Can be a list of strings. Pass nothing for all.
        """

        #Getting list of timers to include in checkpoint
        timerList = ParseKeyInput(timerName,self.timerDict,'timerName')

        #Initialising dictionary for this checkpoint
        self.checkpoints[checkpointName] = {}

        #Looping through timers.
        #Timers may be running so need to grab current elapsed time without
        #stopping the timer.
        for timer in timerList:
            #Grabbing time value
            time = UpdateTimer(self.timerDict[timer],inPlace=False)
            self.checkpoints[checkpointName][timer] = time

        print(f'Checkpoint "{checkpointName}" created')


        
    def writeCheckpoint(self,checkpointName=None,timerName=None,printTotal=True,removeCheckpoint=False):
        """
        Writes a report of elapsed time since the checkpoint's creation.

        Optional Arguments:
        checkpointName   -- str: Checkpoint(s) to write out. Default is all. Can
                                 pass list of checkpoints.
        timerName        -- str: Timer(s) to write out. Default is all. Can pass 
                                 list of timers.
        printTotal       -- bool: Whether to print the total elapsed time also. 
                                  Default is True.
        removeCheckpoint -- bool: Whether to remove the checkpoint after printing
                                  Default is False.
        """

        #Grabbing lists of checkpoints and timers to write out
        checkpointList = ParseKeyInput(checkpointName,self.checkpoints,'checkpointName')
        timerList = ParseKeyInput(timerName,self.timerDict,'timerName')

        if printTotal is True:
            #Printing just the total time
            WriteReport([self.timerName],self.timerDict)

        #Dictionary to hold the values to print
        toPrint = {}
        #Looping through checkpoints
        for i,name in enumerate(checkpointList):
            print(f'Time since checkpoint "{name}"')
            
            for timer in timerList:
                #Calculating time since checkpoint, firstly updating still runnning
                totalTime = UpdateTimer(self.timerDict[timer],inPlace=False)
                toPrint[timer] = totalTime - self.checkpoints[name][timer]

            #Writing the report of each checkpoint
            WriteReport(timerName,toPrint,printTotal=False,totalName=self.timerName,totalTime=self.totalTime)

            #Removing checkpoint
            if removeCheckpoint is True:
                del self.checkpoints[name]
                

        
    def writeFullReport(self,timerName=None,final=False):
        """
        Writes a report of elapsed time for all sub-timers.

        Optional Arguments:
        timerName -- str: Timer(s) to write out. Default is all. Can pass 
                          list of timers.
        final     -- bool: Is this the final report. Default is False.
        """
        
        if final is True:
            print('Final report: ')

        #Writing the report
        WriteReport(timerName,self.timerDict)



#Utility functions to support the Timer class
def UpdateTimer(timerInfo,inPlace=True):
    """
    Update the timer with/without stopping it.

    Arguments:
    timerInfo -- list: 2 element list [time,isTimerRunning]. Can just be the time
    inPlace   -- bool: Whether to modify in place and stop the timer.
                       Alternatively returns the current time value. Default is True
    """

    #Attempts to update the timer. If timer is not running, nothing will be added
    try:
        time = timerInfo[0] + timerInfo[1]*perf_counter()
    except TypeError:
        time = timerInfo

    #Returning or updating in place
    if inPlace is True:
        timerInfo = [time,False]
    else:
        return time



def PrintTimeData(timerName,timerInfo,maxNameLength):
    """
    Prints a piece of time data.

    Arguments:
    timerName     -- str: Name of the time data.
    timerInfo     -- list 2 element list [time,isTimerRunning].
    maxNameLength -- int: Length of longest name to be printed, for formatting.
    """

    #Updating running timer
    time = UpdateTimer(timerInfo,inPlace=False)

    #Setting width of printing field
    fieldWidth = maxNameLength + 1

    #Printing the value. timedelta formats in dd-hh:mm:ss format
    timerName += ':'
    print(f'{timerName:{fieldWidth}}\t {timedelta(seconds=time)}')

    

def WriteReport(names,timerDict,printTotal=False,totalName='',totalTime=0):
    """
    Writes a report of the dictionary given.

    Arguments:
    names      -- str: string or list of strings of timerNames to print. 
    timerDict  -- dict: Dictionary of timers to print, keys correspoinding to names
    printTotal -- bool: Whether to print the total data or not. 
    totalName  -- str: Name of the overall timer.
    totalTime  -- int: Total time spent overall.
    """

    #Grabbing the list of timers
    nameList = ParseKeyInput(names,timerDict,'names')

    #Determining the longest name, totalName included
    maxNameLength = printTotal*len(totalName)
    for timerName in nameList:
        if len(str(timerName)) > maxNameLength:
            maxNameLength = len(str(timerName))

    #Printing overall time
    if printTotal is True:
        timerInfo = [totalTime,True]
        PrintTimeData(totalName,timerInfo,maxNameLength)

    #Printing everything
    for timerName in nameList:
        timerInfo = timerDict[timerName]
        PrintTimeData(timerName,timerInfo,maxNameLength)

        

def ParseKeyInput(key,dictionary,variableName):
    """
    Returns a list of keys based on different input types.

    Arguments:
    key          -- str: Input keys, may be str, str list or None. 
    dictionary   -- dict: The dictionary who's keys to return in None case.
    variableName -- str: The variable name of the first argument to raise for input
                         error
    """

    if  key is None:
        keyList = [x for x in dictionary.keys()]
    elif type(key) is list:
        keyList = key
    elif type(key) is str:
        keyList = [key]
    else:
        raise TypeError(f'Expected {variableName} to be string or list of strings')

    return keyList

