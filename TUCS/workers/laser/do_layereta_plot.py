############################################################
#
# do_layereta_plot.py
#
############################################################
#
# Author: Emmanuelle Dubreuil <Emmanuelle.Dubreuil@cern.ch>
#
# 18th March 2013
#
# Goal: Do a plot with variation of each cell in function of
# eta
#
#############################################################

import errno
import time
from src.GenericWorker import *
from src.oscalls import *
#import src.MakeCanvas
#import time
import ROOT

class do_layereta_plot(GenericWorker):
    "Compute variation of each cell in function of eta"
    
    c1 = src.MakeCanvas.MakeCanvas()
    c1.SetFrameFillColor(0)
    c1.SetFillColor(0);
    c1.SetBorderMode(0);
    #self.c1.SetLogy(0); 

    
    def __init__(self, f =(lambda event: event.data['deviation']), label="Deviation"):

        self.f = f
        self.label = label
        self.PMTool   = LaserTools()        
        self.origin   = ROOT.TDatime()
        
        self.LG_evts  = set()
        self.HG_evts  = set()
        self.events   = set()        
        self.time_max = 0
        self.time_min = 10000000000000000

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        self.cells_A = []
        self.cells_C = []
        self.ch_fitA = [-10 for i in range(37)]
        self.ch_fitC = [-10 for i in range(37)]
        self.ch_errA = [-10 for i in range(37)]
        self.ch_errC = [-10 for i in range(37)]
        self.layerA = [-10 for i in range(37)]
        self.layerAerror = [-10 for i in range(37)]
        self.layerB = [-10 for i in range(37)]
        self.layerBerror = [-10 for i in range(37)]
        self.layerD = [-10 for i in range(37)]
        self.layerDerror = [-10 for i in range(37)]

        self.eta_Aside = [-10 for i in range(37)]
        self.eta_Cside = [-10 for i in range(37)]

                
    def ProcessStart(self):
        
        global run_list
        for run in run_list.getRunsOfType('Las'):
            time = run.time_in_seconds
            if self.time_min > time:
                self.time_min = time
                self.origin = ROOT.TDatime(run.time)
                
            if self.time_max < time:
                self.time_max = time


        self.cadre = ROOT.TH2F('Cadre', '',\
                               40, -2, 2, 10000, -2, 2)

        for i in range(10): #A Cells

            name_h = "cell_deviation_a %02d" % (i)
            self.cells_A.append(ROOT.TH1F(name_h, '', 40, -10, +10))

        for i in range(9): #BC Cells

            name_h = "cell_deviation_BC %02d" % (i)
            self.cells_A.append(ROOT.TH1F(name_h, '', 40, -10, +10))

        for i in range(4): #D Cells

            name_h = "cell_deviation_d %02d" % (i)
            self.cells_A.append(ROOT.TH1F(name_h, '', 100, -10, +10))

        for i in range(5): #EA Cells

            name_h = "cell_deviation_ea %02d" % (i)
            self.cells_A.append(ROOT.TH1F(name_h, '', 40, -10, +10))

        for i in range(6): #EB Cells + C10

            name_h = "cell_deviation_eb %02d" % (i)
            self.cells_A.append(ROOT.TH1F(name_h, '', 70, -10, +10))

        for i in range(3): #ED Cells

            name_h = "cell_deviation_ed %02d" % (i)
            self.cells_A.append(ROOT.TH1F(name_h, '', 100, -10, +10))

        
        ###
        for i in range(10): #A Cells

            name_h = "cell_deviation_a_ %02d" % (i)
            self.cells_C.append(ROOT.TH1F(name_h, '', 40, -10, +10))

        for i in range(9): #BC Cells

            name_h = "cell_deviation_BC_ %02d" % (i)
            self.cells_C.append(ROOT.TH1F(name_h, '', 40, -10, +10))

        for i in range(4): #D Cells

            name_h = "cell_deviation_d_ %02d" % (i)
            self.cells_C.append(ROOT.TH1F(name_h, '', 100, -10, +10))

        for i in range(5): #EA Cells

            name_h = "cell_deviation_ea_ %02d" % (i)
            self.cells_C.append(ROOT.TH1F(name_h, '', 40, -10, +10))

        for i in range(6): #EB Cells + C10

            name_h = "cell_deviation_eb_ %02d" % (i)
            self.cells_C.append(ROOT.TH1F(name_h, '', 70, -10, +10))

        for i in range(3): #ED Cells

            name_h = "cell_deviation_ed_ %02d" % (i)
            self.cells_C.append(ROOT.TH1F(name_h, '', 100, -10, +10))

     

    def ProcessRegion(self, region):
        hash = region.GetHash()
        for event in region.GetEvents():
#          
            if 'deviation' in event.data and event.data['is_OK'] and event.data['status']==0:
                if (hash.find('LBC_m28')!=-1 or hash.find('LBA_m54')!=-1 or hash.find('EBC_m01')!=-1 or event.data['HV']<-10 or hash.find('LBA_m13')!=-1):
                    continue
                else:
                    self.events.add(event)

                    



    def ProcessStop(self):

        self.c1.SetTitle("Intermediate plots")
        ROOT.gStyle.SetOptStat(1210)
        ROOT.gStyle.SetOptFit(111)
        ROOT.gROOT.ForceStyle()       
        
        for event in self.events:

            [part, mod, pmt, w] = event.region.GetNumber(1)
            part -= 1

            Celli = self.PMTool.get_cell_index(part,mod,pmt)

            if not event.data['is_OK'] or event.data['status']:
                continue

            if (event.data['calibration']>0.0001 and event.run.data['wheelpos']==8)\
                   or (event.data['calibration']>0.01 and event.run.data['wheelpos']==6):

                if part==0 or part==2: #A side

                    for i in range(37):

                        if ( (i<10) and (Celli == i+101)):
                            self.cells_A[i].Fill(self.f(event))

                        if ( (i>=10) and (i<19) and (Celli == i-10+201)):
                            self.cells_A[i].Fill(self.f(event))

                        if ( (i>=19) and (i<23) and (Celli == i-18+400) ):
                            self.cells_A[i].Fill(self.f(event))

## EA
                        if ( (i>=23) and (i<28) and (Celli == i-23+112)):
                            self.cells_A[i].Fill(self.f(event))
## EB
                        if ( (i>=28) and (i<33) and (Celli == i-28+211)):
                            self.cells_A[i].Fill(self.f(event))
## ED
                        if ( (i>=35) and (i<37) and (Celli == i-34+404)):
                            self.cells_A[i].Fill(self.f(event))
                          

                if part==1 or part==3: #C side

                    for j in range(37):

                        if ( (j<10) and (Celli == j+101)):
                            self.cells_C[j].Fill(self.f(event))

                        if ( (j>=10) and (j<19) and (Celli == j-10+201)):
                            self.cells_C[j].Fill(self.f(event))

                        if ( (j>=19) and (j<23) and (Celli == j-18+400) ):
                            self.cells_C[j].Fill(self.f(event))

## EA
                        if ( (j>=23) and (j<28) and (Celli == j-23+112)):
                            self.cells_C[j].Fill(self.f(event))
## EB
                        if ( (j>=28) and (j<33) and (Celli == j-28+211)):
                            self.cells_C[j].Fill(self.f(event))
## ED
                        if ( (j>=35) and (j<37) and (Celli == j-34+404)):
                            self.cells_C[j].Fill(self.f(event))

        self.c1.cd()
        
        for s in range(37):
            if s==33 or s==34:
                continue
            f_fitA = ROOT.TF1("f1","[0]*exp(-0.5*((x-[1])/[2])**2)",-3.5,3.5)
            #self.c1.cd()

            self.cells_A[s].SetStats(1)
            self.cells_A[s].Draw()
            if s>=30 and s<=36:
                f_fitA.SetParameters(30,0,0.15)
                self.cells_A[s].Fit("f1","Q0L","",-0.5,0.5)
            else:
                #f_fitA.SetParameters(6,0,1.35)
                f_fitA.SetParameters(40,self.cells_A[s].GetMean(),self.cells_A[s].GetRMS())
                self.cells_A[s].Fit("f1","Q0L","",self.cells_A[s].GetMean()-2*self.cells_A[s].GetRMS(),self.cells_A[s].GetMean()+2*self.cells_A[s].GetRMS())
            f_fitA.SetLineColor(3)
            f_fitA.Draw("same")
            mean1 = f_fitA.GetParameter(1)
            RMS1 = f_fitA.GetParameter(2)
            self.cells_A[s].Fit("f1","Q0L","",mean1-2*RMS1,mean1+2*RMS1)
            mean_final= ROOT.TVirtualFitter.Fitter(self.cells_A[s]).GetParameter(1)

            ## if s>=30 and s<=36:
##                 if (abs(mean_final-self.cells_A[s].GetMean())>0.55):
##                     self.ch_fitA[s]=self.cells_A[s].GetMean()
##                     self.ch_errA[s]=self.cells_A[s].GetMeanError()
##                 else:
##                     self.ch_fitA[s]=mean_final
##                     self.ch_errA[s]=ROOT.TVirtualFitter.Fitter(self.cells_A[s]).GetParError(1)
##             else:
##                 if (abs(mean_final-self.cells_A[s].GetMean())>0.3):
##                     self.ch_fitA[s]=self.cells_A[s].GetMean()
##                     self.ch_errA[s]=self.cells_A[s].GetMeanError()
##                 else:
##                     self.ch_fitA[s]=mean_final
##                     self.ch_errA[s]=ROOT.TVirtualFitter.Fitter(self.cells_A[s]).GetParError(1)

            self.ch_fitA[s]=self.cells_A[s].GetMean()
            self.ch_errA[s]=self.cells_A[s].GetMeanError()   
            
            #self.ch_fitA[s]=self.cells_A[s].GetXaxis().GetBinCenter(self.cells_A[s].GetMaximumBin())
            
            f_fitA.SetLineColor(2)
            f_fitA.Draw("same")

            
            
            self.c1.cd()
            curdate=time.strftime("%Y_%m_%d")     #define the current date, use "%H:%M" to display hours/minutes
            dirname=self.dir+'/gaussplots/'
            if not os.path.exists(dirname):       #check if the directory exists
                os.makedirs(dirname)              #if not, make it
            self.c1.Modified()
            self.c1.Update()
            self.c1.Print(self.dir+curdate+"_"+"gauss_cells_lA%s.eps" % (s));
            print('DEBUG dolayer value :',self.ch_fitA[s],'s :',s,'means :',mean1,self.cells_A[s].GetMean(),'fit mean :',mean_final,'mean error',self.ch_errA[s])

        for t in range(37):
            if t==33 or t==34:
                continue
            f_fitC = ROOT.TF1("f2","[0]*exp(-0.5*((x-[1])/[2])**2)",-3.5,3.5)
            #self.c1.cd()
            self.cells_C[t].SetStats(1)
            self.cells_C[t].Draw();
            if t>=30 and t<=36:
                f_fitC.SetParameters(30,0.,1.5)
                self.cells_C[t].Fit("f2","Q0L","")
            #elif t<10 or (t>=23 and t<28):
            #    f_fitC.SetParameters(10,-1,1.35)
            #    self.cells_C[t].Fit("f1","Q0L","",-4,4)
            else:
                f_fitC.SetParameters(40,self.cells_C[t].GetMean(),self.cells_C[t].GetRMS())
                self.cells_C[t].Fit("f2","Q0L","",self.cells_C[t].GetMean()-2*self.cells_C[t].GetRMS(),self.cells_C[t].GetMean()+2*self.cells_C[t].GetRMS())
            f_fitC.SetLineColor(3)
            f_fitC.Draw("same")
            mean2 = f_fitC.GetParameter(1)
            RMS2 = f_fitC.GetParameter(2)
            self.cells_C[t].Fit("f2","Q0L","",mean2-2*RMS2,mean2+2*RMS2)
            mean_final= ROOT.TVirtualFitter.Fitter(self.cells_C[t]).GetParameter(1)
            ## if t>=30 and t<=36:
##                 if (abs(mean_final-self.cells_C[t].GetMean())>0.55):
##                     self.ch_fitC[t]=self.cells_C[t].GetMean()
##                     self.ch_errC[t]=self.cells_C[t].GetMeanError()
##                 else:
##                     self.ch_fitC[t]=mean_final
##                     self.ch_errC[t]=ROOT.TVirtualFitter.Fitter(self.cells_C[t]).GetParError(1)
##             else:
##                 if (abs(mean_final-self.cells_C[t].GetMean())>0.28):
##                     self.ch_fitC[t]=self.cells_C[t].GetMean()
##                     self.ch_errC[t]=self.cells_C[t].GetMeanError()
##                 else:
##                     self.ch_fitC[t]=mean_final
##                     self.ch_errC[t]=ROOT.TVirtualFitter.Fitter(self.cells_C[t]).GetParError(1)
##             if math.fabs(mean_final) < 0.009:
##                 self.ch_fitC[t]=self.cells_C[t].GetMean()

            self.ch_fitC[t]=self.cells_C[t].GetMean()
            self.ch_errC[t]=self.cells_C[t].GetMeanError()

            #self.ch_fitC[t]=self.cells_C[t].GetXaxis().GetBinCenter(self.cells_C[t].GetMaximumBin())
            
            f_fitC.SetLineColor(2)
            f_fitC.Draw("same")

            dirname=self.dir+'/gaussplots/'
            self.c1.cd()
            self.c1.Modified()
            self.c1.Update()
            self.c1.Print(dirname+curdate+"_"+"gauss_cells_lC%s.eps" % (t));
            print('DEBUG dolayer value :',self.ch_fitC[t],'t :',t ,'means :',mean2,self.cells_C[t].GetMean(),'RMSs :',RMS2,self.cells_C[t].GetRMS(),'fit mean :',mean_final,'fit RMS :',f_fitC.GetParameter(2))

        
        self.graph_lA = ROOT.TGraphErrors()
        self.graph_lB = ROOT.TGraphErrors()
        self.graph_lD = ROOT.TGraphErrors()

        etaA = [ -1.55, -1.45, -1.35, -1.25, -1.15, -0.95, -0.85, -0.75, -0.65, -0.55, -0.45, -0.35, -0.25, -0.15, -0.05, 0.05,  0.15,  0.25,  0.35,  0.45,  0.55,  0.65,  0.75,  0.85,  0.95, 1.15,  1.25,  1.35,  1.45,  1.55]
        etaB = [ -1.45, -1.35, -1.25, -1.15, -1.05, -0.85, -0.75, -0.65, -0.55, -0.45, -0.35, -0.25, -0.15, -0.05, 0.05,  0.15,  0.25,  0.35,  0.45,  0.55,  0.65,  0.75,  0.85, 1.05,  1.15,  1.25,  1.35,  1.45]
        etaD = [ -1.2, -1.0, -0.6, -0.4, -0.2, -0.01, 0.01, 0.2, 0.4, 0.6, 1.0, 1.2]

        for u in range(30): #layer A (0 -> 14 A-side, 15 -> 29 C-side)
            npoints = 0
            if u < 5:
                self.layerA[u]=self.ch_fitA[int(math.fabs(u-27))]
                self.layerAerror[u]=self.ch_errA[int(math.fabs(u-27))]
            if u >= 5 and u < 15:
                self.layerA[u]=self.ch_fitA[int(math.fabs(u-14))]
                self.layerAerror[u]=self.ch_errA[int(math.fabs(u-14))]
            if u >= 15 and u < 25:
                self.layerA[u]=self.ch_fitC[u-15]
                self.layerAerror[u]=self.ch_errC[u-15]
            if u >= 25:
                self.layerA[u]=self.ch_fitC[u-2]
                self.layerAerror[u]=self.ch_errC[u-2]
            npoints = self.graph_lA.GetN()
            self.graph_lA.SetPoint(npoints,etaA[u],self.layerA[u])
            self.graph_lA.SetPointError(npoints,0,self.layerAerror[u])
            

        for v in range(28): #layer B (0 -> 13 A-side, 14 -> 27 C-side)
            npoints = 0
            if v < 5:
                self.layerB[v]=self.ch_fitA[int(math.fabs(v-32))]
                self.layerBerror[v]=self.ch_errA[int(math.fabs(v-32))]
            if v >= 5 and v < 14:
                self.layerB[v]=self.ch_fitA[int(math.fabs(v-23))]
                self.layerBerror[v]=self.ch_errA[int(math.fabs(v-23))]
            if v >= 14 and v < 23:
                self.layerB[v]=self.ch_fitC[v-4]
                self.layerBerror[v]=self.ch_errC[v-4]
            if v >= 23:
                self.layerB[v]=self.ch_fitC[v+5]
                self.layerBerror[v]=self.ch_errC[v+5]
            npoints = self.graph_lB.GetN()
            self.graph_lB.SetPoint(npoints,etaB[v],self.layerB[v])
            self.graph_lB.SetPointError(npoints,0,self.layerBerror[v])
            

        for w in range(12): #layer D (0 -> 5 A-side, 6 -> 11 C-side)
            npoints = 0
            if w < 2:
                self.layerD[w]=self.ch_fitA[int(math.fabs(w-36))]
                self.layerDerror[w]=self.ch_errA[int(math.fabs(w-36))]
            if w >= 2 and w < 6:
                self.layerD[w]=self.ch_fitA[int(math.fabs(w-24))]
                self.layerDerror[w]=self.ch_errA[int(math.fabs(w-24))]
            if w >= 6 and w < 10:
                self.layerD[w]=self.ch_fitC[w+13]
                self.layerDerror[w]=self.ch_errC[w+13]
            if w >= 10:
                self.layerD[w]=self.ch_fitC[w+25]
                self.layerDerror[w]=self.ch_errC[w+25]
            npoints = self.graph_lD.GetN()
            self.graph_lD.SetPoint(npoints,etaD[w],self.layerD[w])
            self.graph_lD.SetPointError(npoints,0,self.layerDerror[w])
            
        self.c1.SetTitle("Plots versus eta")            
        self.c1.cd()
#        ROOT.gStyle.SetOptStat(0)
#        ROOT.gStyle.SetOptFit(0)    
#        ROOT.gROOT.ForceStyle()

        self.cadre.SetStats(0)
        self.cadre.GetXaxis().SetLabelOffset(0.01)
        self.cadre.GetYaxis().SetTitleOffset(1.1)
        self.cadre.GetXaxis().SetLabelSize(0.04)
        self.cadre.GetYaxis().SetLabelSize(0.04)
        self.cadre.GetXaxis().SetNdivisions(503)
        self.cadre.GetXaxis().SetNoExponent()
        self.cadre.GetYaxis().SetTitle("%s in %%" % self.label)
        self.cadre.GetXaxis().SetTitle("eta")
        self.cadre.Draw()
        self.graph_lA.SetMarkerStyle(29)
        self.graph_lA.SetMarkerColor(2)
        self.graph_lB.SetMarkerStyle(22)
        self.graph_lB.SetMarkerColor(4)
        self.graph_lD.SetMarkerStyle(23)
        self.graph_lD.SetMarkerColor(8)
        self.graph_lA.Draw("Pe1,same")
        self.graph_lB.Draw("Pe1,same")
        self.graph_lD.Draw("Pe1,same")

        leg0 = ROOT.TLegend(0.7, 0.8, 0.95, 0.95)
        leg0.SetBorderSize(0)
        leg0.SetFillStyle(0)

        leg0.AddEntry(self.graph_lA, "Sample A", "P")
        leg0.AddEntry(self.graph_lB, "Sample B", "P")
        leg0.AddEntry(self.graph_lD, "Sample D", "P")
        leg0.Draw()


        offsetx = 0.2
        offsety = 0.5

        #--- ATLAS Label
        ATLAS = ROOT.TLatex()
        ATLAS.SetNDC()
        ATLAS.SetTextFont(72)
        ATLAS.SetTextSize(0.06)
        ATLAS.SetTextColor(kBlack)
        ATLAS_Text = "ATLAS Preliminary"
        self.c1.cd()
        #ATLAS.DrawLatex(0.15+offsetx,0.3+offsety,ATLAS_Text)

       
        #--- Preliminary
        WIP = ROOT.TLatex()
        WIP.SetNDC()
        WIP.SetTextFont(72)
        WIP.SetTextSize(0.05)
        WIP.SetTextColor(kBlack)
        WIP_Text = ""
        WIP_Text = "Tile Calorimeter"              
        #WIP.DrawLatex(0.15+offsetx,0.23+offsety,WIP_Text) 
   
        Stat = ROOT.TLatex()
        Stat.SetNDC()
        Stat.SetTextFont(72)
        Stat.SetTextSize(0.035)
        Stat.SetTextColor(kBlack)
        
        self.c1.cd()
        #Stat.DrawLatex(0.15+offsetx,0.17+offsety,"March-Nov 2012")
        self.c1.Modified()
        self.c1.Update()
        self.c1.Print(self.dir+"layer.C")
        self.c1.Print(self.dir+"layer%s.eps"%self.label.replace(' ','_'))
        self.c1.Print(self.dir+"layer%s.C"%self.label.replace(' ','_'))
        self.c1.Print(self.dir+"layer%s.root"%self.label.replace(' ','_'))
        self.c1.Print(self.dir+"layer%s.pdf"%self.label.replace(' ','_'))
