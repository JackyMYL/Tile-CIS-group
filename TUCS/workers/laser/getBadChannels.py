############################################################
#
# getBadChannels.py
#
############################################################
#
# Author: Henric 
#
# November 01, 2011
#
# Goal: 
#    No advertized purpose
#
#
#############################################################
from __future__ import print_function
from src.GenericWorker import *
from src.region import *
from src.oscalls import *


class getBadChannels(GenericWorker):
    "This worker computes the variance wrt 0 deviation over the period"    
        
    def __init__(self):
        self.list = []

            
    def ProcessRegion(self, region):
        var = 0
        n = 0
        problems = set()
        for event in region.GetEvents():
            if 'deviation' in event.data:
                if event.data['deverr']>0.:
                    var += (event.data['deviation']*event.data['deviation'])/(event.data['deverr']*event.data['deverr'])
                    n+=1
            
            if 'problems' in event.data:
                for problem in event.data['problems']:
                    problems.add(problem)

        if n>0:
            self.list.append((region.GetHash(),var/n, problems))


    def ProcessStop(self):
        textout = open(os.path.join(getResultDirectory(),"LaserBch.txt"),'w')
        for item in sorted(self.list,key=lambda channel: channel[1], reverse=True):
            print(item, file=textout)
        self.list = []
