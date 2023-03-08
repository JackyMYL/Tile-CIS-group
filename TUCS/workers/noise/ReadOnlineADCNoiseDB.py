from src.ReadGenericCalibration import ReadGenericCalibration
from workers.noise.NoiseWorker import NoiseWorker

from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK
from TileCalibBlobObjs.Classes import *
from src.oscalls import *

#=== get a logger
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger

class ReadOnlineADCNoiseDB(ReadGenericCalibration,NoiseWorker):
    '''
    Reads online ADC noise values for optimal filter from conditions database
    '''
    
    def __init__(self,runType='Ped',useSqlite=True,dbConn='CONDBR2',dbFile='tileSqlite.db'):
        self.runType = runType
        self.ftDict = {} # Each element is a [TTree, TFile]
        self.useSqlite = useSqlite
        self.dbConn = dbConn
        self.dbPath=os.path.join(getResultDirectory(), dbFile)
    
    def get_index(self, part, mod, chan, gain):
        return part  *64*48*2\
            + mod      *48*2\
            + chan        *2\
            + gain

    def ProcessStart(self):
        loggerTCT = getLogger("TileCalibTools")
        loggerTCT.setLevel(logging.ERROR)
        
        # Open up a DB connection
        self.db = None
        if self.useSqlite:
            if not os.path.exists(self.dbPath):
                print('ReadOnlineADCNoiseDB: Failed to find ',self.dbPath)
                exit
            self.db = TileCalibTools.openDb('SQLITE', self.dbConn, 'READONLY', sqlfn=self.dbPath)
            print('ReadOnlineADCNoiseDB: Opened ',self.dbPath,' to read constants')
        else:
            self.db = TileCalibTools.openDb('ORACLE', self.dbConn, 'READONLY', "COOLONL_TILE")
            

        if not self.db:
            print("ReadOnlineADCNoiseDB: Failed to open a connection to the COOL database")
        else:
            #tag         = 'TileOnl01NoiseOfni-'+self.folderTag
            folder = '/TILE/ONL01/NOISE/OFNI'
            #folder      = TileCalibTools.getTilePrefix()+'NOISE/OFNI'
            
            print('Using folder: ',folder)
            self.blobReader = TileCalibTools.TileBlobReader(self.db, folder, '')
            
    def ProcessStop(self):
        if self.db:
            self.db.closeDatabase()

    def ProcessRegion(self, region):
        if len(region.GetEvents())==0: return
        # only interested in adc level
        if 'gain' not in region.GetHash():
            return
        
        # Get indices 
        [part, mod, chan, gain] = region.GetNumber()        
        for event in region.GetEvents():
            if event.run.runType == self.runType:
                self.checkForExistingData(event.data)
                # Query the database for the current Noise constants
                blob = self.blobReader.getDrawer(part, mod-1, (event.run.runNumber, 0))  # DB module numbers start from 0
                event.data['noise_db']   = blob.getData(chan, gain, 0)
                event.data['pilenoise_db']   = blob.getData(chan, gain, 1)
                print(region.GetHash(), event.data['noise_db'], event.data['pilenoise_db'])
                    
