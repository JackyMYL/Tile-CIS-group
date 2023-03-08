# October 11th 2011: Creation of the worker by Henric
# Note August 2020: Apparently a modification of ReadBchFromCool.py written by Grey Wilburn (Chicago), unsure what functionality was added or changed - Elias Oakes

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


class ReadBadChFromCool(ReadGenericCalibration):
    '''
    Read bad channels from COOL
    '''

    def __init__(self, schema="OFL", data = 'DATA',
                 folder="/TILE/OFL02/STATUS/ADC", tag="UPD4", Fast=False, storeADCinfo=False, runNumber=1000000000):
        self.schema       = schema
        self.folder       = folder
        self.tag          = tag
        self.runMgrs      = {}
        self.Fast         =  Fast
        self.data         =  data
        self.storeADCinfo = storeADCinfo
        self.runNumber    = runNumber

        if "sqlite" in schema:
            splitname=schema.split("=")
            if not "/" in splitname[1]: 
                splitname[1]=os.path.join(getResultDirectory(), splitname[1])
                self.schema="=".join(splitname)


    def ProcessStart(self):
        #print "This worker was heavily modified by Grey Wilburn in early December, 2014."
        #logger = getLogger("TileCalibTools")
        #logger.setLevel(logging.ERROR)

        if self.Fast:
            self.mgr_r1 = TileBchTools.TileBchMgr()
            self.mgr_r2 = TileBchTools.TileBchMgr()
            logger = getLogger("TileBchMgr")
            logger.setLevel(logging.ERROR)

        self.r1 = False
        self.r2 = False
        IOV_list_r2 = []
        IOV_list_r1 = []

        for run in Use_run_list:
            if int(run) < 232000 and not self.Fast:
                 self.r1 = True
            else:
                 self.r2 = True

        own_schema = False
        if 'OFFLINE' in self.schema or 'OFL' in self.schema:
            if '1' in self.schema:
                linepath = 'OFL01'
                self.folder_full = '/TILE/OFL01/STATUS/ADC'
            else:
                linepath = 'OFL02'
                self.folder_full = '/TILE/OFL02/STATUS/ADC'
            schemepath = 'COOLOFL'

        elif 'ONLINE' in self.schema or 'ONL' in self.schema:
            linepath = 'ONL01'
            self.folder_full = '/TILE/ONL01/STATUS/ADC'
            schemepath = 'COOLONL'

        elif '.db' in self.schema:
            own_schema = True
            print(("ReadBchFromCool: reading SQL file %s" % self.schema))
            self.schema_r1 = self.schema
            self.schema_r2 = self.schema
            self.folder_full = self.folder

        else:
            own_schema = True
            print(("Warning: using an unorthodox schema %s" % self.schema))
            schema_r1 = self.schema
            schema_r2 = self.schema
            self.folder_full = self.folder

        print("ReadBadChFromCool", self.r2, self.r1, self.data, self.folder_full, self.tag)
        if self.r2 and not self.data == 'MC':
             if not own_schema:
                  self.schema_r2 = '%s_TILE/CONDBR2' % schemepath
             try: 
                  self.dbBadChanls_r2 = TileCalibTools.openDbConn(self.schema_r2, 'READONLY')    
             except Exception as e:
                  print("ReadBchFromCOOL: Failed to open RUN 2 database connection, this can be an AFS token issue")
                  print(e)
                  sys.exit(-1)
             self.folderTag_r2 = TileCalibTools.getFolderTag(self.dbBadChanls_r2, self.folder_full, self.tag)
             if self.Fast:
                  self.mgr_r2.initialize(self.dbBadChanls_r2, self.folder_full, self.folderTag_r2, (self.runNumber,0))
             else:
                  self.BlobReader_r2 = TileCalibTools.TileBlobReader(self.dbBadChanls_r2, self.folder_full, self.folderTag_r2)
                  IOV_list_r2 = self.GetIOV(self.BlobReader_r2)

             print(('RUN2 Channel Statuses from \n schema: %s\n folder: %s \n tag: %s' % (self.schema_r2, self.folder_full, self.folderTag_r2)))
        
        if self.r1 or self.data == 'MC':
             if not own_schema:
                  if self.data == 'MC':
                       self.schema_r1 = '%s_TILE/OFLP200' % schemepath
                  else:
                       self.schema_r1 = '%s_TILE/COMP200' % schemepath
                  self.folderTag_r1 = TileCalibTools.getFolderTag(self.schema_r1, self.folder_full, self.tag)
             try: 
                  self.dbBadChanls_r1 = TileCalibTools.openDbConn(self.schema_r1, 'READONLY')     
             except Exception as e:
                  print("ReadBchFromCOOL: Failed to open RUN 1 database connection, this can be an AFS token issue")
                  print(e)
                  sys.exit(-1)
             self.folderTag_r1 = TileCalibTools.getFolderTag(self.schema_r1, self.folder_full, self.tag)
             #print self.folderTag_r1
             if self.Fast:
                  self.mgr_r1.initialize(self.dbBadChanls_r1, self.folder_full, self.folderTag_r1, (self.runNumber,0))
             else:
                  self.BlobReader_r1 = TileCalibTools.TileBlobReader(self.dbBadChanls_r1, self.folder_full, self.folderTag_r1)
                  IOV_list_r1 = self.GetIOV(self.BlobReader_r1)
             print(('MC' if self.data == 'MC' else 'RUN1','Channel Statuses from \n schema: %s\n folder: %s \n tag: %s' % (self.schema_r1, self.folder_full, self.folderTag_r1)))

        if self.runNumber!=1000000000:
            print(('Using run:',  self.runNumber))

        if not self.Fast:
             self.run_manager_dict = self.GetManagers(IOV_list_r1, IOV_list_r2)


    def ProcessRegion(self, region):

        if len(region.GetNumber()) == 4 : # This is an ADC
            [part, module, channel, gain] = region.GetNumber()
            drawer = module-1

            for event in region.GetEvents():
                event.data['isBad'] = False

                if self.runNumber == 1000000000:
                    runNumber = event.run.runNumber
                else:
                    runNumber = self.runNumber

                status = None

                if self.Fast:
                    if runNumber > 232000 and not self.data == 'MC':
                        problems = self.mgr_r2.getAdcProblems(part, drawer, channel, gain)
                        status = self.mgr_r2.getAdcStatus(part, drawer, channel, gain)
                    else:
                        problems = self.mgr_r1.getAdcProblems(part, drawer, channel, gain)
                        status = self.mgr_r1.getAdcStatus(part, drawer, channel, gain)
                else:
                    mgr = self.run_manager_dict[event.run.runNumber]
                    problems = mgr.getAdcProblems(part, drawer, channel, gain)
                    status = mgr.getAdcStatus(part, drawer, channel, gain)
                
                event.data['isStatusBad'] = status.isBad()

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
        if self.r1:
            self.dbBadChanls_r1.closeDatabase()
        if self.r2 and not self.data == 'MC':
            self.dbBadChanls_r2.closeDatabase()
        print(" ")


    def GetIOV(self, blobReader):
        iovList = []
        dbobjs = blobReader.getDBobjsWithinRange(-1, 1000)
        while dbobjs.goToNext():
            obj = dbobjs.currentRef()
            objsince = obj.since()
            sinceRun = objsince >> 32
            sinceLum = objsince & 0xFFFFFFFF
            since    = (sinceRun, sinceLum)
            objuntil = obj.until()
            untilRun = objuntil >> 32
            untilLum = objuntil & 0xFFFFFFFF
            until    = (untilRun, untilLum)
            iov = (since, until)
            iovList.append(iov)
        return iovList

    def GetManagers(self, list_r1, list_r2):
        mgr_dict = {}
        run_min_list = []
        for run in Use_run_list:
           if run > 232000:
               list = list_r2
               db = self.dbBadChanls_r2
               ftag = self.folderTag_r2
           else: 
               list = list_r1
               db = self.dbBadChanls_r1
               ftag = self.folderTag_r1
           for iov in list:
               run_min = int(iov[0][0])
               run_max = int(iov[1][0])
               if run_min <= run <= run_max:
                   if not run_min in run_min_list:
                       run_min_list.append(run_min)
                       runMgr = TileBchTools.TileBchMgr()
                       runMgr.initialize(db, self.folder_full, ftag, (run_min,0))
                       logger = getLogger("TileBchMgr")
                       logger.setLevel(logging.ERROR)
                   mgr_dict[run] = runMgr
        return mgr_dict
