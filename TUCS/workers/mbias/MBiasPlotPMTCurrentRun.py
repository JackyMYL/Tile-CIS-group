from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
import numpy

# class to test plotting of mbias data, e.g. PMT current vs., Lumiblock for all runs but special PMT
# class is called by plotPMTCurrentDistr.py in macros/mbias/
class MBiasPlotPMTCurrentRun(GenericWorker):
    "A test plotting worker for MBias"
    
    def __init__(self, module):
        self.dir = getPlotDirectory() #where to save the plots
	    
	#will be histos later
        self.pmtCurrent1 = None # list, one plot for each run
        self.pmtCurrent2 = None # two PMT channels for one module
	# used events (one per run)
        self.eventsList = []
	#detector region
	#corresponding name
        self.regionName = module
	
        self.module = None
        self.part = None
        if(module=='A13'):
            self.module = [10,11] #channels belonging to module A13
            self.part = 2
        if(module=='D5'):
            self.module = [16,17] #channels belonging to module D5	   
            self.part = 2		

    def ProcessRegion(self, region):
	
        if region.GetEvents() == set():
            return
	
	#Name = region.GetHash()
	#self.regionName = Name[8:19] # shorter name without TILECAL_ in front
	
        for event in region.GetEvents():
            # and only look at laser runs, for now
            if event.run.runType == 'Las' or event.run.runType == 'Phys':
                self.eventsList.append(event)
		#print 'Run ', event.run.runNumber
		    
		    
    def	ProcessStop(self):
	    	    
	#self.c1.Clear()
        #self.c1.cd()
        c = ROOT.TCanvas('c','',1000,500)
		
	#for histogram building
        EventNumber = []
        Maximum = []
        Minimum = []
        runNumber = 0
	#pairs = []
	
	
        for event in self.eventsList:

            print('Run', event.run.runNumber)
            runNumber = event.run.runNumber
            print(len(event.run.data['LumiBlock']))
            if len(event.run.data['LumiBlock'])==0:
                continue   
	   
            EventNumber.append(event.run.data['LumiBlock'][-1]) # last element of LumiBlock vector
            maximum = 0.0
            minimum = 10000.0
	    
            PMTCurrent1 = []
            PMTCurrent2 = []
	   
	    # get pmt current averaged over phi
            for lb in range(len(event.run.data['LumiBlock'])):
                pmtcurrent1 = 0.
                pmtcurrent2 = 0.
                count1 = 0.
                count2 = 0.
                for m in range(64):
                    if event.run.data['PMTCurrent'][lb][self.part][m][16]!=0:
                        pmtcurrent1+=event.run.data['PMTCurrent'][lb][self.part][m][self.module[0]]/event.run.data['PMTCurrent'][lb][self.part][m][16]
                    if event.run.data['PMTCurrent'][lb][self.part][m][17]!=0:	    
                        pmtcurrent2+=event.run.data['PMTCurrent'][lb][self.part][m][self.module[1]]/event.run.data['PMTCurrent'][lb][self.part][m][17]
                    if event.run.data['PMTCurrent'][lb][self.part][m][self.module[0]]!=0. and event.run.data['PMTCurrent'][lb][self.part][m][16]!=0:
                        count1+=1.
                    if event.run.data['PMTCurrent'][lb][self.part][m][self.module[1]]!=0. and event.run.data['PMTCurrent'][lb][self.part][m][17]!=0:
                        count2+=1.
                print(count1, count2)
                if count1!=0.:	  
                    PMTCurrent1.append(pmtcurrent1/count1)
                    PMTCurrent2.append(pmtcurrent2/count2)
                else:
                    PMTCurrent1.append(0.0)
                    PMTCurrent2.append(0.0)		
		 
            LumiBlock = event.run.data['LumiBlock']
	   
            for j in range(len(PMTCurrent1)): # find extreme values for building histograms
                if PMTCurrent1[j]>maximum:
                    maximum = PMTCurrent1[j]
                if PMTCurrent1[j]<minimum:
                    minimum = PMTCurrent1[j]  	   	 
	   
            Maximum.append(maximum)
            Minimum.append(minimum) 	    	 
           	   		 
	    #for i in range(len(PMTCurrent)):
		#pairs.append([LumiBlock[i],PMTCurrent[i]]) # fill 2d histo
		
        minimum = min(Minimum)
        maximum = max(Maximum)
	
        eventnumber = max(EventNumber)
	#print minimum, maximum	
        helppmtCurrent1 = ROOT.TH1F("helppmtCurrent1","",50,minimum-0.2,maximum+0.2)
        helppmtCurrent2 = ROOT.TH1F("helppmtCurrent2","",50,minimum-0.2,maximum+0.2)
	
	#self.CurrentVsLumiBlock = ROOT.TH2F("CurrentVsLumiBlock",'',eventnumber+2, 0, eventnumber+2, 50, minimum-0.5,maximum+5.)
		
        for i in range(len(PMTCurrent1)):
            helppmtCurrent1.Fill(PMTCurrent1[i]) # fill pmtcurrents
            helppmtCurrent2.Fill(PMTCurrent2[i]) # fill pmtcurrents
	    #self.CurrentVsLumiBlock.Fill(pairs[i][0],pairs[i][1]) # fill 2d histogram	
	   
        mean1 = helppmtCurrent1.GetMean()  
        mean2 = helppmtCurrent2.GetMean()
	
        rms1 = helppmtCurrent1.GetRMS()
        rms2 = helppmtCurrent2.GetRMS()
	
        mini1 = mean1-3.*rms1
        mini2 = mean2-3.*rms2
        maxi1 = mean1+3.*rms1
        maxi2 = mean2+3.*rms2
	
        self.pmtCurrent1 = ROOT.TH1F("pmtCurrent1","",50, mini1, maxi1)
        self.pmtCurrent2 = ROOT.TH1F("pmtCurrent2","",50, mini2, maxi2)
			   
        for i in range(len(PMTCurrent1)):
            self.pmtCurrent1.Fill(PMTCurrent1[i]) # fill pmtcurrents
            self.pmtCurrent2.Fill(PMTCurrent2[i]) # fill pmtcurrents
			   	   
        c.Divide(2,1)
        c.cd(1)	    		 
	     
        pmtCurrent1.Draw()
        #ROOT.gPad.SetLogy()
        pmtCurrent1.GetXaxis().SetTitle("ratio PMTCurrent ch %s/ch 16" % (self.module[0])) 
        pmtCurrent1.GetYaxis().SetTitle("Events") 
        pmtCurrent1.GetYaxis().SetTitleOffset(1.3) 
	   		 
        c.cd(2)
			 
        pmtCurrent2.Draw()
        #ROOT.gPad.SetLogy()
        pmtCurrent2.GetXaxis().SetTitle("ratio PMTCurrent ch %s/ch 17" % (self.module[1])) 
        pmtCurrent2.GetYaxis().SetTitle("Events") 
        pmtCurrent2.GetYaxis().SetTitleOffset(1.3) 
			 
        c.Modified()
        c.Update()
	   
        self.plot_name = "RatioPlot_MBias_%s" % (runNumber) 
        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/%s_%s.eps" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/%s_%s.png" % (self.dir,self.plot_name, self.regionName))
        del c
	    
        self.pmtCurrent1.Delete()
        self.pmtCurrent2.Delete()
        del self.eventsList
	    
