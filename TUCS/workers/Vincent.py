############################################################
#
# Vincent.py
#
############################################################
#
# Author: Henric
# Date: during the June Atlas week 2013
# Aim: produce the famous Vincent plot in TUCS
#
# Input parameters are:
#
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8 
#2345678901234567890123456789012345678901234567890123456789012345678901234567890
#
###########################################################

from src.GenericWorker import *
import src.MakeCanvas
import src.oscalls
import os.path

class Vincent(GenericWorker):
    "Compute history plot Las(Direct&Statistical)&Cs"
    c1 = None
    
    def __init__(self, doEps = False, verbose=False):
        self.verbose = verbose
        self.doEps    = doEps
        self.origin   = ROOT.TDatime()

        self.tgraph_cesium = ROOT.TGraphErrors()
        self.tgraph_direct = ROOT.TGraphErrors()
        self.tgraph_stat   = ROOT.TGraphErrors()

        self.time_max = 0
        self.time_min = 10000000000000000

        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),'Vincent')
        src.oscalls.createDir(self.dir)

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Vincent's history plots")

        self.data_direct = dict()
        self.data_stat = dict()
        self.data_cesium = dict()
        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.HIST.root")
        self.HistFile.cd()




    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('Las') + run_list.getRunsOfType('cesium'):            
            if run.time == None: continue
            
            if run.time_in_seconds < self.time_min:
                self.time_min = run.time_in_seconds
                self.origin = ROOT.TDatime(str(run.time))
                
            if run.time_in_seconds > self.time_max:
                self.time_max = run.time_in_seconds

            if run.runType=='Las':
                self.data_direct[run.runNumber] = stats()
                self.data_stat[run.runNumber] = stats()
            elif run.runType=='cesium':
                self.data_cesium[run.runNumber] = stats()


    def ProcessRegion(self, region):
        numbers = region.GetNumber()

        if len(numbers)==4:
            [part, module, channel, gain] = numbers
        elif len(numbers)==3:
            [part, module, channel] = numbers
        else:
            return 

        for event in region.GetEvents():
            if event.run.runType=='Las':
                if event.data['status']!=0:
                    continue

            if 'deviation' in event.data:
                self.data_direct[event.run.runNumber].fill(event.data['deviation'])            
            if 'Pisa_deviation' in event.data:
                print(event.data['Pisa_deviation'])
                if abs(event.data['Pisa_deviation'])<50.:
                    self.data_stat[event.run.runNumber].fill(event.data['Pisa_deviation'])            

            elif event.run.runType=='cesium' and 'calibration' in event.data:
                if isinstance(event.data['calibration'], float):
                    self.data_cesium[event.run.runNumber].fill(100.*(event.data['calibration']/event.data['f_integrator_db']-1.))


    def ProcessStop(self):
       for run in run_list.getRunsOfType('Las'):
           time = run.time_in_seconds-self.time_min
           print(run.runNumber)
           print('clermont ', self.data_direct[run.runNumber].entries, self.data_direct[run.runNumber].mean(), self.data_direct[run.runNumber].error())
           if self.data_direct[run.runNumber].entries!=0:
               npoints = self.tgraph_direct.GetN()
               self.tgraph_direct.SetPoint( npoints,
                                            time, 
                                            self.data_direct[run.runNumber].mean())
               self.tgraph_direct.SetPointError(npoints, 
                                                0., 
                                                self.data_direct[run.runNumber].error())

           print('pisa ', self.data_stat[run.runNumber].entries, self.data_stat[run.runNumber].mean(), self.data_stat[run.runNumber].error())
           if self.data_stat[run.runNumber].entries!=0:
               npoints = self.tgraph_stat.GetN()
               self.tgraph_stat.SetPoint( npoints,
                                          time, 
                                          self.data_stat[run.runNumber].mean())
               self.tgraph_stat.SetPointError(npoints, 
                                              0., 
                                              self.data_stat[run.runNumber].error())

       for run in run_list.getRunsOfType('cesium'):
           time = run.time_in_seconds-self.time_min
           print(run.runNumber)

           print('cesium ', self.data_cesium[run.runNumber].entries, self.data_cesium[run.runNumber].mean(), self.data_cesium[run.runNumber].error())
           if self.data_cesium[run.runNumber].entries!=0:
               npoints = self.tgraph_cesium.GetN()
               self.tgraph_cesium.SetPoint( npoints,
                                            time, 
                                            self.data_cesium[run.runNumber].mean())
               self.tgraph_cesium.SetPointError(npoints, 
                                                0., 
                                                self.data_cesium[run.runNumber].error())

       
        
       self.HistFile.cd()       
       self.tgraph_direct.SetName("direct")
       self.tgraph_direct.Write()
       self.tgraph_stat.SetName("stat")
       self.tgraph_stat.Write()
       self.tgraph_cesium.SetName("cesium")
       self.tgraph_cesium.Write()




class stats:
    def __init__(self):
        self.entries = 0
        self.sum     = float(0.)
        self.sum2    = float(0.)

    def fill(self, value):
        self.entries += 1 
        self.sum     += value
        self.sum2    += value*value

    def mean(self):
        if self.entries>0:
            return self.sum/self.entries
    
    def rms(self):
        if self.entries>0:
            return sqrt(self.sum2/self.entries)

    def stddev(self):
        if self.entries>0:
            return sqrt(self.sum2/self.entries-self.mean()*self.mean())

    def error(self):
        if self.entries>0:
            return sqrt((self.sum2/self.entries-self.mean()*self.mean())/self.entries)

    
#    def entries(self):
#        return int(self.entries)
    
        


        
    
