# October 18th 2011: Creation based on ReadDb.py
# Andrey Kamenshchikov, 23-10-2013 (akamensh@cern.ch)
################################################################

from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *

# For reading from DB
from TileCalibBlobPython import TileCalibTools
from TileCalibBlobObjs.Classes import *

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger

#file = open(os.path.join(getResultDirectory(),"RCFCdebug.txt"),"wb")

class ReadCalibFromCool(ReadGenericCalibration):
    '''
    Read database calibration constants from COOL
    '''

    ## the default value of this tag is left hardcoded for now so this upgrade
    ## does not break for other systems who haven't implemented the leaf tag code
    ## however this is temporary, and non-CIS systems should update the code to implement
    ## the leaf tagging. See the CIS parts of this code for examples.

    def __init__(self, runType='CIS',
                 folder='CALIB/CIS', tag = 'UPD1', schema = 'OFL', runNumber=1000000000, data = 'DATA',
                 meandev_threshold = 0.005, verbose=False):
        self.runType   = runType
        self.data      = data
        self.folder    = folder
        self.tag       = tag
        self.schema    = schema
        self.runNumber = runNumber
        #self.data      = data
        self.verbose   = verbose
        self.meandev_threshold = float(meandev_threshold) #for 'Mean Deviation' CIS TUCS flag
	
        if schema!='ONL' and schema!='OFL' and schema!='ONLINE' and schema!='OFFLINE' \
           and 'COOLO' not in schema and ':' not in schema and ';' not in schema:
            dbname = 'CONDBR2' if data == 'DATA' else 'OFLP200'
            self.schema='sqlite://;schema='+schema+';dbname='+dbname

        if "sqlite" in schema:
            splitname=schema.split("=")
            if not "/" in splitname[1]: 
                splitname[1]=os.path.join(getResultDirectory(), splitname[1])
                self.schema="=".join(splitname)

        if self.verbose:
            getLogger("ReadCalFromCool").setLevel(logging.DEBUG)
            getLogger("TileCalibTools").setLevel(logging.DEBUG)
        else:
            getLogger("ReadCalFromCool").setLevel(logging.ERROR)
            getLogger("TileCalibTools").setLevel(logging.ERROR)


    def ProcessStart(self):
        # Turn off the damn TileCalibTools startup prompt. grr.
        #getLogger("TileCalibTools").setLevel(logging.ERROR)

        ######
        ### Open up a DB connection
        ######
        self.r1 = False
        self.r2 = False
        if self.runNumber!=1000000000:
            if int(self.runNumber) > 232000:
                self.r2 = True
            else:
                self.r1 = True
        else:
            for run in Use_run_list:
                if int(run) > 232000:
                    self.r2 = True
                else:
                    self.r1 = True

        own_schema = False
        linepath = 'OFL02'
        if self.schema == 'OFFLINE' or self.schema == 'OFL':
            linepath = 'OFL02'
            schemepath = 'COOLOFL'
        elif self.schema == 'ONLINE' or self.schema == 'ONL':
            linepath = 'ONL01'
            schemepath = 'COOLONL'
        elif ".db" in self.schema or "sqlite" in self.schema or 'oracle' in self.schema:
            own_schema = True	
            print(("ReadCalibFromCool: reading SQL file %s" % self.schema))
            self.schema_r1 = self.schema
            self.schema_r2 = self.schema
        else:
            own_schema = True	
            print(("Warning: using an unorthodox schema %s" % self.schema))
            self.schema_r1 = self.schema
            self.schema_r2 = self.schema

        own_folder = False       
        if self.folder.startswith('/TILE'):
            self.folder_r1 = self.folder
            self.folder_r2 = self.folder
            own_folder = True
            print(("ReadCalibFromCool: using full folder path %s" % self.folder))
            print("WARNING: Be aware than some folder names are different in r1 and r2 databases")

        if not own_folder:
            if self.folder == 'CALIB/CIS':
                if linepath == 'ONL01':
                    self.folder_r1 = '/TILE/%s/CALIB/CIS/LIN' % linepath
                else:
                    self.folder_r1 = '/TILE/%s/CALIB/CIS/FIT/LIN' % linepath
                self.folder_r2 = '/TILE/%s/CALIB/CIS/LIN' % linepath
            elif self.folder == 'CALIB/LAS':
                self.folder_r1 = '/TILE/%s/CALIB/LAS/LIN' % linepath
                self.folder_r2 = '/TILE/%s/CALIB/LAS/LIN' % linepath
            elif self.folder == 'CALIB/CES':
                self.folder_r1 = '/TILE/%s/CALIB/CES' % linepath
                self.folder_r2 = '/TILE/%s/CALIB/CES' % linepath
            elif self.folder == 'CALIB/EMS':
                self.folder_r1 = '/TILE/%s/CALIB/EMS' % linepath
                self.folder_r2 = '/TILE/%s/CALIB/EMS' % linepath
            elif self.folder == 'INTEGRATOR':
                self.folder_r1 = '/TILE/%s/INTEGRATOR' % linepath
                self.folder_r2 = '/TILE/%s/INTEGRATOR' % linepath
            elif self.folder == 'CALIB/LAS/FIBER':
                self.folder_r2 = '/TILE/%s/CALIB/LAS/FIBER' % linepath
                self.folder_r1 = '/TILE/%s/CALIB/LAS/FIBER' % linepath
            else:
                self.folder_r1 = self.folder
                self.folder_r2 = self.folder

        if self.r2 and not self.data == 'MC':
            if not own_schema: 
                self.schema_r2 = '%s_TILE/CONDBR2' % schemepath

            try:
                self.dbConstants_r2 = TileCalibTools.openDbConn(self.schema_r2, 'READONLY')
            except Exception as e:
                print("ReadCalFromCOOL: Failed to open a database connection, this can be an AFS token issue")
                print(e)
                sys.exit(-1)

            tag_r2 = TileCalibTools.getFolderTag(self.dbConstants_r2, self.folder_r2, self.tag)

            print("Creating RUN 2 Blob reader for\n schema: %s\n folder: %s\n tag:  %s" % (self.schema_r2, self.folder_r2, tag_r2))
            self.blobReader_r2 = TileCalibTools.TileBlobReader(self.dbConstants_r2, self.folder_r2, tag_r2)

 
        if self.r1 or self.data == 'MC':
            if not own_schema:
                if self.data == 'DATA':
                    self.schema_r1 = '%s_TILE/COMP200' % schemepath	
                elif self.data == 'MC':
                    self.schema_r1 = '%s_TILE/OFLP200' % schemepath 

            try:
                self.dbConstants_r1 = TileCalibTools.openDbConn(self.schema_r1, 'READONLY')
            except Exception as e:
                print("ReadCalFromCOOL: Failed to open a database connection, this can be an AFS token issue")
                print(e)
                sys.exit(-1)
 
            tag_r1 = TileCalibTools.getFolderTag(self.schema_r1, self.folder_r1, self.tag)
            print("Creating RUN 1 Blob reader for\n schema: %s\n folder: %s\n tag:  %s" % (self.schema_r1, self.folder_r1, tag_r1))
            self.blobReader_r1 = TileCalibTools.TileBlobReader(self.dbConstants_r1, self.folder_r1, tag_r1)

        if self.runNumber!=1000000000:
            print('Using run:',  self.runNumber)


    def ProcessStop(self):

        if self.r2 and not self.data == 'MC':
            self.dbConstants_r2.closeDatabase()
        if self.r1:
            self.dbConstants_r1.closeDatabase()
        print(" ")


    def ProcessRegion(self, region):

        if len(region.GetNumber()) == 4:    # This is an ADC
            [ros, module, channel, gain] = region.GetNumber()
        elif len(region.GetNumber()) == 3:  # This is a channel
            [ros, module, channel] = region.GetNumber()
            gain=0                          # Cesium stores DB stuff in gain 0
        else:
            return                          # We only get conditions for channels and ADCs
        drawer = module-1
        
        cis_calib = []
        cis_calib_all = []

        for event in sorted(region.GetEvents(), key=lambda event: event.run.runNumber):
            if 'calibration' not in event.data:
                continue
            # start with all the selections, not to do DB accesses for nothing
#            if self.runType == 'CIS':
#                if not event.run.runType in ['CIS','all']:
#                    continue
            if self.runType == 'Las_REF':
                if event.run.runType != 'Las':
                    continue
#            elif self.runType == 'LasFibre':
#                if event.run.runType != 'Las':
#                    continue
#            elif self.runType == 'cesium':
#                if event.run.runType != 'cesium':
#                    continue
                
            if self.runNumber == 1000000000:
                runNumber = event.run.runNumber
            else:
                runNumber = self.runNumber

            if int(runNumber) > 232000 and not self.data == 'MC':
		
                try:
                    oldDrawer = self.blobReader_r2.getDrawer(ros, drawer, (runNumber, 0))  # DB module numbers start from 0
                except:
                   print('No DB info !!! for run ', runNumber)
                   continue
                if not oldDrawer:
                    continue


            else:
                try:
                    oldDrawer = self.blobReader_r1.getDrawer(ros, drawer, (runNumber, 0))  # DB module numbers start from 0
                except:
                   print('No DB info !!! for run ', runNumber)
                   continue
                if not oldDrawer:
                    continue



            if self.folder == 'CALIB/CIS' or self.runType == 'CIS':
                event.data['f_cis_db']     = oldDrawer.getData(channel, gain, 0)

            elif 'CES' in self.folder or self.runType == 'cesium' or self.runType == 'CES':
                if self.runType == 'cesium':
                    event.data['f_cesium_db']  = oldDrawer.getData(channel, gain, 0)

                if self.runType == 'Las_REF':
                    event.data['lasref_db']    = oldDrawer.getData(channel, gain, 1)
                    if 'gain_Pisa' in event.data:
                        event.data['gain_Pisaref_db']    = oldDrawer.getData(channel, gain, 4)

                event.data['hv_db']        = oldDrawer.getData(channel, gain, 2)
                # event.data['temp_db']      = oldDrawer.getData(channel, gain, 3)
                #event.data['Pisa_REF']     = oldDrawer.getData(channel, gain, 4)

            elif self.folder == 'CALIB/EMS' or self.runType == 'EMS':
                event.data['f_emscale_db'] = oldDrawer.getData(channel, gain, 0)

            elif self.folder == 'LAS/LIN' or self.runType == 'Las_LIN':
                event.data['f_laser_db']   = oldDrawer.getData(channel, gain, 0)

            elif self.folder == 'INTEGRATOR' or self.runType == 'integrator':
                #   3rd gain (2 because counting from 0) 28.85 - our mean value
                event.data['f_integrator_db'] = oldDrawer.getData(channel, 2, 0)/28.85

            elif self.folder == 'LAS/FIBER' or self.runType == 'Las_FIBER':
                if 'part_var_db' not in event.run.data:
                    event.run.data['part_var_db'] = 100*(oldDrawer_P.getData(LASPARTCHAN, gain, 0)-1)
                event.data['fib_var_db']   = 100*(oldDrawer.getData(channel, gain, 0)-1)

            if self.runType == 'CIS':
                # CIS values from DB
                if event.run.runType in ['CIS','all']:
                    event.data['deviation'] =  (event.data['calibration'] - event.data['f_cis_db'])/event.data['f_cis_db']

                    if event.data['CIS_problems']['Fail Likely Calib.'] == False:
                        cis_calib.append(event.data['calibration'])

                    if 'CIS_problems' not in event.data:
                        event.data['CIS_problems'] = {}

                    if event.data['deviation'] and event.data['CIS_problems']:
                        if math.fabs(event.data['deviation']) > 0.01:
                            event.data['CIS_problems']['DB Deviation'] = True
                        else:
                            event.data['CIS_problems']['DB Deviation'] = False

                    if not event.data['deviation']:
                        print(str(region.GetHash())+"does not have key 'DB Deviation', setting to 'False'")
                        event.data['CIS_problems']['DB Deviation'] = False


                if event.run.runType == 'CIS':
                    # Check for default calibration
                    if 'high' in region.GetHash() and\
                           abs((event.data['f_cis_db'] - 81.3669967651)) < 0.00000001:
                        event.data['CIS_problems']['Default Calibration'] = True
                    elif 'low' in region.GetHash() and\
                             abs((event.data['f_cis_db'] - 1.29400002956)) < 0.00000001:
                        event.data['CIS_problems']['Default Calibration'] = True
                    else:
                        event.data['CIS_problems']['Default Calibration'] = False


            elif self.runType == 'Las_REF' and event.run.runType == 'Las':
                if event.data['lasref_db'] <= 0:
                    if self.verbose:
                        if 'problems' in event.data:
                            # Okay this is somehow known
                            #print '!! Run '+str(event.run.runNumber)+\
                            #      ' : No reference for: '+\
                            #      event.region.GetHash() +' '+str(event.data["problems"])
                            pass
                        else:
                            print('!! Run '+str(event.run.runNumber)+\
                                  ' : No reference for: '+\
                                  event.region.GetHash() + ', but no known problem')
                else:
                    event.data['deviation'] = 100. * (event.data['calibration']-event.data['lasref_db']) \
                                              / (event.data['lasref_db'])
                    event.data['deverr'] = 100. * event.data['caliberror']/event.data['lasref_db']

                if 'gain_Pisa' in event.data:
                    event.data['Pisa_deviation'] = 100. * ( event.data['gain_Pisa'] -
                                                            event.data['gain_Pisaref_db']) / event.data['gain_Pisaref_db']
                    event.data['Pisa_deverr'] = 100. * ( event.data['gainerror_Pisa'] /
                                                        event.data['gain_Pisaref_db'] )
                    

            elif self.runType == 'integrator':
                if event.run.runType!='cesium':
                    continue
                event.data['integrator'] = oldDrawer.getData(channel, 2, 0)/28.85 # 3rd gain (2 because counting from 0) 28.85 - our mean value

            elif self.runType == 'cesium':
                #get HV and calibration
                event.data['calibration_db'] = oldDrawer.getData(channel, gain, 0)
                event.data['Las_db']  = oldDrawer.getData(channel, gain, 1)
                event.data['HV_db']   = oldDrawer.getData(channel, gain, 2)
                event.data['temp_db'] = oldDrawer.getData(channel, gain, 3)
                #print oldDrawer.getData(z, w, 0)


                        #print event.data['gain_Pisa'], event.data['gain_Pisaref_db'], event.data['Pisa_deviation'], event.data['Pisa_deverr']

#            if self.runType == 'LasFibre' and event.run.runType == 'Las':
#                #   Laser Fiber and partition corrections from DB
#                event.data['fib_var_db']  = 100*(oldDrawer.getData(channel, gain, 0)-1)           # fiber variation
#                try:
#                    oldDrawer_P = self.blobReader.getDrawer(ros, 0, (runNumber, 0))
#                except:
#                    print 'No DB info !!!'
#                    continue
#                if not oldDrawer_P:
#                    continue
#                event.run.data['part_var_db'] = 100*(oldDrawer_P.getData(LASPARTCHAN, gain, 0)-1)       # partition variation

        # Mark unstable CIS channels
        if len(cis_calib) > 0:
            unstable = False
            mean = ROOT.TMath.Mean(len(cis_calib), array('f', cis_calib))
            rms  = ROOT.TMath.RMS(len(cis_calib), array('f', cis_calib))

            if rms/mean*100 > 0.389059:
                unstable = True
            for event in region.GetEvents():
                try:
                    event.data['CIS_problems']['Unstable'] = unstable
                except:
                    #print("EVENT DICTIONARY NOT BUILT YET. CHECK AGAIN LATER FOR UNSTABLE CIS CHANNELS...")
                    print("")
                if 'calibration' not in event.data:
                    continue

                if abs((event.data['calibration'] - mean) / mean) > self.meandev_threshold:
                    try:
                        event.data['CIS_problems']['Mean Deviation'] = True
                    except:
                        print("EVENT DICTIONARY NOT BUILT YET. CHECK AGAIN LATER FOR DEVIATING CIS CHANNELS....")
                else:
                    try: 
                        event.data['CIS_problems']['Mean Deviation'] = False
                    except:
                        print("EVENT DICTIONARY NOT BUILT YET. CHECK AGAIN LATER FOR DEVIATING CIS CHANNELS.....") 
