# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# For DB constants
#
# March 04, 2009
#
# July 16, 2009 : Adapted to LASER by Seb Viret <viret@in2p3.fr>
#
# April 14, 2011: Adapted to CIS by Andrew Hard <ahard@uchicago.edu>
#
# May 14, 2013: Improved LASER part by Andrey Kamenshchikov <akamensh@cern.ch>
#
# October 23, 2013: Improved CESIUM part by Andrey Kamenshchikov <akamensh@cern.ch>

from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *
from array import array
import decimal
#from exceptions import *
from types import *

# For reading from DB
from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK, LASPARTCHAN
from TileCalibBlobObjs.Classes import *

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger

class WriteDB(ReadGenericCalibration):
    "write out a tileSqlite.db file with database constants"

    def __init__(self, useSqliteRef=False, runType = 'CIS', runNumber=-1, 
                 offline_tag = 'RUN2-HLT-UPD1-00', version = 2, forcedreg = [], 
                 reprocessingstep=-1, deftargets=[], HV_datakey='HV',writeHV=True, 
                 check_difference=True, write_badHV=True, allowZeroHV=False, skipMBTS=True, maxHVdiff=100):

        self.runType       = runType
        self.runNumber     = runNumber
        self.useSqliteRef  = useSqliteRef
        self.forced_recals = forcedreg
        self.reprocessingstep = int(reprocessingstep)
        self.HV_datakey	=HV_datakey		#akamensh: option for defenition of HV's type - key for event.data[key]
        self.writeHV	= writeHV 		#akamensh: option for writing HV value in 2-d column (write if True - don't write if False)
        self.check_difference=check_difference	#akamensh: option for compare blobs with its previous state (check if current informtion is the same as already -
                                                #          - attends in database with latest IOV)
        self.write_badHV=write_badHV		#akamensh: option for what to do if HV<500V (write -3 if True or write 0 if False)
        self.allowZeroHV = allowZeroHV          #akamensh: allowZeroHV
        self.skipMBTS = skipMBTS                #akamensh: skipMBTS
        self.maxHVdiff = maxHVdiff              # write new HV only if difference is below this value
        self.deftargets       = deftargets
        self.BlobWriters = []

        self.database={}                        #akamensh: creation of buffer database (for necessary drawers, mentioned in Use worker)

        #
        # 'version' can be:
        # 0 - will write to ONL01 folder
        # 1 - will write to OFL01 folder
        # 2 - will write to OFL02 folder
        # Version is usually 2, because OFL01 folder is obsolete now 
        # and ONL01 folder is created as copy of OLF02 outside TUCS 
        #
        vers = ['ONL01','OFL01','OFL02']
        tags = ['Onl01','Ofl01','Ofl02']

        #
        # Here things are done depending on runType
        #
        if runType == 'CIS':
            self.offline_tag      = 'Tile%sCalibCisLin-%s' % (tags[version],offline_tag)
            self.offline_folder   = '/TILE/%s/CALIB/CIS/LIN' % vers[version]
            
        elif runType == 'Las':
            self.offline_tag      = 'Tile%sCalibLasLin-%s' % (tags[version],offline_tag)
            self.offline_folder   = '/TILE/%s/CALIB/LAS/LIN' % vers[version]
            # fiber is always OFL02
            self.offline_tag_F    = 'Tile%sCalibLasFiber-%s' % (tags[2],offline_tag)
            self.offline_folder_F = '/TILE/%s/CALIB/LAS/FIBER' % vers[2]

        elif runType == 'Las_NLN': # Lookup table for ADC saturation recovery
            self.offline_tag      = 'Tile%sCalibLasNln-%s' % (tags[version],offline_tag)
            self.offline_folder   = '/TILE/%s/CALIB/LAS/NLN' % vers[version]

        elif runType == 'Las_REF':
            self.offline_tag      = 'Tile%sCalibCes-%s' % (tags[version],offline_tag)
            self.offline_folder   = '/TILE/%s/CALIB/CES' % vers[version]

        elif runType == 'timing':
            self.offline_tag      = 'Tile%sTimeChanneloffsetPhy-%s' % (tags[version],offline_tag)
            self.offline_folder   = '/TILE/%s/TIME/CHANNELOFFSET/PHY' % vers[version]

        elif runType=='cesium':
            self.offline_tag      = 'Tile%sCalibCes-%s' % (tags[version],offline_tag)
            self.offline_folder   = '/TILE/%s/CALIB/CES' % vers[version]

        else:
            print('WriteDB: Failed to initialize')
            return

        if version==0: # no tag in single-version ONL01 folder
            self.offline_tag = ''

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

        # Don't need anything else for the LASER lookup table
        if self.runType == 'Las_NLN':
            return

        # Special loop for recovering Cesium reference values
        if self.runType == 'Las_REF' or self.runType == 'cesium' or self.runType == 'timing' or self.runType == 'Las':

            # another DB to read new laser ref values for Cesium update or new Cesium for Laser update
            dbPath=os.path.join(getResultDirectory(), 'tileSqlite.db')

            if self.useSqliteRef:
                if not os.path.exists(dbPath):
                    print(('ReadDB: Failed to find %s - using ORACLE ' % dbPath))
                    self.db_REF = TileCalibTools.openDbConn('COOLOFL_TILE/CONDBR2', 'READONLY')
                else:
                    print(('ReadDB: using sqlite file %s as DB with reference values' % dbPath))
                    self.db_REF = TileCalibTools.openDb('SQLITE', 'CONDBR2', 'READONLY', sqlfn=dbPath)
            else:
                self.db_REF = TileCalibTools.openDbConn('COOLOFL_TILE/CONDBR2', 'READONLY')

            self.blobReader = TileCalibTools.TileBlobReader(self.db_REF, self.offline_folder, self.offline_tag)

            # the same tileSqlite.db in which new constants are being written or any other DB (to read previous values)
            if self.useSqliteRef:
                if not os.path.exists(dbPath):
                    print(('ReadDB: Failed to find %s - using ORACLE for previous values' % dbPath))
                    self.db_PREV = TileCalibTools.openDbConn('COOLOFL_TILE/CONDBR2', 'READONLY')
                else:
                    print(('ReadDB: using sqlite file %s as DB with previous values' % dbPath))
                    self.db_PREV = TileCalibTools.openDb('SQLITE', 'CONDBR2', 'READONLY', sqlfn=dbPath)
            else:
                self.db_PREV = TileCalibTools.openDbConn('COOLOFL_TILE/CONDBR2', 'READONLY')

            self.blobReaderPrev = TileCalibTools.TileBlobReader(self.db_PREV, self.offline_folder, self.offline_tag)

            if self.runType == 'Las': # For fiber and partition stuff
                self.blobWriterOffline_F = TileCalibTools.TileBlobWriter(self.db,self.offline_folder_F, 'Flt')
                self.BlobWriters.append(self.blobWriterOffline_F)

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

        elif self.runType == 'Las':
            default = PyCintex.gbl.std.vector('float')()
            default1 = PyCintex.gbl.std.vector('float')()
            default.push_back(1.)
            default1.push_back(1.)
           
            if self.writeHV:		        #akamensh: extending of the initialization due to -
                default.push_back(-2.)		#          - inserting of HV to LAS/LIN folder 

            loGainDefVec = default
            hiGainDefVec = default
            
            loGainDefVec_other = default1      #akamensh: old variant of initialization for other folders (with one field only)
            hiGainDefVec_other = default1
         
        elif self.runType == 'Las_REF' or self.runType == 'cesium':
            default = PyCintex.gbl.std.vector('float')()
            default.push_back(  1.) # cesium constant
            default.push_back( -1.) # laser default value
            default.push_back(700.) # reference HV
            default.push_back( 20.) # reference temperature (same for all channels)
            default.push_back( -1.) # reference Pisa value

            loGainDefVec = default
            hiGainDefVec = default

        elif self.runType == 'timing':
            default = PyCintex.gbl.std.vector('float')()
            default.push_back(0.)

            loGainDefVec = default
            hiGainDefVec = default

        self.defVec = PyCintex.gbl.std.vector('std::vector<float>')()
        self.defVec.push_back(loGainDefVec)
        self.defVec.push_back(hiGainDefVec)

        if self.runType == 'Las':
            self.defVec_other = PyCintex.gbl.std.vector('std::vector<float>')()    #akamensh: separate vector's initialization -
                                                                                   #          - for other folders (not LAS/LIN) -
            self.defVec_other.push_back(loGainDefVec_other)			   #          - initialization (old variant with one field)
            self.defVec_other.push_back(hiGainDefVec_other)


        # Then we initialize everything
        
        if self.runType=='Las':                                                     #akamensh: open db to check if blobs 0-19 already exist
            dbPath=os.path.join(getResultDirectory(), 'tileSqlite.db')
            self.check_db=TileCalibTools.openDb('SQLITE', 'CONDBR2', 'READONLY', sqlfn=dbPath)
            self.ref_blobReader = TileCalibTools.TileBlobReader(self.check_db, self.offline_folder, self.offline_tag)
            
        limit = (lambda runType: 1 if runType=='Las' else util.max_ros())           #akamensh: modifying of blob's initialization depending on runType -
                                                                                    #          - for Las run in LAS/LIN folder initialize only blobs 0-19 -
                                                                                    #	       - and only if they don't exist.
        for ros in range(limit(self.runType)):                                     #          If run is not Las - make old variant of -
            for drawer in range(util.getMaxDrawer(ros)):                           #          - initialization (for all blobs).
                if self.runType=='Las':                                             
                    try:
                        ref_drawer_R = self.ref_blobReader.getDrawer(ros, drawer, (self.runNumber, 0))
                        if type(ref_drawer_R)==NoneType:
                            flt = self.blobWriterOffline.getDrawer(ros,drawer)
                            flt.init(self.defVec, 48, 1)		    
                        else:
                            print(("blob "+str((ros,drawer))+" already exists: not going to recreate it!!!"))
                    except Exception as e:
                        print(e)
                else:
                    for blobWriter in self.BlobWriters:                    
                        flt = blobWriter.getDrawer(ros,drawer)
                        flt.init(self.defVec, 48, 1)
                if self.runType == 'Las_REF':
                    drawer_R = self.blobReader.getDrawer(ros, drawer, (self.latestRun, 0))
                    drawer_W = self.blobWriterOffline.getDrawer(ros, drawer)
                    for chan in range(48):
                        for gain in range(2):
                            drawer_W.setData(int(chan), int(gain), 0, drawer_R.getData(chan, gain, 0))
                            drawer_W.setData(int(chan), int(gain), 1, drawer_R.getData(chan, gain, 1))
                            drawer_W.setData(int(chan), int(gain), 2, drawer_R.getData(chan, gain, 2))
                            drawer_W.setData(int(chan), int(gain), 3, drawer_R.getData(chan, gain, 3))

        #self.check_db.closeDatabase()                                              #ndulchin: appears to crash everything but 'Las' runs, moved below to fix

        if self.runType == 'Las':		                                    #akamensh: full initializing for other -
            self.check_db.closeDatabase()
            for ros in range(util.max_ros()):                                      #          - blobs (not LAS/LIN folder)
                for drawer in range(util.getMaxDrawer(ros)):
                    for blobWriter in self.BlobWriters:
                        if (blobWriter!= self.blobWriterOffline):
                            flt1 = blobWriter.getDrawer(ros,drawer)
                            flt1.init(self.defVec_other, 48, 1)

                    
    def ProcessStop(self):

        if self.runType=='Las':				                                #akamensh: new writing method for Las run

            if self.check_difference:
                print("Trying to check previous blobs")
                decimal.getcontext().prec = 5		                                #akamensh: establish precision of comparison
                try:
                    dbPath=os.path.join(getResultDirectory(), 'tileSqlite.db')
                    self.ref_db=TileCalibTools.openDb('SQLITE', 'CONDBR2', 'READONLY', sqlfn=dbPath)
                    self.ref_blobReader = TileCalibTools.TileBlobReader(self.ref_db, self.offline_folder, self.offline_tag)

                    for (part, drawer) in list(self.database.keys()):		                #akamensh: comparing with previous blobs
                        try:
                            ref_drawer_R = self.ref_blobReader.getDrawer(part, drawer, (self.runNumber, 0))
#			    print "Type of ref_drawer_R is ", type(ref_drawer_R)
                            if type(ref_drawer_R)==TileCalibDrawerFlt:
                                indic=0
                                if ref_drawer_R.getObjSizeUint32()!=len(self.database[(part, drawer)][0][0]):
                                    indic=1						#akamensh: change indicator if blobs (potential and existing) sizes - 
                                                                                        #          - are not equal
                                else:                                                   
                                    for i in range(48):
                                        for k in range(2):
                                            for l in range(ref_drawer_R.getObjSizeUint32()):
                                                if +decimal.Decimal(str(ref_drawer_R.getData(i, k, l))) != +decimal.Decimal(str(self.database[(part, drawer)][i][k][l])):
                                                    indic=1				#akamensh: change indicator if blobs (potential and existing) contents -
                                if indic==0:						#          - are not equivalent
                                    self.database.pop( (part, drawer) )		        #akamensh: delete potential blob if it is equivalent to existing -
                                                                                        #          - blob with latest IOV
                        except Exception as e:                                            
                            print(("Some problem with "+str((part, drawer))+" drawer"))
                            print(e)
                    self.ref_db.closeDatabase()
                except Exception as e:
                    print(("Some problem with existing database (%s)" & dbPath))
                    print(e)

                print("Stop checking previous blobs")
            else:
                print("Not going to check previous blobs")


            for (part, drawer) in list(self.database.keys()):			                #akamensh: write residual records of buffer database(potential blobs) - 
                drawer_W = self.blobWriterOffline.getDrawer(part, drawer)               #          - in blobs of tileSqlite.db
                drawer_W.init(self.defVec, 48, 1)
                for i in range(48):
                    for k in range(2):
                        for l in range(drawer_W.getObjSizeUint32()):
                            drawer_W.setData(i, k, l, self.database[(part, drawer)][i][k][l])


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

        if self.runType != 'Las_NLN':
            print((self.runNumber))
            print((self.offline_iov))

        quote = lambda x: " ".join([y if len(y)>0 else repr('') for y in x])
        self.blobWriterOffline.setComment(author, "TUCS %s" % (quote(sys.argv)))
        self.blobWriterOffline.register(self.offline_iov, iovUntil, self.offline_tag)

        if self.runType == 'Las':
            self.blobWriterOffline_F.setComment(author, "TUCS %s" % (quote(sys.argv)))
            self.blobWriterOffline_F.register(self.offline_iov, iovUntil, self.offline_tag_F)
            print(("commiting to DB %d %d" % self.offline_iov))

        if self.runType == 'Las_REF' or self.runType == 'cesium' or self.runType == 'Las': # For fiber and partition stuff

            self.db_REF.closeDatabase()
            self.db_PREV.closeDatabase()

        self.db.closeDatabase()

    #
    # Here we do the writing
    #

    def ProcessRegion(self, region):
        numbers = region.GetNumber()

        if len(numbers)==4: # Here we have an ADC
            part, mod, chan, gain = numbers
            drawer = mod-1
            # First the LASER case


            if self.runType == 'Las' or self.runType == 'Las_REF' or self.runType == 'Las_NLN':
                drawer_W = self.blobWriterOffline.getDrawer(part, drawer)
                if self.runType == 'Las':
                    drawer_F = self.blobWriterOffline_F.getDrawer(part, drawer)
                if self.runType == 'Las_REF':       # Case 2: reference values
                    drawer_R = self.blobReader.getDrawer(part, drawer, (self.latestRun, 0))

                badHV_limit=float(500)
                for event in region.GetEvents():

                    # Case 1: relative variation
                    if self.runType == 'Las':

 #### added for automatic calibration
                        if (event.run.runNumber != self.runNumber):
                            continue
                        if (gain != 0):
                            continue

                        if (part,drawer) not in list(self.database.keys()): 	#akamensh: initializing of buffer database
                            initvalues = (lambda writeHV: (float(1),float(-2)) if writeHV else (float(1),))
                            chlist=[]
                            for i in range(48):
                                glist=[]
                                for k in range(2):
                                    glist.insert(k,initvalues(self.writeHV))
                                chlist.insert(i,glist)
                            self.database[(part,drawer)]=chlist		
                       
                        if 'calibration' in event.data and 'f_laser' in event.data:                         
                            drawer_F = self.blobWriterOffline_F.getDrawer(part, drawer)                    
                            # Then we update if there is a new value (coefficients are in %, so we put in correct format)
                            # First update PMT variation
                            f_laser = float(1/event.data['f_laser'])

                            # Testing the special flags from Laser behvior study
                            #
                            pmt_region = str(region)
                            region_flag=''
                            for x in range(8,19):
                                region_flag+=pmt_region[x]

                            try:
                                Ch_flag = Chan_flag[region_flag][0]
                            except:
                                Ch_flag = "void"
                                print("Warning, no flag defined. All channels calibrated!")

                            drawer_R = self.blobReader.getDrawer(part, drawer, (self.latestRun, 0))
                            f_laser_previous = drawer_R.getData(chan, gain, 0)

                            # cases where no constant should applied or updated: put old one
                            #
                            if ( ((Ch_flag == "Bad_Chan") and (abs(1.0-f_laser)>0.15)) or (Ch_flag == "Fast Drift") or (Ch_flag == "Fiber") or (Ch_flag == "status_pb") or (Ch_flag == "DQ_pb") or (Ch_flag == "No laser") or (Ch_flag == "OK_pb") ):
                                f_laser = f_laser_previous



                            # special case: if no deviation and not calibrated before: constant set 1.0
                            if ((Ch_flag == "No_Dev") and (f_laser_previous == 1)):
                                f_laser = 1

                            # special case: MBTS constant set 1.0
                            if (Ch_flag == "MBTS"):
                                f_laser = 1

                        else: # if no good f_laser, keep old one.
                            drawer_R = self.blobReader.getDrawer(part, drawer, (self.latestRun, 0))
                            f_laser = drawer_R.getData(chan, gain, 0)

                        if self.HV_datakey in event.data:	        #akamensh: prepearing of HV values for buffer database
                            if abs(f_laser)!=float(1):
                                if (event.data[self.HV_datakey]>badHV_limit):
                                    HV_laser=event.data[self.HV_datakey]
                                else:
                                    HVwrite=(lambda write_badHV: float(-3) if write_badHV else float(0))
                                    HV_laser=HVwrite(self.write_badHV)
                            else:
                                HV_laser=float(-1)
                        else:
                            HV_laser=float(-2)

                        data_values=(lambda writeHV: (f_laser,HV_laser) if writeHV else (f_laser,)) #akamensh: filling of buffer database with data

 
 #### added for automatic calibration
                        self.database[(part,drawer)][chan][0]=data_values(self.writeHV)
                        self.database[(part,drawer)][chan][1]=data_values(self.writeHV)

                        
 ####

                    if self.runType == 'Las_REF':       # Case 2: reference values

                        if 'is_OK' in event.data: # Channel has a relevant value, store it
                            reference = -1.
                            pisaref = -1.
                            if  event.data['is_OK']:
                                reference = event.data['calibration']

                            # TMP TMP TMP used to keep E cells unchanged
                            if self.layer[pmt_region] in ['E1','E2','E3','E4']:
                                print((' using default value for special cell ', self.layer[pmt_region], reference, ' -> ', drawer_R.getData(chan, gain, 1)))
                                reference = drawer_R.getData(chan, gain, 1)


                            #else:
                            #    print 'No data, set default for region', region.GetHash()

                            if 'gain_Pisa' in event.data:
                                pisaref = event.data['gain_Pisa']
                                    # print pisaref
#                            print  "%s old value=%f new value=%f" %(region.GetHash(),
#                                                                    drawer_R.getData(chan, gain, 1),
#                                                                    reference )
                            drawer_W.setData(int(chan), int(gain), 0, drawer_R.getData(chan, gain, 0))
                            drawer_W.setData(int(chan), int(gain), 1, float(reference))
                            drawer_W.setData(int(chan), int(gain), 2, drawer_R.getData(chan, gain, 2))
                            if 'HV' in event.data:
                                if  event.data['HV']>500.:
                                    drawer_W.setData(int(chan), int(gain), 2, float(event.data['HV']) )
                            drawer_W.setData(int(chan), int(gain), 3, drawer_R.getData(chan, gain, 3))
                            drawer_W.setData(int(chan), int(gain), 4, float(pisaref))

                            #if region.GetMBTStype() and event.data.has_key('HV'):
                            #    drawer_W.setData(int(chan), int(gain), 2, float(event.data['HV']) )
                            #    print "Setting HV:",   float(event.data['HV'])

                        else: # Put the default Cesium stuff, without any LASER info
                            #   This would happen if we selected only a sub-region of TileCal
                            print("This I hope never happens")
                            self.writeCsDef(region,drawer_W,chan,drawer_R,False,False,False)

                    # Case 3: LookUp table
                    if self.runType == 'Las_NLN':

                        if 'LUTx' in event.data:
                            drawer = self.blobWriterOffline.getDrawer(0,0)

                            lut = PyCintex.gbl.std.vector('float')()

                            for i in range(len(event.data['LUTx'])):
                                lut.push_back(event.data['LUTx'][i]) # X values

                            for i in range(len(event.data['LUTy'])):
                                lut.push_back(event.data['LUTy'][i]) # Y values

                            defLut = PyCintex.gbl.std.vector('std::vector<float>')()
                            defLut.push_back(lut)
                            drawer.init(defLut, 1, 100)

         # Then cesium
        
            elif self.runType=='cesium':
                
                if gain!=0:
                    return
                
                drawer = self.blobWriterOffline.getDrawer(part, mod-1)
                tower=region.GetParent('physical').GetParent('physical')
                drawer_P = self.blobReaderPrev.getDrawer(part, mod-1, self.offline_iov)
                drawer_R = self.blobReader.getDrawer(part, mod-1, self.offline_iov)

                writeDef=True
                HV=-1.0
                if region.GetEvents():
                    if len(region.GetEvents()):
                        writeDef=False
                    for event in region.GetEvents():
                        if self.HV_datakey in event.data and ((event.data[self.HV_datakey]>499.0 and event.data[self.HV_datakey]<989.0) or (self.allowZeroHV and (event.data[self.HV_datakey]==0.0 or event.data[self.HV_datakey]>989.0))):
                            HV=event.data[self.HV_datakey]
                            if HV>989.0:
                                HV=0.0
                        if event.run.runType==self.runType:
                            #drawer_P = self.blobReaderPrev.getDrawer(part, mod-1, (event.runNumber, 0))
                            if event.data['update_needed']:
                                # channel was calibrated
                                calibration = event.data['calibration']
                                calibration_db = drawer_P.getData(chan, 0, 0)
                                if calibration<0: # will keep old constant, but update HV value
                                    calibration = calibration_db
                                Las_db = str(drawer_R.getData(chan, 0, 1))+"/"+str(drawer_R.getData(chan, 1, 1))
                                if 'HV' in event.data and ((event.data['HV']>499.0 and event.data['HV']<989.0) or (self.allowZeroHV and (event.data['HV']==0.0 or event.data['HV']>989.0))):
                                    HV=event.data['HV']
                                    if HV>989.0:
                                        HV=0.0
                                else:
                                    HV=drawer_P.getData(chan, 0, 2)
                                if 'temp' in event.data and event.data['temp']>15.0 and event.data['temp']<35.0:
                                    T=event.data['temp']
                                else:
                                    T=drawer_P.getData(chan, 0, 3)
                                for gn in [0,1]:
                                    drawer.setData(int(chan), int(gn), 0, calibration)
                                    drawer.setData(int(chan), int(gn), 1, drawer_R.getData(chan, int(gn), 1))
                                    drawer.setData(int(chan), int(gn), 2, HV)
                                    drawer.setData(int(chan), int(gn), 3, T)
                                towerHash = tower.GetHash()
                                if ('sD_t00' in towerHash) and (part==2):
                                    towerHash = towerHash.replace('LBA','LBC')
                                if ('MBTS' in towerHash) and self.skipMBTS:
                                    self.writeCsDef(region,drawer,chan,drawer_P,drawer_R,False,False,True)
                                else:
                                    if (calibration_db!=0):
                                        print(('writing new const for', towerHash, "ch%02i"%chan, calibration,\
                                              'instead of', calibration_db,'ratio is', calibration/calibration_db,\
                                              'Lasref=',Las_db,'HV=',HV,'T=',T))
                                    else:
                                        print(('writing new const for', towerHash, "ch%02i"%chan, calibration,\
                                              'instead of', calibration_db,'ratio is 999999999999.',\
                                              'Lasref=',Las_db,'HV=',HV,'T=',T))
                                        
                            else:
                                # channel was not calibrated, keep old value or put default
                                self.writeCsDef(region,drawer,chan,drawer_P,drawer_R,True,False,True,HV)
                        else:
                            self.writeCsDef(region,drawer,chan,drawer_P,drawer_R,False,False,True,HV)
            
                if writeDef:
                    # channel was not selected, keep old value
                    self.writeCsDef(region,drawer,chan,drawer_P,drawer_R,False,False,True,HV)

            # Then timing

            elif self.runType=='timing':

                drawer_W = self.blobWriterOffline.getDrawer(part, drawer)
                drawer_R = self.blobReader.getDrawer(part, drawer, self.offline_iov)

                writeDef=True
                for event in region.GetEvents():
                    if event.run.runType==self.runType and 'timing' in event.data:
                        writeDef=False
                        print(("Timing for %i / %i / %i / %i == %f - Writing new value" % (part,mod,chan,gain,event.data['timing'])))
                        drawer_W.setData(int(chan), int(gain), 0, event.data['timing'])

                if writeDef:
                    # channel was not selected, keep old value
                    print(("Timing for %i / %i / %i / %i == %f - Keeping old value" % (part,mod,chan,gain,drawer_R.getData(int(chan), int(gain), 0))))
                    drawer_W.setData(int(chan), int(gain), 0, drawer_R.getData(int(chan), int(gain), 0))

            # Then the CIS.

            elif self.runType == 'CIS':
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

                # Preserve original CIS constant for EBA27 MB4 channels:
                if part ==3 and mod == 27 and chan in range(0,12):
                    self.checksum5 += 1
                    CIS_constant = event.data['f_cis_db']
                    #print 'EBA27 db value: ', region.GetHash(), CIS_constant

                # Re-calibrate channels passing CISRecalibrateProcedure.py:
                elif calibration and region.GetHash() in self.list_of_targets:
                    self.checksum += 1
                    CIS_constant = float(calibration)
                    print(('region recalibrated: ', region.GetHash(), CIS_constant))
                    if region.GetHash() in self.forced_recals:
                        self.checksumforce += 1

                # Otherwise, keep db value:
                elif dbval_exists == True:
                    self.checksum2 += 1
                    CIS_constant = event.data['f_cis_db']
                    #print 'region db val: ', region.GetHash(), CIS_constant

                #Channels targeted for default during reprocessing
                elif region.GetHash() in self.deftargets:
                    self.checksum3+=1
                    if gain==1: #high-gain
                        CIS_constant=float(64.*1023./800.)
                    else:       #low-gain            
                        CIS_constant=float(1023./800.)
                    #print 'targeted region default: ', region.GetHash(), CIS_constant
                
                # If no db value exists, give channel default value.
                else:
                    self.checksum3 += 1
                    if gain == 1: # High gain
                        CIS_constant = float(64.*1023./800.)
                    else:                        #lowgain
                        CIS_constant = float(1023./800.)
                    #print 'region default: ', region.GetHash(), CIS_constant

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


    #
    # Here we write default Cs values
    #

    def writeCsDef(self,region,drawer,chan,drawer_P,drawer_R,fixError,writeDefault,writeLASER,HV=-1.0):

        calibration_db = drawer_P.getData(chan, 0, 0)
        Las_db = str(drawer_R.getData(chan, 0, 1))+"/"+str(drawer_R.getData(chan, 1, 1))
        calibration=calibration_db
        HV0 = int(drawer_R.getData(chan, 0, 2)*100+0.5)/100.
        HV1 = int(drawer_R.getData(chan, 1, 2)*100+0.5)/100.
        HV = int(HV*100+0.5)/100.
        if (HV0 != HV1):
            HV_db = "HV= "+str(HV0)+"/"+str(HV1)
        else:
            HV_db = "HV= "+str(HV0)
        if (HV>=0.0):
            HVdiff = int((1000.+HV-HV0)*100+0.5)/100.-1000.
            if HVdiff>0.001 or -HVdiff>0.001:
                HV_db += " NEW_HV= "+str(HV)+" DIF= "+str(HVdiff)
            else:
                HV_db += " NEW_HV= "+str(HV)+" DIF= 0"
            #if HVdiff>self.maxHVdiff or -HV>self.maxHVdiff:
            if HVdiff>self.maxHVdiff:
                HV=-1.0
                HV_db += " TOO BIG DIFF - ignoring new HV"

        tower=region.GetParent('physical').GetParent('physical')
        module=region.GetParent().GetParent()
        towerHash = tower.GetHash()
        if ('sD_t00' in towerHash) and ('LBC' in module.GetHash()):
            towerHash = towerHash.replace('LBA','LBC')

        if fixError and module.GetMBTStype()>0 and chan==0 and calibration_db>100.0:
            calibration=1./1.05  # overwrite calibration for MBTS
            print(('writing default for MBTS ', towerHash, "ch%02i"%chan, calibration,\
                  'instead of', calibration_db, 'Lasref=', Las_db))
        elif fixError and ('sE' in towerHash or ('EB' in towerHash and chan<2)) and fabs(calibration_db-1.0)<0.00001:
            calibration=1.5 # overwrite calibration for crack scin, if it was 1.0 in DB
            print(('writing default for', towerHash, "ch%02i"%chan, calibration,\
                  'instead of', calibration_db, 'Lasref=', Las_db))
        elif writeDefault:
            # set different defaults for different samplings
            calibration=1.0
            if 'sD' in towerHash and not 't10' in towerHash and not 't12' in towerHash:
                calibration=1.2
            if 'sBC' in towerHash and 't09' in towerHash :
                calibration=1.2
                #if ((mod>=39 and mod<=42) or (mod>=55 and mod<=58)):
                #    calibration=2.4 # special C10 with single PMT readout
            if 'sE' in towerHash or ('EB' in towerHash and chan<2):
                calibration=1.5
            print(('writing default for', towerHash, "ch%02i"%chan, calibration, 'Lasref=', Las_db, HV_db))
        else:
            print(('keeping old value for', towerHash, "ch%02i"%chan, calibration, 'Lasref=', Las_db, HV_db))

        for gn in [0,1]:
            drawer.setData(int(chan), int(gn), 0, calibration)
            if (HV<0.0):
                drawer.setData(int(chan), int(gn), 2, drawer_P.getData(chan, gn, 2))
            else:
                drawer.setData(int(chan), int(gn), 2, HV)
            drawer.setData(int(chan), int(gn), 3, drawer_P.getData(chan, gn, 3))

            if writeLASER:
                drawer.setData(int(chan), int(gn), 1, drawer_R.getData(chan, gn, 1))


