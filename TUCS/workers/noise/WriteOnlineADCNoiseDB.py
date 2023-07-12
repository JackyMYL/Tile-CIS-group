from src.ReadGenericCalibration import ReadGenericCalibration

# For reading from DB
from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK
from TileCalibBlobObjs.Classes import *
from src.oscalls import *

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger

class WriteOnlineADCNoiseDB(ReadGenericCalibration):
    '''
    Writes online channel noise constants to sqlite file.
    '''

    def __init__(self, runType = 'Ped',dbConn='CONDBR2', sqlfn='tileSqlite.db'):
        self.type = 'readout'
        self.runType = runType
        self.dbConn = dbConn
        self.dbPath=os.path.join(getResultDirectory(), sqlfn)
    
    def ProcessStart(self):
        PyCintex.makeClass('std::vector<float>')
        
        # open DB connection to sqlite file
        self.db = TileCalibTools.openDb('SQLITE', self.dbConn, mode="RECREATE", sqlfn=self.dbPath)

        loGainDefVec = PyCintex.gbl.std.vector('float')()
        hiGainDefVec = PyCintex.gbl.std.vector('float')()
        loGainDefVec.push_back(0.0)
        loGainDefVec.push_back(0.0)
        hiGainDefVec.push_back(0.0)
        hiGainDefVec.push_back(0.0)
        
        defVec = PyCintex.gbl.std.vector('std::vector<float>')()
        defVec.push_back(loGainDefVec)
        defVec.push_back(hiGainDefVec)
        
        folder = '/TILE/ONL01/NOISE/OFNI'
        blobObjVersion = 1
        self.blobWriterOnline  = TileCalibTools.TileBlobWriter(self.db,folder, 'Flt', False)
        for part in range(5):
            for drawer in range(min(64,TileCalibUtils.getMaxDrawer(part))):
                modBlob = self.blobWriterOnline.getDrawer(part, drawer)
                modBlob.init(defVec, 48,blobObjVersion)
                    
    def ProcessStop(self):
        import os
        author   = "%s through Tucs" % os.getlogin()
        
        quote = lambda x: " ".join([y if len(y)>0 else repr('') for y in x])
        self.blobWriterOnline.setComment(author, quote(sys.argv))
        self.blobWriterOnline.register((0,0), (MAXRUN,MAXLBK))
    
        self.db.closeDatabase()
            
    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash():
            return

        [part, mod, chan, gain] = region.GetNumber()

        for event in region.GetEvents():
            if event.run.runType == self.runType:
                modBlob = self.blobWriterOnline.getDrawer(part, mod-1)
                if modBlob:
                    #printout channels with large noise, rms>5ADC counts 
                    if (event.data['efixed_rms']>3):
                        print(part, mod, chan, gain, "NEW:", event.data['efixed_rms'], "OLD:",event.data['noise_db'], "new>3 ")

                    #set noise constants to the rms. if new value is zero, keep old value from db    
                    if event.data['efixed_rms']<0.1:
                        modBlob.setData(chan, gain, 0, event.data['noise_db'])
                        print(part, mod, chan, gain, "NEW:", event.data['efixed_rms'], "OLD:",event.data['noise_db'], "Patched with old value ")
                    else:
                        modBlob.setData(chan, gain, 0, event.data['efixed_rms'])

                    #set pileup constants to those in the database 
                    modBlob.setData(chan, gain, 1, event.data['pilenoise_db'])

                else:
                    print('WriteDB: Could not get blobwriter')
                        
