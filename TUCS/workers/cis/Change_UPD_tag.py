# Updated Nov, 2011: Joshua Montgomery <Joshua.Montgomery@cern.ch>
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
# March 04, 2009
#

from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *
import logging, getopt



from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK
from TileCalibBlobObjs.Classes import *
from PyCool import cool
#import xmlrpc.client
#import shlex


class Change_UPD_tag(ReadGenericCalibration):
    "Make a local copy of the tileSqlite.db with UPD1 tags"

    def __init__(self,runType='all', sqlfn1='tileSqlite.db', sqlfn2='tileSqlite.UPD1.db', logfn='db_copy_log'):
        self.runType = runType
        self.dbPathIn=os.path.join(getResultDirectory(), sqlfn1)
        self.dbPath=os.path.join(getResultDirectory(), sqlfn2)
        self.logPath=os.path.join(getResultDirectory(), logfn)
        self.latestRun = TileCalibTools.getLastRunNumber()
        print('The latest run is', self.latestRun)
                                
    def ProcessStart(self):
        # It would be nice if this wasn't a system call...

        self.folder = '/TILE/OFL02/STATUS/ADC'
        self.folderTag = TileCalibTools.getFolderTag('COOLOFL_TILE/CONDBR2', self.folder, 'CURRENT')
        print('This is the input tag for UPD1: ' + self.folderTag)

        if os.path.exists(self.dbPath): 
            os.unlink(self.dbPath)
        elif not os.path.exists(os.path.dirname(self.dbPath)):
            os.makedirs(os.path.dirname(self.dbPath))

        print("CopyLocalChanStat: Warning: I'm about to do a system call to AtlCoolCopy.exe.  This is dangerous, and I should feel ashamed.  Check %s for the output." % self.logPath)
        os.system("""AtlCoolCopy.exe  "sqlite://;schema={0};dbname=CONDBR2" "sqlite://;schema={1};dbname=CONDBR2"  -create -folder /TILE/OFL02/STATUS/ADC -tag {2}  -outfolder /TILE/OFL02/STATUS/ADC -outtag TileOfl02StatusAdc-RUN2-HLT-UPD1-00  -run 9999999 -alliov -newrunlumisince {3} 0 2>&1 1>{4}""".format(self.dbPathIn,self.dbPath,self.folderTag,self.latestRun,self.logPath))
        

    def ProcessRegion(self, region):
        pass
