#!/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
# March 04, 2009
# Modified for Resource Debugging: Joshua Montgomery <Joshua.Montgomery@cern.ch>
# March 01, 2012

import gc
from src.region import *
import datetime
import time
from threading import Thread
import re
import math
import workers.PlotResources
from src.oscalls import *

#from guppy import hpy; h=hpy()

# This processes everything
class Go:
    def __init__(self, workers, withMBTS=True, withSpecialMods=True, memdebug=False, RUN2=True):
        print('Welcome to TUCS (pid %d).  Building detector tree... ' % os.getpid())
        
        self.debug = memdebug
        startup  = datetime.datetime.today()
        self.startlog = time.time()
        if self.debug:
            self.memlog = []
            self.timelog = []
            self.starting = True
            self.procID = os.getpid()
            self.resdir=getResultDirectory('ResourceLogs'),
            thread = Thread(target=self.readresources, args=(str(self.procID),.5))
            thread.start()
            self.timeline = open(self.resdir+'timeline_{0}.log'.format(os.getpid()), 'a')
            for line in open('/proc/{0}/cmdline'.format(self.procID)):
                gocommand = str(line).lstrip('python')
            self.timeline.write('{0} \n'.format(gocommand))
            self.timelog.append(gocommand)
            self.timeline.write('TUCS START: +{0}+ \n'.format(self.startlog - self.startlog))
            self.timelog.append('TUCS START: +{0}+'.format(self.startlog - self.startlog))
            self.timeline.close()
        self.detector = constructTileCal(useMBTS=withMBTS,useSpecialEBmods=withSpecialMods,RUN2=RUN2)
        print('done!')
        print()
        print('Entering worker loop:')
        
        if workers:
            for worker in workers:
                if worker:
                    print('Running %s - %s' % (worker.__class__.__name__, worker.__class__.__doc__))
                    
                    if self.debug:
                        print('{0} started at:'.format(worker.__class__.__name__), time.time() - self.startlog)
                        self.timeline = open(self.resdir+'timeline_{0}.log'.format(os.getpid()), 'a')                        
                        self.timeline.write('{0} Starts at: +{1}+ \n'.format(worker.__class__.__name__,
                                                                    time.time() - self.startlog))
                        self.timelog.append('{0} Starts at: +{1}+'.format(worker.__class__.__name__,
                                                                    time.time() - self.startlog))
                        self.timeline.close()

                    self.detector = worker.HandleDetector(self.detector)
                    sys.stdout.flush()
                    n = gc.collect()

                    if self.debug:
                        print('Unreachable objects:', n)
#                        print h.heap()
#                        print h.heap().more

                        self.timeline = open(self.resdir+'timeline_{0}.log'.format(os.getpid()), 'a')
                        print('Worker Ended At:', time.time() - self.startlog)
                        self.timeline.write('{0} Ended at: +{1}+ \n'.format(worker.__class__.__name__,
                                                                    time.time() - self.startlog))
                        self.timelog.append('{0} Ended at: +{1}+'.format(worker.__class__.__name__,
                                                                    time.time() - self.startlog))
                        self.timeline.close()

                    if not isinstance(self.detector, Region):
                        print("The following worker returned non-sense:", worker)
                        break
                    

        # free up memory
        for region in self.detector.RegionGenerator():
            region.SetEvents(set())
            region.SetChildren(set())
        del self.detector
        gc.collect(2)
        print()
        print('TUCS finished in:', datetime.datetime.today() - startup)
        if self.debug:
            self.timeline = open(self.resdir+'timeline_{0}.log'.format(os.getpid()), 'a')
            self.timeline.write('TUCS finished at: +{0}+'.format(time.time() - self.startlog))
            self.timelog.append('TUCS finished at: +{0}+'.format(time.time() - self.startlog))
            self.timeline.close()
            self.starting = False
            thread.join()

            
    def readresources(self, PID, sleeptime,*args):
        while self.starting:
            self.memuseage = open(self.resdir+'memusage_{0}.log'.format(self.procID), 'a')    
            re_parser = re.compile(r'^(?P<key>\S*):\s*(?P<value>\d*)\s*kB')
            result = dict()
            for line in open('/proc/meminfo'):
                match = re_parser.match(line)
                if not match:
                    continue # skip lines that don't parse
                key, value = match.groups(['key', 'value'])
                result[key] = int(value)
            tmem = int(result['MemTotal'])
            
            for line in open('/proc/{0}/status'.format(self.procID)):
                if 'VmSize' in line:
                    timept = time.time() - self.startlog
                    vmem   = int(line.split(':')[1].split('k')[0].strip())
            memuse = 100*float(vmem)/float(tmem)
            self.memuseage.write('Mem:_{0}_ time:_{1}_ \n'.format(memuse, timept))
            self.memlog.append('Mem:_{0}_ time:_{1}_ '.format(memuse, timept))
            self.memuseage.close()
            time.sleep(sleeptime) #sleep for a specified amount of time.
        workers.PlotResources.makeplots(MemLog=self.memlog, TimeLine=self.timelog, Output=PID)
                
