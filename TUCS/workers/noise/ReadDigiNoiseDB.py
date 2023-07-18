from src.ReadGenericCalibration import ReadGenericCalibration
from workers.noise.NoiseWorker import NoiseWorker

from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK
from TileCalibBlobObjs.Classes import *
from src.oscalls import *
import bisect

#=== get a logger
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger

class ReadDigiNoiseDB(ReadGenericCalibration,NoiseWorker):
    '''
    Class to read digital noise values from conditions database
    '''
    
    def __init__(self, runType = 'Ped', useSqlite = True, dbConn = 'CONDBR2', dbFile = 'tileSqlite.db',
                 load_autocr = True, folderTag = 'RUN2-HLT-UPD1-01', folderTagAC = 'RUN2-HLT-UPD1-01', readIOVs=False,
                 IOVRun=None):
        
        self.runType = runType
        self.ftDict = {} # Each element is a [TTree, TFile]
        self.useSqlite = useSqlite
        self.dbConn = dbConn
        self.dbPath=os.path.join(getResultDirectory(), dbFile)
        self.load_autocr = load_autocr
        self.folderTag=folderTag
        self.folderTagAC=folderTagAC
        self.dbObjects = {}
        self.readIOVs = readIOVs
        if IOVRun == 'latest':
            IOVRun = MAXRUN
        elif IOVRun:
            IOVRun = int(IOVRun)
        self.IOVRun = IOVRun
    
    def get_index(self, part, mod, chan, gain):
        return part  *64*48*2\
            + mod      *48*2\
            + chan        *2\
            + gain

    def ProcessStart(self):
        loggerTCT = getLogger("TileCalibTools")
        loggerTCT.setLevel(logging.INFO)
        
        # Open up a DB connection
        self.db = None
        if self.useSqlite:
            if not os.path.exists(self.dbPath):
                print('ReadDigiNoiseDB: Failed to find ',self.dbPath)
                exit
            self.db = TileCalibTools.openDb('SQLITE', self.dbConn, 'READONLY', sqlfn=self.dbPath)
            print('ReadDigiNoiseDB: Opened ',self.dbPath,' to read constants')
        else:
            self.db = TileCalibTools.openDb('ORACLE', self.dbConn, 'READONLY', "COOLOFL_TILE")
            

        if not self.db:
            print("ReadDigiNoiseDB: Failed to open a connection to the COOL database")
        else:
            self.blobReader = {}
            # tagDigi         = 'TileOfl02NoiseSample-'+self.folderTag
            folderDigi      = TileCalibTools.getTilePrefix(True,True)+'NOISE/SAMPLE'

            tagDigi = TileCalibTools.getFolderTag(self.db, folderDigi, self.folderTag)

            print('Using folder: ',folderDigi,' with tag: ',tagDigi)
            self.blobReader['Digi'] = TileCalibTools.TileBlobReader(self.db, folderDigi, tagDigi)
            
            if(self.load_autocr):
                #tagDigi         = 'TileOfl02NoiseAutocr-'+self.folderTagAC
                folderDigi      = TileCalibTools.getTilePrefix(True,True)+'NOISE/AUTOCR'
                tagDigi = TileCalibTools.getFolderTag(self.db, folderDigi, self.folderTagAC)

                print('Using folder: ',folderDigi,' with tag: ',tagDigi)
                self.blobReader['autocr'] = TileCalibTools.TileBlobReader(self.db, folderDigi, tagDigi)

        print(" ")
            

    def ProcessStop(self):
        if self.db:
            self.db.closeDatabase()
        print(" ")

    def ProcessRegion(self, region):
        if len(region.GetEvents())==0: return
        # only interested in channel or adc level
        if 'gain' not in region.GetHash():
            #for event in region.GetEvents():
            #    if event.run.runType != 'staging':
            #        newevents.add(event)
            #region.SetEvents(newevents)
            return
        
        # Get indices 
        [part, mod, chan, gain] = region.GetNumber()
        for event in region.GetEvents():
            if event.run.runType == self.runType:
                self.checkForExistingData(event.data)
                # Query the database for the current Noise constants
                for key in list(self.blobReader.keys()):
                    dbRunNr = event.run.runNumber if self.IOVRun == None else self.IOVRun
                    blob = self.blobReader[key].getDrawer(part, mod-1, (dbRunNr, 0))  # DB module numbers start from 0
                    if key == 'Digi':
                        event.data['ped_db']   = blob.getData(chan, gain, 0)
                        event.data['hfn_db']   = blob.getData(chan, gain, 1)
                        try:
                            event.data['lfn_db']   = blob.getData(chan, gain, 2)
                        except RuntimeError:
                            event.data['lfn_db']   = 0.0
                        try:
                            event.data['hfnsigma1_db']   = blob.getData(chan, gain, 3)
                        except RuntimeError:
                            event.data['hfnsigma1_db']   = 0.0
                        try:
                            event.data['hfnsigma2_db']   = blob.getData(chan, gain, 4)
                        except RuntimeError:
                            event.data['hfnsigma2_db']   = 0.0
                        try:
                            event.data['hfnnorm_db']   = blob.getData(chan, gain, 5)
                        except RuntimeError:
                            event.data['hfnnorm_db']   = 0.0
                    elif key =='autocr':
                        for i in range(6):
                            event.data['autocorr'+str(i)+'_db']   = blob.getData(chan, gain, i)
        if self.readIOVs:
            # Get information about the DB objects, i.e. their IOV
            db_key = '%d_%d' % (part, mod-1)
            if db_key not in self.dbObjects:
                # get sorted list of runs, determine the first and last run
                runs = [event.run.runNumber for event in region.GetEvents() if event.run.runType == self.runType]
                runs.sort()
                firstRun = runs[0]
                lastRun = runs[-1]

                # Get all DB objects from firstRun to lastRun
                objs = self.blobReader['Digi'].getDBobjsWithinRange(ros=part, drawer=mod-1, point1inTime=(firstRun,0), point2inTime=(lastRun,0))            
                iov_runs = [TileCalibTools.runLumiFromCoolTime(obj.get().since())[0] for obj in objs]
                
                # find the closest run for each IOV
                closest_runs = []
                for run in iov_runs:
                    closest_run = None
                    if run > firstRun:
                        idx = bisect.bisect_left(runs, run)
                        closest_run = runs[idx] if idx < len(runs) and abs(runs[idx] - run) < abs(runs[idx - 1] -run) else runs[idx-1]
                    elif run == firstRun:
                        closest_run = run
                    if closest_run:
                        closest_runs.append(closest_run)
                self.dbObjects[db_key] = closest_runs
                print("ReadDigiNoiseDB: IOVs part %s start: %s end: %s orig: %s => %s" % (db_key, firstRun, lastRun, iov_runs, self.dbObjects[db_key]))
            dbObj = self.dbObjects[db_key]
            for event in region.GetEvents():
                if event.run.runType == self.runType and event.run.runNumber in dbObj:
                    event.data['ped_db_iov_start'] = True
            
