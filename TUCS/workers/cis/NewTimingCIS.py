# Author:Christopher D'Amboise,  Dave Hollander <daveh@uchicago.edu>
#
# June 16, 2010
#

from src.ReadGenericCalibration import *
from src.oscalls import *
from src.region import *
from array import array
from src.MakeCanvas import *
from ROOT import TFile
from time import strptime, strftime 

class NewTimingCIS(ReadGenericCalibration):
    "Get the fitted time for channels in a module as a function of injected charge - fixed for new ntuple format/location"
    
    def __init__(self, processingDir='root://castoratlas//castor/cern.ch/atlas/atlascerngroupdisk/det-tile/{Tyear}/',
                 getSamples=True, getInjDist=True, all=False,Phase=0,dachi=10,daclo=512, TFlagMacro=False):
        
        self.processingDir = processingDir
        self.TFlagMacro = TFlagMacro
        self.all=all
        self.ftDict = {} # Used for linear constant.  Each element is a [TTree, TFile]
        self.badRuns = set()
        self.dir = getPlotDirectory() + "/cis"
        createDir('%s/TimingFlag' % self.dir)
        self.dir = '%s/ChannelTiming' % self.dir
        createDir(self.dir) 
        self.c1 = MakeCanvas()
        self.c1.SetHighLightColor(2)
        self.c2 = MakeCanvas()
        self.Phase=Phase
        self.DAChi=dachi
        self.DAClo=daclo
      #  self.c2.SetHighLightClolor(2)

    def Get_Index(self, ros, mod, chan):
        return ros  *64*48\
            + mod      *48\
            + chan
    
    def Get_SampIndex(self, ros, mod, chan, samp):
        return ros  *64*48*7\
            + mod      *48*7\
            + chan        *7 + samp
            
    def ProcessStart(self):
        self.timeEny2D_hi = ROOT.TProfile2D('timeEny2D', '', 48, 0, 48, 12, -1, 13)
        self.timeEny2D_lo = ROOT.TProfile2D('timeEny2D', '', 48, 0, 48, 40, 50, 800)
        self.SAMPLES_lo = ROOT.TProfile('SAMPLES', '',7, 0, 6)
        self.SAMPLES_hi = ROOT.TProfile('SAMPLES', '',7, 0, 6)
    def ProcessStop(self):
        
        if not 'self.module' in globals():
            self.module = 'unknown_01'
        if self.timeEny2D_hi and self.timeEny2D_lo:
            self.c1.cd()
            self.c1.SetLeftMargin(0.14)
            self.c1.SetRightMargin(0.14)
            ROOT.gStyle.SetPalette(1)
            self.timeEny2D_hi.GetXaxis().SetTitle("PMT - 1 (high gain)")
            self.timeEny2D_lo.GetXaxis().SetTitle("PMT - 1 (low gain)")

            for timeEny in [self.timeEny2D_hi, self.timeEny2D_lo]:
                timeEny.GetYaxis().SetTitle("Injected charge (pC)")
                timeEny.GetZaxis().SetTitle("Fitted time (ns)")
                timeEny.Draw('COLZ')
                if timeEny == self.timeEny2D_hi:
                    gain = 'hi'
                else:
                    gain = 'lo' 
                self.c1.Print("%s/timing_stack_%s_%s.png" % (self.dir, self.module, gain))


     

            self.c1.Print("%s/timing_stack_%s.ps]" % (self.dir, self.module))

        elif self.SAMPLES_hi and self.SAMPLES_lo:
            self.c2.cd()
            self.c2.SetLeftMargin(0.14)
            self.c2.SetRightMargin(0.14)
            ROOT.gStyle.SetPalette(1)
            self.SAMPLES_hi.GetXaxis().SetTitle("PMT - 1 (high gain)")
            self.SAMPLES_lo.GetXaxis().SetTitle("PMT - 1 (low gain)")

            for SAMPLES in [self.SAMPLES_hi, self.SAMPLES_lo]:
                SAMPLES.GetYaxis().SetTitle("ADC Counts ")
                SAMPLES.GetZaxis().SetTitle("Sample #")

                if SAMPLES == self.SAMPLES_hi:
                    gain = 'hi'
                else:
                    gain = 'lo' 
                self.c2.Print("%s/SAMPLES_%s_%s.png" % (self.dir, self.module, gain))

            
        else:
            pass
           
    
    def ProcessRegion(self, region):
        # See if it's a gain
        global NTimingCIS
        if 'gain' not in region.GetHash():
            return
                
        self.c1.cd()
                       
        self.dirstr = '%s%02d' % (region.GetHash().split('_')[1], int(region.GetHash().split('_')[2][1:]))
        factor = 2.0*4.096*100.0/1023.0 # From TileCisDefaultCalibTool.cxx
                        
        # Prepare events
        foundEventToProcess = False
              
        for event in region.GetEvents():                       
            
            if not NTimingCIS:
                print('no specific bad timing channels found in list from MapFlagFailure...using all given regions instead')
            
            if event.run.runType == 'CIS':
            
                if self.TFlagMacro:
                    proceed = False
                    if NTimingCIS:
                        for (ernumb, data_region, NTi, NTdac, NTphase) in NTimingCIS:
                            if (ernumb, data_region) == (event.run.runNumber, region.GetHash()):
                                proceed = True
                        if not proceed:
                            continue
                               
                if 'moreInfo' not in event.data and not self.all:
                    continue                
                if not self.all and not event.data['moreInfo']:
                    continue
                              
                foundEventToProcess = True

                if event.run.runNumber and event.run.runNumber not in self.ftDict:
                    
                    if event.run.runNumber > 189319:
                        self.processingDir = 'root://eosatlas///eos/atlas/atlascerngroupdisk/det-tile/{Tyear}/'
                    timeform = time.strptime(event.run.time, "%Y-%m-%d %H:%M:%S")
                    eventyear = time.strftime('%Y',timeform)
                    f = TFile.Open('{Tdir}tile_{Tnum}_CIS.0.aan.root'.format(Tdir=self.processingDir.format(
                        Tyear=str(eventyear)), Tnum=str(event.run.runNumber)),"read")

                    if f == None:
                        t = None
                    else:
                        t = f.Get('h2000')
                    #t.Print()
                                      
                    if [f, t] == [None, None]:
                        if event.run.runNumber not in self.badRuns:
                            print("Error: GetSamples couldn't load run", event.run.runNumber, ' for %s...' % self.dirstr)
                            self.badRuns.add(event.run.runNumber)
                        continue
                    self.ftDict[event.run.runNumber] = [f, t]

        
        if not foundEventToProcess:
            return

        map = {'LBA': 'A', 'LBC': 'C', 'EBA': 'D', 'EBC': 'E'}
        if 'lowgain' in region.GetHash():
            gain = 'lo'
        else:
            gain = 'hi'

        chan = int(region.GetHash(1).split('_')[3][1:]) - 1
        
        newevents = set()
        self.c1.Print("%s/timing_%s.png" % (self.dir, region.GetHash()))
        for event in region.GetEvents():
            if event.run.runType == 'CIS':
                timeEny_lo = ROOT.TProfile("fitted time", "", 48, 0, 800)
                timeEny_hi = ROOT.TProfile("fitted time", "", 12, 0, 12)
                SAMPLES_lo = ROOT.TProfile("Samples", "",7, 0, 6)
                SAMPLES_hi = ROOT.TProfile("Samples", "",7, 0, 6)
                ROOT.gStyle.SetOptStat(0)
                
                if not self.all and \
                       ('moreInfo' in event.data and not event.data['moreInfo']):
                    continue

                # Load up the tree, file and scans for this run
                if event.run.runNumber not in self.ftDict:
                    continue
                
                [f, t] = self.ftDict[event.run.runNumber]
                [x, y, z, w] = region.GetNumber()
                index = self.Get_Index(x-1, y-1, z)
                for p in range(0,7):
                    indexSamp = self.Get_SampIndex(x-1, y-1, z, p)
                    
                 
                t.SetBranchStatus("*", 0)
                t.SetBranchStatus("tFit_%s" % (gain), 1)
                t.SetBranchStatus("cispar", 1)
                t.SetBranchStatus("DMUBCID_%s" % (gain), 1)
                t.SetBranchStatus("sample_%s" %(gain) , 1)
            

                injections = {}

                nevt = t.GetEntries()
                
                j = 0
                #t.Print()
                for i in range(300, nevt):
                    if t.GetEntry(i) <= 0:
                        print('huh?')
                        return
                    
                    # Make sure that it is the 100 pF capacitor
                    if t.cispar[7] != 100:
                        continue
                
                    phase = t.cispar[5]
                    dac = t.cispar[6]
                                       
                    t_of_fit = getattr(t, 'tFit_%s' % (gain))
                    t_bcid = getattr(t, 'DMUBCID_%s' % (gain))
                    Sample= getattr(t,'sample_%s' %(gain))
                   

                    if phase==self.Phase:
                        if dac*factor>300 and dac*factor<700:
                            if 'lo' in region.GetHash():
                                self.timeEny2D_lo.Fill(chan, dac*factor, t_of_fit[index])
                                timeEny_lo.Fill(dac*factor, t_of_fit[index])
                        elif dac*factor>3 and dac*factor<10:   
                            if 'hi' in region.GetHash():
                                self.timeEny2D_hi.Fill(chan, dac*factor, t_of_fit[index])
                                timeEny_hi.Fill(dac*factor, t_of_fit[index])
                          
                    if phase==self.Phase:
                        for p in range(0,7):
                            indexSamp = self.Get_SampIndex(x-1, y-1, z, p)
                            if dac==self.DAClo : # 512 is default 
                                if 'lo' in region.GetHash():
                                    self.SAMPLES_lo.Fill(p, Sample[indexSamp])
                                    SAMPLES_lo.Fill(p, Sample[indexSamp])
                                    
                            if dac==self.DAChi: # 512 is default         
                                if 'hi' in region.GetHash():
                                    self.SAMPLES_hi.Fill(p, Sample[indexSamp])
                                    SAMPLES_hi.Fill(p, Sample[indexSamp])
                                    print(p, ' Sample  ',Sample[indexSamp], 'event number', i , ' dac  ' ,dac , ' CAP', t.cispar[7])


                                

                tl = ROOT.TLatex()
                tl.SetTextAlign(12)
                tl.SetTextSize(0.03)
                tl.SetNDC()

                self.module = self.dirstr
                
                   
                if 'lo' in region.GetHash():
                    timeEny_lo.Draw()
                    timeEny_lo.GetXaxis().SetTitle("Injected charge (pC)")
                    timeEny_lo.GetYaxis().SetTitle("Fitted time (ns)")
                    timeEny_lo.Draw()
                    tl.DrawLatex(0.20,0.90,"{0}".format(region.GetHash()))
                    tl.DrawLatex(0.20,0.87,"Lowgain")
                    tl.DrawLatex(0.20,0.84,"Run %d" % event.run.runNumber)
                    tl.DrawLatex(0.20,0.81,"DAC %d" % self.DAClo)
                    tl.DrawLatex(0.20,0.78,"Phase %d" % self.Phase)
                    self.c1.Print("%s/timing_%s.png" % (self.dir, region.GetHash()))

                    self.c2.cd()
                    SAMPLES_lo.Draw()
                    SAMPLES_lo.GetXaxis().SetTitle("Sample #")
                    SAMPLES_lo.GetYaxis().SetTitle("ADC")
                    SAMPLES_lo.Draw()
                    tl.DrawLatex(0.20,0.90,"{0}".format(region.GetHash()))
                    tl.DrawLatex(0.20,0.87,"Lowgain")
                    tl.DrawLatex(0.20,0.84,"Run %d" % event.run.runNumber)
                    tl.DrawLatex(0.20,0.81,"DAC %d" % self.DAClo)
                    tl.DrawLatex(0.20,0.78,"Phase %d" % self.Phase)
                    self.c2.Print("%s/SAMPLES_%s.png" % (self.dir, region.GetHash()))
                
                
                else:
                    self.c1.cd()
                    timeEny_hi.Draw()
                    timeEny_hi.GetXaxis().SetTitle("Injected charge (pC)")
                    timeEny_hi.GetYaxis().SetTitle("Fitted time (ns)")
                    timeEny_hi.Draw()
                    tl.DrawLatex(0.20,0.90,"{0}".format(region.GetHash()))
                    tl.DrawLatex(0.20,0.87,"Highgain")
                    tl.DrawLatex(0.20,0.84,"Run %d" % event.run.runNumber)
                    tl.DrawLatex(0.20,0.81,"DAC %d" % self.DAClo)
                    tl.DrawLatex(0.20,0.78,"Phase %d" % self.Phase)
                    self.c1.Print("%s/timing_%s.png" % (self.dir, region.GetHash()))

                    self.c2.cd()
                    SAMPLES_hi.Draw()
                    SAMPLES_hi.GetXaxis().SetTitle("sample #")
                    SAMPLES_hi.GetYaxis().SetTitle("ADC")
                    SAMPLES_hi.Draw()
                    tl.DrawLatex(0.20,0.90,"{0}".format(region.GetHash()))
                    tl.DrawLatex(0.20,0.87,"Highgain")
                    tl.DrawLatex(0.20,0.84,"Run %d" % event.run.runNumber)
                    tl.DrawLatex(0.20,0.81,"DAC %d" % self.DAClo)
                    tl.DrawLatex(0.20,0.78,"Phase %d" % self.Phase)
                    self.c2.Print("%s/SAMPLES_%s.ps" % (self.dir, region.GetHash()))
        self.c1.Print("%s/timing_%s.png" % (self.dir, region.GetHash()))
        self.c2.Print("%s/SAMPLES_%s.png" % (self.dir, region.GetHash()))
     
