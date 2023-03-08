############################################################
#
# ReadLaser.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# July 08, 2009
#
# Goal:
# Get the Laser event and fill them with relevant info
#
# Input parameters are:
#
# -> processingDir: where to find the ROOTuple processed with TileLaserDefaultTool
#          DEFAULT VAL = '/afs/cern.ch/user/t/tilecali/w0/ntuples/las'
#
# -> diode_num: the diode you want to use in order to get the ratio
#          DEFAULT VAL = 0 : BUT OVERWRITTEN FOR THE MOMENT
#
# -> box_par: option which select only the box parameter
#          DEFAULT VAL = False
#
# **-> v2: Can also read the laser events in the empty bunch, stored as a high gain readout with lasFilter =2
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.ReadGenericCalibration import *
from src.run import *
import random
import time

# For using the LASER tools
from src.laser.toolbox import *
from src.stats import *

class ReadLaser_phyRuns(ReadGenericCalibration):
        "The Laser Calibration Data Reader"
        
        processingDir  = None
        numberEventCut = None


        def __init__(self, processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/las', diode_num=-1, box_par=False, doTime=False, doPisa=False, verbose=False):
                self.processingDir  = processingDir
                self.numberEventCut = 10
                
                self.diode          = diode_num
                self.box_par        = box_par
                self.PMTool         = LaserTools()
                self.run_dict       = {}
                self.run_list       = set()
                self.verbose        = verbose
                self.doPisa         = doPisa
                self.doTime         = doTime

                        
        def ProcessStart(self):
                # Prepare the list of runs <-> files
                #
                #global run_list
                for run in run_list.getRunsOfType('Las'):
                        print(run.runNumber)            
                                        
                        laserRun_Tuplename = "%s/tileCalibLAS_%s_Las.0.root" % (self.processingDir,run.runNumber)
                        physicsRun_Tuplename = "%s/tileCalibLAS_%s_Las.calibration_Tile.root" % (self.processingDir,run.runNumber)

                        if os.path.exists(laserRun_Tuplename):
                                run.data['filename'] = os.path.basename(laserRun_Tuplename)
                                self.run_list.add(run)
                                self.run_dict[run.runNumber] = []
                                print("filename =",laserRun_Tuplename)
                        elif os.path.exists(physicsRun_Tuplename):
                                run.data['filename'] = os.path.basename(physicsRun_Tuplename)
                                self.run_list.add(run)
                                self.run_dict[run.runNumber] = []
                                print("filename =",physicsRun_Tuplename)
                        else:
                                print('not processed yet, removing ',run.runNumber)
                                run_list.remove(run)


        def ProcessRegion(self, region):
                # Prepare event lists
                #
                for event in region.GetEvents():
                        if event.run.runType == 'Las' and 'filename' in event.run.data:
                                self.run_dict[event.run.runNumber].append(event)
                return

        def ProcessStop(self):
                # In the finalization loop we store the LASER relevant info
                # For each run we just open the tree once, otherwise it's awfully slow...
        
                for run in sorted(self.run_list, key=lambda run: run.runNumber):
                        f, t = self.getFileTree(run.data['filename'], 'h3000')
                        if [f, t] == [None, None]:
                                print('Failed for run ',run.runNumber)
                                continue
                        t.GetEntry(0)

                        run.data['wheelpos']       = t.wheelpos        # Filter wheel position
                        run.data['requamp']        = t.requamp         # Requested amplitude


                        if self.box_par: # Special case for laser box parameters following

                                # humidity was stored by LaserI system for some time
                                # kept here for backward compatibility
                                run.data['humid']     = 0
                                
                                if not self.isLaserII:
                                    run.data['PMT1']      = t.PMT_1
                                    run.data['PMT2']      = t.PMT_2

                                    run.data['Diode1']    = t.diode[0]
                                    run.data['Diode2']    = t.diode[1]
                                    run.data['Diode3']    = t.diode[2]
                                    run.data['Diode4']    = t.diode[3]
                                    
                                    run.data['Diode1_p']  = t.diode_Ped[0]
                                    run.data['Diode2_p']  = t.diode_Ped[1]
                                    run.data['Diode3_p']  = t.diode_Ped[2]
                                    run.data['Diode4_p']  = t.diode_Ped[3]
                                    
                                    run.data['Diode1_sp'] = t.diode_sPed[0]
                                    run.data['Diode2_sp'] = t.diode_sPed[1]
                                    run.data['Diode3_sp'] = t.diode_sPed[2]
                                    run.data['Diode4_sp'] = t.diode_sPed[3]
                                    
                                    run.data['Diode1_a']  = t.diode_Alpha[0]
                                    run.data['Diode2_a']  = t.diode_Alpha[1]
                                    run.data['Diode3_a']  = t.diode_Alpha[2]
                                    run.data['Diode4_a']  = t.diode_Alpha[3]
                                    
                                    run.data['Diode1_sa'] = t.diode_sAlpha[0]
                                    run.data['Diode2_sa'] = t.diode_sAlpha[1]
                                    run.data['Diode3_sa'] = t.diode_sAlpha[2]
                                    run.data['Diode4_sa'] = t.diode_sAlpha[3]
                                   
                                    if run.runNumber > 135000:
                                        run.data['humid']     = t.humid     # Relative humidity (in %)

                                if self.isLaserII:
                                    # signal values for monitoring diodes
                                    run.data['Diode0_LG_Signal']          = t.LG_Diode0_Signal
                                    run.data['Diode1_LG_Signal']          = t.LG_Diode1_Signal
                                    run.data['Diode2_LG_Signal']          = t.LG_Diode2_Signal
                                    run.data['Diode3_LG_Signal']          = t.LG_Diode3_Signal
                                    run.data['Diode4_LG_Signal']          = t.LG_Diode4_Signal
                                    run.data['Diode5_LG_Signal']          = t.LG_Diode5_Signal
                                    run.data['Diode6_LG_Signal']          = t.LG_Diode6_Signal
                                    run.data['Diode7_LG_Signal']          = t.LG_Diode7_Signal
                                    run.data['Diode8_LG_Signal']          = t.LG_Diode8_Signal
                                    run.data['Diode9_LG_Signal']          = t.LG_Diode9_Signal
                                    run.data['PMT1_LG_Signal']            = t.LG_Diode9_Signal
                                    run.data['PMT2_LG_Signal']            = t.LG_Diode9_Signal
                                    run.data['ExtCIS0_LG_Signal']         = t.LG_Diode9_Signal
                                    run.data['ExtCIS1_LG_Signal']         = t.LG_Diode9_Signal
                                    run.data['IntCIS_LG_Signal']          = t.LG_Diode9_Signal
                                    run.data['DiodePhocal_LG_Signal']     = t.LG_Diode9_Signal

                                    run.data['Diode0_HG_Signal']          = t.HG_Diode0_Signal
                                    run.data['Diode1_HG_Signal']          = t.HG_Diode1_Signal
                                    run.data['Diode2_HG_Signal']          = t.HG_Diode2_Signal
                                    run.data['Diode3_HG_Signal']          = t.HG_Diode3_Signal
                                    run.data['Diode4_HG_Signal']          = t.HG_Diode4_Signal
                                    run.data['Diode5_HG_Signal']          = t.HG_Diode5_Signal
                                    run.data['Diode6_HG_Signal']          = t.HG_Diode6_Signal
                                    run.data['Diode7_HG_Signal']          = t.HG_Diode7_Signal
                                    run.data['Diode8_HG_Signal']          = t.HG_Diode8_Signal
                                    run.data['Diode9_HG_Signal']          = t.HG_Diode9_Signal
                                    run.data['PMT1_HG_Signal']            = t.HG_Diode9_Signal
                                    run.data['PMT2_HG_Signal']            = t.HG_Diode9_Signal
                                    run.data['ExtCIS0_HG_Signal']         = t.HG_Diode9_Signal
                                    run.data['ExtCIS1_HG_Signal']         = t.HG_Diode9_Signal
                                    run.data['IntCIS_HG_Signal']          = t.HG_Diode9_Signal
                                    run.data['DiodePhocal_HG_Signal']     = t.HG_Diode9_Signal

                                    # sigma values for monitoring diodes
                                    run.data['Diode0_LG_Sigma']           = t.LG_Diode0_Sigma
                                    run.data['Diode1_LG_Sigma']           = t.LG_Diode1_Sigma
                                    run.data['Diode2_LG_Sigma']           = t.LG_Diode2_Sigma
                                    run.data['Diode3_LG_Sigma']           = t.LG_Diode3_Sigma
                                    run.data['Diode4_LG_Sigma']           = t.LG_Diode4_Sigma
                                    run.data['Diode5_LG_Sigma']           = t.LG_Diode5_Sigma
                                    run.data['Diode6_LG_Sigma']           = t.LG_Diode6_Sigma
                                    run.data['Diode7_LG_Sigma']           = t.LG_Diode7_Sigma
                                    run.data['Diode8_LG_Sigma']           = t.LG_Diode8_Sigma
                                    run.data['Diode9_LG_Sigma']           = t.LG_Diode9_Sigma
                                    run.data['PMT1_LG_Sigma']             = t.LG_Diode9_Sigma
                                    run.data['PMT2_LG_Sigma']             = t.LG_Diode9_Sigma
                                    run.data['ExtCIS0_LG_Sigma']          = t.LG_Diode9_Sigma
                                    run.data['ExtCIS1_LG_Sigma']          = t.LG_Diode9_Sigma
                                    run.data['IntCIS_LG_Sigma']           = t.LG_Diode9_Sigma
                                    run.data['DiodePhocal_LG_Sigma']      = t.LG_Diode9_Sigma

                                    run.data['Diode0_HG_Sigma']           = t.HG_Diode0_Sigma
                                    run.data['Diode1_HG_Sigma']           = t.HG_Diode1_Sigma
                                    run.data['Diode2_HG_Sigma']           = t.HG_Diode2_Sigma
                                    run.data['Diode3_HG_Sigma']           = t.HG_Diode3_Sigma
                                    run.data['Diode4_HG_Sigma']           = t.HG_Diode4_Sigma
                                    run.data['Diode5_HG_Sigma']           = t.HG_Diode5_Sigma
                                    run.data['Diode6_HG_Sigma']           = t.HG_Diode6_Sigma
                                    run.data['Diode7_HG_Sigma']           = t.HG_Diode7_Sigma
                                    run.data['Diode8_HG_Sigma']           = t.HG_Diode8_Sigma
                                    run.data['Diode9_HG_Sigma']           = t.HG_Diode9_Sigma
                                    run.data['PMT1_HG_Sigma']             = t.HG_Diode9_Sigma
                                    run.data['PMT2_HG_Sigma']             = t.HG_Diode9_Sigma
                                    run.data['ExtCIS0_HG_Sigma']          = t.HG_Diode9_Sigma
                                    run.data['ExtCIS1_HG_Sigma']          = t.HG_Diode9_Sigma
                                    run.data['IntCIS_HG_Sigma']           = t.HG_Diode9_Sigma
                                    run.data['DiodePhocal_HG_Sigma']      = t.HG_Diode9_Sigma

                                    # pedestal values for monitoring diodes
                                    run.data['Diode0_LG_Ped']            = t.LG_Diode0_Ped
                                    run.data['Diode1_LG_Ped']            = t.LG_Diode1_Ped
                                    run.data['Diode2_LG_Ped']            = t.LG_Diode2_Ped
                                    run.data['Diode3_LG_Ped']            = t.LG_Diode3_Ped
                                    run.data['Diode4_LG_Ped']            = t.LG_Diode4_Ped
                                    run.data['Diode5_LG_Ped']            = t.LG_Diode5_Ped
                                    run.data['Diode6_LG_Ped']            = t.LG_Diode6_Ped
                                    run.data['Diode7_LG_Ped']            = t.LG_Diode7_Ped
                                    run.data['Diode8_LG_Ped']            = t.LG_Diode8_Ped
                                    run.data['Diode9_LG_Ped']            = t.LG_Diode9_Ped
                                    run.data['PMT1_LG_Ped']              = t.LG_Diode9_Ped
                                    run.data['PMT2_LG_Ped']              = t.LG_Diode9_Ped
                                    run.data['ExtCIS0_LG_Ped']           = t.LG_Diode9_Ped
                                    run.data['ExtCIS1_LG_Ped']           = t.LG_Diode9_Ped
                                    run.data['IntCIS_LG_Ped']            = t.LG_Diode9_Ped
                                    run.data['DiodePhocal_LG_Ped']       = t.LG_Diode9_Ped

                                    run.data['Diode0_HG_Ped']            = t.HG_Diode0_Ped
                                    run.data['Diode1_HG_Ped']            = t.HG_Diode1_Ped
                                    run.data['Diode2_HG_Ped']            = t.HG_Diode2_Ped
                                    run.data['Diode3_HG_Ped']            = t.HG_Diode3_Ped
                                    run.data['Diode4_HG_Ped']            = t.HG_Diode4_Ped
                                    run.data['Diode5_HG_Ped']            = t.HG_Diode5_Ped
                                    run.data['Diode6_HG_Ped']            = t.HG_Diode6_Ped
                                    run.data['Diode7_HG_Ped']            = t.HG_Diode7_Ped
                                    run.data['Diode8_HG_Ped']            = t.HG_Diode8_Ped
                                    run.data['Diode9_HG_Ped']            = t.HG_Diode9_Ped
                                    run.data['PMT1_HG_Ped']              = t.HG_Diode9_Ped
                                    run.data['PMT2_HG_Ped']              = t.HG_Diode9_Ped
                                    run.data['ExtCIS0_HG_Ped']           = t.HG_Diode9_Ped
                                    run.data['ExtCIS1_HG_Ped']           = t.HG_Diode9_Ped
                                    run.data['IntCIS_HG_Ped']            = t.HG_Diode9_Ped
                                    run.data['DiodePhocal_HG_Ped']       = t.HG_Diode9_Ped

                                    # sigma of pedestal values for monitoring diodes
                                    run.data['Diode0_LG_Ped_Sigma']      = t.LG_Diode0_Ped_Sigma
                                    run.data['Diode1_LG_Ped_Sigma']      = t.LG_Diode1_Ped_Sigma
                                    run.data['Diode2_LG_Ped_Sigma']      = t.LG_Diode2_Ped_Sigma
                                    run.data['Diode3_LG_Ped_Sigma']      = t.LG_Diode3_Ped_Sigma
                                    run.data['Diode4_LG_Ped_Sigma']      = t.LG_Diode4_Ped_Sigma
                                    run.data['Diode5_LG_Ped_Sigma']      = t.LG_Diode5_Ped_Sigma
                                    run.data['Diode6_LG_Ped_Sigma']      = t.LG_Diode6_Ped_Sigma
                                    run.data['Diode7_LG_Ped_Sigma']      = t.LG_Diode7_Ped_Sigma
                                    run.data['Diode8_LG_Ped_Sigma']      = t.LG_Diode8_Ped_Sigma
                                    run.data['Diode9_LG_Ped_Sigma']      = t.LG_Diode9_Ped_Sigma
                                    run.data['PMT1_LG_Ped_Sigma']        = t.LG_Diode9_Ped_Sigma
                                    run.data['PMT2_LG_Ped_Sigma']        = t.LG_Diode9_Ped_Sigma
                                    run.data['ExtCIS0_LG_Ped_Sigma']     = t.LG_Diode9_Ped_Sigma
                                    run.data['ExtCIS1_LG_Ped_Sigma']     = t.LG_Diode9_Ped_Sigma
                                    run.data['IntCIS_LG_Ped_Sigma']      = t.LG_Diode9_Ped_Sigma
                                    run.data['DiodePhocal_LG_Ped_Sigma'] = t.LG_Diode9_Ped_Sigma

                                    run.data['Diode0_HG_Ped_Sigma']      = t.HG_Diode0_Ped_Sigma
                                    run.data['Diode1_HG_Ped_Sigma']      = t.HG_Diode1_Ped_Sigma
                                    run.data['Diode2_HG_Ped_Sigma']      = t.HG_Diode2_Ped_Sigma
                                    run.data['Diode3_HG_Ped_Sigma']      = t.HG_Diode3_Ped_Sigma
                                    run.data['Diode4_HG_Ped_Sigma']      = t.HG_Diode4_Ped_Sigma
                                    run.data['Diode5_HG_Ped_Sigma']      = t.HG_Diode5_Ped_Sigma
                                    run.data['Diode6_HG_Ped_Sigma']      = t.HG_Diode6_Ped_Sigma
                                    run.data['Diode7_HG_Ped_Sigma']      = t.HG_Diode7_Ped_Sigma
                                    run.data['Diode8_HG_Ped_Sigma']      = t.HG_Diode8_Ped_Sigma
                                    run.data['Diode9_HG_Ped_Sigma']      = t.HG_Diode9_Ped_Sigma
                                    run.data['PMT1_HG_Ped_Sigma']        = t.HG_Diode9_Ped_Sigma
                                    run.data['PMT2_HG_Ped_Sigma']        = t.HG_Diode9_Ped_Sigma
                                    run.data['ExtCIS0_HG_Ped_Sigma']     = t.HG_Diode9_Ped_Sigma
                                    run.data['ExtCIS1_HG_Ped_Sigma']     = t.HG_Diode9_Ped_Sigma
                                    run.data['IntCIS_HG_Ped_Sigma']      = t.HG_Diode9_Ped_Sigma
                                    run.data['DiodePhocal_HG_Ped_Sigma'] = t.HG_Diode9_Ped_Sigma

                                    # alpha run values for monitoring diodes
                                    run.data['Diode0_LG_Alpha']            = t.LG_Diode0_Alpha
                                    run.data['Diode1_LG_Alpha']            = t.LG_Diode1_Alpha
                                    run.data['Diode2_LG_Alpha']            = t.LG_Diode2_Alpha
                                    run.data['Diode3_LG_Alpha']            = t.LG_Diode3_Alpha
                                    run.data['Diode4_LG_Alpha']            = t.LG_Diode4_Alpha
                                    run.data['Diode5_LG_Alpha']            = t.LG_Diode5_Alpha
                                    run.data['Diode6_LG_Alpha']            = t.LG_Diode6_Alpha
                                    run.data['Diode7_LG_Alpha']            = t.LG_Diode7_Alpha
                                    run.data['Diode8_LG_Alpha']            = t.LG_Diode8_Alpha
                                    run.data['Diode9_LG_Alpha']            = t.LG_Diode9_Alpha
                                    run.data['PMT1_LG_Alpha']              = t.LG_Diode9_Alpha
                                    run.data['PMT2_LG_Alpha']              = t.LG_Diode9_Alpha
                                    run.data['ExtCIS0_LG_Alpha']           = t.LG_Diode9_Alpha
                                    run.data['ExtCIS1_LG_Alpha']           = t.LG_Diode9_Alpha
                                    run.data['IntCIS_LG_Alpha']            = t.LG_Diode9_Alpha
                                    run.data['DiodePhocal_LG_Alpha']       = t.LG_Diode9_Alpha

                                    run.data['Diode0_HG_Alpha']            = t.HG_Diode0_Alpha
                                    run.data['Diode1_HG_Alpha']            = t.HG_Diode1_Alpha
                                    run.data['Diode2_HG_Alpha']            = t.HG_Diode2_Alpha
                                    run.data['Diode3_HG_Alpha']            = t.HG_Diode3_Alpha
                                    run.data['Diode4_HG_Alpha']            = t.HG_Diode4_Alpha
                                    run.data['Diode5_HG_Alpha']            = t.HG_Diode5_Alpha
                                    run.data['Diode6_HG_Alpha']            = t.HG_Diode6_Alpha
                                    run.data['Diode7_HG_Alpha']            = t.HG_Diode7_Alpha
                                    run.data['Diode8_HG_Alpha']            = t.HG_Diode8_Alpha
                                    run.data['Diode9_HG_Alpha']            = t.HG_Diode9_Alpha
                                    run.data['PMT1_HG_Alpha']              = t.HG_Diode9_Alpha
                                    run.data['PMT2_HG_Alpha']              = t.HG_Diode9_Alpha
                                    run.data['ExtCIS0_HG_Alpha']           = t.HG_Diode9_Alpha
                                    run.data['ExtCIS1_HG_Alpha']           = t.HG_Diode9_Alpha
                                    run.data['IntCIS_HG_Alpha']            = t.HG_Diode9_Alpha
                                    run.data['DiodePhocal_HG_Alpha']       = t.HG_Diode9_Alpha

                                    # sigma of alpha run values for monitoring diodes
                                    run.data['Diode0_LG_Alpha_Sigma']      = t.LG_Diode0_Alpha_Sigma
                                    run.data['Diode1_LG_Alpha_Sigma']      = t.LG_Diode1_Alpha_Sigma
                                    run.data['Diode2_LG_Alpha_Sigma']      = t.LG_Diode2_Alpha_Sigma
                                    run.data['Diode3_LG_Alpha_Sigma']      = t.LG_Diode3_Alpha_Sigma
                                    run.data['Diode4_LG_Alpha_Sigma']      = t.LG_Diode4_Alpha_Sigma
                                    run.data['Diode5_LG_Alpha_Sigma']      = t.LG_Diode5_Alpha_Sigma
                                    run.data['Diode6_LG_Alpha_Sigma']      = t.LG_Diode6_Alpha_Sigma
                                    run.data['Diode7_LG_Alpha_Sigma']      = t.LG_Diode7_Alpha_Sigma
                                    run.data['Diode8_LG_Alpha_Sigma']      = t.LG_Diode8_Alpha_Sigma
                                    run.data['Diode9_LG_Alpha_Sigma']      = t.LG_Diode9_Alpha_Sigma
                                    run.data['PMT1_LG_Alpha_Sigma']        = t.LG_Diode9_Alpha_Sigma
                                    run.data['PMT2_LG_Alpha_Sigma']        = t.LG_Diode9_Alpha_Sigma
                                    run.data['ExtCIS0_LG_Alpha_Sigma']     = t.LG_Diode9_Alpha_Sigma
                                    run.data['ExtCIS1_LG_Alpha_Sigma']     = t.LG_Diode9_Alpha_Sigma
                                    run.data['IntCIS_LG_Alpha_Sigma']      = t.LG_Diode9_Alpha_Sigma
                                    run.data['DiodePhocal_LG_Alpha_Sigma'] = t.LG_Diode9_Alpha_Sigma

                                    run.data['Diode0_HG_Alpha_Sigma']      = t.HG_Diode0_Alpha_Sigma
                                    run.data['Diode1_HG_Alpha_Sigma']      = t.HG_Diode1_Alpha_Sigma
                                    run.data['Diode2_HG_Alpha_Sigma']      = t.HG_Diode2_Alpha_Sigma
                                    run.data['Diode3_HG_Alpha_Sigma']      = t.HG_Diode3_Alpha_Sigma
                                    run.data['Diode4_HG_Alpha_Sigma']      = t.HG_Diode4_Alpha_Sigma
                                    run.data['Diode5_HG_Alpha_Sigma']      = t.HG_Diode5_Alpha_Sigma
                                    run.data['Diode6_HG_Alpha_Sigma']      = t.HG_Diode6_Alpha_Sigma
                                    run.data['Diode7_HG_Alpha_Sigma']      = t.HG_Diode7_Alpha_Sigma
                                    run.data['Diode8_HG_Alpha_Sigma']      = t.HG_Diode8_Alpha_Sigma
                                    run.data['Diode9_HG_Alpha_Sigma']      = t.HG_Diode9_Alpha_Sigma
                                    run.data['PMT1_HG_Alpha_Sigma']        = t.HG_Diode9_Alpha_Sigma
                                    run.data['PMT2_HG_Alpha_Sigma']        = t.HG_Diode9_Alpha_Sigma
                                    run.data['ExtCIS0_HG_Alpha_Sigma']     = t.HG_Diode9_Alpha_Sigma
                                    run.data['ExtCIS1_HG_Alpha_Sigma']     = t.HG_Diode9_Alpha_Sigma
                                    run.data['IntCIS_HG_Alpha_Sigma']      = t.HG_Diode9_Alpha_Sigma
                                    run.data['DiodePhocal_HG_Alpha_Sigma'] = t.HG_Diode9_Alpha_Sigma

                        try:
                                run.data['MeanTime'] = t.meantime[ros][gain]
                        except:
                                pass


                        kappastats = stats()
                        if self.doPisa:
                                for k in t.Kappa:
                                        if k>0. and k<0.005:
                                                kappastats.fill(k)

                        kappa = kappastats.mean()

                        for event in self.run_dict[run.runNumber]: # Then loop on events

                                if event.run != run:
                                        continue

                                [part, mod, chan, gain] = event.region.GetNumber()

                                if self.PMTool.get_PMT_index(part-1,mod-1,chan) < 0: # Not a channel (ie_EBA_m15 EBC_m18 c18 & c19)
                                        continue

                                if gain==0 and t.wheelpos == 8: # don't look at low gain events for filter 8 runs
                                        continue
                    
                                if gain==0 and t.wheelpos == 2: # don't look at low gain events for filter 2 runs
                                        continue    

                                if gain==1 and t.wheelpos == 6: # don't lool at high gain events for filter 6 runs
                                        continue

                                if t.wheelpos == 2:
                                        self.numberEventCut = 0
                
                                if t.wheelpos == 8:
                                        self.numberEventCut = 30000
                
                                if t.wheelpos == 6:
                                        self.numberEventCut = 3000

                                event.data['is_OK']    = True # This channel could be calibrated
        
                                index = self.PMTool.get_index(part-1, mod-1, chan, gain)

                                if self.diode == -1: # Means you are using the default reference values
                                        if gain==0:
                                                diode = 2
                                        elif gain==1:
                                                diode = 1
                                else:
                                        diode = self.diode

                                m_diode = diode*24576

                                n = 0
                                try:
                                        n = t.n_LASER_entries[m_diode+index]
                                except:
                                        pass

                                try:
                                        n = t.LASER_entries[index]
                                except:
                                        pass

                                if n < self.numberEventCut or t.signal[index] <= 0.001:
                                        event.data['is_OK']    = False
                                        if self.verbose and n!=0 and  t.Status[index]==0:
                                                print('ReadLaser failed cuts for run %6d %28s %6d %6.1f %1d' % (
                                                        run.runNumber, event.region.GetHash(),
                                                        n, t.signal[index], t.Status[index]))

                                event.data['number_entries'] = n  # Number of entries for the channel
                                # event.data['wheelpos']       = t.wheelpos This is moved to run.data dictionary
                                               
                                event.data['calibration']    = t.signal_cor[m_diode+index]       # Calibration value (PMT/Diode) for the channel
                                
                                if n>1:
                                        event.data['caliberror']  = t.signal_cor_s[m_diode+index] / math.sqrt(n)
                                else:
                                        event.data['calibration'] = 0.
                                        event.data['caliberror']  = 0.

                                try:
                                        event.data['status']     = t.Status[index]
                                except AttributeError:
                                        event.data['status']     = 0

                                try:
                                        event.data['HV'] = t.HV[index/2]
                                        event.data['HVSet'] = t.HVSet[index/2]
#                                        Hack for broken PVSS2COOL in Spring 2013:
#                                        if event.data['HV']<-20:
#                                                event.data['HV'] = event.data['HVSet']
                                        if self.doTime and n>0:
                                                event.data['cellTime']    = t.time[index]
                                                event.data['cellTimeErr'] = t.time_s[index] / math.sqrt(n)
                                except AttributeError:
                                        # Old version of the N-tuple didn't have these fields.
                                        pass

                                # Laser signals in pC
                                event.data['signal']     = t.signal[index]
                                event.data['signalerr']  = t.signal_s[index]
                                event.data['f_laser']    = 1.

                                if self.doPisa and gain==1:  # Pisa method only works for High gain
                                        fe = 1/(1.3*1.602176e-7);
                                        try:
                                                #[part, mod, pmt, gain] = event.region.GetNumber(1)
                                                #offset = (((pmt%2)+1)%2)*2+gain
                                                #kappa = t.Kappa[int(index/96)*96+offset]
                                                # kappa = 0.0024
                                                q     = t.signal[index]
                                                v     = t.signal_s[index]*t.signal_s[index]
                                                gainP = fe*(v/q - kappa*q );

                                                N     = t.LASER_entries[index]
                                                dmean = sqrt(v/N)
                                                dvar  = v*sqrt(2/N)
                                                gainPerror = fe*sqrt( (dvar/q)*(dvar/q) + (dmean*dmean)*(kappa+v/(q*q))*(kappa+v/(q*q)) )

                                                #print gainP, N, q, v, kappa
                                        except:
                                                gainP  = 0
                                                gainPerror = 0

                                        if gainP>10000. and kappa>0. and kappa<0.01:
                                                event.data['gain_Pisa'] = gainP
                                                event.data['gainerror_Pisa'] = gainPerror
                                        else:
                                                # print 'Pisa gain is low,',event.region.GetHash(), \
                                                #       gainP, N, q, v, kappa
                                                pass

                        f.Close()

                self.events = {}


        def setNumberEventCut(self, numberEventCut):
                self.numberEventCut = numberEventCut

