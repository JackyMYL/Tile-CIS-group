################################################################################
#
# channelEvolution_combined.py
#
################################################################################
#
# Author: Rute following Ammara's workers/laser/cellEvolutionCombined.py
#
# Sep 9th 2019
#
# Goal:
#     Save TGraphs of channel using combined method 
#########1#########2#########3#########4#########5#########6#########7#########8

from src.GenericWorker import *
from src.oscalls import *
import ROOT
import math
import time

class channelEvolution_combined(GenericWorker):
     "Makes TGraphs of specific cells evolution over time"

     c2 = None

     def __init__(self, cells='all', verbose=False):

          self.cells = cells
          self.verbose  = verbose
          self.t_max  = 0
          self.t_min  = 10000000000000000
          self.outputTag = outputTag # global variable to tag output histogram file name
          self.dir = getPlotDirectory(subdir=self.outputTag)

          self.tgraphs = {}

          try:
               self.HistFile.cd()
          except:
               self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag))
          self.HistFile.cd()
              
          self.dirname = "CellsEvolution"
          if not ROOT.gDirectory.cd(self.dirname):
               ROOT.gDirectory.mkdir(self.dirname)
          ROOT.gDirectory.cd(self.dirname)


     def ProcessStart(self):

          global run_list
          self.ordered_run_list = sorted(run_list.getRunsOfType('Las'), key=lambda run: run.runNumber)
          n = len(self.ordered_run_list)
          if n!=0:
               self.t_min = int(self.ordered_run_list[0].time_in_seconds)
               self.t_max = int(self.ordered_run_list[n-1].time_in_seconds)
                    

     def ProcessRegion(self, region):

          numbers = region.GetNumber(1)
          if len(numbers)!=4:
               return region
          # only for ADCs 
          [part, module, pmt, gain] = numbers
          partition = region.get_partition()
          cell  = region.GetCellName()
          channel = region.get_channel()
        
          for event in region.GetEvents():
               if event.run.runType=='Las':
                    if 'status' not in event.data:
                         continue
                
                    if event.data['status']&0x4 or event.data['status']&0x10:
                         continue
                                
                    if (abs(event.data['HV']-event.data['hv_db'])>10.):  # Bad HV, will bias results.
                         continue
                
                    saturation_limits = [800., 12.] # in pC Saturation limits
                    if (event.data['signal']>saturation_limits[gain]): 
                         print("Channel {} signal {} pC  over saturation limits ({} pC)".format(event.region.GetHash(), event.data['signal'],saturation_limits[gain])) 
                         continue
                
                    underflow_limits = [4., 0.06]   # in pC Underflow limits
                    if (event.data['signal']<underflow_limits[gain]):  
                         continue

                    if 'deviation' in event.data and (cell in self.cells or self.cells=='all'):
                         deverr=0
                         if 'deverr' in event.data:
                              deverr=event.data['deverr']

                         tgraphname = "Combined_{}_ch{}_{}{}".format(cell,channel,partition,module)

                         # if the channel tgraph was not yet initialized
                         if tgraphname not in self.tgraphs:
                              self.tgraphs[tgraphname] = ROOT.TGraphErrors()
                              self.tgraphs[tgraphname].SetName(tgraphname)
                              
                         # Fill data point
                         npoints=self.tgraphs[tgraphname].GetN()
                         self.tgraphs[tgraphname].SetPoint(npoints, event.run.time_in_seconds, event.data['deviation'])
                         self.tgraphs[tgraphname].SetPointError(npoints, 600, deverr)
                         if self.verbose:
                              print("cell {} channel {} {}{} run {} deviation {} +/- {}".format(cell,channel,partition,module,event.run.runNumber,event.data['deviation'],deverr))
         
                
     def ProcessStop(self):
                 
          # Write tgraph list
          self.HistFile.cd(self.dirname)
          for channel in list(self.tgraphs.keys()):
               self.tgraphs[channel].Sort()
               self.tgraphs[channel].Write()
