# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 17, 2009
#

from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *
import logging
from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK
from TileCalibBlobObjs.Classes import *

class CopyDBConstantsOFL(ReadGenericCalibration):
    "Make a local copy of the DB constants to tileSqliteOFL.db"

    def __init__(self, runType, recreate=False, sqlfn="tileSqliteOFL.db", logfn='db_copy_constants_log'):
        self.runType = runType
        self.recreate = recreate
        self.dbPath=os.path.join(getResultDirectory(), sqlfn)
        self.logPath=os.path.join(getResultDirectory(), logfn)
                                
    def ProcessStart(self):
        # It would be nice if this wasn't a system call...
        
        if os.path.exists(self.dbPath) and self.recreate: 
            os.unlink(self.dbPath)
        elif not os.path.exists(os.path.dirname(self.dbPath)):
            os.makedirs(os.path.dirname(self.dbPath))

        print("CopyDBConstants: Warning: I'm about to do a system call to AtlCoolCopy.exe.  This is dangerous, and I should feel ashamed.  Check %s for the output." % self.logPath)

        self.folder = None
        if self.runType == 'CIS':
            self.folder = '/TILE/OFL02/CALIB/CIS/LIN'
        if self.runType == 'LAS':
            self.folder = '/TILE/OFL02/CALIB/LAS/LIN'
        if self.runType == 'CES':
            self.folder = '/TILE/OFL02/CALIB/CES'
        if self.runType == 'EMS':
            self.folder = '/TILE/OFL02/CALIB/EMS'

        if self.folder:
            self.folderTag = TileCalibTools.getFolderTag('COOLOFL_TILE/CONDBR2', self.folder, 'CURRENT')
            print('Using folder '+str(self.folder))
            print('Using tag '+str(self.folderTag))
            command = """AtlCoolCopy.exe "COOLOFL_TILE/CONDBR2" "sqlite://;schema=%s;dbname=CONDBR2" -create -f %s -t %s 2>&1 1>%s""" % (self.dbPath, self.folder, self.folderTag, self.logPath)
            print('running: ', command)
            os.system(command)
        else:
            print('Unknown run type: ', self.runType)

    def ProcessRegion(self, region):
        pass
