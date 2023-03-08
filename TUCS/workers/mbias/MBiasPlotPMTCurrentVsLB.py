from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
import numpy


# class to test plotting of mbias data,  PMT current vs. Lumiblock for single runs and special PMT
# class is called by PlotPMTCurrentvsLumiBlock.py in macros/mbias/
class MBiasPlotPMTCurrentVsLB(GenericWorker):
    "A plot worker for MBias"
    
    def __init__(self):
        self.dir = getPlotDirectory() #where to save the plots
	    
	#will be histos later
        self.CurrentVsLumiBlock = None
	# used events (one per run)
        self.eventsList = []
	#detector region
	#corresponding name
        self.regionName = None
        self.plot_name = None
        self.Runnumber = None
	#what kind of plotting?
	

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
        if os.environ.get('TUCS'):
            ROOT.gROOT.LoadMacro("$TUCS/root_macros/AtlasStyle.C")
            ROOT.SetAtlasStyle()
            ROOT.gROOT.ForceStyle()

 
	#self.c1.Clear()
        #self.c1.cd()
        c = ROOT.TCanvas('c','',700,500)
		
	#for histogram building
        EventNumber = 0
        PMTCurrent = None
        LumiBlock = None
	
        for event in self.eventsList:

            print('Run', event.run.runNumber)
            print(len(event.run.data['LumiBlock']))
            if len(event.run.data['LumiBlock'])==0:
                continue   
	   
            self.Runnumber = str(event.run.runNumber)
	   
            EventNumber = event.run.data['LumiBlock'][-1] # last element of LumiBlock vector
            PMTCurrent = []
            LumiBlock = []
            for i in range(len(event.run.data['PMTCurrent'])):
                if event.run.data['IsGood'][i]:
                    PMTCurrent.append(event.run.data['PMTCurrent'][i])
                    LumiBlock.append(event.run.data['LumiBlock'][i])
	   
        pmtcurrent = array('f', PMTCurrent)
        lumiblock = array('f', LumiBlock)
        self.CurrentVsLumiBlock = TGraph(len(pmtcurrent), lumiblock, pmtcurrent) 
		
        self.CurrentVsLumiBlock.Draw("AP")
        self.CurrentVsLumiBlock.SetMarkerStyle(21)
	#self.CurrentVsLumiBlock.SetMarkerSize(0.1)
        self.CurrentVsLumiBlock.GetXaxis().SetTitle("LumiBlock")
        self.CurrentVsLumiBlock.GetYaxis().SetTitle("PMTCurrent %s [nA]" % (self.regionName))

	   
        c.Modified()
        c.Update()
	   
        self.plot_name = "RegionPlot_MBias_%s" % (self.regionName)

        # save plot, several formats...
        c.Print("%s/%s.root" % (self.dir, self.plot_name ))
        c.Print("%s/%s.eps" % (self.dir, self.plot_name))
        c.Print("%s/%s.png" % (self.dir,self.plot_name))
        del c
	    
        self.CurrentVsLumiBlock.Delete()
        del self.eventsList
	    
