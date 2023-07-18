from src.GenericWorker import *
import src.MakeCanvas
import time
import numpy
import src.stats
import math
from src.region import *
from src.run import *
from src.laser.toolbox import *


# class to calculate the coefficients for current/inst lumi, done separately for A and C side beause we want to distibueish different etas
# worker is called by macro getCoefficient.py
# then we want to plot this for A,B,DC and E cells  against eta --> another worker
class GetLumiCoefficient_2015(GenericWorker):
    "A plot worker for MBias"
    
    def __init__(self, checkCell=False, num_average=1):
        self.dir = getPlotDirectory() #where to save the plots
	    

        self.PMTool         = LaserTools()
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
                if 'LumiBlock' in  list(event.run.data.keys()):# valid entries in run?? some files seem buggy for 2015
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
        c = ROOT.TCanvas('c','',1400,500)
		
	#for histogram building
        Maximum = []
        Minimum = []
        MaxLumi = []
        MinLumi = []
        pairsA = []
        pairsC = []
        PMTCurrent = None
        LumiBlock = None

	# get files with info on inst. lumi for given lumiblock
#        filename = '/afs/cern.ch/user/c/cfischer/TUCS_QT/Tucs/ilumicalc_histograms_None_276262-284484.root'
        filename = os.getenv('TUCS')+'data/ilumicalc_histograms_None_297730-308084_OflLumi-13TeV-005.root'
        print(filename)
        file = TFile(filename,'READ' )
        file.cd()	

        for event in self.eventsList:

            print('Run', event.run.runNumber)
#            if event.run.runNumber==285096 or event.run.runNumber==285354 or event.run.runNumber==285355 or event.run.runNumber==285357: continue
            if event.run.runNumber<=284484: continue # avoid crash
#            if event.run.runNumber<276262: continue
            print(len(event.run.data['LumiBlock']))
            if len(event.run.data['LumiBlock'])==0 or event.run.runNumber==206299: #no lumi-file for this run
                continue   
	    
            histoFile = file.Get('run%s_peaklumiplb' % event.run.runNumber)
#            histoFile = file.Get('lumi_lhcall_del')
	   
            #self.Runnumber = str(event.run.runNumber)
	   
            maximum = 0.0
            maxlumi = 0.0
            minlumi = 1000.0
            minimum = 10000.0
	    
            PMTCurrentA = []
            PMTCurrentC = []

            PMTCurrentHelp = event.run.data['PMTCurrent']
            PMTStatusHelp = event.run.data['PMTStatus']
            LumiBlock = event.run.data['LumiBlock']
            PMTGoodHelp = event.run.data['IsGood']

            #  first prepare pmtcurrent vector --> average over modules
            if self.checkCell:
                cellmeanA= stats()
                cellmeanC= stats()
		#loop over lb entries
                for l in range(len(PMTCurrentHelp)):
		    #loop over modules in A and C-side	but save inputs separately )need to average over all modules
                    countA=0
                    countC=0
                    for m in range(len(PMTCurrentHelp[l])):
#                        if m==39-1 or m==40-1 or m==41-1 or m==42-1 or m==55-1 or m==56-1 or m==57-1 or m==58-1 or m==39+63 or m==40+63 or m==41+63 or m==42+63 or m==55+63 or m==56+63 or m==57+63 or m==58+63:
#                            continue
                        if PMTCurrentHelp[l][m]==0.0: continue
                        if PMTGoodHelp[l][m]<1: continue
                        if PMTStatusHelp[l][m]<1: continue
#                        print "here", m
                        if m<64: # a side
                            countA+=1
                            cellmeanA.fill(PMTCurrentHelp[l][m])
                        else: # c side
                            countC+=1
                            cellmeanC.fill(PMTCurrentHelp[l][m])
                    if countA==0: PMTCurrentA.append(0.0)
                    else: PMTCurrentA.append(cellmeanA.mean())
                    if countC==0: PMTCurrentC.append(0.0)
                    else: PMTCurrentC.append(cellmeanC.mean())
#                    print "Cell means ",  cellmeanC.mean(), cellmeanA.mean()
                    cellmeanA.reset()
                    cellmeanC.reset()
            else:
                print("has to be a cell here!")
                return 0


            # this is for calculating means over num_average consecutive entries of PMTCurrents                                                                                                                                            
                                                                                                                                                                                                                                           
            counterA=0
            counterC=0
            meanPMTA = stats()
            meanLumiA = stats()
            meanPMTC = stats()
            meanLumiC = stats()
		
	    
            for j in range(len(PMTCurrentA)): # find extreme values for building histograms, here A side
                counterA+=1
                InstLumi = histoFile.GetBinContent(LumiBlock[j]+1)/1000.
#                print "InstLumi" , InstLumi
                #arely
                if InstLumi<2.0: continue
#                if InstLumi>4.0: continue

		#find extreme values for histogram
                if PMTCurrentA[j]>maximum:
                    maximum = PMTCurrentA[j]
                if PMTCurrentA[j]<minimum:
                    minimum = PMTCurrentA[j]
                if InstLumi>maxlumi:
                    maxlumi = InstLumi
                if InstLumi< minlumi:
                    minlumi = InstLumi
                ##fill stats                                                                                                                                                                                                                
                meanPMTA.fill(PMTCurrentA[j])
                meanLumiA.fill(InstLumi)
                if counterA == len(PMTCurrentA)-1:
                    counterA = 10000
                if counterA%self.num_average!=0: continue
                #if ten values: fill vector                                                                                                                                                                                                 
                #print "counter %i, mean Lumi %f, mean PMTCurrent %f" % (counter, meanLumi.mean(), meanPMT.mean())                                                                                                                          
                pairsA.append([meanLumiA.mean(),meanPMTA.mean()]) # fill 2d histo                                                                                                                                                           
                meanLumiA.reset()
                meanPMTA.reset()

            del meanLumiA, meanPMTA

#                pairsA.append([InstLumi,PMTCurrentA[j]]) # fill 2d histo

            for j in range(len(PMTCurrentC)): # find extreme values for building histograms, here C side
                counterC+=1
                InstLumi = histoFile.GetBinContent(LumiBlock[j]+1)/1000.
                #arely
                if InstLumi<2.0: continue
#                if InstLumi>4.0: continue
		#find extreme values for histogram
                if PMTCurrentC[j]>maximum:
                    maximum = PMTCurrentC[j]
                if PMTCurrentC[j]<minimum:
                    minimum = PMTCurrentC[j]
                #probably doesn't change
                if InstLumi>maxlumi:
                    maxlumi = InstLumi
                if InstLumi< minlumi:
                    minlumi = InstLumi
                meanPMTC.fill(PMTCurrentC[j])
                meanLumiC.fill(InstLumi)
                if counterC == len(PMTCurrentC)-1:
                    counterC = 10000
                if counterC%self.num_average!=0: continue
                #if ten values: fill vector                                                                                                                                                                                                 
                #print "counter %i, mean Lumi %f, mean PMTCurrent %f" % (counter, meanLumi.mean(), meanPMT.mean())                                                                                                                          
                pairsC.append([meanLumiC.mean(),meanPMTC.mean()]) # fill 2d histo                                                                                                                                                           
                meanLumiC.reset()
                meanPMTC.reset()

            del meanLumiC, meanPMTC
#                pairsC.append([InstLumi,PMTCurrentC[j]]) # fill 2d histo
	
	    		   
            Maximum.append(maximum)
            Minimum.append(minimum)
            MaxLumi.append(maxlumi)
            MinLumi.append(minlumi)
	               	   		 
        minimum = min(Minimum)
        maximum = max(Maximum)
        maxlumi = max(MaxLumi)
        minlumi = min(MinLumi)

        self.CurrentVsInstLumiA = ROOT.TH2F("CurrentVsInstLumiA",'', 30, minlumi, maxlumi, 30, minimum-0.5,maximum+0.5)
        self.CurrentVsInstLumiC = ROOT.TH2F("CurrentVsInstLumiC",'', 30, minlumi, maxlumi, 30, minimum-0.5,maximum+0.5)

        fitplotA = ROOT.TH2F("fitplotA",'', 25, minlumi, maxlumi, 70, minimum-0.5,maximum+0.5)	
        fitplotC = ROOT.TH2F("fitplotC",'', 25, minlumi, maxlumi, 70, minimum-0.5,maximum+0.5)	
		
        #fill both fit plots
        for i in range(len(pairsA)):
            if pairsA[i][1]==0.0: continue
            self.CurrentVsInstLumiA.Fill(pairsA[i][0],pairsA[i][1]) # fill 2d histogram 
            if pairsA[i][0]>=minlumi:
                fitplotA.Fill(pairsA[i][0],pairsA[i][1]) # histogram to be fitted later

        for i in range(len(pairsC)):
            if pairsC[i][1]==0.0: continue
            self.CurrentVsInstLumiC.Fill(pairsC[i][0],pairsC[i][1]) # fill 2d histogram 
            if pairsC[i][0]>=minlumi:
                fitplotC.Fill(pairsC[i][0],pairsC[i][1]) # histogram to be fitted later
	
        # from Arely:                                                                                                                                                                                                                       
        ## determine the range in y (to make the binning equally significant).                                                                                                                                                              
        ##minimum is OK.                                                                                                                                                                                                                    
        ##maxmum from the average of the last few bins of the others.                                                                                                                                                                       

        xMaxA = 1
        yMaxA = 1
        zMaxA = 1
        xMaxC = 1
        yMaxC = 1
        zMaxC = 1

        self.CurrentVsInstLumiA.GetXaxis().SetRange(25,30)                                                                                                                                                                                 
        self.CurrentVsInstLumiC.GetXaxis().SetRange(25,30)                                                                                                                                                                                 
#        self.CurrentVsInstLumiA.GetMaximumBin(xMaxA,yMaxA,zMaxA)                                                                                                               
#        self.CurrentVsInstLumiC.GetMaximumBin(xMaxC,yMaxC,zMaxC)                                                                                                                                                                           

        arelyProjA = self.CurrentVsInstLumiA.ProjectionY("arelyProjA",25,30)# last 5 bins 
        arelyProjC = self.CurrentVsInstLumiC.ProjectionY("arelyProjC",25,30)# last 5 bins                                                                                                                                                    
        maxCurrA = arelyProjA.GetMaximumBin()
        maxCurrC = arelyProjC.GetMaximumBin()

        newMaxCurrent = 0.
        if (self.CurrentVsInstLumiA.GetYaxis().GetBinCenter(maxCurrA) > self.CurrentVsInstLumiC.GetYaxis().GetBinCenter(maxCurrC)):
           newMaxCurrent = self.CurrentVsInstLumiA.GetYaxis().GetBinCenter(maxCurrA) * 1.3
        else:
           newMaxCurrent = self.CurrentVsInstLumiC.GetYaxis().GetBinCenter(maxCurrC) * 1.3

        fitplotA = ROOT.TH2F("fitplotA",'', 25, minlumi, maxlumi, 50, minimum-0.5,newMaxCurrent)
        fitplotC = ROOT.TH2F("fitplotC",'', 25, minlumi, maxlumi, 50, minimum-0.5,newMaxCurrent)

        #fill both fit plots                                                                                                                                                                                                                 
        for i in range(len(pairsA)):
            if pairsA[i][1]==0.0: continue
            if pairsA[i][1] > newMaxCurrent: continue
            if pairsA[i][0]>=minlumi:
                fitplotA.Fill(pairsA[i][0],pairsA[i][1]) # histogram to be fitted later                                                                                                                                                    
                                                                                                                                                                                                                                             
        for i in range(len(pairsC)):
            if pairsC[i][1]==0.0: continue
            if pairsC[i][1] > newMaxCurrent: continue
            if pairsC[i][0]>=minlumi:
                fitplotC.Fill(pairsC[i][0],pairsC[i][1]) # histogram to be fitted later 

       
        c.Divide(2,1)
        c.cd(1)
        profilexA = self.CurrentVsInstLumiA.ProfileX()

        fitplotA.Draw("COLZ")
#        profilexA.Draw("SAME")
        ROOT.gPad.SetRightMargin(0.2)                                                                                                                
        fitplotA.GetXaxis().SetTitle("Inst. Lumi [10^{33}cm^{-2}s^{-1}]")
        fitplotA.GetYaxis().SetTitle("Current %s [nA] A side" % (self.regionName))
        fitplotA.GetYaxis().SetTitleOffset(1.7)
        fitplotA.GetZaxis().SetTitle("Events")

        c.cd(2)
        profilexC = self.CurrentVsInstLumiC.ProfileX()

        fitplotC.Draw("COLZ")
#        profilexC.Draw("SAME")
        ROOT.gPad.SetRightMargin(0.2)                                                                                                                
        fitplotC.GetXaxis().SetTitle("Inst. Lumi [10^{33}cm^{-2}s^{-1}]")
        fitplotC.GetYaxis().SetTitle("Current %s [nA] C side" % (self.regionName))
        fitplotC.GetYaxis().SetTitleOffset(1.7)
        fitplotC.GetZaxis().SetTitle("Events")

        c.Modified()
        c.Update()

        self.plot_name = "CurrentVsLumi_MBiasSplit_2016"
        # save plot, several formats...                                                                                                              \
                                                                                                                                                      
        c.Print("%s/%s_%s.root" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/%s_%s.eps" % (self.dir, self.plot_name, self.regionName))
        c.Print("%s/%s_%s.png" % (self.dir,self.plot_name, self.regionName))
        del c, profilexA, pairsA
        self.CurrentVsInstLumiA.Delete()


	# do fit and save coefficient ##############################################################################
	# A side:
#        profileA = fitplotA.ProfileX()

        profileA = ROOT.TH1F("profileA","",fitplotA.GetNbinsX(),minlumi,maxlumi)
        for bin in range(1,fitplotA.GetNbinsX()+1):
            histoProj = fitplotA.ProjectionY("histoProj",bin,bin)
#            histoProj.GetXaxis().SetRange(histoProj.GetMaximumBin()-10,histoProj.GetMaximumBin()+10) #this is to remove outliers
            profileA.SetBinContent(bin,histoProj.GetMean())
            profileA.SetBinError(bin,histoProj.GetMeanError())
#        profileA = fitplotA.ProjectionY("profileA")
            del histoProj
            
#        profileC = fitplotC.ProfileX()                                                                                                               
        profileC = ROOT.TH1F("profileC","",fitplotC.GetNbinsX(),minlumi,maxlumi)
        for bin in range(1,fitplotC.GetNbinsX()+1):
            histoProj = fitplotC.ProjectionY("histoProj",bin,bin)
#            histoProj.GetXaxis().SetRange(histoProj.GetMaximumBin()-10,histoProj.GetMaximumBin()+10) # remove outliers
            profileC.SetBinContent(bin,histoProj.GetMean())
            profileC.SetBinError(bin,histoProj.GetMeanError())
#        profileC = fitplotC.ProjectionY("profileC")
            del histoProj

        pol1 = ROOT.TF1("pol1","pol1",minlumi, maxlumi)
        profileA.Fit('pol1',"r")
        cfitA = ROOT.TCanvas('cfitA','',800,600)
        cfitA.cd()
        pad1 = ROOT.TPad("pad1","pad1",0,0.420,.99,1)
        pad1.SetBottomMargin(0)
        pad1.Draw()
        pad1.cd()

        profileA.Draw()
        pol1.Draw("same")
        pol1.SetLineColor(ROOT.kRed)

        legendA = ROOT.TLegend(0.2,0.65,0.55,0.9)
        legendA.SetFillStyle(0)
        legendA.SetFillColor(0)
        legendA.SetBorderSize(0)
        legendA.AddEntry(profileA, "Data 2015, #sqrt{s}=13 TeV", "ep")
        legendA.AddEntry(pol1, "Pol1 fit: f(x)= %1.2fx+%1.2f" %(pol1.GetParameter(1), pol1.GetParameter(0)),'l' )
        legendA.Draw()

        l1 = TLatex()
        l1.SetNDC()
        l1.SetTextSize(0.06)
        if pol1.GetNDF()!=0:
            l1.DrawLatex(0.2,0.6, "#chi^{2}/ndf=%1.1f" % (pol1.GetChisquare()/pol1.GetNDF()))

        profileA.GetYaxis().SetTitle("Current %s [nA] A side" % (self.regionName))
        profileA.GetYaxis().SetTitleOffset(1.0)
        profileA.GetYaxis().SetTitleSize(0.07)
        profileA.GetYaxis().SetLabelSize(0.075)
        profileA.GetXaxis().SetLabelColor(0)

        cfitA.cd()

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

        fitfuncA = ROOT.TH1F("fitfuncA","", 1 ,minlumi, maxlumi)
        fitfuncA.SetBinContent(1,1)
        fitfuncA.SetLineColor(ROOT.kRed)
        fitfuncA.Draw()
        fitfuncA.GetXaxis().SetLabelSize(0.1)
        fitfuncA.GetYaxis().SetTitleSize(0.12)
        fitfuncA.GetXaxis().SetTitleSize(0.12)
        fitfuncA.GetYaxis().SetTitleOffset(0.57)
        fitfuncA.GetYaxis().CenterTitle()
        fitfuncA.GetXaxis().SetTitleOffset(1.1)
        fitfuncA.GetYaxis().SetLabelSize(0.1)
        fitfuncA.GetYaxis().SetNdivisions(504)
        fitfuncA.GetYaxis().SetDecimals()
        fitfuncA.SetMinimum(0.982)
        fitfuncA.SetMaximum(1.018)

        ratiohistA = ROOT.TH1F("ratiohistA","",25, minlumi, maxlumi)
        for i in range(ratiohistA.GetNbinsX()):
            x = profileA.GetBinContent(i+1)
            if x==0.: continue
            y = pol1.Eval(profileA.GetBinCenter(i+1))
            quotient = x/y
            x_err = profileA.GetBinError(i+1)
            y_err = 0.0 #math.sqrt((pol1.GetParError(1)*x)**2+pol1.GetParError(0)**2)              
            quoerr = quotient*math.sqrt((x_err/x)**2+(y_err/y)**2)
            ratiohistA.SetBinContent(i+1, quotient)
            ratiohistA.SetBinError(i+1, quoerr)

        ratiohistA.Draw("SAMEp")
        fitfuncA.GetXaxis().SetTitle("Inst. Luminosity [10^{33}cm^{-2}s^{-1}]")
        fitfuncA.GetYaxis().SetTitle("Current/f(x)")

        # save plot, several formats...                                                                                                                                                      
        cfitA.Print("%s/%s_%s_ratioPlotA.root" % (self.dir, self.plot_name, self.regionName))
        cfitA.Print("%s/%s_%s_ratioPlotA.eps" % (self.dir, self.plot_name, self.regionName))
        cfitA.Print("%s/%s_%s_ratioPlotA.png" % (self.dir,self.plot_name, self.regionName))


        # need this :pol1.GetParameter(1), pol1.GetParameter(0)),'l' ) + error
        # C side:
        event.data[self.regionName+"coeff"]=pol1.GetParameter(1)
        event.data[self.regionName+"coeffErr"]=pol1.GetParError(1)

        del pad1,pad2
        
#        profileC = fitplotC.ProfileX()
        profileC.Fit('pol1',"r")

        cfitC = ROOT.TCanvas('cfitC','',800,600)
        cfitC.cd()
        pad1 = ROOT.TPad("pad1","pad1",0,0.420,.99,1)
        pad1.SetBottomMargin(0)
        pad1.Draw()
        pad1.cd()

        profileC.Draw()
        pol1.Draw("same")
        pol1.SetLineColor(ROOT.kRed)

        legendC = ROOT.TLegend(0.2,0.65,0.55,0.9)
        legendC.SetFillStyle(0)
        legendC.SetFillColor(0)
        legendC.SetBorderSize(0)
        legendC.AddEntry(profileC, "Data 2015, #sqrt{s}=13 TeV", "ep")
        legendC.AddEntry(pol1, "Pol1 fit: f(x)= %1.2fx+%1.2f" %(pol1.GetParameter(1), pol1.GetParameter(0)),'l' )
        legendC.Draw()

        if pol1.GetNDF()!=0:
            l1.DrawLatex(0.2,0.6, "#chi^{2}/ndf=%1.1f" % (pol1.GetChisquare()/pol1.GetNDF()))

        profileC.GetYaxis().SetTitle("Current %s [nA] C side" % (self.regionName))
        profileC.GetYaxis().SetTitleOffset(1.0)
        profileC.GetYaxis().SetTitleSize(0.07)
        profileC.GetYaxis().SetLabelSize(0.075)
        profileC.GetXaxis().SetLabelColor(0)

        cfitC.cd()

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

        fitfuncC = ROOT.TH1F("fitfuncC","", 1 ,minlumi, maxlumi)
        fitfuncC.SetBinContent(1,1)
        fitfuncC.SetLineColor(ROOT.kRed)
        fitfuncC.Draw()
        fitfuncC.GetXaxis().SetLabelSize(0.1)
        fitfuncC.GetYaxis().SetTitleSize(0.12)
        fitfuncC.GetXaxis().SetTitleSize(0.12)
        fitfuncC.GetYaxis().SetTitleOffset(0.57)
        fitfuncC.GetYaxis().CenterTitle()
        fitfuncC.GetXaxis().SetTitleOffset(1.1)
        fitfuncC.GetYaxis().SetLabelSize(0.1)
        fitfuncC.GetYaxis().SetNdivisions(504)
        fitfuncC.GetYaxis().SetDecimals()
        fitfuncC.SetMinimum(0.982)
        fitfuncC.SetMaximum(1.018)

        ratiohistC = ROOT.TH1F("ratiohistC","",25, minlumi, maxlumi)
        for i in range(ratiohistC.GetNbinsX()):
            x = profileC.GetBinContent(i+1)
            if x==0.: continue
            y = pol1.Eval(profileC.GetBinCenter(i+1))
            quotient = x/y
            x_err = profileC.GetBinError(i+1)
            y_err = 0.0 #math.sqrt((pol1.GetParError(1)*x)**2+pol1.GetParError(0)**2)
            quoerr = quotient*math.sqrt((x_err/x)**2+(y_err/y)**2)
            ratiohistC.SetBinContent(i+1, quotient)
            ratiohistC.SetBinError(i+1, quoerr)

        ratiohistC.Draw("SAMEp")
        fitfuncC.GetXaxis().SetTitle("Inst. Luminosity [10^{33}cm^{-2}s^{-1}]")
        fitfuncC.GetYaxis().SetTitle("Current/f(x)")

        # save plot, several formats..
        cfitC.Print("%s/%s_%s_ratioPlotC.root" % (self.dir, self.plot_name, self.regionName))
        cfitC.Print("%s/%s_%s_ratioPlotC.eps" % (self.dir, self.plot_name, self.regionName))
        cfitC.Print("%s/%s_%s_ratioPlotC.png" % (self.dir,self.plot_name, self.regionName))

        event.data[self.regionName+"coeff-"]=pol1.GetParameter(1)
        event.data[self.regionName+"coeffErr-"]=pol1.GetParError(1)
        
        det_reg = self.PMTool.getRegionName2015(self.regionName)
        Part = det_reg[0] #long barrel or extended barrel                                                                                  
        PMTch = det_reg[1] #pmts belonging to cell, will use my own mapping for channel vs eta                                                    

        # using mapping from website: only using first pmt                                                                                           
        etamapLB = {0:0.01,1:0.05,2:0.05,5:0.15,6:0.15,9:0.25,11:0.25,13:0.2,15:0.35,16:0.35,19:0.45,21:0.45,23:0.55,25:0.4,28:0.55,34:0.65,27:0.65,\
33:0.75,37:0.85,40:0.75,39:0.6,44:0.85,46:0.95}
        # e cells added manually                                                                                                                                                                            
        etamapEB = {0:1.05,12:1.05,1:1.15,13:1.15,2:0.85,4:0.95,6:1.15942,8:1.05869,10:1.25867,14:1.15803,16:1.00741,20:1.35795,22:1.25738,32:1.35678,28:1.45728,42:1.4562,36:1.20632,40:1.55665}


        etaValueA = 10.
        etaValueC = -10.
        

        if Part[0]==1:
            etaValueA= etamapLB[PMTch[0]]
        else:
            etaValueA= etamapEB[PMTch[0]]
        
        etaValueC = -1.*etaValueA

        f = open('coefficient_vs_eta_data2016_10bins.txt', 'a+')

        f.write('%s %s %s \n' % (str(etaValueA), str(event.data[self.regionName+"coeff"]), str(event.data[self.regionName+"coeffErr"]) ))
        f.write('%s %s %s \n' % (str(etaValueC), str(event.data[self.regionName+"coeff-"]), str(event.data[self.regionName+"coeffErr-"]) ))

        f.close()


	#####################################################################################################################
	    
        del self.eventsList
	   
