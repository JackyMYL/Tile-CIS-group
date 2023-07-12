from src.ReadGenericCalibration import ReadGenericCalibration

# For reading from DB
from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK
from TileCalibBlobObjs.Classes import *
from src.oscalls import *
import cppyy

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger

class WriteDigiNoiseDB(ReadGenericCalibration):
    '''
    Writes digital noise constants to sqlite file.
    '''

    def __init__(self, runType = 'PedUpdate', parameter='all',offline_iov_beg = (-1,0),offline_iov_end=(-1,0),load_autocr=True,folderTag='RUN2-HLT-UPD1-01',folderTagAC='RUN2-HLT-UPD1-00',dbConn='CONDBR2', sqlfn='tileSqlite.db', onlyWriteUpdated=False, verbose=False, outputDirectory=None):
        self.type = 'readout'
        self.writeOnline = False
        self.runType = runType
        self.load_autocr = load_autocr
        self.folderTag=folderTag
        self.folderTagAC=folderTagAC
        self.dbConn = dbConn
        if not outputDirectory:
            outputDirectory = getResultDirectory()
        self.dbPath=os.path.join(outputDirectory, sqlfn)
        self.m_onlyWriteUpdated = onlyWriteUpdated
        self.m_verbose = verbose
        self.indexDB = {'ped':0,'hfn':1,'lfn':2,'hfnsigma1':3,'hfnsigma2':4,'hfnnorm':5}
        for x in range(6):
            self.indexDB['autocorr'+str(x)] = x

        self.parameters = []
        if parameter =='all':
            self.parameters = ['ped','hfn','lfn','hfnsigma1','hfnsigma2','hfnnorm']
            if load_autocr:
                self.parameters += ['autocorr'+str(x) for x in range(6)]
        else:
            self.parameters.append(parameter)
        
        self.keys = ['Digi']
        if self.load_autocr: self.keys.append('autocr') 
       
        self.offline_folder = {}
        self.offline_tag = {}
        self.online_folder = {}
        self.online_tag = {}
        for key in self.keys:
            if key == 'Digi':
                folder = 'NOISE/SAMPLE'
                self.offline_tag[key] = 'TileOfl02NoiseSample-'+self.folderTag
                self.offline_folder[key] = TileCalibTools.getTilePrefix(True,True)+folder
            else:
                folder = 'NOISE/AUTOCR'
                self.offline_tag[key] = 'TileOfl02NoiseAutocr-'+self.folderTagAC
                self.offline_folder[key] = TileCalibTools.getTilePrefix(True,True)+folder
            
            self.online_folder[key]  = TileCalibTools.getTilePrefix(ofl=False)+folder
            self.online_tag[key]     = ""
        
        
        if offline_iov_beg[0] == -1:
            self.offline_iov_beg = (MAXRUN,MAXLBK)
        else:
            self.offline_iov_beg = offline_iov_beg  # The format of this is (run number, lumi block). Example: (92929, 0)
        
        if offline_iov_end[0] == -1:
            self.offline_iov_end = (MAXRUN,MAXLBK)
        else:
            self.offline_iov_end = offline_iov_end  # The format of this is (run number, lumi block). Example: (92929, 0)

    
    def ProcessStart(self):
        loggerTCT = getLogger("TileCalibTools")
        loggerTCT.setLevel(logging.INFO)

        #cppyy.makeClass('std::vector<float>')
        
        # open DB connection to sqlite file
        self.db = TileCalibTools.openDb('SQLITE', self.dbConn, 'UPDATE', sqlfn=self.dbPath)
        
        self.blobWriterOnline = {}
        self.blobWriterOffline = {}        
        for key in self.keys:
            loGainDefVec = cppyy.gbl.std.vector('float')()
            hiGainDefVec = cppyy.gbl.std.vector('float')()
            nValues = 6
            if key == 'autocr': nValues = 6
            for i in range(nValues):
                loGainDefVec.push_back(0.0)
                hiGainDefVec.push_back(0.0)
            defVec = cppyy.gbl.std.vector('std::vector<float>')()
            defVec.push_back(loGainDefVec)
            defVec.push_back(hiGainDefVec)
        
            self.m_defVec = defVec

            self.blobWriterOffline[key] = TileCalibTools.TileBlobWriter(self.db,self.offline_folder[key], 'Flt', True)
            blobObjVersion = 1
            if not self.m_onlyWriteUpdated:
                for part in range(5):
                    for drawer in range(min(64,TileCalibUtils.getMaxDrawer(part))):
                        modBlob = self.blobWriterOffline[key].getDrawer(part, drawer)
                        modBlob.init(defVec, 48,blobObjVersion)
            if self.writeOnline:
                self.blobWriterOnline[key]  = TileCalibTools.TileBlobWriter(self.db,self.online_folder[key], 'Flt', False)
                    
            
        
        
    def ProcessStop(self):
        import os
        author   = "%s through Tucs" % os.getlogin()
        
        quote = lambda x: " ".join([y if len(y)>0 else repr('') for y in x])
        for key in self.keys:
            #self.blobWriterOnline[key].setComment(author, quote(sys.argv))
            #self.blobWriterOnline[key].register(self.online_iov, iovUntil, self.online_tag[key])
    
            self.blobWriterOffline[key].setComment(author, quote(sys.argv))
            self.blobWriterOffline[key].register(self.offline_iov_beg, self.offline_iov_end, self.offline_tag[key])
            
        self.db.closeDatabase()
            
    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash():
            return

        [part, mod, chan, gain] = region.GetNumber()

        for event in region.GetEvents():
            if event.run.runType == self.runType:
                for p in self.parameters:
                    if p in ['ped','hfn','lfn','hfnsigma1','hfnsigma2','hfnnorm']:
                        key = 'Digi'
                    else:
                        key = 'autocr'
                    
                    try:
                        value = event.data[p]

                        blobObjVersion = 1
                        modBlob = self.blobWriterOffline[key].getDrawer(part, mod-1)
                        if modBlob:
                            # create drawer blobs on demand
                            if self.m_onlyWriteUpdated and (modBlob.getNChans() == 0):
                                if self.m_verbose:
                                    print("Creating Drawer data for partition: %d drawer: %d" % (part, mod))
                                modBlob.init(self.m_defVec, 48,blobObjVersion)
                            modBlob.setData(chan, gain, self.indexDB[p], float(value))
                        else:
                            print('WriteDB: Could not get blobwriter')

                        if self.writeOnline:
                            modBlob = self.blobWriterOnline[key].getDrawer(part, mod-1)
                            if modBlob:
                                modBlob.setData(chan, gain,  self.indexDB[p], float(value))
        
                    except ValueError:
                        print('Skipping writing of ',p,' for ',region.GetHash())

