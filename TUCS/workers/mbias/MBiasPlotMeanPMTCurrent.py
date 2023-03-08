from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
import numpy

# class to test plotting of mbias data, e.g. mean PMT current for 4*48 cells 
# class is called by PlotMeanPMTCurrent.py in macros/mbias/
class MBiasPlotMeanPMTCurrent(GenericWorker):
    "A plot test worker for MBias"
    
    def __init__(self, lb):
        self.dir = getPlotDirectory() #where to save the plots
	    
        self.lb = lb #which lumiblock should be considered for average
	#will be histos later
        self.pmtCurrentEBA = None
        self.pmtCurrentEBC = None
        self.pmtCurrentLBA = None
        self.pmtCurrentLBC = None			
        # used events (one per run)
        self.eventsList = []
        #detector region
	#corresponding name
	#self.regionName = None
	

    def ProcessRegion(self, region):
	
        if region.GetEvents() == set():
            return
	
        print("Plot for %s" % region.GetHash())
        print(region.GetNumber())
        print(region.GetName())	
		
	#Name = region.GetHash()
	#self.regionName = Name[8:19] # shorter name without TILECAL_ in front
	
        for event in region.GetEvents():
            if event.run.runType == 'Las' or event.run.runType == 'Phys':
                self.eventsList.append(event)
                #print 'Run ', event.run.runNumber
		    

    def	ProcessStop(self):
	    	    
	#self.c1.Clear()
        #self.c1.cd()
        c = ROOT.TCanvas('c','',1000,1000)
		
	#for histogram building
        Maximum = []
        Minimum = []
	
        LumiBlock = None
        meanCurrents = [] # if more than one event (should not be the case)
        runName = None 
	
        for event in self.eventsList:

            print('Run', event.run.runNumber)
            print("TIME", event.run.time)
            runName = str(event.run.runNumber)
            print(len(event.run.data['LumiBlock']))
            if len(event.run.data['LumiBlock'])==0:
                continue   
	   
            maximum = [0.0, 0.0, 0.0, 0.0]
            minimum = [10000., 1000., 1000., 1000.]
	   
	   
	    #PMTCurrent = event.run.data['PMTCurrent']
            LumiBlock = event.run.data['LumiBlock'][self.lb]
            MeanCellCurrents = numpy.zeros((4,48))
            count = 0
	   
            for i in range(4):	
                for j in range(48):
                    count = 0	
                    for l in range(64):
                        MeanCellCurrents[i][j]+=event.run.data['PMTCurrent'][self.lb][i][l][j] #add the currents for cell from all modules
                        if  event.run.data['PMTCurrent'][self.lb][i][l][j]!=0.0:
                            count+=1
				
				
                    if count!=0: MeanCellCurrents[i][j] = MeanCellCurrents[i][j]/float(count) # or divided by count
                    else: MeanCellCurrents[i][j] = MeanCellCurrents[i][j]/64.
		    
		    #if(MeanCellCurrents[i][j]>maximum[i]): # find extreme values for building histograms
			    #maximum[i]= MeanCellCurrents[i][j]
		    #if(MeanCellCurrents[i][j]<minimum[i]):
			    #minimum[i]= MeanCellCurrents[i][j]
			    
            meanCurrents.append(MeanCellCurrents)

	    #Maximum.append(maximum)
	    #Minimum.append(minimum) 	    	 
        print('events: ', len(meanCurrents))   	   		 
	#print "events ", len(Maximum) 			 
	#minimumLBA = min(Minimum[0][0])
	#maximumLBA = max(Maximum[0][0])
	
	#minimumLBC = min(Minimum[0][1])
	#maximumLBC = max(Maximum[0][1])
	
	#minimumEBA = min(Minimum[0][2])
	#maximumEBA = max(Maximum[0][2])
	
	#minimumEBC = min(Minimum[0][3])
	#maximumEBC = max(Maximum[0][3])
	
        self.pmtCurrentLBA = ROOT.TH1F("pmtCurrentLBA","",48,0,48)
        self.pmtCurrentLBC = ROOT.TH1F("pmtCurrentLBC","",48,0,48)
        self.pmtCurrentEBA = ROOT.TH1F("pmtCurrentEBA","",48,0,48)
        self.pmtCurrentEBC = ROOT.TH1F("pmtCurrentEBC","",48,0,48)	
		
        for j in range(48):
            print(j, meanCurrents[0][2][j])
            self.pmtCurrentLBA.SetBinContent(j+1,meanCurrents[0][0][j]) 	
            self.pmtCurrentLBC.SetBinContent(j+1,meanCurrents[0][1][j])
            self.pmtCurrentEBA.SetBinContent(j+1,meanCurrents[0][2][j])
            self.pmtCurrentEBC.SetBinContent(j+1,meanCurrents[0][3][j])
					 
        c.Divide(2,2)
        c.cd(1)
	     
        self.pmtCurrentLBA.Draw("P")
        ROOT.gPad.SetGridy()
        ROOT.gPad.SetGridx()
        self.pmtCurrentLBA.SetMinimum(-0.5)
        self.pmtCurrentLBA.GetXaxis().SetTitle("Channel number" )
        self.pmtCurrentLBA.GetYaxis().SetTitle("Mean of PMT current") 
        self.pmtCurrentLBA.GetYaxis().SetTitleOffset(1.3)
	 
        lumi = ROOT.TLatex(0.2,0.8, "lb"+str(LumiBlock))
        lumi.SetNDC()
        lumi.SetTextSize(0.04)
        lumi.Draw()
	
        partition = ROOT.TLatex(0.2,0.96, "LBA cells")
        partition.SetNDC()
        partition.SetTextSize(0.045)
        partition.Draw()
				 
        c.cd(2)
	   		 
        self.pmtCurrentLBC.Draw("P")
        self.pmtCurrentLBC.SetMinimum(-0.5)
        ROOT.gPad.SetGridy()
        ROOT.gPad.SetGridx()
        self.pmtCurrentLBC.GetXaxis().SetTitle("Channel number")
        self.pmtCurrentLBC.GetYaxis().SetTitle("Mean of PMT current") 
        self.pmtCurrentLBC.GetYaxis().SetTitleOffset(1.3)
	 
        partition1 = ROOT.TLatex(0.2,0.96, "LBC cells")
        partition1.SetNDC()
        partition1.SetTextSize(0.045)
        partition1.Draw()   		 
			 
        c.cd(3)
				 
        self.pmtCurrentEBA.Draw("P")
        self.pmtCurrentEBA.SetMinimum(-0.5)
        ROOT.gPad.SetGridy()
        ROOT.gPad.SetGridx()
        self.pmtCurrentEBA.GetXaxis().SetTitle("Channel number")
        self.pmtCurrentEBA.GetYaxis().SetTitle("Mean of PMT current") 
        self.pmtCurrentEBA.GetYaxis().SetTitleOffset(1.3)
	
        partition2 = ROOT.TLatex(0.2,0.96, "EBA cells")
        partition2.SetNDC()
        partition2.SetTextSize(0.045)
        partition2.Draw()   		 
				 
        c.cd(4)
	
        self.pmtCurrentEBC.Draw("P")
        self.pmtCurrentEBC.SetMinimum(-0.5)
        ROOT.gPad.SetGridy()
        ROOT.gPad.SetGridx()
        self.pmtCurrentEBC.GetXaxis().SetTitle("Channel number")
        self.pmtCurrentEBC.GetYaxis().SetTitle("Mean of PMT current") 
        self.pmtCurrentEBC.GetYaxis().SetTitleOffset(1.3)
	 
        partition3 = ROOT.TLatex(0.2,0.96, "EBC cells")
        partition3.SetNDC()
        partition3.SetTextSize(0.045)
        partition3.Draw()   					 
				 
			 
        c.Modified()
        c.Update()
	   
        self.plot_name = "MeanCurrent_MBias%s" % runName 
        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir, self.plot_name, str(self.lb)))
        c.Print("%s/%s_%s.eps" % (self.dir, self.plot_name, str(self.lb)))
        c.Print("%s/%s_%s.png" % (self.dir,self.plot_name, str(self.lb)))
        del c
	    
        self.pmtCurrentLBA.Delete()
        self.pmtCurrentLBC.Delete()
        self.pmtCurrentEBA.Delete()
        self.pmtCurrentEBC.Delete()
        del self.eventsList
	    
