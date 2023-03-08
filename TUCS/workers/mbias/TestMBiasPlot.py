from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
import numpy

# class to test plotting of mbias data, e.g. PMT current vs., Lumiblock for specific run
# class is called by plotTest.py in macros/mbias/plotTest.py
class TestMBiasPlot(GenericWorker):
    "A plot test worker for MBias"
    c1 = None
    
    def __init__(self):
        self.dir = getPlotDirectory() #where to save the plots
        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
	    
        print(self.c1.GetName())
        self.c1.cd()
	
	#will be histos later
        self.pmtCurrent = None
        self.CurrentVsLumiBlock = None
	# used events (one per run)
        self.eventsList = []


    def ProcessRegion(self, region):
	
        if region.GetEvents() == set():
            return
	
        print("Plot for %s, but doesn't mean anything for now, use all PMTs" % region.GetHash())
	
        for event in region.GetEvents():
            # and only look at laser runs, for now
            if event.run.runType == 'Las' or event.run.runType == 'Phys':
                self.eventsList.append(event)
		    
		    
    def	ProcessStop(self):
	    	    
        ROOT.gStyle.SetPalette(1)	    
	#self.c1.Clear()
        #self.c1.cd()
        c = ROOT.TCanvas('c','',700,500)	    
		    
        for event in self.eventsList:
            EventNumber = event.run.data['LumiBlock'][-1] # last element of LumiBlock vector
            maximum = 0.0
            minimum = 10000.0
            PMTCurrent = []
            LumiBlock = []
            for i in range(len(event.run.data['LumiBlock'])): # loop over run entries
                currentVector = event.run.data['PMTCurrent'][i].flatten()# for now, take just all PMTs, don't care about position
                PMTCurrent.append(currentVector)
                for j in range(len(currentVector)):
                    if currentVector[j]>maximum:
                        maximum = currentVector[j]
                    if currentVector[j]<minimum:
                        minimum = currentVector[j]  	   	 
		    	 
            self.pmtCurrent = ROOT.TH1F("pmtCurrent","",50,minimum-0.5,maximum+5.)
            self.CurrentVsLumiBlock = ROOT.TH2F("CurrentVsLumiBlock",'',EventNumber+2, 0, EventNumber+2, 50, minimum-0.5,maximum+5.)
	   		 
            for i in range(len(PMTCurrent)):
                for j in range(len(PMTCurrent[0])):   
                    self.pmtCurrent.Fill(PMTCurrent[i][j]) # fill PMTCurrent histo for all PMTs
                    if PMTCurrent[i][j]!=0.:
                        self.CurrentVsLumiBlock.Fill(event.run.data['LumiBlock'][i],PMTCurrent[i][j]) # fill 2d histo
		    		 
	   #c.Divide(2,1)
	   #c.cd(1)
	     
	   #pmtCurrent.Draw()
	   #ROOT.gPad.SetLogy()
	   #pmtCurrent.GetXaxis().SetTitle("PMTCurrent all")
	   #pmtCurrent.GetYaxis().SetTitle("Events")  
	   		 
	   #c.cd(2)
	   		 
            CurrentVsLumiBlock.Draw("COLZ")
            ROOT.gPad.SetRightMargin(0.2)
            CurrentVsLumiBlock.GetXaxis().SetTitle("LumiBlock")
            CurrentVsLumiBlock.GetYaxis().SetTitle("PMTCurrent all")
            CurrentVsLumiBlock.GetYaxis().SetTitleOffset(1.7)
            CurrentVsLumiBlock.GetZaxis().SetTitle("Events")
	   		 
            c.Modified()
            c.Update()
	   
            self.plot_name = "TestPlot_MBias_%s" % ( str(event.run.runNumber))
            # save plot, several formats...
            c.Print("%s/%s.root" % (self.dir, self.plot_name))
            c.Print("%s/%s.eps" % (self.dir, self.plot_name))
            c.Print("%s/%s.png" % (self.dir,self.plot_name))
	    
        self.pmtCurrent.Delete()
        self.CurrentVsLumiBlock.Delete()
        del self.c1
        del c
	    
