# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#
# July 30, 2010 Adapted to trigger by Bernardo Peralva <bernardo@cern.ch>

from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *
import logging, getopt
#import _mysql
#mypath="/afs/cern.ch/user/t/tilebeam/offline/lib/python%d.%d/site-packages" % sys.version_info[:2]
#sys.path.append(mypath)
#import pymysql
#import urllib.request, urllib.parse, urllib.error
from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK
from TileCalibBlobObjs.Classes import *
#from PyCool import cool
#import xmlrpc.client
#import shlex


class WriteChanStat(ReadGenericCalibration):
    "The Channel Status DB Writer to tileSqlite.db"

    def __init__(self, tag='RUN2-UPD4-08', runType='all',\
                 run = 0, sqlfn='tileSqlite.db'):
            self.tag = tag
            self.runType = runType
            self.db = None
            self.mgr = None
            self.dbPath=os.path.join(getResultDirectory(), sqlfn)
            
            if run != 0:
                    self.fixedRun = True
                    self.runNumber = run
            else:
                    self.fixedRun = False
                    
    def ProcessStart(self):
            # check if the file exists
            try:
                    self.fout = open(os.path.join(getResultDirectory(),"noCIS.txt"), "r")
            except IOError:
                    self.cisFile = False
            else:
                    self.cisFile = True
            
            self.latestRun = TileCalibTools.getLastRunNumber()
            print('The latest run is', self.latestRun)
            self.db = TileCalibTools.openDb('SQLITE', 'CONDBR2', mode="UPDATE", sqlfn=self.dbPath)
            logger = getLogger("TileCalibTools")
            logger.setLevel(logging.ERROR)
            

            if not self.db:
                    print("WriteChanStat: Failed to open a connection to the COOL SQLite database")
            else:
                    if self.runType == 'L1Calo':
                            self.folder = '/TILE/ONL01/STATUS/ADC'
                            self.folderTag = ""
                    else:                            
                            self.folder = '/TILE/OFL02/STATUS/ADC'
                            self.folderTag = TileCalibTools.getFolderTag('COOLOFL_TILE/CONDBR2', self.folder, 'CURRENT')
                    self.mgr = TileBchTools.TileBchMgr()
                    self.mgr.setLogLvl(logging.WARNING)
                    
                    if self.fixedRun:
                            run = self.runNumber
                    else:
                            run = self.latestRun
                        
                    self.mgr.initialize(self.db, self.folder, self.folderTag, (run, 0))

                    if not self.mgr:
                            print("WriteChanStat: Failed to create a Bad Channel manager from the DB")


    def ProcessStop(self):                
            author   = "%s" % os.getlogin()

            if self.db and self.mgr:
                    if self.fixedRun:
                            run = self.runNumber
                    else:
                            run = self.latestRun

                    comment = "Created by TUCS using the command %s - " % (" ".join(sys.argv)) 
                    if self.runType == 'L1Calo':
                            line = open(os.path.join(getResultDirectory(),"trigCommentDB.txt")).readline()
                            fields = line.strip().split()
                            #=== read in fields
                            deadChan = int(fields[0])
                            halfChan = int(fields[1])
                            minX = fields[2]
                            maxX = fields[3]
                            os.remove(os.path.join(getResultDirectory(),'trigCommentDB.txt'))
                            comment2 = "%s channels have been flagged as no-gain and %s channels as half-gain from %s to %s." % (deadChan,halfChan,minX,maxX)
                            # comment3 = "This SQLite file was generated after reading from UPD4-00 while UPD4-00 un-synchronized from UPD1-00 during Aug. 23rd update by DQ"

                            comment = comment + comment2
                            self.mgr.commitToDb(self.db, self.folder, self.folderTag,\
                                TileBchDecoder.BitPat_onl01, author, comment, (run,0))    
                    else:
                            self.mgr.commitToDb(self.db, self.folder, self.folderTag,\
                                TileBchDecoder.BitPat_ofl01, author, comment, (run,0))     # this looks suspicious         
                    self.db.closeDatabase()

                    if self.cisFile:
                            self.fout.close()
                            os.remove(os.path.join(getResultDirectory(),'noCIS.txt'))


    def ProcessRegion(self, region):
            if 'gain' not in region.GetHash():
                    return    

            for event in region.GetEvents():
                    if event.run.runType != self.runType and self.runType != 'all':
                            continue

                    if not self.db or not self.mgr:
                            return

                    if 'gain' in region.GetHash():
                            setbit = False
                            if 'goodRegion' in event.data and \
                                   not event.data['goodRegion']:
                                    setbit = True

                            [x, y, z, w] = region.GetNumber()

                            if event.run.runType == 'L1Calo':       
                                    if event.data['isHalfGainL1']:
                                            self.mgr.addAdcProblem(x, y-1, z, w, TileBchPrbs.TrigHalfGain)
                                    else:
                                            self.mgr.delAdcProblem(x, y-1, z, w, TileBchPrbs.TrigHalfGain)

                                    if event.data['isNoGainL1']:
                                            self.mgr.addAdcProblem(x, y-1, z, w, TileBchPrbs.TrigNoGain)
                                    else:
                                            self.mgr.delAdcProblem(x, y-1, z, w, TileBchPrbs.TrigNoGain)
                                    return
                            else:
                                    type = None
                                    if event.run.runType == 'CIS':
                                            type = TileBchPrbs.NoCis
                                    elif event.run.runType == 'Laser':
                                            type = TileBchPrbs.NoLaser
                                    elif event.run.runType == 'Cesium':
                                            type = TileBchPrbs.NoCesium
                                    elif event.run.runType == 'Timing':
                                            type = TileBchProbs.NoTiming

                                    if type:
                                            if setbit:
                                                self.mgr.addAdcProblem(x, y-1, z, w, type)
                                                return # this will break things for many run types at same time
                                            else:
                                                self.mgr.delAdcProblem(x, y-1, z, w, type)
                                                return

                                    else:
                                             print('Unknown runtype ', event.run.runType)            

            # This marks all channels not giving data as bad, 'No CIS calibration'
            if self.cisFile:
                    for line in self.fout:
                            x = int(line.split(' ')[0])
                            y = int(line.split(' ')[1])
                            z = int(line.split(' ')[2])
                            w = int(line.split(' ')[3])

                            type = TileBchPrbs.NoCis

                            self.mgr.addAdcProblem(x, y-1, z, w, type)
                            return

