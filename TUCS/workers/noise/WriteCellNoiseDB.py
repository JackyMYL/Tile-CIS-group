from src.ReadGenericCalibration import ReadGenericCalibration

# For reading from DB
from CaloCondBlobAlgs import CaloCondTools
from CaloCondBlobAlgs.CaloCondLogger import CaloCondLogger, getLogger
from TileCalibBlobPython import TileCalibTools
from src.oscalls import *
import cppyy

class WriteCellNoiseDB(ReadGenericCalibration):
    '''
    Writes cell noise constants to sqlite file.
    '''

    def __init__(self, runType = 'PedUpdate', parameter='all',offline_iov_beg=-1,offline_iov_end=-1,load_autocr=False,folderTag='REPC-02',dbConn='CONDBR2', sqlfn='caloSqlite.db',ngains=4):
        self.type = 'physical'
        self.runType = runType
        self.writeOnline = False
        self.folderTag = folderTag
        self.dbConn = dbConn
        self.dbPath=os.path.join(getResultDirectory(), sqlfn)
        self.ngains=ngains
        self.counter=0

        self.paramIndex  = {'cellnoise':0,'pilenoise':1,'cellsigma1':2,'cellsigma2':3,'cellnorm':4}
        self.gainIndex = {'LGLG':0,'LGHG':1,'HGLG':2,'HGHG':3,'HG--':4,'--HG':5}

        if parameter == 'all':
            self.parameters = ['cellnoise'+g for g in list(self.gainIndex.keys())]
            self.parameters += ['pilenoise'+g for g in list(self.gainIndex.keys())]
            self.parameters += ['cellsigma1'+g for g in list(self.gainIndex.keys())]
            self.parameters += ['cellsigma2'+g for g in list(self.gainIndex.keys())]
            self.parameters += ['cellnorm'+g for g in list(self.gainIndex.keys())]
        else:
            self.parameters = [parameter]
        
        self.offline_folder = '/TILE/OFL02/NOISE/CELL'
        self.offline_tag    = TileCalibUtils.getFullTag(self.offline_folder,self.folderTag)
        self.online_folder  = '/CALO/Noise/CellNoise'
        self.online_tag     = 'CaloNoiseCellnoise-RUN2-UPD1-00'

        if offline_iov_beg[0] == -1:
            self.offline_iov_beg = (MAXRUN,MAXLBK)
        else:
            self.offline_iov_beg = offline_iov_beg  # The format of this is (run number, lumi block). Example: (92929, 0)
        
        if offline_iov_end[0] == -1:
            self.offline_iov_end = (MAXRUN,MAXLBK)
        else:
            self.offline_iov_end = offline_iov_end  # The format of this is (run number, lumi block). Example: (92929, 0)
        
        #self.online_iov = (0, 0)


    def ProcessStart(self):
        print('WriteCellNoise ProcessStart')
        #cppyy.makeClass('std::vector<float>')
        
        # open DB connection to sqlite file
        self.db = TileCalibTools.openDb('SQLITE', self.dbConn, 'UPDATE', sqlfn=self.dbPath)

        GainDefVec = cppyy.gbl.std.vector('float')()
        GainDefVec.push_back(0.0)
        GainDefVec.push_back(0.0)
        GainDefVec.push_back(0.0)
        GainDefVec.push_back(0.0)
        GainDefVec.push_back(0.0)
        self.defVec = cppyy.gbl.std.vector('std::vector<float>')()
        for i in range(self.ngains):
            self.defVec.push_back(GainDefVec)
        
        # initialize Blob for writing
        self.blobWriterOffline = CaloCondTools.CaloBlobWriter(self.db,self.offline_folder, 'Flt', True)
        detectorId = 48 # Cool det. ID for TileCal
        self.cellBlobOffline = self.blobWriterOffline.getCells(detectorId)
        if self.cellBlobOffline:
            blobObjVersion = 1
            self.cellBlobOffline.init(self.defVec, 5184,blobObjVersion)
            self.cellBlobOffline = self.blobWriterOffline.getCells(detectorId)
        if self.writeOnline: 
            self.blobWriterOnline  = CaloCondTools.CaloBlobWriter(self.db,self.online_folder, 'Flt', False)
            self.cellBlobOnline = self.blobWriterOnline.getCells(detectorId)
            if self.cellBlobOnline:
                blobObjVersion = 1
                self.cellBlobOnline.init(self.defVec, 5184,blobObjVersion)
                self.cellBlobOnline = self.blobWriterOnline.getCells(detectorId)

        print("Writing to DB the following values:")
        print(self.parameters)
        print(" ")


    def ProcessStop(self):
        print('WriteCellNoise ProcessStop')
        print("Total number of cells written:",self.counter)
        import os
        author   = "%s through Tucs" % os.getlogin()
    
        #self.blobWriterOffline.setComment(author, " ".join(sys.argv))
        self.blobWriterOffline.register(self.offline_iov_beg, self.offline_iov_end, self.offline_tag)
            
        self.db.closeDatabase()
            
    def ProcessRegion(self, region):
        #print 'WriteCellNoise ProcessRegion'
        if '_t' not in region.GetHash():
            return

        [part, module, sample, tower] = region.GetNumber()
        detectorId = 48 # Cool det. ID for TileCal
        cellHash = CaloCondTools.getCellHash(detectorId,part,module-1,sample,tower)

        #print 'WriteCellNoise ProcessRegion 2'
        #print self.runType

        for event in region.GetEvents():
            #print event.run.runType
            if event.run.runType == self.runType:
                print("Cell counter",self.counter)
                self.counter+=1
                for p in self.parameters:

                    if self.gainIndex[p[-4:]] >= self.ngains:
                        print("skipping", region.GetHash(),p)
                        continue

                    try:
                        value = event.data[p]
                        print(p[-4:], p[:-4], [cellHash, self.gainIndex[p[-4:]], self.paramIndex[p[:-4]]], value)
                        
                        #if 'LBA_m01' in region.GetHash():
                        #    if p == 'cellsigma1HGHG':
                        #        print event.data[p]

                        if self.writeOnline and self.cellBlobOnline:
                            self.cellBlobOnline.setData(cellHash, self.gainIndex[p[-4:]], self.paramIndex[p[:-4]], float(value))

                        if self.cellBlobOffline:
                            self.cellBlobOffline.setData(cellHash, self.gainIndex[p[-4:]],  self.paramIndex[p[:-4]], float(value))

                    except KeyError:
                        print('Skipping writing of ',p,' for ',region.GetHash())
                        pass
