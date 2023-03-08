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
# -> diode_num_lg: the diode you want to use in order to get the ratio low gain
# -> diode_num_hg: the diode you want to use in order to get the ratio high gain
#
# -> box_par: option which select only the box parameter
#          DEFAULT VAL = False
#
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################
from __future__ import print_function

import time

# For using the LASER tools
from src.laser.toolbox import *
from src.stats import *

class ReadLaser(ReadGenericCalibration):
    "The Laser Calibration Data Reader"

    processingDir  = None
    numberEventCut = None


    def __init__(self, processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/las', diode_num_lg=0, diode_num_hg=0,
                 box_par=False, doTime=False, doPisa=False, verbose=False):

        self.processingDir  = processingDir
        self.numberEventCut = 300

        self.diode_lg       = diode_num_lg
        self.diode_hg       = diode_num_hg
        self.box_par        = box_par
        self.PMTool         = LaserTools()
        self.run_dict       = {}
        self.run_list       = set()
        self.verbose        = verbose
        self.doPisa         = doPisa
        self.doTime         = doTime


    def ProcessStart(self):

        for run in run_list.getRunsOfType('Las'):
            filename = "%s/tileCalibLAS_%s_Las.0.root" % (self.processingDir,run.runNumber)
            if os.path.exists(filename):
                run.data['filename'] = os.path.basename(filename)
                self.run_list.add(run)
                self.run_dict[run.runNumber] = []
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
            print("Reading ",run.data['filename'])
            run.data['wheelpos']       = t.wheelpos        # Filter wheel position
            run.data['requamp']        = t.requamp         # Requested amplitude

            diode = array('f',(0.,)*20)
            diode_s= array('f',(0.,)*20)
            
            try :
                for d in range(20):
                    diode[d] = t.diode[d]
                    diode_s[d] = t.diode_s[d]
            except:
                print("Problem in ntuple", run.runNumber)

            run.data['diodes']         = diode
            run.data['diodes_s']       = diode_s

            #for diode in range(10):
            #    print t.diode[2*diode], t.diode[2*diode+1], t.diode[2*diode+1]/t.diode[2*diode]

            if self.box_par: # Special case for laser box parameters following
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

                run.data['humid']     = 0
                if run.runNumber > 135000:
                    run.data['humid']     = t.humid     # Relative humidity (in %)
                    #self.box_par = False                # Add it to a single region

            try:
                meantime = array('f',(0.,)*4)
                for ros in range(4):
                    meantime[ros] = t.meantime[ros]
                run.data['MeanTime'] = meantime
            except:
                pass


            kappastats = stats()
            if self.doPisa:
                for k in t.Kappa:
                    if k>0. and k<0.005:
                        kappastats.fill(k)

            kappa = kappastats.mean()
            run.data['kappa'] = kappa

            signalstat = stats()
            signalerrorstat = stats()
            for event in self.run_dict[run.runNumber]: # Then loop on events

                if event.run != run:
                    continue

                [part, mod, chan, gain] = event.region.GetNumber()

                if self.PMTool.get_PMT_index(part-1,mod-1,chan) < 0: # Not a channel (ie_EBA_m15 EBC_m18 c18 & c19)
                    continue

                if gain==0 and t.wheelpos == 8: # don't look at low gain events for filter 8 runs
                    continue

                if gain==1 and t.wheelpos == 6: # don't lool at high gain events for filter 6 runs
                    continue

                # if t.wheelpos == 8:
                #     self.numberEventCut = 300 #lower cuts for laser 2

                # if t.wheelpos == 6:
                #     self.numberEventCut = 300

                event.data['is_OK']    = True # This channel could be calibrated

                index = self.PMTool.get_index(part-1, mod-1, chan, gain)

                if gain==0:
                    diode = self.diode_lg
                else:
                    diode = self.diode_hg
                m_diode = diode*24576                

                n = 0
               
                try:
                    n = t.LASER_entries[index]
                except:
                    try:
                        n = t.n_LASER_entries[m_diode+index]
                    except:
                        pass


                try:
                    event.data['status']     = t.Status[index]
                except:
                    event.data['status']     = 0

                #                print run.runNumber, event.region.GetHash(), event.data['status']
#                print "%1d %7.4f %7.4f %d" %(gain, t.rawsignal[index],t.signal[index],n)
                
                if n < self.numberEventCut or t.rawsignal[index] <= 2.0:  # below 2 ADC counts there is clearly no signal
                    event.data['is_OK']    = False
                    if self.verbose and not event.data['is_OK']  and  t.Status[index]==0:
                        print('ReadLaser failed cuts for run %6d %28s %6d %6.1f while status is good' % (
                            run.runNumber, event.region.GetHash(),
                            n, t.signal[index] ))

                event.data['number_entries'] = n                            # Number of entries for the channel
                event.data['calibration']    = t.signal_cor_good[m_diode+index]  # Calibration value (PMT/Diode) for the channel
                
                if n>1:
                    event.data['caliberror']  = t.signal_cor_good_s[m_diode+index] / math.sqrt(n)
                else:
                    event.data['calibration'] = t.signal_cor[m_diode+index]
                    event.data['caliberror']  = 0.

                if not event.data['is_OK'] and t.signal_cor[m_diode+index]>0:
                    event.data['calibration'] = t.signal_cor[m_diode+index]
                    event.data['caliberror']  = t.signal_cor_s[m_diode+index] # /math.sqrt( t.diode_entries[0] )
                    #event.data['is_OK'] = True

                try: # Old version of the N-tuple didn't have these fields.
                    event.data['HV'] = t.HV[index//2]
                    event.data['HVSet'] = t.HVSet[index//2]
                except Exception as inst:
                    print(type(inst))
                    print(inst.args)
                    print(inst)
#                    print("No HV in ",f)


                if self.doTime:
                    try: # Old version of the N-tuple didn't have these fields.
                        event.data['cellTime']    = t.time[index]
                        event.data['cellTimeErr'] = t.time_s[index] / math.sqrt(n)
                    except:
                        pass

                # Laser signals in pC
                event.data['signal']     = t.signal[index]
                event.data['signalerr']  = t.signal_s[index]
                event.data['signal_variance']   = t.signal_s[index]*t.signal_s[index]
                if (n>0):
                    try:
                        event.data['pmt_ratio']  = t.pmt_ratio[index]
                        event.data['pmt_ratio_s'] = t.pmt_ratio_s[index] / math.sqrt(n)
                    except:
                        pass
                event.data['f_laser']    = 1.

                signalstat.fill(t.signal[index])
                signalerrorstat.fill(t.signal_s[index])
            
                if self.doPisa and gain==1:  # Pisa method only works for High gain
                    fe = 1/(1.3*1.602176e-7)
                    f_noise=1.3
                    e=1.602176e-7
                    try:
                        q     = t.signal[index]
                        v     = t.signal_s[index]*t.signal_s[index]
                        #gainP = (v/(q*f_noise) - kappa*q)/e
                        gainP = (v/q - kappa*q)/(e*f_noise)
                        
                        dmean = math.sqrt(v/n)
                        dvar  = v*sqrt(2./n)
                        gainPerror = fe*sqrt( (dvar/q)*(dvar/q) + (dmean*dmean)*(kappa+v/(q*q))*(kappa+v/(q*q)) )
                        #gainPerror = math.sqrt( 
                        #    (dvar/(f_noise*q))*(dvar/(f_noise*q)) + 
                        #    (dmean*dmean)*(kappa+v/(f_noise*q*q))*(kappa+v/(f_noise*q*q))
                        #    )/e

                        # print gainP, N, q, v, kappa
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

