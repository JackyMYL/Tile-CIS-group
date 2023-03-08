################################################################################
#
# cellEvolution_perModule_combined.py
#
################################################################################
#
# Author: Rute following Ammara's workers/laser/cellEvolutionCombined.py
#
# Sep 9th 2019
#
# Goal:
#     Save TGraphs of cell evolution per module using combined method 
#########1#########2#########3#########4#########5#########6#########7#########8

from src.GenericWorker import *
from src.oscalls import *
import ROOT
import math
import time

class cellEvolution_perModule_combined(GenericWorker):
     "Makes TGraphs of specific cells evolution over time"

     c2 = None

     def __init__(self, cells=[], verbose=False):

          self.cells = cells
          self.verbose  = verbose
          self.t_max  = 0
          self.t_min  = 10000000000000000
          self.outputTag = outputTag # global variable to tag output histogram file name
          self.dir = getPlotDirectory(subdir=self.outputTag)

          self.deviations = {}
          for cell in self.cells:
               self.deviations[cell] = dict()
               for i in range(64):
                    self.deviations[cell]['{}'.format(i+1)] = dict()
                    
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

                    if 'deviation' in event.data and cell in self.cells:
                         deverr=0
                         if 'deverr' in event.data:
                              deverr=event.data['deverr']

                         # if the partition was not yet initialized
                         if partition not in self.deviations[cell][str(module)]:
                              self.deviations[cell][str(module)][partition] = {}

                         # if the run was already initialized: fill data of second PMT
                         if str(event.run.runNumber) in self.deviations[cell][str(module)][partition]:
                              self.deviations[cell][str(module)][partition][str(event.run.runNumber)]['2ndPMTdev'] = event.data['deviation']
                              self.deviations[cell][str(module)][partition][str(event.run.runNumber)]['2ndPMTdeverr'] = deverr

                         # initialize run and fill data of first PMT
                         else:
                              self.deviations[cell][str(module)][partition][str(event.run.runNumber)]={}
                              self.deviations[cell][str(module)][partition][str(event.run.runNumber)]['1stPMTdev'] = event.data['deviation']
                              self.deviations[cell][str(module)][partition][str(event.run.runNumber)]['1stPMTdeverr'] = deverr
                         
         
                
     def ProcessStop(self):

          self.HistFile.cd(self.dirname)

          # Loop on cell list
          for cell in self.cells:

               # Loop on modules
               for mod in range(64):
                    module = mod +1
                    
                    # Loop on partitions (will be A and C sides: LBA and LBC or EBA and EBC)
                    for part in list(self.deviations[cell][str(module)].keys()):

                         # A TGraph per cell type, per partition and module
                         tgraph = ROOT.TGraphErrors()
                         npoints = 0

                         for run in self.ordered_run_list:
                              if str(run.runNumber) not in self.deviations[cell][str(module)][part]:
                                   continue

                              if self.verbose:
                                   print("cell {} {}{} run {}".format(cell,part,module,run.runNumber))

                              #1st PMT
                              dev=self.deviations[cell][str(module)][part][str(run.runNumber)]['1stPMTdev']
                              deverr=self.deviations[cell][str(module)][part][str(run.runNumber)]['1stPMTdeverr']
                              if self.verbose:
                                   print("  -- deviation 1st PMT {} +/- {}".format(self.deviations[cell][str(module)][part][str(run.runNumber)]['1stPMTdev'],
                                                                                   self.deviations[cell][str(module)][part][str(run.runNumber)]['1stPMTdeverr']))

                              #2nd PMT
                              if '2ndPMTdev' in self.deviations[cell][str(module)][part][str(run.runNumber)]:
                                   dev += self.deviations[cell][str(module)][part][str(run.runNumber)]['2ndPMTdev']
                                   dev = dev/2
                                   deverr += self.deviations[cell][str(module)][part][str(run.runNumber)]['2ndPMTdeverr']
                                   deverr = deverr/2
                                   if self.verbose:
                                        print("  -- deviation 2nd PMT {} +/- {}".format(self.deviations[cell][str(module)][part][str(run.runNumber)]['2ndPMTdev'],
                                                                                         self.deviations[cell][str(module)][part][str(run.runNumber)]['2ndPMTdeverr']))
                              if self.verbose:
                                   print("  -- deviation {} +/- {}".format(dev,deverr))

                              # Fill tgraph
                              tgraph.SetPoint(npoints, run.time_in_seconds, dev)
                              tgraph.SetPointError(npoints, 600, deverr)
                              npoints+=1

                         # End fill tgraph with data from all runs: write TGraph
                         tgraph.Sort()
                         tgraph.SetName("Combined_{}_{}{}".format(cell,part,module))
                         tgraph.Write()


               

     
