# Author: Henric
#
# A sunday in Januray 2012
#
#
# Changed by Andrey kamenshchikov (akamensh@cern.ch), 14.05.2013.
import time


class Run:
    "This is a Tile run"

    def __init__(self, runNumber, runType, time, data):
        global run_list
        self.runNumber =  int(runNumber)
        self.runType   =  str(runType)
        if time != None:
            t=str(time)
            if ',' in t:
                self.time=t.split(",")[0]
                self.endtime=t.split(",")[1]
            else:
                self.time = t
                self.endtime = t
        else:
            self.time = None
            self.endtime = None
        self.data      =  data
        run_list.append(self)

    @property
    def time_in_seconds(self):
        return self.getTimeSeconds()

    def getTimeSeconds(self):
        if self.time == 'None' :
            print('wtf?')
            return 0.0

        c = time.strptime(self.time, '%Y-%m-%d %H:%M:%S')
        return time.mktime(c)

    def __str__(self):
        return '%6d, %s, %s %s'%(self.runNumber, self.runType, self.time, self.data)

    def __repr__(self):
        return '%s-%6d' % (self.runType, self.runNumber)
    
    def __lt__(self, other):
         return self.runNumber < other.runNumber

class RunList:
    "This is a Tile run list"

    def __init__(self):
        self.run_list = []

    def __getitem__(self,i):
        if i==-1:
            print((len(self.run_list)))
            return self.run_list[len(self.run_list)-1]
        else:
            return self.run_list[i]

    def getRunsOfType(self, runType=''):
        list = []
        for run in self.run_list:
            if run.runType==runType:
                list.append(run)
        return list

    def append(self,run):
        self.run_list.append(run)

    def remove(self,run):
        self.run_list.remove(run)
        del run
    
    
run_list = RunList()
