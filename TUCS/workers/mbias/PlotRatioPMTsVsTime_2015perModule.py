from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import src.stats
import time
import numpy
from math import sqrt
from array import *
from src.laser.toolbox import *

# class to plot ratio of cell/D6 of mbias data,  PMT current ratio vs. Time (runnumber)
# class is called by plotPMTsRatiovsTime.py in macros/mbias/
class PlotRatioPMTsVsTime_2015perModule(GenericWorker):
    "An analysis  worker for MBias"
    
    def __init__(self, modnum=64, detector_region=None, refCell="D6"):
        self.dir = getPlotDirectory() #where to save the plots
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

    def ProcessRegion(self, region):
        
        if region.GetEvents() == set():
            print("set()!")
            return
        
        if not self.detector_region:
            ros, mod, pmt, dummy = region.GetNumber()
            #self.detector_region = self.PMTool.getCellName(ros, mod, pmt)
            print(self.detector_region)
            self.detector_region=region.GetHash()
            self.detector_region=self.detector_region[8:19]
        #self.mod = region.GetNumber()[1]
        #self.regionName = Name[8:19] # shorter name without TILECAL_ in front
        
        for event in region.GetEvents():
            if event.run.runType == 'Las' or event.run.runType == 'Phys':
                if 'LumiBlock' in  list(event.run.data.keys()):# valid entries in run?? some files seem buggy for 2015
                    self.eventsList.append(event)
                #print 'Run ', event.run.runNumber
                    
                    
    def        ProcessStop(self):
                
        if os.environ.get('TUCS'):
            ROOT.gROOT.LoadMacro("$TUCS/root_macros/AtlasStyle.C")
            ROOT.SetAtlasStyle()
            ROOT.gROOT.ForceStyle()
        ROOT.gStyle.SetPalette(1)
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

            print('--- * --- * --- * --- * --- * --- * --- * --- * --- * ---')
            print('Run', event.run.runNumber)
            #averaging only sensible for more than 200 entries per run
            if(len(event.run.data['LumiBlock'])<150):
                print("------------ Skipping run: ",event.run.time)
                print("Number of LBs: ",len(event.run.data['LumiBlock']))
                continue   
            if event.run.runNumber==276161 or event.run.runNumber==282625 or event.run.runNumber==270448 or event.run.runNumber==283608 or event.run.runNumber==281385 or event.run.runNumber==270953:# they have weird numbers 
                continue   
            print("------------ Doing analysis for: ",event.run.time)           
            print("Number of LBs: ",len(event.run.data['LumiBlock']))
            #if len(event.run.data['LumiBlock'])==0:
                #continue   
                
            ## Number of modules
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
                                
                    helppmtCurrent1 = ROOT.TH1F("","",70,minimum[m]-5.,maximum[m]+5.)
                       #build means for each module separately        
                    for i in range(len(PMTCurrent1)):
                        if PMTCurrent1[i][m]!=0 and PMTCurrent1[i][m]>0.1:# and PMTCurrent1[i][m]<20.0: # a bit of cleaning...general for all modules
                             helppmtCurrent1.Fill(PMTCurrent1[i][m]) # fill pmtcurrents-ratios           
                    
                    if helppmtCurrent1.GetEntries()<100: #only sensible fits with more than 200 entries
                        meansgaus.append(0.0)
                        errorsGaus.append(0.0)
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
                    if self.pmtCurrent1.GetEntries()<100:
                        meansgaus.append(0.0)
                        errorsGaus.append(0.0)
                        continue
                    if self.pmtCurrent1.GetEntries()<len(event.run.data['LumiBlock'])-100:
                            print("Here less entries, module number: ", m , "---------------------------------------------------------------------------------------")
                    self.pmtCurrent1.Fit("gaus")
                    gaus = self.pmtCurrent1.GetFunction("gaus")        
                
                    meangaus = gaus.GetParameter(1)
                    meanerrorgaus = gaus.GetParameter(2)#gaus.GetParError(1)
                        
                    if pmtCurrent1.GetEntries()<100: #only sensible fits with more than 200 entries
                        meansgaus.append(0.0)
                        continue        
                
                    if meangaus<0.0 or  gaus.GetParameter(2)>0.2*meangaus: # quality requirement on fit
                        meansgaus.append(0.0)
                        errorsGaus.append(0.0)
                        continue
                
                       #for global plot at the end#######
                    means.append(mean1) #mean1
                    #print "arelycg:", mean1
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
            print("How many modules passed? --> ", len(means))
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
#           del ctest2, getmean
           
            print(getmean.GetMean(), getmean.GetRMS())
            #print getmean.GetMeanError()

            # instead of averaging we save the whole vector for all 64 modules
            Means.append(meansgaus)
            Errors.append(errorsGaus)
           
                         
            runtime = datetime.datetime.strptime(event.run.time,'%Y-%m-%d %H:%M:%S')# get runtime
            date.append(ROOT.TDatime(runtime.year, runtime.month, runtime.day, runtime.hour, runtime.minute, runtime.second))
            runNumber.append(float(event.run.runNumber)) # find first run (lowest runNumber, because runs don't get sorted!)        
               
            #add relevant data to event that is needed later on:
#            event.data['meanA13oD5']  = helpmean/helpnumber
#            event.data['errorA13oD5'] = sqrt(helperror)/helpnumber
#            event.data['date']        = ROOT.TDatime(runtime.year, runtime.month, runtime.day, runtime.hour, runtime.minute, runtime.second)

                   
 #           del helpmean, helperror#, getmean
           ############################################################
           
 
            
            
        print(len(Means), len(date), len(Errors))                                                                     
        #final plot                           
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
                    
        #find index of first run
        indexmin =1000
        indexmin2 = 1000
        indexmin3 = 1000
        indexmin4 = 1000
    
        run = 1000000
        run2 = 1000000
        run3 = 1000000
        run4 = 1000000

        for i in range(len(runNumber)):
            if(runNumber[i]<run):
                run=runNumber[i]
                indexmin=i
#            if(runNumber[i]<run2 and runNumber[i]>run):
#                run2=runNumber[i]
#                indexmin2=i
#            if(runNumber[i]<run3 and runNumber[i]>run2):
#                run3=runNumber[i]
#                indexmin3=i
#            if(runNumber[i]<run4 and runNumber[i]>run3):
#                run4=runNumber[i]
#                indexmin4=i#

#        print run, run2, run3, run4
        
        relat = array('f',[])
        error = array('f',[])
        
        for i in range(len(Means)):
            print("second dimension", len(Means[i]), " ", indexmin)
            for j in range(len(Means[i])):
#                print "index", j
#                print Means[indexmin][j], Means[indexmin2][j], Means[indexmin3][j], Means[indexmin4][j]
                if Means[indexmin][j]!=0.: # module did not pass in reference run --> everything will end up at 9999
                    relat.append(Means[i][j]/Means[indexmin][j]-1.) #build relative variation wrt first run        
                    error.append(sqrt(Errors[i][j]**2/Means[indexmin][j]**2+Errors[indexmin][j]**2*Means[i][j]**2/Means[indexmin][j]**4))
#                elif Means[indexmin2][j]!=0.: # module did not pass in reference run --> everything will end up at 0
#                    relat.append(Means[i][j]/Means[indexmin2][j]-1.) #build relative variation wrt first run        
#                    error.append(sqrt(Errors[i][j]**2/Means[indexmin2][j]**2+Errors[indexmin2][j]**2*Means[i][j]**2/Means[indexmin2][j]**4))
#                elif Means[indexmin3][j]!=0.: # module did not pass in reference run --> everything will end up at 0
#                    relat.append(Means[i][j]/Means[indexmin3][j]-1.) #build relative variation wrt first run        
#                    error.append(sqrt(Errors[i][j]**2/Means[indexmin3][j]**2+Errors[indexmin3][j]**2*Means[i][j]**2/Means[indexmin3][j]**4))
#                elif Means[indexmin4][j]!=0.: # module did not pass in reference run --> everything will end up at 0
#                    relat.append(Means[i][j]/Means[indexmin4][j]-1.) #build relative variation wrt first run        
#                    error.append(sqrt(Errors[i][j]**2/Means[indexmin4][j]**2+Errors[indexmin4][j]**2*Means[i][j]**2/Means[indexmin4][j]**4))
                else:
                    relat.append(9999.0)
                    error.append(9999.0)
#                print relat[j], error[j]

                # write values to file
                f = open('Mbias_NewEcells_variation_2015.txt', 'a+')
            
                f.write('%s %s %s %i \n' % (str(Time[i]), str(relat[j]), self.detector_region, j ))
                
                f.close()

            del relat[:] # reset list
            del error[:]
            

        del self.eventsList
            
