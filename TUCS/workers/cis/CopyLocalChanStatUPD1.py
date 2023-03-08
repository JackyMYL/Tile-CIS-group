# Updated Sept, 2011: Joshua Montgomery <Joshua.Montgomery@cern.ch>
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#
# October 4, 2012 Adapted from CopyLocalChanStat.py to source UPD1 status directly
# from UPD1 rather than sourcing from UPD4 and then changing the tag 
# by Noah Wasserman <noah.david.wasserman@cern.ch>


from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *
import logging, getopt
from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK
from TileCalibBlobObjs.Classes import *
#import urllib.request, urllib.parse, urllib.error
#import xmlrpc.client
#import shlex


class CopyLocalChanStatUPD1(ReadGenericCalibration):
    "Make a local copy of the Channel Status DB to tileSqlite.UPD1.db"
    
    def __init__(self, runType='all', CISIOV=False, sqlfn='tileSqlite.UPD1.db', logfn='db_copy_log'):
        self.runType = runType
        self.CISIOV = CISIOV
        self.dbPath=os.path.join(getResultDirectory(), sqlfn)
        self.logPath=os.path.join(getResultDirectory(), logfn)
        
    def ProcessStart(self):
        # Apparently it would be nice if this wasn't a system call...
        
        self.folder = '/TILE/OFL02/STATUS/ADC'
        self.folderTag = TileCalibTools.getFolderTag('COOLOFL_TILE/CONDBR2', self.folder, 'CURRENT')
        
        ## For applications that use an IOV from the latest run we use the getLastRunNumber() function ##
        self.latestrun = TileCalibTools.getLastRunNumber()
        
        ## If not, for UPD4 tags, the IOV must be within the 36 hour calibration loop and greater than the last IOV used ##
        ## In general one can assume that 1+ the oldest run in the calibration loop is a legitimate choice. If the last IOV
        ## Updated is aboveis, one simply needs to change the index on caliblooplist[] below to move closer to the newest
        ## Runs in the calibration loop
        
        self.cloopfile = open('/afs/cern.ch/user/a/atlcond/scratch0/nemo/prod/web/calibruns.txt' , 'r')
        self.calist = self.cloopfile.readlines()
        if len(self.calist): self.calibloopIOV = int(self.calist[-1].strip('\n'))+1
        else: self.calibloopIOV=0
        
        if not self.CISIOV:
            print("\n NOTICE: calibloopIOV chosen is  "+str(self.calibloopIOV)+" to 0 \n")
        else:
            print(" \n NOTICE: calibloop IOV has been FORCED to be {0} \n \n".format(self.CISIOV))
            self.calibloopIOV = self.CISIOV
            
        if os.path.exists(self.dbPath): 
            os.unlink(self.dbPath)
        elif not os.path.exists(os.path.dirname(self.dbPath)):
            os.makedirs(os.path.dirname(self.dbPath))
            
        print("CopyLocalChanStatUPD1: I'm about to do a system call to AtlCoolCopy.exe. Check %s for output. You are a good person and people like you." % self.logPath)
        
        os.system("""AtlCoolCopy.exe "COOLOFL_TILE/CONDBR2" "sqlite://;schema={0};dbname=CONDBR2" -create -f /TILE/OFL02/STATUS/ADC -t {1} -run 9999999 -alliov -newrunlumisince {2} 0 2>&1 1>{3}""".format(self.dbPath, self.folderTag, str(self.calibloopIOV), self.logPath))
        
    def ProcessRegion(self, region):
        pass
