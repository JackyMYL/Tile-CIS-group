from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
import numpy

# class to test plotting of mbias data, e.g. PMT current vs., Lumiblock for all runs but special PMT
# class is called by PlotPMTCurrent.py in macros/mbias/
class MBiasPlotPMTCurrent(GenericWorker):
    "A plot test worker for MBias"
    
    def __init__(self):
        self.dir = getPlotDirectory() #where to save the plots
	    
        #will be histos later
        self.pmtCurrent = None
        self.CurrentVsLumiBlock = None
	# used events (one per run)
        self.eventsList = []
	#detector region
	#corresponding name
        self.regionName = None
	

    def ProcessRegion(self, region):

        if region.GetEvents() == set():
            return
	
        print("Plot for %s" % region.GetHash())
		
        Name = region.GetHash()
        self.regionName = Name[8:19] # shorter name without TILECAL_ in front
	
        for event in region.GetEvents():
            # and only look at laser runs, for now
            if event.run.runType == 'Las' or event.run.runType == 'Phys':
                self.eventsList.append(event)
                #print 'Run ', event.run.runNumber
		    
		    
    def	ProcessStop(self):
	    	    
        ROOT.gStyle.SetPalette(1)	    
	#self.c1.Clear()
        #self.c1.cd()
        c = ROOT.TCanvas('c','',700,500)
		
	#for histogram building
        EventNumber = []
        Maximum = []
        Minimum = []
        pairs = []
	
	
        for event in self.eventsList:

            print('Run', event.run.runNumber)
            print(len(event.run.data['LumiBlock']))
            if len(event.run.data['LumiBlock'])==0:
                continue   
	   
            EventNumber.append(event.run.data['LumiBlock'][-1]) # last element of LumiBlock vector
            maximum = 0.0
            minimum = 10000.0
            PMTCurrent = event.run.data['PMTCurrent']
            LumiBlock = event.run.data['LumiBlock']

            for j in range(len(PMTCurrent)): # find extreme values for building histograms
                if PMTCurrent[j]>maximum:
                    maximum = PMTCurrent[j]
                if PMTCurrent[j]<minimum:
                    minimum = PMTCurrent[j]  	   	 
	   
            Maximum.append(maximum)
            Minimum.append(minimum) 	    	 
           	   		 
            for i in range(len(PMTCurrent)):
                pairs.append([LumiBlock[i],PMTCurrent[i]]) # fill 2d histo
		
        minimum = min(Minimum)
        maximum = max(Maximum)
	
        eventnumber = max(EventNumber)
		
        self.pmtCurrent = ROOT.TH1F("pmtCurrent","",50,minimum-0.5,maximum+5.)
        self.CurrentVsLumiBlock = ROOT.TH2F("CurrentVsLumiBlock",'',eventnumber+2, 0, eventnumber+2, 50, minimum-0.5,maximum+5.)
		
        for i in range(len(pairs)):
            if pairs[i][1]==0.0: continue
            self.pmtCurrent.Fill(pairs[i][1]) # fill pmtcurrents
            self.CurrentVsLumiBlock.Fill(pairs[i][0],pairs[i][1]) # fill 2d histogram	
		    		 
	#c.Divide(2,1)
	#c.cd(1)
	     
	#pmtCurrent.Draw()
	#ROOT.gPad.SetLogy()
	#pmtCurrent.GetXaxis().SetTitle("PMTCurrent %s" % (self.regionName))
	#pmtCurrent.GetYaxis().SetTitle("Events") 
	#pmtCurrent.GetYaxis().SetTitleOffset(1.3) 
	   		 
	#c.cd(2)
	   		 
        CurrentVsLumiBlock.Draw("COLZ")
        ROOT.gPad.SetRightMargin(0.2)
        CurrentVsLumiBlock.GetXaxis().SetTitle("LumiBlock")
        CurrentVsLumiBlock.GetYaxis().SetTitle("PMTCurrent %s" % (self.regionName))
        CurrentVsLumiBlock.GetYaxis().SetTitleOffset(1.7)
        CurrentVsLumiBlock.GetZaxis().SetTitle("Events")
	   		 
        c.Modified()
        c.Update()
	   
        self.plot_name = "RegionPlot_MBias" 
        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/%s_%s.eps" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/%s_%s.png" % (self.dir,self.plot_name, self.regionName))
        del c
	    
        self.pmtCurrent.Delete()
        self.CurrentVsLumiBlock.Delete()
        del self.eventsList
	    
