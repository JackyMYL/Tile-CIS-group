#!/usr/bin/env python
#Gabriele Bertoli <gbertoli@cern.ch>, 24 Jan 2014

from src.ReadGenericCalibration import ReadGenericCalibration
from workers.noise.NoiseWorker import NoiseWorker
from TileCalibBlobPython import TileCalibTools
from CaloCondBlobAlgs import CaloCondTools
from src.oscalls import *

class ReadCellNoiseDB(ReadGenericCalibration, NoiseWorker):
    '''
    Read cell noise values from condition database.
    '''

    def __init__(self, runType = 'Ped', useSqlite = True, dbConn = 'CONDBR2',
                 sqlfn = 'caloSqlite.db', folderTag = 'RUN2-UPD1-00', runNumber=-1):

        self.runType = runType
        self.useSqlite = useSqlite
        self.dbConn = dbConn
        self.dbPath=os.path.join(getResultDirectory(), sqlfn)
        self.folderTag = folderTag
        self.type = 'physical'
        self.db = None
        self.blobReader = None
        self.blob = None
        self.gainStr = ('LGLG','LGHG','HGLG','HGHG','HG--','--HG')
        self.runNumber = runNumber
        self.detectorId = 48
        self.verbose = False


    def ProcessStart(self):
        loggerTCT = getLogger("TileCalibTools")
        loggerTCT.setLevel(logging.INFO)

        #Opend the database

        if self.useSqlite:

            #Check if file exist

            try:

                with open(self.dbPath):
                    
                    self.db = TileCalibTools.openDb('SQLITE', self.dbConn, 'READONLY', sqlfn=self.dbPath)
                    
                    print('Opened DB with: ', self.dbPath)

            except IOError:
                
                print('ReadCellNoiseDB: Failed to find ', self.dbPath)
                
        else:
            
            schema = 'COOLOFL_TILE/'+self.dbConn
            
            self.db = TileCalibTools.openDbConn(schema, 'READONLY')
            
            print('Opened DB with: ', schema)

        if not self.db:
            
            print("ReadCellNoiseDB: Failed to open a connection to the COOL database")

        else:

            folderCell = '/TILE/OFL02/NOISE/CELL'
            #tagCell = TileCalibUtils.getFullTag(folderCell, self.folderTag)#'TileOfl02NoiseCell-' + self.folderTag
            tagCell = TileCalibTools.getFolderTag(self.db, folderCell, self.folderTag)

            print('Using folder:',folderCell)
            print('Using tag:',   tagCell)
                    
            self.blobReader = CaloCondTools.CaloBlobReader(self.db, folderCell, tagCell)
                    
            if self.blobReader and self.runNumber>=0:
                print('Using run:',  self.runNumber)
                self.blob = self.blobReader.getCells(self.detectorId,(self.runNumber, 0))

            print("DB Retrieved")
        print(" ")

    def ProcessRegion(self, region):

        if not region.GetEvents():

            return

        if not ('_t' in region.GetHash() or 'MBTS' in region.GetHash()):

            return

        if not self.db:

            return
            
        (ros, drawer, sample, tower) = region.GetNumber()

        if self.verbose:
            print("Entering in ProcessRegion " , region , " events " , region.GetEvents())
            print(ros , drawer , sample , tower)

        cellHash = CaloCondTools.getCellHash(self.detectorId, ros, drawer - 1, sample, tower)
        
        for event in region.GetEvents():

            if event.run.runType != self.runType:

                continue

            self.checkForExistingData(event.data)
                
            if self.blobReader:

                if self.blob:
                    blob = self.blob
                else:
                    blob = self.blobReader.getCells(self.detectorId,(event.run.runNumber, 0))
                    #print blob

                for gain in range(6):
                    
                    try:

                        event.data['cellnoise' + self.gainStr[gain] + '_db']  = blob.getData(cellHash, gain, 0)

                    except Exception:

                        event.data['cellnoise' + self.gainStr[gain] + '_db']  = 0.0

                    try:

                        event.data['pilenoise' + self.gainStr[gain] + '_db']  = blob.getData(cellHash, gain, 1)

                    except Exception:

                        event.data['pilenoise' + self.gainStr[gain] + '_db'] = 0.0

                    try:

                        event.data['cellsigma1' + self.gainStr[gain] + '_db'] = blob.getData(cellHash,gain, 2)

                    except Exception:

                        event.data['cellsigma1' + self.gainStr[gain] + '_db'] = 0.0

                    try:

                        event.data['cellsigma2' + self.gainStr[gain] + '_db'] = blob.getData(cellHash,gain, 3)

                    except Exception:

                        event.data['cellsigma2' + self.gainStr[gain] + '_db'] = 0.0

                    try:

                        event.data['cellnorm' + self.gainStr[gain] + '_db']   = blob.getData(cellHash,gain, 4)

                    except Exception:

                        event.data['cellnorm' + self.gainStr[gain] + '_db']   = 0.0

                    if self.verbose:
                        print(cellHash, gain, \
                            event.data['cellnoise' + self.gainStr[gain] + '_db'], \
                            event.data['pilenoise' + self.gainStr[gain] + '_db'], \
                            event.data['cellsigma1' + self.gainStr[gain] + '_db'], \
                            event.data['cellsigma2' + self.gainStr[gain] + '_db'], \
                            event.data['cellnorm' + self.gainStr[gain] + '_db']) 

    def ProcessStop(self):

        if self.db:

            self.db.closeDatabase()

        print(" ")
