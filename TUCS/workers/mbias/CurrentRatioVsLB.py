from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
import numpy


#   PMT current ratio vs. Lumiblock for single runs and specified PMT/D5
# class is called by plotPMTRatiovsLumiBlock.py in macros/mbias/
class CurrentRatioVsLB(GenericWorker):
    "A plot worker for MBias"
    
    def __init__(self, doRatio=False):
	    
        self.doRatio = doRatio    
        if not self.doRatio:
            return   
	   
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
	
        if not self.doRatio: return
	
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
            ROOT.gStyle.SetPalette(1)

        ROOT.gStyle.SetPalette(1)	    	    
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
                current=0.
                counter=0.		    
                for m in range(len(event.run.data['PMTCurrent'][i])):
                    if event.run.data['PMTCurrent'][i][m]!=0 and event.run.data['IsGood'][i][m]:
                        counter+=1. 
                        current+=event.run.data['PMTCurrent'][i][m]
                PMTCurrent.append(current/counter)	
            LumiBlock = event.run.data['LumiBlock']
	   
        pmtcurrent = array('f', PMTCurrent)
        lumiblock = array('f', LumiBlock)
        self.CurrentVsLumiBlock = TGraph(len(pmtcurrent), lumiblock, pmtcurrent) 
		
        self.CurrentVsLumiBlock.Draw("AP")
        self.CurrentVsLumiBlock.SetMarkerStyle(21)
	#self.CurrentVsLumiBlock.SetMarkerSize(0.1)
        self.CurrentVsLumiBlock.GetXaxis().SetTitle("LumiBlock")
        self.CurrentVsLumiBlock.GetYaxis().SetTitle("Ratio %s/D1" % (self.regionName))
	   
        c.Modified()
        c.Update()
	   
        self.plot_name = "RatioPlot_MBias_%s" %  (self.Runnumber)
	   	
        # save plot, several formats...
        c.Print("%s/%s_%soD1.root" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/%s_%soD1.eps" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/%s_%soD1.png" % (self.dir,self.plot_name, self.regionName))
        del c
	    
        self.CurrentVsLumiBlock.Delete()
        del self.eventsList
	    
        self.DoProfile(x=lumiblock, y=pmtcurrent)
	   
	   	
    def DoProfile(self, x, y):
	    
        minix = 10000.
        maxix = 0.		
        miniy = 10000.
        maxiy = 0.
				
        for i in range(len(x)):
            if x[i]>maxix:
                maxix = x[i]
            if x[i]<minix:
                minix = x[i]
            if y[i]>maxiy:
                maxiy = y[i]
            if y[i]<miniy:
                miniy = y[i]
				
        binsx = (maxix+50.-(minix-50.))/50.
        binsy = (maxiy+0.1-(miniy-0.1))/0.02
        histo = ROOT.TH2F("histo","", int(binsx), minix-50., maxix+50., int(binsy), miniy-0.1, maxiy+0.1)
        for i in range(len(x)):
            histo.Fill(x[i], y[i])	
	   
	   
        profilex = histo.ProfileX()   
        c = ROOT.TCanvas('c','',700,500)
        c.SetRightMargin(0.1)
        histo.Draw("COLZ")
        profilex.Draw("SAME")
        histo.GetXaxis().SetTitle("LumiBlock")
        histo.GetYaxis().SetTitle("Ratio %s/D5" % (self.regionName))
	
        c.Modified()
        c.Update()
	
	
	# save plot, several formats...
        c.Print("%s/2D%s_%soD1.root" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/2D%s_%soD1.eps" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/2D%s_%soD1.png" % (self.dir,self.plot_name, self.regionName))
