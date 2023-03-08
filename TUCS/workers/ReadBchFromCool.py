# October 11th 2011: Creation of the worker by Henric
#
# Henric is the author of this code. Do not modify unless explicit 
# agreement of the author
#

from src.ReadGenericCalibration import *
from src.region import *

from TileCalibBlobPython import TileCalibTools, TileBchTools

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger
getLogger("ReadBchFromCool").setLevel(logging.DEBUG)
getLogger("TileCalibTools").setLevel(logging.DEBUG)
from src.oscalls import *

import sys
try:
   # ROOT5
   import PyCintex
except:
   # ROOT6
   import cppyy as PyCintex
   sys.modules['PyCintex'] = PyCintex


class ReadBchFromCool(ReadGenericCalibration):
    "Read bad channels from COOL"

    def __init__(self, schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2",
                 folder="/TILE/OFL02/STATUS/ADC", tag="", Fast=False, storeADCinfo=False):
        self.schema       = schema
        self.folder       = folder
        self.tag          = tag
        self.runMgrs      = {}
        self.Fast         =  Fast
        self.storeADCinfo = storeADCinfo



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
            self.folderTag = ''
        elif self.folder== '/TILE/OFL01/STATUS/ADC':
            self.folderTag = 'TileOfl01StatusAdc-HLT-UPD1-00'
        elif self.folder== '/TILE/OFL02/STATUS/ADC':
            self.folderTag = TileCalibTools.getFolderTag(self.dbBadChanls, self.folder, self.tag)
        print(('Channel Statuses from %s folder %s tag "%s"' % (self.schema, self.folder, self.folderTag)))

        if self.Fast:
            self.mgr.initialize(self.dbBadChanls, self.folder, self.folderTag)


    def ProcessRegion(self, region):

        if len(region.GetNumber()) == 4 : # This is an ADC
            [part, module, channel, gain] = region.GetNumber()
            drawer = module-1
            for event in region.GetEvents():

                event.data['isBad'] = False

                if self.Fast:
                    problems = self.mgr.getAdcProblems(part, drawer, channel, gain)
                else:
                    if event.run.runNumber not in self.runMgrs:
                        self.runMgrs[event.run.runNumber] = TileBchTools.TileBchMgr()
                        logger = getLogger("TileBchMgr")
                        logger.setLevel(logging.ERROR)

                        self.runMgrs[event.run.runNumber].initialize(self.dbBadChanls, self.folder, self.folderTag,(event.run.runNumber,0))
                    problems = self.runMgrs[event.run.runNumber].getAdcProblems(part, drawer, channel, gain)
                #
                ### Houston we have a problem!
                #
                if len(problems) != 0:
                    event.data['isBad'] = True
                    if self.storeADCinfo:
                        if 'problems' not in event.data:
                            event.data['problems'] = set()
                        for prbCode in sorted(problems.keys()):
                            event.data['problems'].add(problems[prbCode])

                    if 'problems' not in region.data:
                        region.data['problems'] = set()
                    for prbCode in list(problems.keys()):
                        region.data['problems'].add(problems[prbCode])

                     
#                    print region.GetHash(), problems
                if event.run.runType == 'L1Calo':
                    [ros, module, channel, gain] = region.GetNumber()
                    if gain==0: # Low gain
                        stat = self.mgr.getAdcStatus(part, drawer, channel, gain)
                        if event.data['isHalfGainL1'] != stat.isHalfGainL1():
                            self.trigChange = True
                            print("********************************************")
                            print(("ADC %i / %i / %i / %i " % (ros,module,channel,gain)))
                            print(('Half Gain value from this calibration test: ', event.data['isHalfGainL1']))
                            print(('Half Gain value from the database: ', stat.isHalfGainL1()))

                        if event.data['isNoGainL1'] != stat.isNoGainL1():
                            self.trigChange = True
                            print("********************************************")
                            print(("ADC %i / %i / %i / %i " % (ros,module,channel,gain)))
                            print(('No Gain value from this calibration test: ', event.data['isNoGainL1']))
                            print(('No Gain value from the database: ', stat.isNoGainL1()))


    def ProcessStop(self):
        self.runMgrs.clear()
        self.dbBadChanls.closeDatabase()


