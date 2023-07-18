################################################################################
#
# do_LasCesLayer_plots.py
#
################################################################################
#
# Author: Ammara
#
# Nov 8th 2017
#
# Goal:
#     Do a plot for laser combined method for     
#     specific layers only using Laser and Cs Runs 
#########1#########2#########3#########4#########5#########6#########7#########8

from src.GenericWorker import *
from src.stats import *
import src.MakeCanvas
import src.oscalls
import os.path
import time
class do_LasCesLayer_plots(GenericWorker):
    "Compute history plot Las(combined)&Cs"
    c2 = None
    
    def __init__(self, doPdfEps = False, verbose = False, layers = [], label = "", nDays = -1):
        self.verbose  = verbose
        self.doPdfEps    = doPdfEps
        self.origin   = ROOT.TDatime()
        self.layers    = layers
        self.label    = label
        self.nDaysBef = nDays
        self.tgraph_cesium = {}
        self.tgraph_laser = {}

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir = getPlotDirectory(subdir=self.outputTag)

        for layer in self.layers:
            self.tgraph_laser[layer] = ROOT.TGraphErrors()
            self.tgraph_cesium[layer] = ROOT.TGraphErrors()
        self.time_max = 0
        self.time_min = 10000000000000000

        if self.c2==None:
            self.c2 = src.MakeCanvas.MakeCanvas()
            self.c2.SetTitle("Average layer history plots")

        self.data_laser = dict()
        self.data_cesium = dict()
        for layer in self.layers:
            self.data_laser[layer] = dict()
            self.data_cesium[layer] = dict()
        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag))
        self.HistFile.cd()
        
        self.dirname = "LasCesiumLayersEvolution"
        ROOT.gDirectory.mkdir(self.dirname)
        ROOT.gDirectory.cd(self.dirname)


    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('Las') + run_list.getRunsOfType('cesium'): 
            for layer in self.layers:
                if run.runType=='Las':
                  
                    self.data_laser[layer][run.runNumber] = stats()
                   
                if run.runType=='cesium':
                    self.data_cesium[layer][run.runNumber] = stats()
   
      
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
        layer  = region.GetLayerName() 
        if layer not in self.layers:
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
### histogram filling
                if 'deviation' in event.data:
                    if abs(event.data['deviation'])>100.:
                        print(("error in Laser", event.data['deviation'], " in ",region.GetHash()))
                    else:
                        self.data_laser[layer][event.run.runNumber].fill(event.data['deviation'])        
### Cesium Run information    
            if event.run.runType=='cesium' and 'calibration' in event.data:        
                
                if isinstance(event.data['calibration'], float):
                    if abs(100.*(event.data['calibration']/event.data['f_integrator_db']-1.))>50.:
                        print(("error in Cs", event.data['calibration'],event.data['f_integrator_db'], "in ",region.GetHash()))
          #### filling of histograms for D layers              
                    elif (layer=='D') and abs(100.*(event.data['calibration']/event.data['f_integrator_db']-1.2))<50.:
                        self.data_cesium[layer][event.run.runNumber].fill(100.*(event.data['calibration']/event.data['f_integrator_db']-1.2)/1.2)     #### filling of histograms for all other layers
                    else:
                        self.data_cesium[layer][event.run.runNumber].fill(100.*(event.data['calibration']/event.data['f_integrator_db']-1.))   


    def ProcessStop(self):
        self.HistFile.cd() 
        ROOT.gDirectory.cd(self.dirname)
##### Tgraph for laser evolution
        for layer in self.layers:
            self.tgraph_laser[layer] = ROOT.TGraphErrors()
            for run in run_list.getRunsOfType('Las'):
                print((run.runNumber))
                print(('combined method [laser] ', 'Layer',layer, self.data_laser[layer][run.runNumber].entries, self.data_laser[layer][run.runNumber].mean(), self.data_laser[layer][run.runNumber].error()))
     
                if self.data_laser[layer][run.runNumber].entries!=0:
                    npoints = self.tgraph_laser[layer].GetN()
                    self.tgraph_laser[layer].SetPoint( npoints,run.time_in_seconds,self.data_laser[layer][run.runNumber].mean())
                    self.tgraph_laser[layer].SetPointError(npoints,0., self.data_laser[layer][run.runNumber].error())
             
            self.tgraph_laser[layer].Sort()
            self.tgraph_laser[layer].SetName("Laser"+layer)
            self.tgraph_laser[layer].Write()
               
###### Tgraph for cesium layer evolution                              
        for layer in self.layers:
            self.tgraph_cesium[layer] = ROOT.TGraphErrors()
            i = 0
            for run in run_list.getRunsOfType('cesium') :
                if run.runNumber<100000:
                    continue
                print(run)
                print(('cesium ', 'layer', layer, self.data_cesium[layer][run.runNumber].entries, self.data_cesium[layer][run.runNumber].mean(), self.data_cesium[layer][run.runNumber].error()))
                if self.data_cesium[layer][run.runNumber].entries!=0:
                    self.tgraph_cesium[layer].SetPoint( i, run.time_in_seconds, self.data_cesium[layer][run.runNumber].mean())
                    self.tgraph_cesium[layer].SetPointError(i, 0., self.data_cesium[layer][run.runNumber].error())
                    i = i+1
##### Normalizing all the cesium points to ist cesium point in graph           
        
            if self.tgraph_cesium[layer].GetN()>0:
                self.tgraph_cesium[layer].Sort()
                Y = self.tgraph_cesium[layer].GetY()
                EY = self.tgraph_cesium[layer].GetEY()
                X = self.tgraph_cesium[layer].GetX()
                Y0 = Y[0]
                for i in range(self.tgraph_cesium[layer].GetN()):
                    Y[i] = Y[i] - Y0
                    self.tgraph_cesium[layer].SetPoint( i, X[i], Y[i])
                    self.tgraph_cesium[layer].SetPointError(i , 0., EY[i])
        
            self.tgraph_cesium[layer].Sort()
            self.tgraph_cesium[layer].SetName("cesium"+layer)
            self.tgraph_cesium[layer].Write()
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
        layerLegends = self.layers
        colors = [1+i for i in range(2*len(self.layers))]
        marker = 20
        color = 0
      
        for layer in sorted (list(set(self.layers))):
            self.tgraph_laser[layer].SetMaximum(10.0)
            self.tgraph_laser[layer].SetMinimum(-10.)
            
            self.draw_layer(self.tgraph_laser[layer],option,colors[color],marker)
            legend.AddEntry(self.tgraph_laser[layer],"%s Laser Combined "%layer,"P")
            self.tgraph_laser[layer].GetYaxis().SetTitle("Average Layer Response[%]")
                
                
            option="P,same"
            color +=1

        self.c2.cd()
        layerLegends = self.layers
       
        for layer in sorted (list(set(self.layers))):
            self.tgraph_cesium[layer].SetMaximum(10.0)
            self.tgraph_cesium[layer].SetMinimum(-10.)
                    
            self.draw_layer(self.tgraph_cesium[layer],option,colors[color],marker)
            legend.AddEntry(self.tgraph_cesium[layer],"%s Cesium"%layer,"P")
            self.tgraph_cesium[layer].GetYaxis().SetTitle("Average Layer Response[%]")
              
              
            marker +=1
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
            self.c2.Print(self.dir+"/combinedLasCesLayer.pdf")
            self.c2.Print(self.dir+"/combinedLasCesLayer.eps")
        else:
            self.c2.Print(self.dir+"/combinedLasCesLayer.root")
           
                
    def draw_layer(self, tgraph, option, color=-1, marker=-1):
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

       
         
         
        
