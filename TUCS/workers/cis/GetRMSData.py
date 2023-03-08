# Author: Andrew Hard <ahard@uchicago.edu>
#
# November 19, 2011

from src.ReadGenericCalibration import *
from src.oscalls import *
from src.region import *
from array import array
from src.MakeCanvas import *
from ROOT import TFile
from time import strptime, strftime 

class GetRMSData(ReadGenericCalibration):
    "Prints the RMS values as a function of injected charge for CIS scans. Also prints fitted amplitude distributions for details on the RMS values."

    def __init__(self, processingDir='root://castoratlas//castor/cern.ch/atlas/atlascerngroupdisk/det-tile/{Tyear}/',
                 all=False, region=None, draw_distribution_plots=False, folder_name='Generic_Folder'):
        self.processingDir = processingDir
        self.all=all
        self.ftDict = {}
        self.badRuns = set()
        self.folder_name = folder_name
        self.dir = getPlotDirectory() + "/cis"
        createDir(self.dir)
        self.dir = "{0}/{1}".format(self.dir, 'RMSdata')
        createDir(self.dir)
        self.dir = "{0}/{1}".format(self.dir, self.folder_name)
        createDir(self.dir)
        self.c1 = MakeCanvas()
        self.c1.SetHighLightColor(2)
        self.c2 = MakeCanvas()

        self.selected_region = region
        self.draw_distribution_plots = draw_distribution_plots
        
    def Get_Index(self, ros, mod, chan):
        return ros  *64*48\
            + mod      *48\
            + chan
    
    def Get_SampIndex(self, ros, mod, chan, samp):
        return ros  *64*48*7\
            + mod      *48*7\
            + chan        *7 + samp
        
    def ProcessStart(self):
        # these 4 dictionaries will store plot data
        self.RMS_dict = {}
        self.range_dict = {}
        self.RMSscanlo = {}
        self.RMSscanhi = {}
            
    def ProcessStop(self):
        for a in self.RMS_dict:
            # converting the key name back into the dac value
            if 'lo' in a:
                dac2 = int(a.replace("_lo",""))
                print(dac2)
                gain_name = 'lo'
            elif 'hi' in a:
                dac2 = int(a.replace("_hi",""))
                print(dac2)
                gain_name = 'hi'

            # recall the list of reconstructed amplitudes associated with the dac_gain dictionary keys.
            reco_amplitude_list = self.RMS_dict[a]

            # dictionaries that will hold the min and max reconstructed amplitudes for each list.
            minimum = self.range_dict['%s_%s_min' % (dac2,gain_name)]
            maximum = self.range_dict['%s_%s_max' % (dac2,gain_name)]

            # create histograms and obtain RMS information.
            if self.draw_distribution_plots:
                self.c2.cd()
                self.RMShist=ROOT.TH1D('RMS_%s_%s' % (gain_name,dac2),'',20,int(minimum-20),int(maximum+20))
                for amplitude in reco_amplitude_list:
                    self.RMShist.Fill(float(amplitude))

                # dictionaries with dac keys and RMS values.
                if gain_name == 'lo':
                    self.RMSscanlo[dac2] = self.RMShist.GetRMS()
                elif gain_name == 'hi':
                    self.RMSscanhi[dac2] = self.RMShist.GetRMS()

                self.RMShist.GetXaxis().SetTitle("ADC Counts")
                self.RMShist.GetXaxis().SetTitleOffset(1)
                self.RMShist.Draw()
                self.c2.Print("%s/Fit_Amp_Dist_%s_%s_%s.pdf" % (self.dir, self.selected_region[0], dac2, gain_name))

            # get RMS values without generating fitted amplitude histograms.
            elif not self.draw_distribution_plots:
                if gain_name == 'lo':
                    self.RMSscanlo[dac2] = ROOT.TMath.RMS(len(reco_amplitude_list),array('f',reco_amplitude_list))
                elif gain_name == 'hi':
                    self.RMSscanhi[dac2] = ROOT.TMath.RMS(len(reco_amplitude_list),array('f',reco_amplitude_list))
        
        # Official ATLAS formatting for CIS note plots.
        #ROOT.gROOT.ProcessLine(".x Style.C")
        
        self.c1.cd()
        RMShi = ROOT.TGraphErrors()
        RMSlo = ROOT.TGraphErrors()

        # adding points to the RMS plots
        k = 0
        for b in self.RMSscanhi:
            RMShi.SetPoint(k, b*0.801, self.RMSscanhi[b])
            k += 1
            
        j = 0
        for c in self.RMSscanlo:
            RMSlo.SetPoint(j, c*0.801, self.RMSscanlo[c])
            j += 1

        self.c1.cd()

        for plot in [RMSlo,RMShi]:
            plot.Draw("AP")
            plot.GetXaxis().SetTitle("Injected Charge (pC)")
            plot.GetYaxis().SetTitle("RMS (ADC counts)")
            plot.GetYaxis().SetTitleOffset(1)
            plot.GetXaxis().SetTitleOffset(1)
            plot.Draw('AP')
                
            l1 = ROOT.TLine()
            l1.SetLineColor(4)
            l1.SetLineWidth(3)
            l1.SetLineStyle(2)
            l2 = ROOT.TLine()
            l2.SetLineColor(4)
            l2.SetLineWidth(3)
            l2.SetLineStyle(2)
            l3 = ROOT.TLine()
            l3.SetLineColor(2)
            l3.SetLineWidth(3)

            # lines showing the boundaries of the fit range as well as the RMS cutoff.
            if plot == RMSlo:
                l1.DrawLine(300,5,300,0)
                l2.DrawLine(700,5,700,0)
                l3.DrawLine(300,5,700,5)

                self.c1.Print("%s/RMS_values_%s_lo.pdf" % (self.dir,self.selected_region[0]))
                self.c1.Print("%s/RMS_values_%s_lo.root" % (self.dir,self.selected_region))
               
            elif plot == RMShi:
                l1.DrawLine(3,5,3,0)
                l2.DrawLine(10,5,10,0)
                l3.DrawLine(3,5,10,5)

                self.c1.Print("%s/RMS_values_%s_hi.pdf" % (self.dir,self.selected_region[0]))
                self.c1.Print("%s/RMS_values_%s_hi.root" % (self.dir,self.selected_region))
    
    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash():
            return
        dirstr = '%s%02d' % (region.GetHash().split('_')[1], int(region.GetHash().split('_')[2][1:]))
        factor = 2.0*4.096*100.0/1023.0
        foundEventToProcess = False
        
        for event in region.GetEvents():
            if event.run.runType == 'CIS':
                if 'moreInfo' not in event.data and not self.all:
                    continue
                if not self.all and not event.data['moreInfo']:
                    continue
                foundEventToProcess = True
                if event.run.runNumber and event.run.runNumber not in self.ftDict:
                    if event.run.runNumber > 189319:
                        self.processingDir = 'root://eosatlas///eos/atlas/atlascerngroupdisk/det-tile/{Tyear}/'
                    timeform = time.gmtime(event.data['time'])
                    eventyear = time.strftime('%Y',timeform)
                    f = TFile.Open('{Tdir}tile_{Tnum}_CIS.0.aan.root'.format(Tdir=self.processingDir.format(
                        Tyear=str(eventyear)), Tnum=str(event.run.runNumber)),"read")

                    if f == None:
                        print('Failed to open a file.')
                        t = None
                        if event.run.runNumber not in self.badRuns:
                            print('Error: GetRMSData could not load run', event.run.runNumber, ' for %s...' % dirstr)
                            self.badRuns.add(event.run.runNumber)
                        continue
                    else:
                        t = f.Get('h2000') ## This may have to be changed to h3000
                    self.ftDict[event.run.runNumber] = [f, t]
                   
        if not foundEventToProcess:
            return

        if 'lowgain' in region.GetHash():
            gain = 'lo'
        else:
            gain = 'hi'
            
        module = int(region.GetHash().split('_')[2][1:])
        channel = int(region.GetHash(1).split('_')[3][1:]) - 1
        partition = region.GetHash().split('_')[1]

        newevents = set()
        for event in region.GetEvents():
            if event.run.runType == 'CIS':

                if not self.all and \
                       ('moreInfo' in event.data and not event.data['moreInfo']):
                    continue
                if event.run.runNumber not in self.ftDict:
                    continue
                
                [f, t] = self.ftDict[event.run.runNumber]
                [x, y, z, w] = region.GetNumber()
                index = self.Get_Index(x-1, y-1, z)

                # retrieving data from ntuple
                t.SetBranchStatus("*", 0)
                t.SetBranchStatus("tFit_%s" % (gain), 1)
                t.SetBranchStatus("cispar", 1)
                t.SetBranchStatus("DMUBCID_%s" % (gain), 1)
                t.SetBranchStatus("sample_%s" % (gain), 1)
                t.SetBranchStatus("eFit_%s" % (gain), 1)
                t.SetBranchStatus("pedFit_%s" % (gain), 1)

                injections = {}
                nevt = t.GetEntries()
                # loop over CIS events (individual injections)
                for i in range(300, nevt):
                    if t.GetEntry(i) <= 0:
                        return
                    if t.cispar[7] != 100:
                        continue

                    # define the CIS parameters (see TUCS CIS Twiki)
                    phase = t.cispar[5]
                    dac = t.cispar[6]
                    cap = t.cispar[7]
                    charge = factor * dac
                    
                    t_of_fit = getattr(t, 'tFit_%s' % (gain))
                    e_of_fit = getattr(t, 'eFit_%s' % (gain))
                    p_of_fit = getattr(t, 'pedFit_%s' % (gain))
                    samples = getattr(t, 'sample_%s' % (gain))

                    # This section creates a dictionary for the RMS plot data
                    minhi = '%d_hi_min' % dac
                    maxhi = '%d_hi_max' % dac
                    minlo = '%d_lo_min' % dac
                    maxlo = '%d_lo_max' % dac
                        
                    if phase in range (0,225,16):
                            
                        if 'lo' in region.GetHash():
                            dac_gain = '%d_lo' % dac
                            if dac in range (0,993,32):
                                if dac_gain not in self.RMS_dict:
                                    self.RMS_dict[dac_gain] = []
                                    self.range_dict[minlo] = 1000
                                    self.range_dict[maxlo] = 0

                                # dictionary with reconstructed amplitudes
                                self.RMS_dict[dac_gain].append(e_of_fit[index])

                                # dictionaries to define fit amp. histogram domains.
                                if e_of_fit[index] > self.range_dict[maxlo]:
                                    self.range_dict[maxlo] = e_of_fit[index]
                                if e_of_fit[index] < self.range_dict[minlo]:
                                    self.range_dict[minlo] = e_of_fit[index]
                                
                        elif 'hi' in region.GetHash():
                            dac_gain = '%d_hi' % dac
                            if dac in range (0,16,1):
                                if dac_gain not in self.RMS_dict:
                                    self.RMS_dict[dac_gain] = []
                                    self.range_dict[minhi] = 1000
                                    self.range_dict[maxhi] = 0

                                # dictionary with reconstructed amplitudes
                                self.RMS_dict[dac_gain].append(e_of_fit[index])

                                # dictionaries to define fit amp. histogram domains.
                                if e_of_fit[index] > self.range_dict[maxhi]:
                                    self.range_dict[maxhi] = e_of_fit[index]
                                if e_of_fit[index] < self.range_dict[minhi]:
                                    self.range_dict[minhi] = e_of_fit[index]

                
