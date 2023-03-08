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
class PlotRatioPMTsVsTime_2015(GenericWorker):
    "An analysis  worker for MBias"
   
    def __init__(self, modnum=64, detector_region=None, refCell="D6"):
        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),'mbias2015','ResponseVariation')
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

        print("-------",self.dir,self.modnum,self.regionName,self.detector_region)



    def ProcessRegion(self, region):

        if region.GetEvents() == set():
            print("!!!!!!!!!!!!!!!!!!set()")
            exit()
            return
       
        if not self.detector_region:
            ros, mod, pmt, dummy = region.GetNumber()
            #self.detector_region = self.PMTool.getCellName(ros, mod, pmt)
            print(self.detector_region)
            self.detector_region=region.GetHash()
            self.detector_region=self.detector_region[8:19]
        #self.mod = region.GetNumber()[1]
        #self.regionName = Name[8:19] # shorter name without TILECAL_ in front

        print(region.GetEvents())
        print(type(region.GetEvents()))
        print(len(region.GetEvents()))

        for event in region.GetEvents():
            if event.run.runType == 'Las' or event.run.runType == 'Phys':
                if 'LumiBlock' in  list(event.run.data.keys()):# valid entries in run?? some files seem buggy for 2015
                    print("EVENT:", event)
                    self.eventsList.append(event)
                #print 'Run ', event.run.runNumber
                   
                   
    def ProcessStop(self):
               
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
      
        print(len(self.eventsList))
        print(self.eventsList)
        print(self.eventsList[0].run.runNumber)
        print(list(self.eventsList[0].run.data.keys()))
        print(self.eventsList[0].run.data)
        exit()

        #event=run, loop over runs
        for event in self.eventsList:

            print('Run', event.run.runNumber)
            #averaging only sensible for more than 200 entries per run
            if(len(event.run.data['LumiBlock'])<100):
                continue
            if event.run.runNumber==276161 or event.run.runNumber==282625 or event.run.runNumber==270448 or event.run.runNumber==283608 or event.run.runNumber==281385 or event.run.runNumber==270953:# they have weird numbers
                continue   
            print(event.run.time)
            print(len(event.run.data['LumiBlock']))
            print(event.run.data['PMTCurrent'])

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
           
            #later for histogram range
            minVal = []
            maxVal = []
           
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
                    #if m==9 or m==35 or m==14 or m==73 or m==84 or m==87:# or m==81 or m==103 or m==109:
                        #continue       
#                   if m==9 or m==73 or m==84 or m==14 or m==35 or m==78 or m==2 or m==11 or m==22 or m==39 or m==43 or m==18+63 or m==31+63 or m==29+63 or m==40+63 or m==33 or m==39 or m==38+63: #for E4#
#                       continue
#                    if m==9 or m==73 or m==84 or m==14 or m==35 or m==78 or m==92 or m==94 or m==103 or m==8 or m==54 or m==46+63 or m==55+63 or m==33 or m==39 or m==18+63 or m==38+63: # for E2
#                        continue
                    #if m==9 or m==8 or m==41 or m==72 or m==73 or m==103 or m==20 or m==28 or m==53  or m==117 or m==92 or m==84 or m==14 or m==35 or m==78: #when A side first, C side second
                        #continue 
#                   if m==0 or m==7 or m==23 or m==30 or m==38 or m==39 or m==42 or m==53 or m==66 or m==71 or m==81 or m==87 or m==95 or m==103 or m==106 or m==117 or m==92 or m==97 or m==100 or m==9 or m==14 or m==35 or m==73 or m==84 or m==78:#for E1
#                       continue
#                   if m==9 or m==73 or m==84 or m==14 or m==35 or m==78 or m==92 or m==94 or m==103 or m==7 or m==23 or m==53 or m==42 or m==8+63 or m==24+63 or m==54+63 or m==43+63 or m==29+63 or m==32+63 or m==34+63 or m==37+63 or m==39 or m==33 or m==18+63 or 8+63: #for E1
#                       continue
#                   if  m==18 or m==41 or m==103 or m==78 or m==73 or m==84 or m==81 or m==92 or m==72 or m==117:# or m==9 or m==35 or m==14 or m==78: #E3#
#                       continue 
#                   if  m==20 or m==39 or m==14 or m==9 or m==8 or m==17 or m==28 or m==53: #E3
#                       continue               
#                   if m==9 or m==73 or m==84 or m==14 or m==35 or m==78 or m==92 or m==94 or m==103 or m==39 or m==81 or m==32+63 or m==33+63 or m==38+63 or m==46+63 or m==55+63 or m==33 or m==39 or m==18+63 or m==38+63: #new E3
#                       continue
#                   if m==9 or m ==14 or m==35 or m==16 or m==47 or m==56 or m==73 or m==103 or m==84 or m==87 or m==92 or m==94 or m==106 or m==113 or m==122 or m==78: #A13
#                        continue
#                   if m==9 or m==14 or m==35 or m==39 or m==54 or m==73 or m==78 or m==84 or m==92 or m==94 or m==103 or m==110 or m==118 or m==33 or m==39 or m==18+63 or m==38+63:
#                       continue               

                    #from Arely:
                    #D5
#                    if m==9 or m==35 or m==39 or m==54 or m==20 or m==17 or m==28 or m==30:# or m==14 or m==81:# or m==103:
#                        continue
                    #A13
#                    if m==9 or m==14 or m==35 or m==39 or m==54 or m==73 or m==78 or m==84 or m==92 or m==94 or m==103 or m==110 or m==118:
#                        continue

                    #special modules for specific cells
                    if self.detector_region=='E1':
                        if m==28+64 or m==31+64 or m==33+64 or m==36+64 or m==28 or m==31 or m==33 or m==36 or m==7 or m==23 or m==42 or m==53 or m==7+64 or m==23+64 or m==42+64 or m==53+64 or m==6 or m==24 or m==43 or m==52 or m==27+64 or m==30+64 or m==34+64 or m==37+64: # E4' modules and outer MBTS
                            continue
                    if self.detector_region=='E3' or self.detector_region=='E4':
                        if m==14 or m==17+64:# special cabeling for EBA15 and EBC18
                            continue

                    if self.detector_region=='C10':
                        if (m>=38 and m<=41) or (m>=54 and m<=57) or (m>=38+64 and m<=41+64) or (m>=54+64 and m<=57+64):
                            continue
                           

                               
                    helppmtCurrent1 = ROOT.TH1F("","",70,minimum[m]-5.,maximum[m]+5.)
                #build means for each module separately
                    for i in range(len(PMTCurrent1)):
                        if PMTCurrent1[i][m]!=0 and PMTCurrent1[i][m]>0.1:# and PMTCurrent1[i][m]<20.0: # a bit of cleaning...general for all modules
                             helppmtCurrent1.Fill(PMTCurrent1[i][m]) # fill pmtcurrents-ratios     
                   
                    if helppmtCurrent1.GetEntries()<100: #only sensible fits with more than 200 entries
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
                    mini1 = mean1-5.*rms1
                    maxi1 = mean1+5.*rms1
                    minVal.append(mini1)
                    maxVal.append(maxi1)
                   
                    #produce plots for each run
                    self.pmtCurrent1 = ROOT.TH1F("pmtCurrent1","",50, mini1, maxi1)
               
                    for i in range(len(PMTCurrent1)):
                        if PMTCurrent1[i][m]!=0 and PMTCurrent1[i][m]> mini1 and PMTCurrent1[i][m]< maxi1: #: #  more refined cut based on inputs...
                             self.pmtCurrent1.Fill(PMTCurrent1[i][m]) # fill pmtcurrents-ratio, 2nd time
                       
                    print("entries ", self.pmtCurrent1.GetEntries())
                    if self.pmtCurrent1.GetEntries()<100: continue
                    if self.pmtCurrent1.GetEntries()<len(event.run.data['LumiBlock'])-100:
                        print("Here less entries, module number: ", m , "---------------------------------------------------------------------------------------")
                    self.pmtCurrent1.Fit("gaus")
                    gaus = self.pmtCurrent1.GetFunction("gaus") 
               
                    meangaus = gaus.GetParameter(1)
                    meanerrorgaus = gaus.GetParameter(2)#gaus.GetParError(1)#
                       
                    if pmtCurrent1.GetEntries()<100: #only sensible fits with more than 200 entries
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

                    Leg2 =  TLatex()
                    Leg2.SetNDC()
                    Leg2.SetTextAlign( 11 )
                    Leg2.SetTextSize( 0.05 )
                    Leg2.SetTextColor( 1 )
                    Leg2.SetTextFont(42)
                    Leg2.DrawLatex(0.32,0.88," Internal")

                    Leg2.DrawLatex(0.19,0.82, "Tile Calorimeter")

                    atlasLabel =  TLatex()
                    atlasLabel.SetNDC()
                    atlasLabel.SetTextFont( 72 )
                    atlasLabel.SetTextColor( 1 )
                    atlasLabel.SetTextSize( 0.05 )
                    atlasLabel.DrawLatex(0.19,0.88, "ATLAS")
           
                    self.plot_name = "Ratio_%i_%s" % (m, event.run.runNumber)
                    cfit.Modified()
                    cfit.Update()
#                    cfit.Print("%s/%s_%s.eps" % (self.dir, self.plot_name, self.regionName))
#                    cfit.Print("%s/%s_%s.png" % (self.dir, self.plot_name, self.regionName))
#                    cfit.Print("%s/%s_%s.C" % (self.dir, self.plot_name, self.regionName))
           
                   
                    del cfit, helppmtCurrent1, gaus
               
                if m==63 and len(means)<51:
                    break       
            #for global plot at the end with average over all modules
            helpmean = 0.0 #
            #helpmean = stats()
            #helpmean.reset()
            helperror = 0.0
           
            #note: the requirement only makes sense if more than 62 (124) modules are considered
            minmodules=51
            if not self.oneside:
                minmodules=102
           
            print(event.run.runNumber)
            print("how many modules passed? --> ", len(means))
            if (len(means)<minmodules and self.modnum>=minmodules) or len(means)<1:
                continue
           
            Mean2d.append(meansgaus)
            #rather determine spread and rms of a TH1 distribution
           
            ctest2 = ROOT.TCanvas('ctest2','',700,500)
            print("minval ", min(minVal))
            getmean = ROOT.TH1F("getmean","",20,min(minVal),max(maxVal))
           
            meanswoextremes = []
           
            for i in range(len(means)):
                getmean.Fill(meansgaus[i])
                if not meansgaus[i]==max(meansgaus) or not meansgaus[i]==min(meansgaus):
                    meanswoextremes.append(meansgaus[i])
            #if len(means)>1:
                #Means.append(getmean.GetMean())
                #Errors.append(getmean.GetMeanError())
            #else:
                #Means.append(meansgaus[0])
                #Errors.append(errorsGaus[0])
           
            getmean.Draw()
#           ctest2.Print("DistrRatioModule_%i.eps" % (event.run.runNumber))
#           ctest2.Print("DistrRatioModule_%i.root" % (event.run.runNumber))
#          del ctest2, getmean
           
            helpnumber =0
            print(getmean.GetMean(), getmean.GetRMS())
            #print getmean.GetMeanError()
            for i in range(len(means)):
                if meansgaus[i]> 2*getmean.GetRMS()+getmean.GetMean() or meansgaus[i]< getmean.GetMean()-2*getmean.GetRMS():#remove outlier modules from mean calculation
                    continue 
                #helpmean.fill(meansgaus[i], 1./(errorsGaus[i]*errorsGaus[i]))
                #if meansgaus[i]==max(meansgaus) or meansgaus[i]==min(meansgaus):
                    #continue
                #if meansgaus[i]==max(meanswoextremes) or meansgaus[i]==min(meanswoextremes):
                    #continue
                helpnumber+=1 
                helpmean+=meansgaus[i]
                helperror+=errorsGaus[i]*errorsGaus[i]
               ###print "mean ", meansgaus[i]
            #Means.append(helpmean.mean())
            #Errors.append(helpmean.weighterr())

#            Means.append(helpmean/helpnumber)
 #           Errors.append(sqrt(helperror)/helpnumber)

            Means.append(meansgaus)# append all means, average later
            Errors.append(errorsGaus)
            #print "error {0} and weighterr {1}".format(helpmean.error(), helpmean.weighterr())
                   
            runtime = datetime.datetime.strptime(event.run.time,'%Y-%m-%d %H:%M:%S')# get runtime
            date.append(ROOT.TDatime(runtime.year, runtime.month, runtime.day, runtime.hour, runtime.minute, runtime.second))
            runNumber.append(float(event.run.runNumber)) # find first run (lowest runNumber, because runs don't get sorted!)   
               
            #add relevant data to event that is needed later on:
            event.data['meanA13oD5']  = helpmean/helpnumber
            event.data['errorA13oD5'] = sqrt(helperror)/helpnumber
            event.data['date']        = ROOT.TDatime(runtime.year, runtime.month, runtime.day, runtime.hour, runtime.minute, runtime.second)

                   
            del helpmean, helperror#, getmean
           ############################################################
           
#       #fill 2d histo and get TProfile and use the values from there   
#        ctest = ROOT.TCanvas('ctest','',1000,500)
#        ctest.SetRightMargin(0.1)
#        ctest.SetGridy()#
       
#        histo2d = ROOT.TH2F("histo2d", "histo2d", int(max(runNumber)-min(runNumber)) , min(runNumber), max(runNumber), 100,getmean.GetMean()-5*getmean.GetRMS(),5*getmean.GetRMS()+getmean.GetMean())
#        entries = []
       
#        for i in range(len(Mean2d)):
#            counter = 0.0
#            for j in range(len(Mean2d[i])):   
#                histo2d.Fill(runNumber[i], Mean2d[i][j])
#                counter+=1
#                entries.append(counter)       
               
#        profile = histo2d.ProfileX()
#       for i in range(len(runNumber)):
##          Means.append(profile.GetBinContent(profile.FindBin(runNumber[i])))
            ##if(entries[i]!=0): Errors.append(profile.GetBinError(profile.FindBin(runNumber[i]))/sqrt(entries[i]))
            ##else: #that was cheated, not right
##            Errors.append(profile.GetBinError(profile.FindBin(runNumber[i])))
           
#        histo2d.Draw("COLZ")
#        profile.Draw("same")
           

#        histo2d.GetXaxis().SetTitle("RunNumber")#

#        histo2d.GetYaxis().SetTitle("Current ratio A13/D5")
         
#        ctest.Print("%s/Response2dhisto_%s.root" % (self.dir, self.regionName))
#        ctest.Print("%s/Response2dhisto_%s.eps" % (self.dir, self.regionName))
           
#        del histo2d, profile, Mean2d , ctest   
           
 
           
           
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
#        Mean = array('f', Means)
#        MeanError = array('f', Errors)
        dummy = []
        for i in range(len(runNumber)):
            dummy.append(0.0)
        Dummy = array('f', dummy)
               
#        self.RatioPlot = ROOT.TGraphErrors(len(Means), Time, Mean, Dummy, MeanError)
#        self.RatioPlot.Draw("AP")
#       #self.RatioPlot.SetMaximum(10.)
#       #self.RatioPlot.SetMinimum(4.)
#        self.RatioPlot.SetMarkerStyle(21)
#        self.RatioPlot.GetXaxis().SetTimeDisplay(1)
#        self.RatioPlot.GetXaxis().SetNdivisions(-505)
#        self.RatioPlot.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}")
#        self.RatioPlot.GetXaxis().SetTimeOffset(0,"gmt")
#        self.RatioPlot.GetXaxis().SetTitle("Time")
#        self.RatioPlot.GetXaxis().SetTitleOffset(1.6)
#        self.RatioPlot.GetXaxis().SetLabelOffset(0.033)
#        self.RatioPlot.GetYaxis().SetTitle("Current ratio %s/%s" % (self.detector_region,self.refCell))
       
                         
#       c.Modified()
#       c.Update()
           
#       self.plot_name = "TimePlot_MBias"   
#       # save plot, several formats...
#       c.Print("%s/%s_%s%s.root" % (self.dir, self.plot_name, self.detector_region, self.regionName))
#       c.Print("%s/%s_%s%s.eps" % (self.dir, self.plot_name, self.detector_region, self.regionName))
#       c.Print("%s/%s_%s%s.png" % (self.dir,self.plot_name, self.detector_region, self.regionName))
#       del c
#       self.RatioPlot.Delete()   
       
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

        Relat = stats()
#        relerr = stats()
 
#        self.RelativeRatio = ROOT.TGraphErrors()
       
        for i in range(len(Means)):
            for l in range(len(Means[i])):
                Relat.fill(Means[i][l]/Means[indexmin][l]-1.,1./(Errors[i][l]**2/Means[indexmin][l]**2+Errors[indexmin][l]**2*Means[i][l]**2/Means[indexmin][l]**4)) #build relative variation wrt first run   
#                self.RelativeRatio.SetPoint(self.RelativeRatio.GetN(), Time[i], Means[i][l]/Means[indexmin][l]-1.)
#                self.RelativeRatio.SetPointError(self.RelativeRatio.GetN()-1, 0 , sqrt(Errors[i][l]**2/Means[indexmin][l]**2+Errors[indexmin][l]**2*Means[i][l]**2/Means[indexmin][l]**4) )
#                relerr.append(sqrt(Errors[i][l]**2/Means[indexmin][l]**2+Errors[indexmin][l]**2*Means[i][l]**2/Means[indexmin][l]**4))
            relat.append(Relat.mean())
            error.append(Relat.weighterr())
            Relat.reset()
            print(relat[i],runNumber[i], error[i])

            # write values to file
#            f = open('Mbias_variation_2015.txt', 'a+')
           
#            f.write('%s %s %s %s \n' % (str(runNumber[i]), str(Time[i]), str(relat[i]), self.detector_region ))
           
#            f.close()

            print("!!!!!!!!!!!!!!!!!!",len(Means), Time, relat, Dummy, error)


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
        c1.Print("%s/%s_%s%s.C" % (self.dir,self.plot_name1, self.detector_region, self.regionName))
       
        self.RelativeRatio.Delete()
        del c1
        del self.eventsList
