################################################################################
#
# do_AverageLayers_GausWidth.py
#
################################################################################
#
# Author: Ammara
#
# created : 07 SEP 2019
# Modified: 1st Feb 2022 to add gaussian width Tgraph
# Goal:
#     Potential public plots of average layer evolution for EB and LB layers seperately as well as combined and gaussian width evolution of the fit using combined method   
#
# Tips:
#     for gaussian width set doGaussianWidthplot = True
#     for splitting LB and EB set splitBarrels=True  
#     default Fit = chi2 if want to use likelihood change Fit=LQ 
# for Run2 chi2 fit method is used in public plots...
#########1#########2#########3#########4#########5#########6#########7#########8

from src.GenericWorker import *
from src.oscalls import *
import ROOT
import math
import time
import csv
class do_AverageLayers_GausWidth(GenericWorker):
     "Makes plots of layer averages For specific region"
     c1 = None
     c2 = None
     def __init__(self,f =(lambda event: event.data['deviation']), label="", layers=['A','BC','D','B'],doPdfEps=False, Fit="chi2", meanwidth=1,splitBarrels=False,doGaussianWidthplot=True, verbose=False ):
         
          self.f = f
          self.splitBarrels = splitBarrels
          self.doGaussianWidthplot = doGaussianWidthplot
          self.meanwidth = meanwidth
          self.label = label
          self.layers = layers
          self.doPdfEps = doPdfEps
          self.verbose  = verbose
          self.Fit = Fit
          self.t_max  = 0
          self.t_min  = 10000000000000000
          self.histo = dict()
          if self.splitBarrels:
               self.histo_LB = dict()
               self.histo_EB = dict()
          for layer in self.layers:
               self.histo[layer] = dict()
               if self.splitBarrels:
                    self.histo_LB[layer] = dict()
                    self.histo_EB[layer] = dict()
               
          self.outputTag = ""
          if 'outputTag' in globals():
               self.outputTag = outputTag # global variable to tag output histogram file name
          self.dir    = getPlotDirectory(subdir=self.outputTag)

          try:
              self.HistFile.cd()
          except:
              self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag))
              self.HistFile.cd()
              
          self.dirname = "AverageResponsePerLayer"
          ROOT.gDirectory.mkdir(self.dirname)
          ROOT.gDirectory.cd(self.dirname)
          if self.c1==None:
               self.c1 = src.MakeCanvas.MakeCanvas()
               self.c1.SetTitle("GaussianWidthPerLayer")

          if self.c2==None:
              self.c2 = src.MakeCanvas.MakeCanvas()
              self.c2.SetTitle("Average Layer Response")

     def ProcessStart(self):

          global run_list
          ordered_list = sorted(run_list.getRunsOfType('Las'), key=lambda run: run.runNumber)
          for run in ordered_list:
               for layer in self.layers:
                    name = "Combined"+layer+repr(run)
                    title = layer+repr(run)
                    self.histo[layer][run] = ROOT.TH1F(name, title, 200, -30., 20.)
                    if self.splitBarrels:
                         self.histo_LB[layer][run] = ROOT.TH1F(name, "LB_"+title, 150, -20., 20.)
                         self.histo_EB[layer][run] = ROOT.TH1F(name, "EB_"+title, 150, -20., 20.)
                   

          n = len(ordered_list)
          if n!=0:
               self.t_min = int(ordered_list[0].time_in_seconds)
               self.t_max = int(ordered_list[n-1].time_in_seconds)
                    

     def ProcessRegion(self, region):
          
          region_name = region.GetHash()
          numbers = region.GetNumber(1)
          if len(numbers)!=4:
               return region
          
          # only for ADCs 
          [part, module, pmt, gain] = numbers
          layer =  region.GetLayerName()
          cell  = region.GetCellName()
        
          for event in region.GetEvents():
               if event.run.runType=='Las':
                    pmt_region = str(event.region)
                   
                    if 'status' not in event.data:
                         continue
                 
                    if event.data['status']&0x4 or event.data['status']&0x10:
                         continue
                    
                    #if (abs(event.data['HV']-event.data['hv_db'])>10.):  # Bad HV, will bias results.
                     #    continue
                
                    saturation_limits = [800., 12.] # in pC Saturation limits
                    if (event.data['signal']>saturation_limits[gain]): 
                         print (event.region.GetHash(), event.data['signal'],saturation_limits[gain]) 
                         continue
                
                    underflow_limits = [4., 0.06]   # in pC Underflow limits
                    if (event.data['signal']<underflow_limits[gain]):  
                         continue

                    if 'deviation' in event.data and layer in self.histo:
                         if abs(event.data['deviation'])>20.:
                              print ("error in Laser", event.data['deviation'], " in ",event.region.GetHash() )
                         else:
                              self.histo[layer][event.run].Fill(event.data['deviation'])
                    
                    if self.splitBarrels:
                         if pmt_region.find('LB')!=-1:
                              if 'deviation' in event.data and layer in self.histo_LB:
                                   self.histo_LB[layer][event.run].Fill(event.data['deviation'])
                         
                         elif pmt_region.find('EB')!=-1: 
                              if 'deviation' in event.data and layer in self.histo_EB:
                                   self.histo_EB[layer][event.run].Fill(event.data['deviation'])
                              
                   
     def ProcessStop(self):
         
          tgraph = {}
          tgraph_LB = {}
          tgraph_EB = {}
          tgraph_width = {}
          outfile = open("LayeraveragesFile2018.csv","w")
          self.HistFile.cd(self.dirname)
          for layer in self.layers:
               tgraph[layer] = ROOT.TGraphErrors()
               tgraph_width[layer] = ROOT.TGraphErrors()
               npoints = 0
               n = 0
               for run, hist in self.histo[layer].items():
                    print ("Layer",layer, run.runNumber, hist.GetEntries(), hist.GetMean(), hist.GetRMS())
                    if hist.GetRMS()!=0.0 and hist.GetMean()!=0.0:
                         fit1 = ROOT.TF1("fit1", "gaus")
                         if hist.GetEntries()>4:
                              hist.Fit(fit1,self.Fit)
                              tgraph[layer].SetPoint(npoints, run.time_in_seconds,fit1.GetParameter(1))
                              tgraph[layer].SetPointError(npoints, 600,fit1.GetParError(1)) 
                              if self.doGaussianWidthplot:
                                   tgraph_width[layer].SetPoint(npoints, run.time_in_seconds,fit1.GetParameter(self.meanwidth))
                                   tgraph_width[layer].SetPointError(npoints, 600,fit1.GetParError(self.meanwidth)) 
                                   n+=1
                              outfile.write("%s, %d, %d, %f\n" % (layer, run.runNumber, run.time_in_seconds,fit1.GetParameter(1)))
                              npoints+=1
                              
                    hist.Write()
                    hist.Delete()
               tgraph[layer].Sort()
               tgraph[layer].SetName("Combined_"+layer)
               tgraph[layer].Write()
               tgraph_width[layer].Sort()
               tgraph_width[layer].SetName("GaussianWidth_"+layer)
               tgraph_width[layer].Write()
          outfile.close()
          

          if self.splitBarrels:
               for layer in self.layers:
                    tgraph_LB[layer] = ROOT.TGraphErrors()
                    npoints = 0
                    for run, hist in self.histo_LB[layer].items():
                         if hist.GetRMS()!=0.0 and hist.GetMean()!=0.0:
                              fit1 = ROOT.TF1("fit1", "gaus")
                              if hist.GetEntries()>4:
                                   hist.Fit(fit1,self.Fit)
                                   tgraph_LB[layer].SetPoint(npoints, run.time_in_seconds, 
                                                             fit1.GetParameter(1))
                                   tgraph_LB[layer].SetPointError(npoints, 600, 
                                                                  fit1.GetParError(1))
                                   npoints+=1
                              
                              hist.Write()
                              hist.Delete()
                    tgraph_LB[layer].Sort()
                    tgraph_LB[layer].SetName("LBCombined_"+layer)
                    tgraph_LB[layer].Write()



               
                    tgraph_EB[layer] = ROOT.TGraphErrors()
                    npoints = 0
                    for run, hist in self.histo_EB[layer].items():
                         if hist.GetRMS()!=0.0 and hist.GetMean()!=0.0:
                              fit1 = ROOT.TF1("fit1", "gaus")
                              if hist.GetEntries()>4:
                                   hist.Fit(fit1,self.Fit)
                                   tgraph_EB[layer].SetPoint(npoints, run.time_in_seconds, 
                                                             fit1.GetParameter(1))
                                   tgraph_EB[layer].SetPointError(npoints, 600, 
                                                                  fit1.GetParError(1))
                                   npoints+=1
                           
                         hist.Write()
                         hist.Delete()
                    tgraph_EB[layer].Sort()
                    tgraph_EB[layer].SetName("EBCombined_"+layer)
                    tgraph_EB[layer].Write()
              
        ###############################################################################################
        ## Now do the drawing part
        #
        ## The following formatting should be good for making public plots
        ##############################################################################################
             
          x = 0.5
          y = 0.7
          ROOT.gStyle.SetTimeOffset(0)
          if self.label=='':
          ### You may have to play with this to make sure the legend is not covering data
               legend = ROOT.TLegend(x+0.11, y, x+0.33, y+0.2) 
          else:
               legend = ROOT.TLegend(x, y, x+0.22, y+0.2)
          
          self.c2.cd()
          option="AP"
          layerLegends = self.layers
          colors = [1+i for i in range(len(self.layers))]
          marker = 20
          color = 0
          for layer in sorted (list(set(self.layers))):
               tgraph[layer].SetMaximum(20.0)
               tgraph[layer].SetMinimum(-20.)
          
               self.draw_layer(tgraph[layer],option,colors[color],marker)
               legend.AddEntry(tgraph[layer],"%s"%layer,"P")
               tgraph[layer].GetYaxis().SetTitle("Average Laser Drift[%]");
          
               marker +=1
               option="P,same"
               color +=1

          if self.doGaussianWidthplot:
               self.c1.cd()
               option="AP"
               layerLegends = self.layers
               colors = [1+i for i in range(len(self.layers))]
               marker = 20
               color = 0
               for layer in sorted (list(set(self.layers))):
                    tgraph_width[layer].SetMaximum(10.0)
                    tgraph_width[layer].SetMinimum(-10.)
              
                    self.draw_layer(tgraph_width[layer],option,colors[color],marker)
                    legend.AddEntry(tgraph_width[layer],"%s Combined "%layer,"P")
                    tgraph_width[layer].GetYaxis().SetTitle("Laser Drift Gaussian width[%][%]");
                    option="P,same"
                    color +=1
         
          if self.splitBarrels:
               self.c2.cd()
               option="AP"
               layerLegends = self.layers
               colors = [1+i for i in range(len(self.layers))]
               marker = 20
               color = 0
               for layer in sorted (list(set(self.layers))):
                    tgraph_LB[layer].SetMaximum(20.0)
                    tgraph_LB[layer].SetMinimum(-20.)
                    tgraph_EB[layer].SetMaximum(20.)
                    tgraph_EB[layer].SetMinimum(-20.)

                    self.draw_layer(tgraph_LB[layer],option,colors[color],marker)
                    legend.AddEntry(tgraph_LB[layer],"%s [LB] "%layer,"P")
                    tgraph_LB[layer].GetYaxis().SetTitle("LB Average Response Deviation [%]");
                    self.draw_layer(tgraph_EB[layer],option,colors[color],marker)
                    legend.AddEntry(tgraph_EB[layer],"%s [EB] "%layer,"P")
                    tgraph_EB[layer].GetYaxis().SetTitle("EB Average Response Deviation [%]")
                    marker +=1
                    option="P,same"
                    color +=1


          legend.Draw()
            #The following code is to at the "ATLAS" label for public plots
          l = ROOT.TLatex()
          l.SetNDC()
          l.SetTextFont(72)
          l.SetTextColor(1)
          l.SetTextSize(0.03)
          l.DrawLatex(.19, .91, "ATLAS")        
          
          p = ROOT.TLatex()
          p.SetNDC()
          p.SetTextFont(42)
          p.SetTextColor(1)
          p.SetTextSize(0.03)
          p.DrawLatex(.27, .91, "Internal")
          
          m = ROOT.TLatex()
          m.SetNDC()
          m.SetTextFont(42)
          m.SetTextColor(1)
          m.SetTextSize(0.03)
          m.DrawLatex(.19, .88, "Tile Calorimeter")
          #End Label Code         
          
          self.c2.Modified()
          self.c2.Update()
          self.c1.Modified()
          self.c1.Update()
          if self.doPdfEps:
               self.c2.Print(self.dir+"/Layer.pdf")
               self.c2.Print(self.dir+"/Layer.eps")
               if self.doGaussianWidthplot:
                    self.c1.Print(self.dir+"/LayerGaussianWidth.pdf")
                    self.c1.Print(self.dir+"/LayerGaussianWidth.eps")
               if self.splitBarrels:
                    self.c2.Print(self.dir+"/EBLayer.pdf")
                    self.c2.Print(self.dir+"/EBLayer.eps")
                    self.c2.Print(self.dir+"/LBLayer.pdf")
                    self.c2.Print(self.dir+"/LBLayer.eps")
          else:
               self.c2.Print(self.dir+"/Layer.root")

     def draw_layer(self, tgraph, option, color=-1, marker=-1):
          size=0.8
          tgraph.GetXaxis().SetTimeDisplay(1)
          tgraph.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
          tgraph.GetXaxis().SetLabelSize(0.03)
          tgraph.GetXaxis().SetLabelOffset(0.02)
          tgraph.GetXaxis().SetTitle("Time [dd/mm and year]")
          tgraph.GetXaxis().SetTitleSize(0.05)
          tgraph.GetYaxis().SetTitleSize(0.05)
       
          if marker!=-1:
               tgraph.SetMarkerStyle(marker)
          tgraph.SetMarkerSize(size)
          if color!=-1:
               tgraph.SetMarkerColor(color)
               tgraph.SetLineColor(color)
          
          tgraph.GetXaxis().SetNdivisions(705, 0) 
          
          d = int(86400)
          tgraph.GetXaxis().SetLimits(d*((self.t_min-d)/d),d*((self.t_max+d)/d))
          tgraph.Sort()
          tgraph.Draw(option)
