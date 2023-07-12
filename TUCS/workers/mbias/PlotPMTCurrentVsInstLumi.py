from src.GenericWorker import *
import src.MakeCanvas
import time
import numpy
import src.stats
import math


# class to test plotting of mbias data,  PMT current vs. Lumiblock for single runs and special PMT
# class is called by PlotPMTCurrentvsLumiBlock.py in macros/mbias/
class PlotPMTCurrentVsInstLumi(GenericWorker):
    "A plot worker for MBias"
    
    def __init__(self, checkCell=False, num_average=1):
        self.dir = getPlotDirectory() #where to save the plots
	    
        self.checkCell =checkCell #handle cell info not just single pmts
	#will be histos later
        self.CurrentVsInstLumi = None
	# used events (one per run)
        self.eventsList = []
	#detector region
	#corresponding name
        self.regionName = None
        self.plot_name = None
        #self.Runnumber = None
        self.num_average = num_average

    def ProcessRegion(self, region):
	
        if region.GetEvents() == set():
            return
		
        Name = region.GetHash()
        self.regionName = Name[8:19] # shorter name without TILECAL_ in front
	
        if self.checkCell: self.regionName = self.checkCell
	
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
	#self.c1.Clear()
        #self.c1.cd()
        c = ROOT.TCanvas('c','',700,500)
		
	#for histogram building
        Maximum = []
        Minimum = []
        MaxLumi = []
        MinLumi = []
        pairs = []
        PMTCurrent = None
        LumiBlock = None
	
        for event in self.eventsList:

            print('Run', event.run.runNumber)
            if  event.run.runNumber>260000: continue
            print(len(event.run.data['LumiBlock']))
            if len(event.run.data['LumiBlock'])==0 or event.run.runNumber==206299: #no lumi-file for this run
                continue   
	    
	    # get files with info on inst. lumi for given lumiblock
            filename = '/afs/cern.ch/atlas/www/GROUPS/DATAPREPARATION/DataSummary/2012/rundata/run%i/run%i.root' % (event.run.runNumber, event.run.runNumber)
            print(filename)
            file = TFile(filename,'READ' )
            file.cd()
            histoFile = file.Get('lumi_lhcall_del')
	   
            #self.Runnumber = str(event.run.runNumber)
	   
            maximum = 0.0
            maxlumi = 0.0
            minlumi = 1000.0
            minimum = 10000.0
	    
            PMTCurrent = []
            PMTStatus = []
            PMTCurrentHelp = event.run.data['PMTCurrent']
            PMTStatusHelp = event.run.data['PMTStatus']
            LumiBlock = event.run.data['LumiBlock']

            # if cell instead of single pmt, first prepare pmtcurrent vector
            if self.checkCell:
                cellmean = stats()
		#loop over lb entries
                for l in range(len(PMTCurrentHelp)):
		    #loop over modules in A and C-side	
                    count=0
                    for m in range(len(PMTCurrentHelp[l])):
                        if PMTStatusHelp[l][m]!=0: continue
                        count+=1
                        cellmean.fill(PMTCurrentHelp[l][m])
                    if count==0: PMTCurrent.append(0.0)
                    else: PMTCurrent.append(cellmean.mean())
                    PMTStatus.append(0)
                    cellmean.reset()	
		    		    
            else:
                PMTCurrent = event.run.data['PMTCurrent']
                PMTStatus = event.run.data['PMTStatus']
		
	    # this is for calculating means over num_average consecutive entries of PMTCurrents
            counter=0
            meanPMT = stats()
            meanLumi = stats()
	    
            for j in range(len(PMTCurrent)): # find extreme values for building histograms
		
                if PMTStatus[j]!=0: continue
                counter+=1
                InstLumi = histoFile.GetBinContent(LumiBlock[j]+1)
		#find extreme values for histogram
                if PMTCurrent[j]>maximum:
                    maximum = PMTCurrent[j]
                if PMTCurrent[j]<minimum:
                    minimum = PMTCurrent[j]
                if InstLumi>maxlumi:
                    maxlumi = InstLumi
                if InstLumi< minlumi:
                    minlumi = InstLumi
		##fill stats
                meanPMT.fill(PMTCurrent[j])
                meanLumi.fill(InstLumi)
                if counter == len(PMTCurrent)-1: 
                    counter = 10000
                if counter%self.num_average!=0: continue
		#if ten values: fill vector
		#print "counter %i, mean Lumi %f, mean PMTCurrent %f" % (counter, meanLumi.mean(), meanPMT.mean())
                pairs.append([meanLumi.mean(),meanPMT.mean()]) # fill 2d histo
		#pairs.append([InstLumi,PMTCurrent[j]]) # fill 2d histo
                meanLumi.reset()
                meanPMT.reset()
			   
            del meanLumi, meanPMT
	    		   
            Maximum.append(maximum)
            Minimum.append(minimum)
            MaxLumi.append(maxlumi)
            MinLumi.append(minlumi)
	               	   		 
        minimum = min(Minimum)
        maximum = max(Maximum)
        maxlumi = max(MaxLumi)
        minlumi = min(MinLumi)
		
        self.CurrentVsInstLumi = ROOT.TH2F("CurrentVsInstLumi",'', 30, minlumi, maxlumi, 30, minimum-0.5,maximum+5.)
        fitplot = ROOT.TH2F("fitplot",'', 25, minlumi+2, maxlumi, 30, minimum-0.5,maximum+5.)	
		
        for i in range(len(pairs)):
            if pairs[i][1]==0.0: continue
            self.CurrentVsInstLumi.Fill(pairs[i][0],pairs[i][1]) # fill 2d histogram
            if pairs[i][0]>=minlumi+2:
                fitplot.Fill(pairs[i][0],pairs[i][1]) # histogram to be fitted later
	       
        profilex = self.CurrentVsInstLumi.ProfileX()       
	       
        self.CurrentVsInstLumi.Draw("COLZ")
        profilex.Draw("SAME")
        ROOT.gPad.SetRightMargin(0.2)
        self.CurrentVsInstLumi.GetXaxis().SetTitle("Inst. Lumi [10^{33}cm^{-2}s^{-1}]")
        self.CurrentVsInstLumi.GetYaxis().SetTitle("Current %s [nA]" % (self.regionName))
        self.CurrentVsInstLumi.GetYaxis().SetTitleOffset(1.7)
        self.CurrentVsInstLumi.GetZaxis().SetTitle("Events")
	   		 
        c.Modified()
        c.Update()
	   
        self.plot_name = "CurrentVsLumi_MBias" 
        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/%s_%s.eps" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/%s_%s.png" % (self.dir,self.plot_name, self.regionName))
        del c, profilex, pairs
        self.CurrentVsInstLumi.Delete()
	
	# do plot plus fit plus ratio ##############################################################################
        cfit = ROOT.TCanvas('c','',700,500)
        cfit.cd()
        pad1 = ROOT.TPad("pad1","pad1",0,0.420,.99,1)
        pad1.SetBottomMargin(0)
        pad1.Draw()
        pad1.cd()
	
        profile = fitplot.ProfileX()
        profile.Draw()
        pol1 = ROOT.TF1("pol1","pol1",minlumi+2, maxlumi)
        profile.Fit('pol1',"r")
        #pol1 = profile.GetFunction('pol1')
        pol1.Draw("SAME")
        pol1.SetLineColor(ROOT.kRed)
	
        legend = ROOT.TLegend(0.2,0.65,0.55,0.9)
        legend.SetFillStyle(0)
        legend.SetFillColor(0)
        legend.SetBorderSize(0)
        legend.AddEntry(profile, "Data 2012, #sqrt{s}=8 TeV", "ep")
        legend.AddEntry(pol1, "Pol1 fit: f(x)= %1.2fx+%1.2f" %(pol1.GetParameter(1), pol1.GetParameter(0)),'l' )
        legend.Draw()
	    
        l1 = TLatex()
        l1.SetNDC()
        l1.SetTextSize(0.06)   
        l1.DrawLatex(0.2,0.6, "#chi^{2}/ndf=%1.1f" % (pol1.GetChisquare()/pol1.GetNDF()))  
	    
	    
        profile.GetYaxis().SetTitle("Current %s [nA]" % (self.regionName))
        profile.GetYaxis().SetTitleOffset(1.0)
        profile.GetYaxis().SetTitleSize(0.07)
        profile.GetYaxis().SetLabelSize(0.075)
        profile.GetXaxis().SetLabelColor(0)
	
        cfit.cd()    
	    
        pad2 = ROOT.TPad('pad2','pad2',0,0.01, .99, 0.395)
        pad2.SetTopMargin(0)
        pad2.SetBottomMargin(0.3)
        #pad2.SetGrid(0,1)
        pad2.SetGridy()
        pad2.Draw()
        pad2.cd()
	
	#avoid crash
        ROOT.SetOwnership(pad1, false)
        ROOT.SetOwnership(pad2, false)

        fitfunc = ROOT.TH1F("fitfunc","", 1 ,minlumi+2, maxlumi)
        fitfunc.SetBinContent(1,1)
        fitfunc.SetLineColor(ROOT.kRed)
        fitfunc.Draw()
        fitfunc.GetXaxis().SetLabelSize(0.1)
        fitfunc.GetYaxis().SetTitleSize(0.12)
        fitfunc.GetXaxis().SetTitleSize(0.12)
        fitfunc.GetYaxis().SetTitleOffset(0.57)
        fitfunc.GetYaxis().CenterTitle()
        fitfunc.GetXaxis().SetTitleOffset(1.1)
        fitfunc.GetYaxis().SetLabelSize(0.1)
        fitfunc.GetYaxis().SetNdivisions(504)
        fitfunc.GetYaxis().SetDecimals()
        fitfunc.SetMinimum(0.982)
        fitfunc.SetMaximum(1.018)
	    
        ratiohist = ROOT.TH1F("ratiohist","",25, minlumi+2, maxlumi)
        for i in range(ratiohist.GetNbinsX()):
            x = profile.GetBinContent(i+1)
            if x==0.: continue
            y = pol1.Eval(profile.GetBinCenter(i+1))
            quotient = x/y
            x_err = profile.GetBinError(i+1)
            y_err = 0.0 #math.sqrt((pol1.GetParError(1)*x)**2+pol1.GetParError(0)**2)
            quoerr = quotient*math.sqrt((x_err/x)**2+(y_err/y)**2)
            ratiohist.SetBinContent(i+1, quotient)
            ratiohist.SetBinError(i+1, quoerr)
	    
        ratiohist.Draw("SAMEp")
        fitfunc.GetXaxis().SetTitle("Inst. Luminosity [10^{33}cm^{-2}s^{-1}]")
        fitfunc.GetYaxis().SetTitle("Current/f(x)")
	
	# save plot, several formats...
        cfit.Print("%s/%s_%s_ratioPlot.root" % (self.dir, self.plot_name, self.regionName))
        cfit.Print("%s/%s_%s_ratioPlot.eps" % (self.dir, self.plot_name, self.regionName))
        cfit.Print("%s/%s_%s_ratioPlot.png" % (self.dir,self.plot_name, self.regionName))
	#####################################################################################################################
	    
        del ratiohist#, fitfunc
        del cfit #, profile, pol1, fitplot
        del self.eventsList
	   
