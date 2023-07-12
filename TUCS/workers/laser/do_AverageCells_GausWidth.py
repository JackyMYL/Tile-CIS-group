################################################################################
#
# do_AverageCells_GausWidth.py
#
################################################################################
#
# Author: Ammara Ahmad 
# created : Sep 21st 2017
# Modified: 31st Jan 2022 to add gaussian width Tgraph
#
# Goal:
#     Do a plot of average cell evolution and gaussian width evolution of the fit using combined method 
# 
# Tips:
#     for gaussian width set doGaussianWidthplot = True
#     for E-cells plot likelihood fit is used for Run2 data which is hard-coded here... 
#########1#########2#########3#########4#########5#########6#########7#########8

from src.GenericWorker import *
from src.oscalls import *
import ROOT
import math
import time
from ROOT import gStyle
import csv
class do_AverageCells_GausWidth(GenericWorker):
     "Makes plots of specific cells evolution over time"

     c2 = None
     c1 = None
     def __init__(self,f =(lambda event: event.data['deviation']), label="", cells=[], doPdfEps=False, verbose=False, doGaussianWidthplot=True, meanwidth=1):

          self.cells = cells
          self.doGaussianWidthplot = doGaussianWidthplot
          self.meanwidth = meanwidth
          self.f = f
          self.label = label
          self.doPdfEps = doPdfEps
          self.verbose  = verbose
          self.t_max  = 0
          self.t_min  = 10000000000000000
          self.histo = dict()
          self.outputTag = outputTag # global variable to tag output histogram file name
          self.dir = getPlotDirectory(subdir=self.outputTag)
        
          for cell in self.cells:
               self.histo[cell] = dict()
                    
          try:
               self.HistFile.cd()
          except:
               self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag)) 
          self.HistFile.cd()
              
          self.dirname = "CellsEvolution"
          ROOT.gDirectory.mkdir(self.dirname)
          ROOT.gDirectory.cd(self.dirname)


          if self.c2==None:
               self.c2 = src.MakeCanvas.MakeCanvas()
               self.c2.SetTitle("Average Cell Response Deviation")
          if self.c1==None:
               self.c1 = src.MakeCanvas.MakeCanvas()
               self.c1.SetTitle("GaussianWidthPerCell")

     def ProcessStart(self):

          global run_list
          ordered_list = sorted(run_list.getRunsOfType('Las'), key=lambda run: run.runNumber)
          for run in ordered_list:
               for cell in self.cells:
                    name = "Combined"+cell+repr(run)
                    title = cell+repr(run)
                    if cell == 'E1' or cell == 'E2' or cell == 'E3' or cell == 'E4':
                         self.histo[cell][run] = ROOT.TH1F(name, title, 150, -40., 20.)
                    else:
                         self.histo[cell][run] = ROOT.TH1F(name, title, 150, -30., 20.)
              
          n = len(ordered_list)
          if n!=0:
               self.t_min = int(ordered_list[0].time_in_seconds)
               self.t_max = int(ordered_list[n-1].time_in_seconds)
                    

     def ProcessRegion(self, region):


          numbers = region.GetNumber(1)
          if len(numbers)!=4:
               return region
        # only for ADCs 
          [part, module, pmt, gain] = numbers
          layer =  region.GetLayerName()
          cell  = region.GetCellName()
        
          for event in region.GetEvents():
               if event.run.runType=='Las':
                    if 'status' not in event.data:
                         continue
                
                    if event.data['status']&0x4 or event.data['status']&0x10:
                         continue
                
                
                    #if (abs(event.data['HV']-event.data['hv_db'])>10.):  # Bad HV, will bias results.
                     #    continue
                

                    saturation_limits = [800., 12.] # in pC Saturation limits
                    if (event.data['signal']>saturation_limits[gain]): 
                         print("Channel {} signal {} pC  over saturation limits ({} pC)".format(event.region.GetHash(), event.data['signal'],saturation_limits[gain])) 
                         continue
                
                    underflow_limits = [4., 0.06]   # in pC Underflow limits
                    if (event.data['signal']<underflow_limits[gain]):  
                         continue

                    if 'deviation' in event.data and cell in self.histo:
                         if abs(event.data['deviation'])>20.:
                              if self.verbose:
                                   print ("error in Laser cell Evol", event.data['deviation'], " in ",event.region.GetHash())
                         else:
                              self.histo[cell][event.run].Fill(event.data['deviation'])
                         
                              
     def ProcessStop(self):
         
          tgraph = {}
          tgraph_width = {}
          outfile = open("CellsCSVFile.csv","w") 
          self.HistFile.cd(self.dirname)
        
          for cell in self.cells:
               tgraph[cell] = ROOT.TGraphErrors()
               tgraph_width[cell] = ROOT.TGraphErrors()
               npoints = 0
               n = 0
               for run, hist in self.histo[cell].items():
                    if self.verbose:
                         print("cell {} run {} histogram: entries {} mean {} and RMS {}".format(cell,run.runNumber, hist.GetEntries(), hist.GetMean(), hist.GetRMS()))
                    if hist.GetRMS()!=0.0 and hist.GetMean()!=0.0:
                         fit1 = ROOT.TF1("fit1", "gaus")
                         if hist.GetEntries()>4:
                              if cell == 'E1' or cell == 'E2' or cell == 'E3' or cell == 'E4':
                                   hist.Fit(fit1,"LQ") #Likelihood fit
                                   if self.verbose:
                                        print ('Likelihood fitting for {}'.format(cell))
                              else:
                                   hist.Fit(fit1,"")     #chi-2 Fit
                                   if self.verbose:
                                        print ('chi2 fitting for {}'.format(cell))
                              tgraph[cell].SetPoint(npoints, run.time_in_seconds,fit1.GetParameter(1))
                              tgraph[cell].SetPointError(npoints, 600,fit1.GetParError(1))
                              if self.doGaussianWidthplot:
                                   tgraph_width[cell].SetPoint(npoints, run.time_in_seconds,fit1.GetParameter(self.meanwidth))
                                   tgraph_width[cell].SetPointError(npoints, 600,fit1.GetParError(self.meanwidth)) 
                                   n+=1
                              outfile.write("%s, %d, %d, %f\n" % (cell, run.runNumber, run.time_in_seconds, fit1.GetParameter(1)))
                              npoints+=1
                        
                    hist.Write()
                    hist.Delete()
               tgraph[cell].Sort()
               tgraph[cell].SetName("Combined_"+cell)
               tgraph[cell].Write()
               tgraph_width[cell].Sort()
               tgraph_width[cell].SetName("GaussianWidth_"+cell)
               tgraph_width[cell].Write()
          outfile.close()
         #
        ## Now do the drawing part
        #
        ## The following formatting should be good for making public plots
        #
             
          x = 0.5
          y = 0.7
          ROOT.gStyle.SetTimeOffset(0)
          if self.label=='':
               # You may have to play with this to make sure the legend 
               # is not covering data
               legend = ROOT.TLegend(x+0.11, y, x+0.33, y+0.2) 
          else:
               legend = ROOT.TLegend(x, y, x+0.22, y+0.2)
               
          self.c2.cd()
          option="AP"
          cellLegends = self.cells
          colors = [1+i for i in range(len(self.cells))]
          marker = 20
          color = 0
          for cell in sorted (list(set(self.cells))):
               tgraph[cell].SetMaximum(10.0)
               tgraph[cell].SetMinimum(-10.)
               self.draw_cell(tgraph[cell],option,colors[color],marker)
               legend.AddEntry(tgraph[cell],"%s Combined "%cell,"P")
               tgraph[cell].GetYaxis().SetTitle("Average Cell Response Deviation [%]");
               option="P,same"
               color +=1
              
               

          if self.doGaussianWidthplot:
               self.c1.cd()
               option="AP"
               cellLegends = self.cells
               colors = [1+i for i in range(len(self.cells))]
               marker = 20
               color = 0
               for cell in sorted (list(set(self.cells))):
                    tgraph_width[cell].SetMaximum(10.0)
                    tgraph_width[cell].SetMinimum(-10.)
              
                    self.draw_cell(tgraph_width[cell],option,colors[color],marker)
                    legend.AddEntry(tgraph_width[cell],"%s Combined "%cell,"P")
                    tgraph_width[cell].GetYaxis().SetTitle("Laser Drift Gaussian width[%][%]");
                    option="P,same"
                    color +=1



          legend.Draw()
 #The following code is to at the "ATLAS" label for public plots
          l = ROOT.TLatex()
          l.SetNDC()
          l.SetTextFont(72)
          l.SetTextColor(1)
          l.SetTextSize(0.05)
          l.DrawLatex(.3, .86, "ATLAS")        
               
          p = ROOT.TLatex()
          p.SetNDC()
          p.SetTextFont(42)
          p.SetTextColor(1)
          p.SetTextSize(0.05)
          p.DrawLatex(.415, .86, "Internal")
               
          m = ROOT.TLatex()
          m.SetNDC()
          m.SetTextFont(42)
          m.SetTextColor(1)
          m.DrawLatex(.32, .81, "Tile Calorimeter")
#End Label Code
          
          self.c2.Modified()
          self.c2.Update()
          self.c1.Modified()
          self.c1.Update()

          if self.doPdfEps:
               self.c2.Print(self.dir+"/CellCombined.pdf")
               self.c2.Print(self.dir+"/CellCombined.eps")
               if self.doGaussianWidthplot:
                    self.c1.Print(self.dir+"/CellGaussianWidth.pdf")
                    self.c1.Print(self.dir+"/CellGaussianWidth.eps")
          else:
               self.c2.Print(self.dir+"/CellCombined.root")
               if self.doGaussianWidthplot:
                    self.c1.Print(self.dir+"/CellGaussianWidth.root")
                    self.c1.Print(self.dir+"/CellGaussianWidth.C")
               self.c2.Print(self.dir+"/CellCombined.C")
           
                
     def draw_cell(self, tgraph, option, color=-1, marker=-1):
          size=1.0
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

     
