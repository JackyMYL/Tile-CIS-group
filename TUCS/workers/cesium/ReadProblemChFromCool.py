# Andrey Kamenshchikov, 05-10-2013 (akamensh@cern.ch)
#
# Based on ReadBchFromCool.py
################################################################

from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *

from TileCalibBlobPython import TileCalibTools, TileBchTools

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger
getLogger("ReadBchFromCool").setLevel(logging.DEBUG)
getLogger("TileCalibTools").setLevel(logging.DEBUG)

class ReadProblemChFromCool(ReadGenericCalibration):
    "Read bad channels from COOL"

    def __init__(self, schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2",
                 folder="/TILE/OFL02/STATUS/ADC", tag="", Fast=False, storeADCinfo=False):
        self.schema       = schema
        self.folder       = folder
        self.tag          = tag
        self.runMgrs      = {}
        self.Fast         =  Fast
        self.storeADCinfo = storeADCinfo
        self.cesiumproblems = (2106,2109,2110)

        if "sqlite" in schema:
            splitname=schema.split("=")
            if not "/" in splitname[1]: 
                splitname[1]=os.path.join(getResultDirectory(), splitname[1])
                self.schema="=".join(splitname)


    def ProcessStart(self):
        #logger = getLogger("TileCalibTools")
        #logger.setLevel(logging.ERROR)
        
        if self.Fast:
            self.mgr = TileBchTools.TileBchMgr()
            logger = getLogger("TileBchMgr")
            logger.setLevel(logging.ERROR)               
        self.dbBadChanls = TileCalibTools.openDbConn(self.schema, 'READONLY')
        if not self.dbBadChanls:
            raise IOError("ReadBchFromCOOL: Failed to open a database connection, this can be an AFS token issue")           
        if self.folder== '/TILE/ONL01/STATUS/ADC':
            self.tag = ''
        elif self.folder== '/TILE/OFL01/STATUS/ADC':
            self.folderTag = 'TileOfl01StatusAdc-HLT-UPD1-00'
        elif self.folder== '/TILE/OFL02/STATUS/ADC':
            self.folderTag = TileCalibTools.getFolderTag(self.dbBadChanls, self.folder, self.tag)
        print('Channel Statuses from %s in with tag "%s"' % (self.folder, self.folderTag))
        if self.Fast:
            self.mgr.initialize(self.dbBadChanls, self.folder, self.folderTag)

        
    def ProcessRegion(self, region):
        if len(region.GetNumber()) == 3 : # This is an Channel
            [part, module, channel] = region.GetNumber()
            drawer = module-1
            for event in region.GetEvents():

##                event.data['isBad'] = False
                problems={}
                if self.Fast:
                    problems = self.mgr.getAdcProblems(part, drawer, channel, 0)
                else:
                    if 'csRun' in event.data:
##                        print event.data['csRun']
                        if event.data['csRun'] not in self.runMgrs:
                            self.runMgrs[event.data['csRun']] = TileBchTools.TileBchMgr()
                            logger = getLogger("TileBchMgr")
    ##                        logger.setLevel(logging.ERROR)
                            self.runMgrs[event.data['csRun']].initialize(self.dbBadChanls, self.folder, self.folderTag,(event.data['csRun'],0))                
                        problems = self.runMgrs[event.data['csRun']].getAdcProblems(part, drawer, channel, 0)
##                    print "Number of problems: "+str(len(problems))##akamensh
                if len(problems) != 0:
##                    event.data['isBad'] = True
                    if self.storeADCinfo:
                        if 'problems' not in event.data:
                            event.data['problems'] = set()
                        for prbCode in sorted(problems.keys()):
##                                print prbCode
##                                print problems[prbCode]
                            if int(prbCode) not in self.cesiumproblems:
                                continue
                            event.data['problems'].add(problems[prbCode])
                            print("New problem "+str(prbCode)+" for "+str(region)) ##akamensh


    def ProcessStop(self):
        self.runMgrs.clear()
        self.dbBadChanls.closeDatabase()

