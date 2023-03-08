from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import src.stats
import time
import numpy
from math import sqrt
from array import *
from src.laser.toolbox import *


# class to plot ratio of cell/D5 of mbias data,  PMT current ratio vs. Time (runnumber)
# class is called by plotPMTsRatiovsTime.py in macros/mbias/
class PlotRatioPMTsVsTime(GenericWorker):
    "An analysis  worker for MBias"
    
    def __init__(self, modnum=64, detector_region=None, refCell="D5"):
        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),'mbias2012','ResponseVariation')
        src.oscalls.createDir(self.dir)

        self.modnum = modnum # how many modules to consider (actually counting from module 0---modnum,
	#will be histos later
        self.pmtCurrent1 = None # list, one plot for each run
        self.RatioPlot = None
        self.RelativeRatio = None
	# used events (one per run)
        self.eventsList = []
        self.refCell = refCell
        self.regionName = "o%s" % (self.refCell)
        #self.mod = None
        self.detector_region=detector_region
        self.PMTool         = LaserTools()
        self.oneside = True

    def ProcessRegion(self, region):
	
        if region.GetEvents() == set():
            return
	
        if not self.detector_region:
            ros, mod, pmt, dummy = region.GetNumber()
#            self.detector_region = self.PMTool.getCellName(ros, mod, pmt)
            print(self.detector_region)
            self.detector_region=region.GetHash()
            self.detector_region=self.detector_region[8:19]
        #self.mod = region.GetNumber()[1]
	#self.regionName = Name[8:19] # shorter name without TILECAL_ in front
	
        for event in region.GetEvents():
            # if event.run.runNumber>215643: continue
            if event.run.runType == 'Las' or event.run.runType == 'Phys':
                self.eventsList.append(event)
                print('Run ', event.run.runNumber)
		    
		    
    def	ProcessStop(self):
		
        ROOT.gStyle.SetPalette(1)	
        if os.environ.get('TUCS'):
            ROOT.gROOT.LoadMacro("$TUCS/root_macros/AtlasStyle.C")
            ROOT.SetAtlasStyle()
            ROOT.gROOT.ForceStyle()

	#for histogram building
        runNumber = [] #runNumbers (with more than 200 lumiblocks)
        date = [] #according time stamp
        Means = []
        Mean2d = []
        MeansGaus = []
        Errors = []
        ErrorsGaus = []
        mean1 =0.
        meangaus=0.
	#pairs = []
	
	#event=run, loop over runs
        for event in self.eventsList:

            print("EVENT: ",event)

            print('Run', event.run.runNumber)
	    #averaging only sensible for more than 200 entries per run
            if(len(event.run.data['LumiBlock'])<200):
                continue   
            if event.run.runNumber==202991 or event.run.runNumber==204769 or event.run.runNumber==208982 or event.run.runNumber==207845 or event.run.runNumber==201289 or event.run.runNumber==207306 or event.run.runNumber==210302: # they have weird numbers 
                continue   
            # if event.run.runNumber>215643: continue # last run on GRL
            print(event.run.time)	   
            print(len(event.run.data['LumiBlock']))
	    #if len(event.run.data['LumiBlock'])==0:
                #continue   
		
            if len(event.run.data['PMTCurrent'][0])==2*self.modnum:
                self.modnum=2*self.modnum
                self.oneside=False	
	   
            maximum = [0.0 for x in range(self.modnum)]
            minimum = [10000.0 for x in range(self.modnum)]
	    
            PMTCurrent1 = []
	   
            # get pmt current ratio averaged over phi
            for lb in range(len(event.run.data['LumiBlock'])):
                pmtcurrent1 = []
                #get values (already ratios) for each module
                for m in range(self.modnum):
                    if event.run.data['PMTCurrent'][lb][m]!=0:
                        pmtcurrent1.append(event.run.data['PMTCurrent'][lb][m])
                    else:
                        pmtcurrent1.append(0.0)
                PMTCurrent1.append(pmtcurrent1)
					
            for j in range(len(PMTCurrent1)): # find extreme values for building histograms
                #loop over modules
                for m in range(self.modnum):
                    if PMTCurrent1[j][m]==0.0:
                        continue	
                    if PMTCurrent1[j][m]>maximum[m]:
                        maximum[m] = PMTCurrent1[j][m]
                    if PMTCurrent1[j][m]<minimum[m]:
                        minimum[m] = PMTCurrent1[j][m]  	   	 
	   
	    #print minimum, maximum
	    #helppmtCurrent1 = []
            means = []
            errors = []
            meansgaus = []
            errorsGaus = []
	   
	    #loop 2 times for both A and C side
            Loops = [1,3]
	    #only one side loop
            if self.oneside:
                Loops = [1,2]
            #print Loops, self.modnum
	    
            for r in range(Loops[0], Loops[1]):
                Range = [self.modnum/2,self.modnum] 
                if r==1:
                    Range = [0,self.modnum/2]
                if self.oneside: Range = [0, self.modnum]
            	
                for m in range(Range[0],Range[1]):
	            #if minimum[m]==10000. and maximum[m]==0.0: #this means, for this module no good entries
		    #continue	   
                    helppmtCurrent1 = ROOT.TH1F("","",70,minimum[m]-5.,maximum[m]+5.)
		
	   	#build means for each module separately	
                    for i in range(len(PMTCurrent1)):
                        if PMTCurrent1[i][m]!=0 and PMTCurrent1[i][m]>0.1:# and PMTCurrent1[i][m]<20.0: # a bit of cleaning...general for all modules
                             helppmtCurrent1.Fill(PMTCurrent1[i][m]) # fill pmtcurrents-ratios	   
			
                    if helppmtCurrent1.GetEntries()<200: #only sensible fits with more than 200 entries
                        continue
			
                    mean1 = helppmtCurrent1.GetMean()
                    meanerror1 = helppmtCurrent1.GetMeanError()  
                    rms1 = helppmtCurrent1.GetRMS()
                    distmean = str(mean1)
                    distmeanerr = str(meanerror1)
                    distrms = str(rms1)
                    distrmserr = str(helppmtCurrent1.GetRMSError())
	
	
	   	    #plot for each run and for each module
                    cfit = ROOT.TCanvas('cfit','',700, 500)
                    #better for plotting
                    mini1 = mean1-7.*rms1
                    maxi1 = mean1+7.*rms1
	   
	   	    #produce plots for each run	
                    self.pmtCurrent1 = ROOT.TH1F("pmtCurrent1","",50, mini1, maxi1)
	   	
                    for i in range(len(PMTCurrent1)):
                        if PMTCurrent1[i][m]!=0 and PMTCurrent1[i][m]> mini1+2*rms1 and PMTCurrent1[i][m]< maxi1-2*rms1: #: #  more refined cut based on inputs...
                             self.pmtCurrent1.Fill(PMTCurrent1[i][m]) # fill pmtcurrents-ratio, 2nd time
			
                    print("entries ", self.pmtCurrent1.GetEntries())
                    self.pmtCurrent1.Fit("gaus")
                    gaus = self.pmtCurrent1.GetFunction("gaus")	
		
                    meangaus = gaus.GetParameter(1)
                    meanerrorgaus = gaus.GetParameter(2)#gaus.GetParError(1)	
			
                    if pmtCurrent1.GetEntries()<200: #only sensible fits with more than 200 entries
                       continue	

                    if meangaus<0.0 or  gaus.GetParameter(2)>0.2*meangaus: # quality requirement on fit 
                       continue

		
	   	    #for global plot at the end#######
                    means.append(mean1) #mean1
	   	    #print "stored mean ", mean1
                    meansgaus.append(meangaus) 
                    stringgaus = str(meangaus)
		
                    errors.append(rms1) # rms1
                    errorsGaus.append(meanerrorgaus)
                    stringerrorg = str(meanerrorgaus)
                    stringRMS = str(gaus.GetParameter(2))
                    stringRMSerror = str(gaus.GetParError(2))
	   	    ##################################
	   
	   
		    #plotting 
                    self.pmtCurrent1.Draw()
                    self.pmtCurrent1.GetXaxis().SetTitle("Ratio PMTCurrent %s/%s (module %i)" % (self.detector_region, self.refCell, m))
                    self.pmtCurrent1.GetYaxis().SetTitle("LumiBlock entries") 
                    self.pmtCurrent1.GetYaxis().SetTitleOffset(1.3)
	    	 
                    gaus.Draw("same")
                    gaus.SetLineColor(ROOT.kRed)
                    l1 = TLatex()
                    l1.SetNDC()
                    l1.SetTextSize(0.04)
                    l1.SetTextColor(ROOT.kRed)
                    l2 = TLatex()
                    l2.SetNDC()
                    l2.SetTextSize(0.04)
                    l2.DrawLatex(0.66,0.85,"Entries "+str(helppmtCurrent1.GetEntries()))
                    l1.DrawLatex(0.66,0.65,"Mean "+stringgaus[:5]+"+/-"+stringerrorg[:5])
                    l1.DrawLatex(0.66,0.6,"RMS "+stringRMS[:5]+"+/-"+stringRMSerror[:5])

                    l2.DrawLatex(0.66,0.8,"Mean "+distmean[:5]+"+/-"+distmeanerr[:5])
                    l2.DrawLatex(0.66,0.75,"RMS "+distrms[:5]+"+/-"+distrmserr[:5])
	   
                    self.plot_name = "Ratio_%i_%s" % (m, event.run.runNumber)
                    cfit.Modified()
                    cfit.Update()
#                    cfit.Print("%s/%s_%s.eps" % (self.dir, self.plot_name, self.regionName))
#                    cfit.Print("%s/%s_%s.png" % (self.dir, self.plot_name, self.regionName))
	   
	   	    
                    del cfit, helppmtCurrent1, gaus
		
                if m==63 and len(means)<61:
                    break 	
            #for global plot at the end with average over all modules
            helpmean = 0.0 #stats()
            #helpmean.reset()
            helperror = 0.0
	    
	    #note: the requirement only makes sense if more than 62 (124) modules are considered
            minmodules=61
            if not self.oneside:
                minmodules=122
	    
            print(event.run.runNumber)
            print("how many modules passed? --> ", len(means))
            if (len(means)<minmodules and self.modnum>=minmodules) or len(means)<1:
                continue
	   
            Mean2d.append(meansgaus)
	    #rather determine spread and rms of a TH1 distribution
	   
#	   ctest2 = ROOT.TCanvas('ctest2','',700,500)
#	   getmean = ROOT.TH1F("getmean","",20,4.,10.)
	   
#	   for i in range(len(means)):
#	       getmean.Fill(meansgaus[i])
	       
#	   Means.append(getmean.GetMean())
#	   Errors.append(getmean.GetMeanError())
	   
#	   getmean.Draw()
#	   ctest2.Print("DistrRatioModule_%i.eps" % (event.run.runNumber))
#	   ctest2.Print("DistrRatioModule_%i.root" % (event.run.runNumber))
#	   del ctest2, getmean
            helpnumber = 0
	    #print getmean.GetMeanError()
            for i in range(len(means)):
                if meansgaus[i]> 2*getmean.GetRMS()+getmean.GetMean() or meansgaus[i]< getmean.GetMean()-2*getmean.GetRMS():#remove outlier modules from mean calculation                                                                    
                    continue
                helpnumber+=1
               ##helpmean.fill(meansgaus[i], 1./(errorsGaus[i]*errorsGaus[i]))   
                helpmean+=meansgaus[i]
                helperror+=errorsGaus[i]*errorsGaus[i]
               ###print "mean ", meansgaus[i]
	   ##Means.append(helpmean.mean())
	   ##Errors.append(helpmean.weighterr())
            Means.append(helpmean/helpnumber)
            Errors.append(sqrt(helperror)/helpnumber)
	   
	    #print "error {0} and weighterr {1}".format(helpmean.error(), helpmean.weighterr())
	      	   
            runtime = datetime.datetime.strptime(event.run.time,'%Y-%m-%d %H:%M:%S')# get runtime
            date.append(ROOT.TDatime(runtime.year, runtime.month, runtime.day, runtime.hour, runtime.minute, runtime.second))
            runNumber.append(float(event.run.runNumber)) # find first run (lowest runNumber, because runs don't get sorted!)	
	       
	    #add relevant data to event that is needed later on:
            event.data['meanA13oD5']  = helpmean/len(means)
            event.data['errorA13oD5'] = sqrt(helperror)/len(means)
            event.data['date']        = ROOT.TDatime(runtime.year, runtime.month, runtime.day, runtime.hour, runtime.minute, runtime.second)
		   
            del helpmean, helperror#, getmean
	   ############################################################
	   
	##fill 2d histo and get TProfile and use the values from there   
        #ctest = ROOT.TCanvas('ctest','',1000,500)
        #ctest.SetRightMargin(0.1)
        #ctest.SetGridy()
	
        #histo2d = ROOT.TH2F("histo2d", "histo2d", int(max(runNumber)-min(runNumber)) , min(runNumber), max(runNumber), 10,4.,10.)
        #entries = []
	
        #for i in range(len(Mean2d)):
            #counter = 0.0
            #for j in range(len(Mean2d[i])):	
                #histo2d.Fill(runNumber[i], Mean2d[i][j])
                #counter+=1
                #entries.append(counter)	
		
        #profile = histo2d.ProfileX()
##	for i in range(len(runNumber)):
##	    Means.append(profile.GetBinContent(profile.FindBin(runNumber[i])))
            ##if(entries[i]!=0): Errors.append(profile.GetBinError(profile.FindBin(runNumber[i]))/sqrt(entries[i]))
	    ##else: #that was cheated, not right
##            Errors.append(profile.GetBinError(profile.FindBin(runNumber[i])))
	   
        #histo2d.Draw("COLZ")
        #profile.Draw("same")
	    

        #histo2d.GetXaxis().SetTitle("RunNumber")

        #histo2d.GetYaxis().SetTitle("Current ratio A13/D5")
	 
        #ctest.Print("%s/Response2dhisto_%s.root" % (self.dir, self.regionName))
        #ctest.Print("%s/Response2dhisto_%s.eps" % (self.dir, self.regionName))
	    
        #del histo2d, profile, Mean2d , ctest   
	    
 
	    
	    
        print(len(Means), len(date), len(Errors))	   	    				   	   
	#final plot			   
        c = ROOT.TCanvas('c','',1000,500)
        c.SetRightMargin(0.1)
        c.SetGridy()
        RunNumber = array('f', runNumber) # use runnumber or better:
	#date
        Date = []
        for i in range(len(date)):
            Date.append(date[i].Convert())
        Time = array('f', Date)
        Mean = array('f', Means)
        MeanError = array('f', Errors)
        dummy = []
        for i in range(len(runNumber)):
            dummy.append(0.0)
        Dummy = array('f', dummy)
	    	
        self.RatioPlot = ROOT.TGraphErrors(len(Means), Time, Mean, Dummy, MeanError)
        self.RatioPlot.Draw("AP")
	#self.RatioPlot.SetMaximum(10.)
	#self.RatioPlot.SetMinimum(4.)
        self.RatioPlot.SetMarkerStyle(21)
        self.RatioPlot.GetXaxis().SetTimeDisplay(1)
        self.RatioPlot.GetXaxis().SetNdivisions(-505)
        self.RatioPlot.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}")
        self.RatioPlot.GetXaxis().SetTimeOffset(0,"gmt")
        self.RatioPlot.GetXaxis().SetTitle("Time")
        self.RatioPlot.GetXaxis().SetTitleOffset(1.6)
        self.RatioPlot.GetXaxis().SetLabelOffset(0.033)
        self.RatioPlot.GetYaxis().SetTitle("Current ratio %s/%s" % (self.detector_region, self.refCell))
	
			 
        c.Modified()
        c.Update()
	   
        self.plot_name = "TimePlot_MBias"   
        # save plot, several formats...
        c.Print("%s/%s_%s%s.root" % (self.dir, self.plot_name, self.detector_region, self.regionName))
        c.Print("%s/%s_%s%s.eps" % (self.dir, self.plot_name, self.detector_region, self.regionName))
        c.Print("%s/%s_%s%s.png" % (self.dir,self.plot_name, self.detector_region, self.regionName))
        del c
        self.RatioPlot.Delete()    
	
        c1 = ROOT.TCanvas('c1','',800,600)
        c1.SetRightMargin(0.1)
        c1.SetGridy()
	#find index of first run
        indexmin =1000
        run = 1000000
        for i in range(len(runNumber)):
            if(runNumber[i]<run):
                run=runNumber[i]
                indexmin=i	
	
        relat = array('f',[])
        error = array('f',[])
        
        for i in range(len(Mean)):
            relat.append(Mean[i]/Mean[indexmin]-1.) #build relative variation wrt first run	
            error.append(sqrt(MeanError[i]**2/Mean[indexmin]**2+MeanError[indexmin]**2*Mean[i]**2/Mean[indexmin]**4))
            print(relat[i],runNumber[i], error[i])
	
        self.RelativeRatio = ROOT.TGraphErrors(len(Means), Time, relat, Dummy, error)
        self.RelativeRatio.Draw("AP")
        self.RelativeRatio.SetMarkerStyle(21)
        self.RelativeRatio.GetXaxis().SetTimeDisplay(1);
        self.RelativeRatio.GetXaxis().SetNdivisions(-505);
        self.RelativeRatio.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}");
        self.RelativeRatio.GetXaxis().SetTimeOffset(0,"gmt");
        self.RelativeRatio.GetXaxis().SetTitle("Time")
        self.RelativeRatio.GetXaxis().SetTitleOffset(1.6)
        self.RelativeRatio.GetXaxis().SetLabelOffset(0.033)
        self.RelativeRatio.GetYaxis().SetTitle("Relative variation of %s cell response" % (self.detector_region))

        c1.Modified()
        c1.Update()
	
        self.plot_name1 = "RelatVarTime"
        # save plot, several formats...
        c1.Print("%s/%s_%s%s.root" % (self.dir, self.plot_name1, self.detector_region, self.regionName))
        c1.Print("%s/%s_%s%s.eps" % (self.dir, self.plot_name1, self.detector_region, self.regionName))
        c1.Print("%s/%s_%s%s.png" % (self.dir,self.plot_name1, self.detector_region, self.regionName))
	
        self.RelativeRatio.Delete()
        del c1
        del self.eventsList
	    
