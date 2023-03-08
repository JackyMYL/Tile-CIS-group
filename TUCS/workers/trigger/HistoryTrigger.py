# HistoryTrigger.py
# Class for reading Trigger channels from ntuple, and update the trigger bits in the Online folder of the TileCal DB.
# Author: Bernardo Sotto-Maior Peralva <bernardo@cern.ch>
# Upodated on December 20, 2013 by Jeff Shahinian <jeffrey.david.shahinian@cern.ch>
from __future__ import print_function
from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *
import src.MakeCanvas
import random
import datetime

class HistoryTrigger(ReadGenericCalibration):
    '''Class for reading Trigger channels from ntuple, and update the trigger bits in the Online folder of the TileCal DB.'''

    c1 = None

    def __init__(self,processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/l1calo', load_autocr=True,Run_List='',plotTime=False):
        self.processingDir = processingDir
        self.ftDict = {} # Each element is a [TTree, TFile]

        self.load_autocr = load_autocr
        self.samples     = set()
        self.run_list    = []
        self.plotTime    = plotTime
        self.maxX        = 0                                                                                          
        self.minX        = 10000000
        self.maxY        = 0
        self.events      = set()
        self.nRunsToUse  = 0  # number of runs to use which have common bad channels
        self.deadCh       = []
        self.halfCh       = []
        self.commonElements = []
        self.dir = getPlotDirectory()
        createDir('%s/print' % self.dir)
        self.dir = '%s/print' % self.dir
        self.zeroGainCut = 0
        self.halfGainCut = 0

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")


    def get_index(self, ros, mod, chan):
        return ros  *64*48\
            + mod      *48\
            + chan

    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        # check if the run list array is empty
        if not self.run_list:
            print('WARNING: Run List array is empty, therefore there will be no update in the database, even though we will read and make a copy of the database!')
            print('')
            return

        if ((self.run_list) and (len(self.run_list) < 3)):
            print('WARNING: There are less than 3 runs for this period or array of runs. There will be no update in the database! For updates, the array of runs or period of time must contain at least 3 runs.')
            print('')
            return

        print('Using at least', end=' ')
        print(self.nRunsToUse, end=' ')
        print('runs with common bad channels (NoGain and HalfGain) in order to update the DB.')
        print('')

        for run in self.run_list:
                self.count1 = 0
                self.count2 = 0
                for event in self.events:
                        if (event.run.runNumber == run):
                                if event.data['zeroChanL1Calo']:
                                        self.count1 = self.count1 + 1
                                if event.data['halfChanL1Calo']:
                                        self.count2 = self.count2 + 1
                if self.count1 > self.count2:
                        if (self.count1 > self.maxY):
                                self.maxY = self.count1
                else:
                        if (self.count2 > self.maxY):
                                self.maxY = self.count2

        self.hhistZero = ROOT.TH2D('histHistoryTriggerZeroGain', 'Stability Trigger Channels Zero-Gain', 100, self.minX, self.maxX+50,100,0,self.maxY+(self.maxY/4))
        self.hhistHalf = ROOT.TH2D('histHistoryTriggerHalfGain', 'Stability Trigger Channels Half-Gain', 100, self.minX, self.maxX+50,100,0,self.maxY+(self.maxY/4))
        ROOT.TGaxis.SetMaxDigits(6)

        self.c1.cd()
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);
        self.c1.SetRightMargin(0.1974922)
        self.hhistZero.GetYaxis().SetTitle("Number of Bad Channels")
        if self.plotTime:
                self.hhistZero.GetXaxis().SetTitle("month/year")
        else:
                self.hhistZero.GetXaxis().SetTitle("run number")
        #self.hhist.GetXaxis().SetNdivisions(-503)
        self.hhistZero.GetXaxis().SetLabelSize(0.05)    
        self.hhistZero.GetYaxis().SetLabelSize(0.05)
        self.hhistZero.GetXaxis().SetTitleSize(0.03)
        self.hhistZero.GetXaxis().SetTitleOffset(3)
        self.hhistZero.SetStats(0)
        
        #print "DEAD CHANNELS: ", self.deadCh
        #print "HALF GAIN CHANNELS: ", self.halfCh

        for k in self.deadCh:
                if (self.deadCh.count(k) == 3):
                        if not k in self.commonElements:
                                self.commonElements.append(k)
        #print "COMMON BAD CHANNELS: ", len(self.commonElements)

        text_file = open(os.path.join(getResultDirectory(),"noGainChanList.txt"), "w")
        text_file.write("<L1Calo No-Gain Channel List>\n\n")
        text_file.write("ros 1-LBA 2-LBC 3-EBA 4-EBC\n")
        text_file.write("eta 0-14\n")
        text_file.write("phi 0-63\n")
        text_file.write("TileChan 0-47\n")
        text_file.write("triggerChan(PMT) 0-5\n")
        text_file.write("\n")
        contDead = 0
        for event in self.events:
                if (event.data['isNoGain']):
                        text_file.write('ros: %s\t' %event.data['partition'])
                        text_file.write("  ")
                        text_file.write('eta: %s\t' %event.data['ietaL1Calo'])
                        text_file.write("  ")
                        text_file.write('phi: %s\t' %event.data['iphiL1Calo'])
                        text_file.write("  ")
                        text_file.write('TileChan: %s\t' %event.data['chan'])
                        text_file.write("  ")
                        text_file.write('triggerChan(PMT): %s' %event.data['ipmtL1Calo'])
                        text_file.write("\n")
                        contDead = contDead + 1

        print("Number of common zero-gain channels: ", contDead)
        text_file.close()

        text_file = open(os.path.join(getResultDirectory(),"halfGainChanList.txt"), "w")
        text_file.write("<L1Calo Half-Gain Channel List>\n\n")
        text_file.write("ros 1-LBA 2-LBC 3-EBA 4-EBC\n")
        text_file.write("eta 0-14\n")
        text_file.write("phi 0-63\n")
        text_file.write("TileChan 0-47\n")
        text_file.write("triggerChan(PMT) 0-5\n")
        text_file.write("\n")
        contHalf = 0
        for event in self.events:
                if (event.data['isHalfGain']):
                        text_file.write('ros: %s\t' %event.data['partition'])
                        text_file.write("  ")
                        text_file.write('eta: %s\t' %event.data['ietaL1Calo'])
                        text_file.write("  ")
                        text_file.write('phi: %s\t' %event.data['iphiL1Calo'])
                        text_file.write("  ")
                        text_file.write('TileChan: %s\t' %event.data['chan'])
                        text_file.write("  ")
                        text_file.write('triggerChan(PMT): %s' %event.data['ipmtL1Calo'])
                        text_file.write("\n")
                        contHalf = contHalf + 1

        print("Number of common half-gain channels: ", contHalf)
        text_file.close()
        print('')

        trigFile = open(os.path.join(getResultDirectory(),"trigCommentDB.txt"),"w")
        trigFile.write('%s ' %contDead)
        trigFile.write('%s ' %contHalf)
        trigFile.write('%s ' %self.minXtime)
        trigFile.write('%s' %self.maxXtime)
        trigFile.close()

        print('INFO in <HistoryTrigger.py>: txt files noGainChanList.txt and halfGainChanList.txt have been created')
        print('')

        for run in self.run_list:
                self.countL1Calo = 0
                self.countZeroL1Calo = 0
                self.countHalfL1Calo = 0
                self.countTile = 0
                self.countZeroTile = 0
                self.countHalfTile = 0
                self.chan = 0
                self.aDead = []

                for event in self.events:
                        if (event.run.runNumber == run):
                                self.zeroGainCut = .1*event.data['DACvalue']
                                self.halfGainCut  = .5*event.data['DACvalue']
                                m = datetime.datetime.strptime(event.run.time,"%Y-%m-%d %H:%M:%S")
                                time = ('%s/%s' % (str(m)[5:7],str(m)[2:4]))
                                if event.data['badChanL1Calo']:
                                        self.countL1Calo = self.countL1Calo + 1
                                if event.data['halfChanL1Calo']:
                                        self.countHalfL1Calo = self.countHalfL1Calo + 1
                                if event.data['zeroChanL1Calo']:
                                        self.aDead.append(self.chan) 
                                        self.countZeroL1Calo = self.countZeroL1Calo + 1
                                if event.data['badChanTile']:
                                        self.countTile = self.countTile + 1
                                if event.data['halfChanTile']:
                                        self.countHalfTile = self.countHalfTile + 1
                                if event.data['zeroChanTile']:
                                        self.countZeroTile = self.countZeroTile + 1
                                self.chan = self.chan + 1
                
                self.chan = 0
                self.hhistZero.SetMarkerColor(2);
                self.hhistZero.Fill(run,self.countZeroL1Calo)
                if self.plotTime:
                        self.hhistZero.GetXaxis().SetBinLabel(self.hhistZero.GetXaxis().FindBin(run),time)
                else:
                        self.hhistZero.GetXaxis().SetBinLabel(self.hhistZero.GetXaxis().FindBin(run),'%s' % run)
                self.hhistZero.Draw()
                self.hhistHalf.SetMarkerColor(4);
                self.hhistHalf.Fill(run,self.countHalfL1Calo)
                if self.plotTime:
                        self.hhistHalf.GetXaxis().SetBinLabel(self.hhistZero.GetXaxis().FindBin(run),time)
                else:
                        self.hhistZero.GetXaxis().SetBinLabel(self.hhistZero.GetXaxis().FindBin(run),'%s' % run)
                self.hhistHalf.Draw("same")
        
                print('*****************************************')
                print('Results for the run:              ', run)
                print('Zero-gain cut (10% DAC value):    ', self.zeroGainCut)
                print('Half-gain cut (50% DAC value):    ', self.halfGainCut)
                print('Number of bad channels L1Calo:    ', self.countL1Calo)
                print('Number zero gain channels L1Calo: ', self.countZeroL1Calo)
                print('Number half gain channels L1Calo: ', self.countHalfL1Calo)
                print('Number of bad channels Tile:      ', self.countTile)
                print('Number zero gain channels Tile:   ', self.countZeroTile)
                print('Number half gain channels Tile:   ', self.countHalfTile)
                print('*****************************************')

        self.leg = ROOT.TLegend(0.82,0.7,0.98,0.94)     
        #self.leg = ROOT.TLegend(0.6,0.7,.9,.9);
        #self.leg.SetHeader("The Legend Title");
        self.leg.SetTextSize(0.02)
        self.leg.AddEntry(self.hhistZero,"L1Calo Zero-Gain","p");
        self.leg.AddEntry(self.hhistHalf,"L1Calo Half-Gain","p");
        self.leg.Draw();
        
        print('')
        self.c1.Print("%s/historyTrigger.ps" % (self.dir))

        print('')
        print('Min run number:', self.minX)
        print('Max run number:', self.maxX)
        print('')

    def ProcessRegion(self,region):
        if region.GetEvents() == 0:
            return
                 
        newevents = set()
        #if 'gain' not in region.GetHash():
        #    for event in region.GetEvents():
        #        if event.runType != 'staging':
        #            newevents.add(event)
        #    region.SetEvents(newevents)
        #    return

        for event in region.GetEvents():
            
            f, t = self.getFileTree('tileCalibL1Calo_%s_%s.%s.root' % (event.run.runNumber,'L1Calo',0), 'h3000')
            if [f, t] != [None, None]:

                self.samples.add(event)

            if [f, t] == [None, None]:
                print('File missing for run: ',event.run.runNumber)
                return False
            else:
                self.ftDict[event.run.runNumber] = [f, t]
                #print f, t
                if (event.run.runNumber > self.maxX):
                    k = datetime.datetime.strptime(event.run.time, "%Y-%m-%d %H:%M:%S")
                    self.maxXtime = ('%s/%s' % (str(k)[5:7],str(k)[2:4]))
                    self.maxX = event.run.runNumber
                if (event.run.runNumber < self.minX):
                    k = datetime.datetime.strptime(event.run.time, "%Y-%m-%d %H:%M:%S")
                    self.minXtime = ('%s/%s' % (str(k)[5:7],str(k)[2:4]))
                    self.minX = event.run.runNumber
                if event.run.runNumber not in self.run_list:
                    self.run_list.append(event.run.runNumber)

        # check if the run list array is empty
        if not self.run_list:
            return
        
        if ((self.run_list) and (len(self.run_list) < 3)):
            return

        if (len(self.run_list) < 6):
            self.nRunsToUse = 3
        else:
            factor = 2/float(3)   # 2/3 of the runs
            self.nRunsToUse = int(round(factor*len(self.run_list)))

        # Either lowgain or highgain should work
        if 'lowgain' in region.GetHash():
            for event in region.GetEvents():
                
                self.events.add(event)
                # Get data from noise tree
                [f, t] = self.ftDict[event.run.runNumber]
                t.GetEntry(0) 
                
                # Get indices
                [part, mod, chan, gain] = region.GetNumber()
            
                index = self.get_index(part, mod - 1, chan)
                #print index
            
                event.data['meanTile']     =  t.meanTile[index]
                event.data['rmsTile']      =  t.rmsTile[index]
                event.data['ietaTile']     =  t.ietaTile[index]
                event.data['iphiTile']     =  t.iphiTile[index]
                event.data['ipmtTile']     =  t.ipmtTile[index]
                event.data['nEvtTile']     =  t.nEvtTile[index]
                event.data['meanL1Calo']   =  t.meanL1Calo[index]
                event.data['rmsL1Calo']    =  t.rmsL1Calo[index]
                event.data['ietaL1Calo']   =  t.ietaL1Calo[index]
                event.data['iphiL1Calo']   =  t.iphiL1Calo[index]
                event.data['ipmtL1Calo']   =  t.ipmtL1Calo[index]
                event.data['nEvtL1Calo']   =  t.nEvtL1Calo[index]

                event.data['isHalfGain'] = 0
                event.data['isNoGain']   = 0

                event.data['partition']  = part
                event.data['module']     = mod
                event.data['chan']       = chan
        
                event.data['changeStat']   = False

                event.data['DACvalue']     =  t.DACvalue
                self.zeroGainCut = .1*event.data['DACvalue']
                self.halfGainCut  = .5*event.data['DACvalue']   
        
                if (event.data['nEvtL1Calo'] != 0):
                        if (event.data['meanL1Calo'] < self.halfGainCut):
                                event.data['badChanL1Calo'] = 1 
                        else:
                                event.data['badChanL1Calo'] = 0

                        if ((event.data['meanL1Calo'] < self.zeroGainCut) and (event.data['meanTile'] > self.halfGainCut)):
                                event.data['zeroChanL1Calo'] = 1
                                self.deadCh.append(index)
                                if (self.deadCh.count(index) == self.nRunsToUse):
                                       event.data['isNoGain'] = 1
                        else:
                                event.data['zeroChanL1Calo'] = 0

                        if (((event.data['meanL1Calo'] > self.zeroGainCut) and (event.data['meanL1Calo'] < self.halfGainCut)) and (event.data['meanTile'] > self.halfGainCut)):
                                event.data['halfChanL1Calo'] = 1
                                self.halfCh.append(index)
                                if (self.halfCh.count(index) == self.nRunsToUse):
                                        event.data['isHalfGain'] = 1 
                        else:
                                event.data['halfChanL1Calo'] = 0
                else:
                        event.data['badChanL1Calo']  = 0
                        event.data['zeroChanL1Calo'] = 0
                        event.data['halfChanL1Calo'] = 0 

                if (event.data['nEvtTile'] != 0):
                        if (event.data['meanTile'] < self.halfGainCut):
                                event.data['badChanTile'] = 1 
                        else:
                                event.data['badChanTile'] = 0

                        if (event.data['meanTile'] < self.zeroGainCut):
                                event.data['zeroChanTile'] = 1 
                        else:
                                event.data['zeroChanTile'] = 0

                        if ((event.data['meanTile'] > self.zeroGainCut) and (event.data['meanTile'] < self.halfGainCut)):
                                event.data['halfChanTile'] = 1 
                        else:
                                event.data['halfChanTile'] = 0
                else:
                        event.data['badChanTile']  = 0
                        event.data['zeroChanTile'] = 0
                        event.data['halfChanTile'] = 0

                newevents.add(Event(event.run, event.data))

        if 'lowgain' in region.GetHash():
            maxrun =0
            for run in self.run_list:
                if maxrun<event.run.runNumber:
                    maxrun = event.run.runNumber
                    
            for event in region.GetEvents():

                event.data['isNoGainL1']   = 0
                event.data['isHalfGainL1'] = 0
                if event.run.runNumber == maxrun:
                        # Get indices
                        [part, mod, chan, gain] = region.GetNumber()
                        index = self.get_index(part, mod - 1, chan)
                        if (self.deadCh.count(index) == 3):
                                event.data['isNoGainL1'] = 1
                        if (self.halfCh.count(index) == 3):
                                event.data['isHalfGainL1'] = 1
                        newevents.add(Event(event.run,event.data))
                        newevents.add(event)
        region.SetEvents(newevents)
        return

                #region.SetEvents(newevents)
                #event.data['badChan'] = self.bad
                #print 'self.bad: ', self.bad

