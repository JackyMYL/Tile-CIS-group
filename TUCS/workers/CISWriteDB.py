# Author: Alexandru Hostiuc <alexandru.hostiuc@cern.ch>
#
# To write a file updating the CIS database constants
#
# Based on the old WriteDB.py by Christopher Tunnell

from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *
from array import array
import decimal
#from exceptions import *
from types import *
from workers.WriteDBNew import *

# For reading from DB
from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK, LASPARTCHAN
from TileCalibBlobObjs.Classes import *

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger

class CISWriteDB(WriteDBNew, ReadGenericCalibration):
    "write out a tileSqlite.db file with database constants"

    def __init__(self, useSqliteRef=False, runType = 'CIS', runNumber=-1, #THE CHANGE U MADE IT HERE
                 offline_tag = 'RUN2-HLT-UPD1-00', version = 2, forcedreg = [], 
                 reprocessingstep=-1, deftargets=[]):

        self.runType       = runType
        self.runNumber     = runNumber
        self.useSqliteRef  = useSqliteRef
        self.forced_recals = forcedreg
        self.reprocessingstep = int(reprocessingstep)
        self.deftargets       = deftargets
        self.BlobWriters = []

        self.database={}                        #akamensh: creation of buffer database (for necessary drawers, mentioned in Use worker)

        if runType == 'CIS':
            version = 2
            print('SETTING VERSION TO 2 FOR CIS')
            
            self.offline_folder = '/TILE/OFL02/CALIB/CIS/LIN'
            self.offline_tag    = TileCalibTools.getFolderTag('COOLOFL_TILE/CONDBR2', self.offline_folder, offline_tag)

        else:
            print('WriteDB: Failed to initialize')
            return

        # use the latest run number as starting point (common to everyone)
        self.latestRun = TileCalibTools.getLastRunNumber()
        if self.runNumber < 0:
            self.runNumber = self.latestRun

        self.offline_iov  = (self.runNumber, 0)
        print((self.offline_iov))

    def ProcessStart(self):
        self.forcefinallist=[]

        if self.runType == 'CIS':
            # checking the statistics of the CIS recalibration.
            [self.checksum, self.checksum2, self.checksum3, self.checksum4, self.checksum5, self.checksumforce] = [0, 0, 0, 0, 0, 0]
            # retrieving information from the re-calibration calculation.
            self.list_of_targets = list_of_targets
            print(('in writeDB', self.list_of_targets))

        #open DB connection to sqlite file
    
        if self.reprocessingstep >= 0:
            filename='tileSqlite{0}.db'.format(self.reprocessingstep)
        else:
            filename='tileSqlite.db'
        self.dbPath=os.path.join(getResultDirectory(), filename)

        if not os.path.exists(os.path.dirname(self.dbPath)):
            os.makedirs(os.path.dirname(self.dbPath))

        self.db = TileCalibTools.openDb('SQLITE', 'CONDBR2', 'UPDATE', sqlfn=self.dbPath)
        
        self.blobWriterOffline = TileCalibTools.TileBlobWriter(self.db,self.offline_folder, 'Flt')
        self.BlobWriters.append(self.blobWriterOffline)

        util = PyCintex.gbl.TileCalibUtils()

        #
        # Once again things are done depending on runType
        #

        if self.runType == 'CIS':
            loGainDef=(1023./800.)
            hiGainDef=(64.*1023./800.)
            loGainDefVec = PyCintex.gbl.std.vector('float')()
            hiGainDefVec = PyCintex.gbl.std.vector('float')()

            loGainDefVec.push_back(loGainDef)
            hiGainDefVec.push_back(hiGainDef)

            print('CIS options setup')

        self.defVec = PyCintex.gbl.std.vector('std::vector<float>')()
        self.defVec.push_back(loGainDefVec)
        self.defVec.push_back(hiGainDefVec)

        limit = (lambda runType: 1 if runType=='Las' else util.max_ros())

        for ros in range(1,limit(self.runType)):                                     #          If run is not Las - make old variant of -
            for drawer in range(util.getMaxDrawer(ros)):
                for blobWriter in self.BlobWriters:                    
                            flt = blobWriter.getDrawer(ros,drawer)
                            flt.init(self.defVec, 48, 1)

    def ProcessStop(self):
        
        if self.runType == 'CIS':
            print(('recalibrating:           ', self.checksum-self.checksumforce))
            print(('forced recal:            ', self.checksumforce))
            print(('keeping db value:        ', self.checksum2))
            print(('receiving default value: ', self.checksum3))
            print(('outlier channel:         ', self.checksum4))
            print(('EBA MB4 channels:        ', self.checksum5))
            print(('total =                  ', int(self.checksum + self.checksum2 + self.checksum3 + self.checksum4 + self.checksum5)))

        # iov until is the end of the interval of validity, so infinity here
        iovUntil = (MAXRUN,MAXLBK)
        print(iovUntil)
        author   = "%s" % os.getlogin()

        print((self.runNumber))
        print((self.offline_iov))

        self.blobWriterOffline.setComment(author, "TUCS %s" % (" ".join(sys.argv)))
        self.blobWriterOffline.register(self.offline_iov, iovUntil, self.offline_tag)

        self.db.closeDatabase()


    def ProcessRegion(self, region):
        numbers = region.GetNumber()

        if len(numbers)==4: # Here we have an ADC
            part, mod, chan, gain = numbers
            drawer = mod-1


            if self.runType == 'CIS':
                calibration = None

                for event in region.GetEvents():
                    if event.run.runType == self.runType:
                        if 'calibratableRegion' in event.data and event.data['calibratableRegion']:
                            if 'mean' in event.data:
                                #retrieving calibration value from CISRecalibrateProcedure.py:
                                calibration = event.data['mean']
                                #print region.GetHash()
                    for evtreg in self.forced_recals:
                        if evtreg in region.GetHash():
                            if evtreg not in self.forcefinallist:
                                self.forcefinallist.append(evtreg)
                                print((self.forcefinallist))
                                print((len(self.forcefinallist)))
                                print(evtreg)
                            if 'mean' in event.data:
                                #print event.data['mean']
                                calibration = event.data['mean']
                                #print 'Forced Event receiving calibration for recal'
                            else:
                                print(('Forced Event in ', evtreg, 'Doesnt have mean event data'))
                        
                blobObjVersion = 1
                # check if db calibration exists
                dbval_exists = True
                try: event.data['f_cis_db']
                except: dbval_exists = False

                 # Different courses of action are taken depending on the calibration status. Some channels, such as EBA27 MB4 have bad calib voltage and should not be re-calibrated until repaired. To retrieve the database calibration: event.data['f_cis_db']. To retrieve new calculated calibration from CISRecalibrateProcedure: CIS_constant=calibration.

                # Re-calibrate channels passing CISRecalibrateProcedure.py:
                if calibration and region.GetHash() in self.list_of_targets:
                    self.checksum += 1
                    CIS_constant = float(calibration)
                    print(('region recalibrated: ', region.GetHash(), CIS_constant))
                    if region.GetHash() in self.forced_recals:
                        self.checksumforce += 1

                # Otherwise, keep db value:
                elif dbval_exists == True:
                    self.checksum2 += 1
                    CIS_constant = event.data['f_cis_db']
                    print(('region db val: ', region.GetHash(), CIS_constant))

                #Channels targeted for default during reprocessing
                elif region.GetHash() in self.deftargets:
                    self.checksum3+=1
                    if gain==1: #high-gain
                        CIS_constant=float(64.*1023./800.)
                    else:       #low-gain            
                        CIS_constant=float(1023./800.)
                    print(('targeted region default: ', region.GetHash(), CIS_constant))
                
                # If no db value exists, give channel default value.
                else:
                    self.checksum3 += 1
                    if gain == 1: # High gain
                        CIS_constant = float(64.*1023./800.)
                    else:                        #lowgain
                        CIS_constant = float(1023./800.)
                    print(('region default: ', region.GetHash(), CIS_constant))

                #default channels for reprocessing
#                if part==1 and mod==53 and chan==32 and gain==0:
#                    self.checksum3 += 1
#                    CIS_constant = float(1023./800.)
#                    print 'region default: ', region.GetHash(), CIS_constant

#                if part==1 and mod==54 and chan==46 and gain==1:
#                    self.checksum3 += 1
#                    CIS_constant = float(64.*1023./800.)
#                    print 'region default: ', region.GetHash(), CIS_constant

                # write the new CIS_constant to the Sqlite file.

                modBlob = self.blobWriterOffline.getDrawer(part, int(mod-1))
                modBlob.setData(chan, gain, int(0), float(CIS_constant))

            # All other cases.

            else:

                calibration = None
                for event in region.GetEvents():
                    if event.run.runType == self.runType:
                        if 'calibratableRegion' in event.data and event.data['calibratableRegion']:
                            if 'mean' in event.data:
                                calibration = event.data['mean']

                blobObjVersion = 1
                modBlobOfl = self.blobWriterOffline.getDrawer(int(part), int(mod-1))

                if calibration:
                    print(('region updated: ', region.GetHash()))
                    constant = float(calibration)

                else:
                    default_val = (64.*1023./800.) # highgain
                    if gain == 0: #lowgain
                        default_val = (1023./800.)
                    print(('region default: ', region.GetHash(), default_val))
                    constant = float(defaul_val)

                modBlobOfl.setData(chan, gain, int(0), constant)

