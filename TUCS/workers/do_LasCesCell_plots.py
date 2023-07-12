################################################################################
#
# do_LasCesCell_plots.py
#
################################################################################
#
# Author: Ammara
#
# Nov 7th 2017
#
# Goal:
#     Do a plot for laser combined method for     
#     specific cells only using Laser and Cs Runs 
#########1#########2#########3#########4#########5#########6#########7#########8

from src.GenericWorker import *
from src.stats import *
import src.MakeCanvas
import src.oscalls
import os.path
import time
class do_LasCesCell_plots(GenericWorker):
    "Compute history plot Las(combined)&Cs"
    c2 = None
    
    def __init__(self, doPdfEps = False, verbose = False, cells = [], label = "", nDays = -1):
        self.verbose  = verbose
        self.doPdfEps    = doPdfEps
        self.origin   = ROOT.TDatime()
        self.cells    = cells
        self.label    = label
        self.nDaysBef = nDays
        self.tgraph_cesium = {}
        self.tgraph_laser = {}

        for cell in self.cells:
            self.tgraph_laser[cell] = ROOT.TGraphErrors()
            self.tgraph_cesium[cell] = ROOT.TGraphErrors()       

        self.time_max = 0
        self.time_min = 10000000000000000

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir = getPlotDirectory(subdir=self.outputTag)

        if self.c2==None:
            self.c2 = src.MakeCanvas.MakeCanvas()
            self.c2.SetTitle("Average cells evolution plots")
### creating Histograms dictionary for cells 
        self.data_laser = dict()
        self.data_cesium = dict()
        for cell in self.cells:
            self.data_laser[cell] = dict()
            self.data_cesium[cell] = dict()
        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag))
        self.HistFile.cd()

        self.dirname = "LasCesiumCellsEvolution"
        ROOT.gDirectory.mkdir(self.dirname)
        ROOT.gDirectory.cd(self.dirname)


    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('Las') + run_list.getRunsOfType('cesium'): 
            for cell in self.cells:
                if run.runType=='Las':
                    self.data_laser[cell][run.runNumber] = stats()
                   
                if run.runType=='cesium':
                    self.data_cesium[cell][run.runNumber] = stats()
   
        for run in run_list.getRunsOfType('Las') + run_list.getRunsOfType('cesium'): 
            if run.time == None: continue
            time = run.time_in_seconds
            if run.time_in_seconds < self.time_min:
                self.time_min = run.time_in_seconds
                self.origin = ROOT.TDatime(str(run.time))
                
            if run.time_in_seconds > self.time_max:
                self.time_max = run.time_in_seconds
            self.nDaysBef = self.time_max - self.nDaysBef*86400
            

    def ProcessRegion(self, region):
        numbers = region.GetNumber()

        if len(numbers)==4:
            [part, module, channel, gain] = numbers
        elif len(numbers)==3:
            [part, module, channel] = numbers
        else:
            return 
        cell  = region.GetCellName() 
        if cell not in self.cells:
            return
        saturation_limits = [760., 12.] # in pC 
        underflow_limits = [4., 0.06]   # in pC Underflow limits

        for event in region.GetEvents():

### Laser Run information           
            if event.run.runType=='Las':

                if event.data['status']!=0 or not event.data['is_OK']:
                    continue
                if (event.data['calibration']<0. or event.data['lasref_db']<=0):
                    continue
                if (event.data['HV']<10.) and (event.data['HVSet']<10.):
                    continue
                if (abs(event.data['HV']-event.data['hv_db'])>10): # bad HV, will bias fiber correction
                    continue
                if (event.data['signal']>saturation_limits[gain]):
                    continue
                if ('problems' in event.data):
                    continue
### laser histogram filling
                if 'deviation' in event.data:
                    self.data_laser[cell][event.run.runNumber].fill(event.data['deviation'])
            
### Cesium Run information
            if event.run.runType=='cesium' and 'calibration' in event.data:        
                if isinstance(event.data['calibration'], float):
                    if abs(100.*(event.data['calibration']/event.data['f_integrator_db']-1.2)/1.2)>100.:
                        print(("error in Cs", event.data['calibration'],event.data['f_integrator_db'], "in ",region.GetHash()))
#### filling of cesium histograms for D cells in LB     
                    elif (cell=='D0' or cell=='D1' or cell=='D2' or cell=='D3'):
                        self.data_cesium[cell][event.run.runNumber].fill(100.*(event.data['calibration']/event.data['f_integrator_db']-1.2)/1.2)   
### filling of cesium histograms for all other cells       
                    else :
                        self.data_cesium[cell][event.run.runNumber].fill(100.*(event.data['calibration']/event.data['f_integrator_db']-1.))   


    def ProcessStop(self):
        self.HistFile.cd()
        ROOT.gDirectory.cd(self.dirname)
##### Tgraph for laser cell evolution
        for cell in self.cells:
            self.tgraph_laser[cell] = ROOT.TGraphErrors()
            for run in run_list.getRunsOfType('Las'):
                print((run.runNumber))
                print(('combined method [laser] ', 'cell',cell, self.data_laser[cell][run.runNumber].entries, self.data_laser[cell][run.runNumber].mean(), self.data_laser[cell][run.runNumber].error()))
                
                if self.data_laser[cell][run.runNumber].entries!=0:
                    npoints = self.tgraph_laser[cell].GetN()
                    self.tgraph_laser[cell].SetPoint(npoints,run.time_in_seconds, self.data_laser[cell][run.runNumber].mean())
                    self.tgraph_laser[cell].SetPointError(npoints, 0., self.data_laser[cell][run.runNumber].error())

            self.tgraph_laser[cell].Sort()
            self.tgraph_laser[cell].SetName("Laser"+cell)
            self.tgraph_laser[cell].Write()
               
###### Tgraph for cesium cell evolution               
        for cell in self.cells:
            self.tgraph_cesium[cell] = ROOT.TGraphErrors()
            i = 0
            for run in run_list.getRunsOfType('cesium') :
                if run.runNumber<100000:
                    continue
                print(run)
                print(('cesium ','cell',cell, self.data_cesium[cell][run.runNumber].entries, self.data_cesium[cell][run.runNumber].mean(), self.data_cesium[cell][run.runNumber].error()))
                if self.data_cesium[cell][run.runNumber].entries!=0:
                    self.tgraph_cesium[cell].SetPoint( i, run.time_in_seconds,self.data_cesium[cell][run.runNumber].mean())
                    self.tgraph_cesium[cell].SetPointError(i, 0.,self.data_cesium[cell][run.runNumber].error())
                    i = i+1

##### Normalizing all the cesium points to ist cesium point in graph    
            if self.tgraph_cesium[cell].GetN()>0:
                self.tgraph_cesium[cell].Sort()
                Y = self.tgraph_cesium[cell].GetY()
                EY = self.tgraph_cesium[cell].GetEY()
                X = self.tgraph_cesium[cell].GetX()
                Y0 = Y[0]
                for i in range(self.tgraph_cesium[cell].GetN()):
                    Y[i] = Y[i] - Y0
                    self.tgraph_cesium[cell].SetPoint( i, X[i], Y[i])
                    self.tgraph_cesium[cell].SetPointError(i , 0., EY[i])
         
            self.tgraph_cesium[cell].Sort()
            self.tgraph_cesium[cell].SetName("cesium"+cell)
            self.tgraph_cesium[cell].Write()       
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
        colors = [1+i for i in range(2*len(self.cells))]
        marker = 20
        color = 0

        for cell in sorted (list(set(self.cells))):
            self.tgraph_laser[cell].SetMaximum(10.0)
            self.tgraph_laser[cell].SetMinimum(-10.)
            
            self.draw_cell(self.tgraph_laser[cell],option,colors[color],marker)
            legend.AddEntry(self.tgraph_laser[cell],"%s Laser combined "%cell,"P")
            self.tgraph_laser[cell].GetYaxis().SetTitle("Average cell Response[%]")
             
            option="P,same"
            color +=1

        self.c2.cd()
        cellLegends = self.cells
       
        for cell in sorted (list(set(self.cells))):
            self.tgraph_cesium[cell].SetMaximum(10.0)
            self.tgraph_cesium[cell].SetMinimum(-10.)
                    
            self.draw_cell(self.tgraph_cesium[cell],option,colors[color],marker)
            legend.AddEntry(self.tgraph_cesium[cell],"%s Cesium"%cell,"P")
            self.tgraph_cesium[cell].GetYaxis().SetTitle("Average cell Response[%]")
              
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
            
        if self.doPdfEps:
            self.c2.Print(self.dir+"/CombinedLasCesCell.pdf")
            self.c2.Print(self.dir+"/CombinedLasCesCell.eps")
        else:
            self.c2.Print(self.dir+"/CombinedLasCesCell.root")
           
                
         
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
        tgraph.Sort()
        tgraph.Draw(option)

       
         
         
        
