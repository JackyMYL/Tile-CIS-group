# October 18th 2011: Creation based on ReadDb.py
# Author: Henric
#
# Henric is the author of this code. Do not modify unless explicit
# agreement of the author
#
#
# Edition:
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

class ReadCalFromCool(ReadGenericCalibration):
    "Read database calibration constants from COOL"

    ## the default value of this tag is left hardcoded for now so this upgrade
    ## does not break for other systems who haven't implemented the leaf tag code
    ## however this is temporary, and non-CIS systems should update the code to implement
    ## the leaf tagging. See the CIS parts of this code for examples.

    def __init__(self, runType='CIS', schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                 folder='/TILE/OFL02/CALIB/CIS/LIN', tag = 'UPD4', runNumber=1000000000,
                 verbose=False):
        self.runType   = runType
        self.schema    = schema
        self.folder    = folder
        self.tag       = tag
        self.runNumber = runNumber
        self.verbose   = verbose

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

        try:
            self.dbConstants = TileCalibTools.openDbConn(self.schema, 'READONLY')
        except Exception as e:
            print("ReadCalFromCOOL: Failed to open a database connection, this can be an AFS token issue")
            print(e)
            sys.exit(-1)

        try:
            tag = TileCalibTools.getFolderTag(self.dbConstants, self.folder, self.tag)
        except Exception as e:
            print(("ReadCalFromCOOL: Failed to resolve tag %s for folder %s" % (self.tag,self.folder)))
            print(e)
            sys.exit(-1)

        print(("Creating Blob reader for %s\n folder: %s\n tag:  %s\n" % (self.schema, self.folder, tag)))
        self.blobReader = TileCalibTools.TileBlobReader(self.dbConstants, self.folder, tag)


    def ProcessStop(self):

        if self.dbConstants:
            self.dbConstants.closeDatabase()


    def ProcessRegion(self, region):
        messageprinted = False
        if len(region.GetNumber()) == 4:    # This is an ADC
            [ros, module, channel, gain] = region.GetNumber()
        elif len(region.GetNumber()) == 3:  # This is a channel
            [ros, module, channel] = region.GetNumber()
            gain=0                          # Cesium stores DB stuff in gain 0
        else:
            return                          # We only get conditions for channels and ADCs
        drawer = module-1

        cis_calib = []

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
#            el

            if self.runNumber == 1000000000:
                runNumber = event.run.runNumber
            else:
                runNumber = self.runNumber

            try:
                oldDrawer = self.blobReader.getDrawer(ros, drawer, (runNumber, 0))  # DB module numbers start from 0
            except:
                print(('No DB info !!! for run ', runNumber))
                continue
            if not oldDrawer:
                continue

            if self.folder == '/TILE/OFL02/CALIB/CIS/LIN' or self.folder == '/TILE/OFL02/CALIB/CIS/LIN':
                event.data['f_cis_db']     = oldDrawer.getData(channel, gain, 0)

            elif self.folder == '/TILE/OFL02/CALIB/CES':
                if self.runType == 'cesium':
                    event.data['f_cesium_db']  = oldDrawer.getData(channel, gain, 0)

                if self.runType == 'Las_REF':
                    event.data['lasref_db']    = oldDrawer.getData(channel, gain, 1)
                    if 'gain_Pisa' in event.data:
                        try:
                            event.data['gain_Pisaref_db'] = oldDrawer.getData(channel, gain, 4)
                        except:
                            pass
                    if 'pmt_ratio' in event.data:
                        try:
                            event.data['pmt_ratioref'] = oldDrawer.getData(channel, gain, 5)
                        except:
                            pass
                    if 'kappa' in event.run.data:
                        try:
                            event.run.data['kappa_db'] = oldDrawer.getData(channel, gain, 6)
                            #print 'kappa_DB: ', event.run.data['kappa_db'], event.run.runNumber
                        except:
                            pass


                event.data['hv_db']        = oldDrawer.getData(channel, gain, 2)
                # event.data['temp_db']      = oldDrawer.getData(channel, gain, 3)
                #event.data['Pisa_REF']     = oldDrawer.getData(channel, gain, 4)

            elif self.folder == '/TILE/OFL02/CALIB/EMS':
                event.data['f_emscale_db'] = oldDrawer.getData(channel, gain, 0)

            elif self.folder == '/TILE/OFL02/CALIB/LAS/LIN':
                try:
                    event.data['f_laser_db']   = oldDrawer.getData(channel, gain, 0)
                except:
                    print(("Problem reading f_laser_db for region ", region.GetHash(), " run ",event.run.runNumber))

            elif self.folder == '/TILE/OFL02/INTEGRATOR':
                #   3rd gain (2 because counting from 0) 28.85 - our mean value
                event.data['f_integrator_db'] = oldDrawer.getData(channel, 2, 0)/28.85

            elif self.folder == '/TILE/OFL02/CALIB/LAS/FIBER':
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
                        print((str(region.GetHash())+"does not have key 'DB Deviation', setting to 'False'"))
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
                        if 'problems' in event.data:  # Okay this is somehow known
                            #print '!! Run '+str(event.run.runNumber)+\
                            #      ' : No reference for: '+\
                            #      event.region.GetHash() +' '+str(event.data["problems"])
                            pass
                        else:
                            if not  messageprinted:
                                print(('!! Run '+str(event.run.runNumber)+
                                    ' : No reference for: '+\
                                    event.region.GetHash() + ', but no known problem'))
                                messageprinted = True
                else:

                    event.data['deviation'] = 100. * (event.data['calibration']-event.data['lasref_db']) \
                                              / (event.data['lasref_db'])
                    event.data['deverr'] = 100. * event.data['caliberror']/event.data['lasref_db']


                if 'gain_Pisa' in event.data and 'gain_Pisaref_db' in event.data:
                    event.data['Pisa_deviation'] = 100. * ( event.data['gain_Pisa'] -
                                                            event.data['gain_Pisaref_db']) / event.data['gain_Pisaref_db']
                    event.data['Pisa_deverr'] = 100. * ( event.data['gainerror_Pisa'] /
                                                        event.data['gain_Pisaref_db'] )
                #if event.run.data.has_key('kappa') and event.run.data.has_key('kappa_db'):
                #    print 'Kappa: ', event.run.data['kappa'], ' kappa_db: ', event.run.data['kappa_db']
                    #event.run.data['kappa_deviation'] = 100* (event.run.data['kappa']/event.run.data['kappa_db'] -1.)
                    #print "kappa deviation: ", event.run.data['kappa_deviation']

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
            mean = ROOT.TMath.Mean(len(cis_calib), array('f', cis_calib))
            rms  = ROOT.TMath.RMS(len(cis_calib), array('f', cis_calib))
            if rms/mean*100 > 0.389059:
                try:
                    event.data['CIS_problems']['Unstable'] = True
                except:
                    print("EVENT DICTIONARY NOT BUILT YET. CHECK AGAIN LATER FOR UNSTABLE CIS CHANNELS.")
            else:
                try:
                    event.data['CIS_problems']['Unstable'] = False
                except:
                    print("EVENT DICTIONARY NOT BUILT YET. CHECK AGAIN LATER FOR UNSTABLE CIS CHANNELS.")
