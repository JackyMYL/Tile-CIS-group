# Author: Henric
#
# For DB constants
#
# End October 2013
#
# Henric is the author of this code. Do not modify unless explicit 
# agreement of the author
#

from src.ReadGenericCalibration import *
from src.oscalls import *
#from decimal import getcontext, Decimal

# For reading from DB
from TileCalibBlobPython import TileCalibTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK, LASPARTCHAN
from TileCalibBlobObjs.Classes import *

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger


class WriteDBNew(ReadGenericCalibration):

    "writeout database constants"

    def __init__( self , input_schema = None,
                  output_schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2', 
                  folder='/TILE/OFL02/CALIB/CIS/LIN',
                  tag='CURRENT',
                  writeHV=False,
                  iov=(0,0),
                  HV_datakey='HV',
                  Pisa_meankey = 'gain_Pisa',
                  useHighGain=False,
                  HVScale=False,
                  runNumber=-1,
                  average_ref = False,
                  average_const = False,
                  setMBTShvZero=True):

        self.input_schema  = input_schema
        self.output_schema  = output_schema
        self.folder  = folder
        self.tag = tag
        self.writeHV = writeHV
        self.HV_datakey  = HV_datakey
        self.useHighGain = useHighGain
        self.Pisa_meankey  = Pisa_meankey
        self.average_ref   = average_ref
        self.average_const = average_const
        self.HVScale = HVScale
        self.runNumber = runNumber
        self.setMBTShvZero = setMBTShvZero
        
        if iov==(0,0):
            self.latestRun = TileCalibTools.getLastRunNumber()
            self.iov     = (self.latestRun,0)
        else:
            self.iov     = iov


    def ProcessStart(self):
        if self.input_schema!=None:
            self.input_db = TileCalibTools.openDbConn(self.input_schema,'READONLY')
            tag = TileCalibTools.getFolderTag(self.input_db, self.folder, self.tag)
            self.blobReader = TileCalibTools.TileBlobReader(self.input_db, self.folder, tag)
            print("Creating Blob reader for %s\n folder: %s\n tag:  %s\n" % (self.input_schema, self.folder, tag))
        else:
            self.input_db = None
            self.blobReader = None
            
        self.output_db = TileCalibTools.openDbConn(self.output_schema,'UPDATE')
        self.blobWriter = TileCalibTools.TileBlobWriter(self.output_db,self.folder, 'Flt')
        print("Creating Blob writer for %s\n folder: %s\n" % (self.output_schema, self.folder))
        

    def ProcessRegion(self, region):

        numbers = region.GetNumber()
        
        if len(numbers)!=4: # Here we have an ADC
            return
        part, mod, chan, gain = numbers

        isMBTS = False
        if region.GetCellName() in ['E5', 'E6']:
            isMBTS=True
            
        drawer = mod-1

        parent_drawer = region.GetParent().GetParent()

        if 'drawerBlob' not in parent_drawer.data:  # Create a drawer BLob for writing 
            writerDrawerBlob = self.blobWriter.getDrawer(part, drawer)
            if writerDrawerBlob is not None:
                parent_drawer.data['drawerBlob'] = writerDrawerBlob
                self.InitTileCalibDrawerFlt(writerDrawerBlob)
            else:
                print("Db query for part %2d drawer %2d didn't return valid TileCalibDrawerFlt"%(part,drawer))
                # Here we should retrieve the previous blob from db 

            if self.blobReader!=None:           # We got an existing entry, we copy it
                readerDrawerBlob = self.blobReader.getDrawer(part, drawer, self.iov)
                if readerDrawerBlob is not None:  
                    self.CopyTileCalibDrawerFlt(readerDrawerBlob, writerDrawerBlob)
                            
                            
        if self.folder.find('CALIB/CIS/LIN')!=-1:         # This is the CIS folder
            for event in region.GetEvents():  
                if event.run.runType!='CIS': # We are not going to write non CIS data in the CIS folder
                    if 'mean' in event.data:
                        CIS_constant = event.data['mean']                        
                        parent_drawer.data['drawerBlob'].setData(chan, gain, 0, float(CIS_constant))


        elif self.folder.find('CALIB/LAS/LIN')!=-1:  # This is the LAS folder
            if isMBTS:
                return

            # Average laser constant
            if self.average_const:
                if 'f_laser' in region.data:

                    try:
                        LAS_constant = float(1./region.data['f_laser'])
                            #print region.GetHash(), LAS_constant 
       
                        if (self.useHighGain and gain==1):
                            parent_drawer.data['drawerBlob'].setData(chan, 0, 0, float(LAS_constant))
                            parent_drawer.data['drawerBlob'].setData(chan, 1, 0, float(LAS_constant))
                        elif (gain==0):
                            parent_drawer.data['drawerBlob'].setData(chan, 1, 0, float(LAS_constant))
                            parent_drawer.data['drawerBlob'].setData(chan, 0, 0, float(LAS_constant))

                        if self.HV_datakey in region.data and self.writeHV:
                            parent_drawer.data['drawerBlob'].setData(chan, 0, 1, float(region.data[self.HV_datakey]))
                            parent_drawer.data['drawerBlob'].setData(chan, 1, 1, float(region.data[self.HV_datakey]))
                    except:
                                print("Laser constant = 0", region.GetHash())
                                pass

            # Laser constant at fixed run
            else:
                for event in region.GetEvents():
                    if event.run.runType=='Las': # We are not going to write LAS data in the LAS folder

                        if event.run.runNumber!=self.runNumber:
                            continue
                    
                        if 'f_laser' in event.data:
                            try:
                                LAS_constant = float(1./event.data['f_laser'])
                                #print region.GetHash(), LAS_constant 
                                
                                if (self.useHighGain and gain==1):
                                    parent_drawer.data['drawerBlob'].setData(chan, 0, 0, float(LAS_constant))
                                    parent_drawer.data['drawerBlob'].setData(chan, 1, 0, float(LAS_constant))
                                elif (gain==0):
                                    parent_drawer.data['drawerBlob'].setData(chan, 1, 0, float(LAS_constant))
                                    parent_drawer.data['drawerBlob'].setData(chan, 0, 0, float(LAS_constant))

                                if self.HV_datakey in event.data and self.writeHV:
                                    parent_drawer.data['drawerBlob'].setData(chan, 0, 1, float(event.data[self.HV_datakey]))
                                    parent_drawer.data['drawerBlob'].setData(chan, 1, 1, float(event.data[self.HV_datakey]))

                            except:
                                print("Laser constant = 0", region.GetHash())
                                pass
                            
                    # if event.data.has_key('calibration'):
                    #     if (event.data['status']&0x10) or math.fabs(deltagain)>10.:
                    #         LAS_constant = 1./event.data['f_laser']
                    #     else:
                    #         LAS_constant = 1./event.data['f_laser']
                            
                    # if event.data.has_key('calibration') and event.data.has_key('f_laser'):                         
                    #     drawer_F = self.blobWriterOffline_F.getDrawer(part, drawer)                    
                    #     # Then we update if there is a new value (coefficients are in %, so we put in correct format)
                    #     # First update PMT variation
                    #     f_laser = float(1/event.data['f_laser'])

                    #     # Testing the special flags from Laser behvior study
                    #     #
                    #     pmt_region = str(region)
                    #     region_flag=''
                    #     for x in xrange(8,19):
                    #         region_flag+=pmt_region[x]

                    #     try:
                    #         Ch_flag = Chan_flag[region_flag][0]
                    #     except:
                    #         Ch_flag = "void"
                    #         print "Warning, no flag defined. All channels calibrated!"

                    #     drawer_R = self.blobReader.getDrawer(part, drawer, (self.latestRun, 0))
                    #     f_laser_previous = drawer_R.getData(chan, gain, 0)

                    #     # cases where no constant should applied or updated: put old one
                    #     #
                    #     if ( ((Ch_flag == "Bad_Chan") and (abs(1.0-f_laser)>0.15)) or (Ch_flag == "Fast Drift") \
                    #          or (Ch_flag == "Fiber") or (Ch_flag == "status_pb") or (Ch_flag == "DQ_pb") \
                    #          or (Ch_flag == "No laser") or (Ch_flag == "OK_pb")):
                    #         print 'WARNING, old constant kept for channel ', region.GetName(), ' old = ',\
                    #             f_laser_previous, ' new ignored = ',f_laser
                    #         f_laser = f_laser_previous

                    #         # special case: if no deviation and not calibrated before: constant set 1.0
                    #     if ((Ch_flag == "No_Dev") and (f_laser_previous == 1)):
                    #         f_laser = 1

                    #     LAS_constant = f_laser

                    #     print region.GetName(), " ", LAS_constant
                    #     if (self.useHighGain and gain==1):
                    #         parent_drawer.data['drawerBlob'].setData(chan, 0, 0, float(LAS_constant))
                    #         parent_drawer.data['drawerBlob'].setData(chan, 1, 0, float(LAS_constant))
                    #     else:
                    #         parent_drawer.data['drawerBlob'].setData(chan, 0, 0, float(LAS_constant))
                    #         parent_drawer.data['drawerBlob'].setData(chan, 1, 0, float(LAS_constant))

                            
                    # if event.data.has_key(self.HV_datakey) and self.WriteHV:
                    #     parent_drawer.data['drawerBlob'].setData(chan, gain, 1, float(event.data[self.HV_datakey]))
            

        elif self.folder.find('CALIB/LAS/FIBER')!=-1:  # This is the LAS fibre folder
            # This we may need to reinvent one day....
            pass


        elif self.folder.find('CALIB/CES')!=-1:                   # This is the cesium folder


            if self.average_ref:
                pisaref = -1.
                if 'gain_Pisa' in region.data and gain==1:    # Pisa for high gain only
                    
                    pisaref = region.data['gain_Pisa']
                    if pisaref==None:
                        pisaref = -1.
                    #parent_drawer.data['drawerBlob'].setData(chan, 0, 4, float(pisaref)) # use it for low gain
                    parent_drawer.data['drawerBlob'].setData(chan, 1, 4, float(pisaref)) # and for high gain
                    if pisaref<80000.:
                        print("writing %6d for %s" % (pisaref, region.GetHash()))

                lasref = -1.
                if 'calibration' in region.data:
                    lasref = region.data['calibration']
                    if lasref==None:
                        lasref=-1.
                    parent_drawer.data['drawerBlob'].setData(chan, gain, 1, float(lasref))            
            
            elif self.HVScale:
                for event in region.GetEvents():
                    lasref_old = parent_drawer.data['drawerBlob'].getData(chan, gain, 1)
                    gain_old =  parent_drawer.data['drawerBlob'].getData(chan, gain, 4)
                    hvold = parent_drawer.data['drawerBlob'].getData(chan, gain, 2)
                    beta = 6.9
                    if 'beta' in region.GetParent().data:
                        if region.GetParent().data['beta']>5:
                            beta = region.GetParent().data['beta']
                
                    hv = hvold
                    if self.HV_datakey in event.data:
                        hv = event.data[self.HV_datakey]
                    try:
                        scale_factor = pow(hv/hvold,beta)
                    except:
                        scale_factor = 1
                    lasref = lasref_old * scale_factor 
                    gain_new = gain_old * scale_factor 
                    parent_drawer.data['drawerBlob'].setData(chan, gain, 1, float(lasref))
                    parent_drawer.data['drawerBlob'].setData(chan, gain, 2, float(hv))
                    parent_drawer.data['drawerBlob'].setData(chan, gain, 4, float(gain_new))
                    kappa_ref = -1.
                    if 'kappa' in event.run.data:
                        kappa_ref = event.run.data['kappa']
                    parent_drawer.data['drawerBlob'].setData(chan, gain, 6, float(kappa_ref))
                        
            else:
                for event in region.GetEvents():
#                             
                    if event.run.runType=='Las':                                  #  We are not going to write LAS reference data in the CES folder
                        lasref_old = parent_drawer.data['drawerBlob'].getData(chan, gain, 1)
#                        if isMBTS:
#                            print(event)
                        
                        if 'calibration' in event.data:
                            LAS_reference = -1.                           
                            if event.data['is_OK']:
                                LAS_reference = event.data['calibration']              
                  
                            parent_drawer.data['drawerBlob'].setData(chan, gain, 1, float(LAS_reference))
                            #                                if LAS_reference<0.:
                            #                                    diff = -100.
                            #                                else:
                            #                                    diff = 100*(LAS_reference-lasref_old)/lasref_old
                            #                            print  "old: %6.3g  new: %6.3g \tvariantion %5.2f%% " % (lasref_old,LAS_reference,diff)
                            
                        if self.HV_datakey in event.data and self.writeHV:
                            hv = event.data[self.HV_datakey]
                            if isMBTS and self.setMBTShvZero:
                                hv=0.
                            parent_drawer.data['drawerBlob'].setData(chan, gain, 2, float(hv))

                        gain_pisa = -1.
                        if 'gain_Pisa' in event.data:
                            gain_pisa = event.data['gain_Pisa']                                
                        parent_drawer.data['drawerBlob'].setData(chan, gain, 4, float(gain_pisa))
                            
                        pmt_ratioref = -1.
                        if 'pmt_ratio' in event.data:
                            pmt_ratioref = event.data['pmt_ratio']
                        parent_drawer.data['drawerBlob'].setData(chan, gain, 5, float(pmt_ratioref))

                        kappa_ref= -1.
                        if 'kappa' in event.run.data:
                            kappa_ref = event.run.data['kappa']
                        parent_drawer.data['drawerBlob'].setData(chan, gain, 6, float(kappa_ref))

                    if event.run.runType=='cesium' and gain==0:                 # We are not going to write cesium reference data in the CES folder
                        if 'update_needed' in event.data and event.data['update_needed']:
                            if 'calibration' in event.data:
                                calibration = event.data['calibration']
                                    ##                                calibration_db = parent_drawer.data['drawerBlob'].getData(chan, 0, 0)
                                if calibration>0: # will update constant #akamensh
                                    ##                                    calibration = calibration_db
                                    parent_drawer.data['drawerBlob'].setData(int(chan), 0, 0, calibration)
                                    parent_drawer.data['drawerBlob'].setData(int(chan), 1, 0, calibration)
                            
                                if 'HV' in event.data and event.data['HV']>499.0:
                                    HV=event.data['HV']
                                    if HV>930.0:
                                        HV=0.0
                                    parent_drawer.data['drawerBlob'].setData(int(chan), 0, 2, HV)
                                    parent_drawer.data['drawerBlob'].setData(int(chan), 1, 2, HV)

                                if 'temp' in event.data and event.data['temp']>15.0 and event.data['temp']<35.0:
                                    T=event.data['temp']
                                    parent_drawer.data['drawerBlob'].setData(int(chan), 0, 3, T)
                                    parent_drawer.data['drawerBlob'].setData(int(chan), 1, 3, T)
                        else:
                            if self.HV_datakey in event.data and self.writeHV:                                        
                                parent_drawer.data['drawerBlob'].setData(chan, gain, 2, float(event.data[self.HV_datakey])) 


        elif self.folder.find('TIME/CHANNELOFFSET')!=-1:  # This is the timing folder
            for event in region.GetEvents():  
                if event.run.runType=='timing':
                    if 'timing' in event.data:
                        print("Timing for %i / %i / %i / %i == %f - Writing new value" % (part,mod,chan,gain,event.data['timing']))
                        parent_drawer.data['drawerBlob'].setData(int(chan), int(gain), 0, event.data['timing'])
        else:
            print("Unknonw Folder")
            exit


                    
    def ProcessStop(self):
        iovUntil = (MAXRUN,MAXLBK)
        author   = "%s" % os.getlogin()
        quote = lambda x: " ".join([y if len(y)>0 else repr('') for y in x])
        self.blobWriter.setComment(author, "TUCS %s" % (quote(sys.argv)))
        tag = TileCalibTools.getFolderTag(self.output_db, self.folder, self.tag)
        self.blobWriter.register(self.iov, iovUntil, tag)
        print("commiting to DB %s %d" % (tag, self.iov[0]))

        if self.input_db:
            self.input_db.closeDatabase()
        self.output_db.closeDatabase()


    #
    # Here we write default Cs values
    #

    def writeCsDef(self,region,drawer,chan,drawer_P,drawer_R,fixError,writeDefault,writeLASER):

        calibration_db = drawer_P.getData(chan, 0, 0)
        Las_db = str(drawer_R.getData(chan, 0, 1))+"/"+str(drawer_R.getData(chan, 1, 1))
        calibration=calibration_db
            
        tower=region.GetParent('physical').GetParent('physical')
        module=region.GetParent().GetParent()
        towerHash = tower.GetHash()
        if ('sD_t00' in towerHash) and ('LBC' in module.GetHash()):
            towerHash = towerHash.replace('LBA','LBC')

        if fixError and module.GetMBTStype()>0 and chan==0 and calibration_db>100.0:
            calibration=1./1.05  # overwrite calibration for MBTS
            print('writing default for MBTS ', towerHash, "ch%02i"%chan, calibration,\
                  'instead of', calibration_db, 'Lasref=', Las_db)
        elif fixError and ('sE' in towerHash or ('EB' in towerHash and chan<2)) and fabs(calibration_db-1.0)<0.00001:
            calibration=1.5 # overwrite calibration for crack scin, if it was 1.0 in DB
            print('writing default for', towerHash, "ch%02i"%chan, calibration,\
                  'instead of', calibration_db, 'Lasref=', Las_db)
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
            print('writing default for', towerHash, "ch%02i"%chan, calibration, 'Lasref=', Las_db)
        else:
            print('keeping old value for', towerHash, "ch%02i"%chan, calibration, 'Lasref=', Las_db)

        for gn in [0,1]:
            drawer.setData(int(chan), int(gn), 0, calibration)
            drawer.setData(int(chan), int(gn), 2, drawer_P.getData(chan, gn, 2))
            drawer.setData(int(chan), int(gn), 3, drawer_P.getData(chan, gn, 3))

            if writeLASER:
                drawer.setData(int(chan), int(gn), 1, drawer_R.getData(chan, gn, 1))


    def DefaultBlob(self,gain):

        blob = PyCintex.gbl.std.vector('float')()
        if self.folder.find('CALIB/CIS/LIN')!=-1:  # This is the CIS folder
            if gain==0: # low gain
                blob.push_back(1023./800.)
            else:  # high gain
                blob.push_back(64.*1023./800.)
        
        if self.folder.find('CALIB/LAS/LIN')!=-1:  # This is the LAS folder
            blob.push_back(1.)   # No laser calibration factor
            blob.push_back(-2.)  # Unvalid HV value
            
        if self.folder.find('CALIB/LAS/FIBER')!=-1:  # This is the LAS fibre folder
            pass

        if self.folder.find('CALIB/CES')!=-1:  # This is the cesium folder
            blob.push_back(  1.)  # No cesium calibration
            blob.push_back( -1.)  # Invalid laser reference
            blob.push_back(700.)  # Reference HV
            blob.push_back( 20.)  # Default temperature 
            blob.push_back( -1.)  # Invalid Pisa reference
            blob.puch_back( -1.)  # Invalid kappa value

        
        if self.folder.find('TIME/CHANNELOFFSET')!=-1:  # This is the timing folder
            blob.push_back(0.)  # No timming correction

        return blob


    def CopyTileCalibDrawerFlt(self,inputCalibDrawer, outputCalibDrawer):
        if inputCalibDrawer is not None and type(inputCalibDrawer)==type(outputCalibDrawer):
            for channel in range(48):
                for gain in [0,1]:
                    for i in range(inputCalibDrawer.getObjSizeUint32()):
                        value = inputCalibDrawer.getData( channel, gain, i)
                        outputCalibDrawer.setData( channel, gain, i, value) 


    def InitTileCalibDrawerFlt(self,outputCalibDrawer):

        if self.folder.find('TIME/CHANNELOFFSET/PHY')!=-1:
            default = PyCintex.gbl.std.vector('float')()
            default.push_back(0.)

            defaultvec = PyCintex.gbl.std.vector('std::vector<float>')()
            defaultvec.push_back(default)
            defaultvec.push_back(default)

            outputCalibDrawer.init(defaultvec, 48, 1)

        elif self.folder.find('CALIB/LAS/NLN')!=-1:
            # This is special and for the momment unused. 
            pass

        elif self.folder.find('CALIB/CIS/LIN')!=-1:
            loGainDef=(1023./800.)
            hiGainDef=(64.*loGainDef)
            loGainDefVec = PyCintex.gbl.std.vector('float')()
            hiGainDefVec = PyCintex.gbl.std.vector('float')()

            loGainDefVec.push_back(loGainDef)
            hiGainDefVec.push_back(hiGainDef)
            
            defaultvec = PyCintex.gbl.std.vector('std::vector<float>')()
            defaultvec.push_back(loGainDefVec)
            defaultvec.push_back(hiGainDefVec)

            outputCalibDrawer.init(defaultvec, 48, 1)

        elif self.folder.find('CALIB/LAS/LIN')!=-1:
            default = PyCintex.gbl.std.vector('float')()
            default.push_back(1.)
            default.push_back(-2.)
             
            defaultvec = PyCintex.gbl.std.vector('std::vector<float>')()
            defaultvec.push_back(default)
            defaultvec.push_back(default)

            outputCalibDrawer.init(defaultvec, 48, 1)

        elif self.folder.find('CALIB/LAS/FIBRE')!=-1:
            default = PyCintex.gbl.std.vector('float')()
            default.push_back(1.)
            default.push_back(0.)
             
            defaultvec = PyCintex.gbl.std.vector('std::vector<float>')()
            defaultvec.push_back(default)
            defaultvec.push_back(default)

            outputCalibDrawer.init(defaultvec, 48, 1)

        elif self.folder.find('CALIB/CES')!=-1:
            default = PyCintex.gbl.std.vector('float')()
            default.push_back(  1.) # cesium constant
            default.push_back( -1.) # laser default value
            default.push_back(700.) # reference HV
            default.push_back( 20.) # reference temperature (same for all channels)
            default.push_back( -1.) # reference Pisa value
            default.push_back( -1.) # reference pmt_ratio value
            default.push_back( -1.) # reference kappa
             
            defaultvec = PyCintex.gbl.std.vector('std::vector<float>')()
            defaultvec.push_back(default)
            defaultvec.push_back(default)

            try:
                outputCalibDrawer.init(defaultvec, 48, 1)
            except:
                print("Failure to init default output blob")
        else:
            print("Unknown Folder type")

