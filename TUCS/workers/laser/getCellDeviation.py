################################################################
#
# Author: Giulia <giulia.di.gregorio@cern.ch> based on work from  Henric
#
# June, 2017
#
# Gloal:
# Evaluate signal and absolute gain deviation for all the cells
#
#
# For more info on LASER system: http://atlas-tile-laser.web.cern.ch
#
################################################################

from src.GenericWorker import *
from src.oscalls import *
from src.region import *
from src.stats import *
from array import *
import src.MakeCanvas
import math
import ROOT

from src.laser.toolbox import *

class getCellDeviation(GenericWorker):
    "Evaluate signal and absolute gain deviation for all the cells"

    def __init__(self, verbose=True, runNumber = 311792):
        self.verbose = verbose
        self.events = set()
        self.PMTool = LaserTools()
        self.run_dict = {}
        self.run_list = []
        self.final_run = runNumber

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        self.cell_name = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6', 'BC7', 'BC8', 'B9', 'D0', 'D1', 'D2', 'D3', 'A12', 'A13', 'A14', 'A15', 'A16', 'B11', 'B12', 'B13', 'B14', 'B15', 'C10', 'D4', 'D5', 'D6', 'E1', 'E2', 'E3', 'E4']
        
        self.histo_signal = dict()
        self.histo_gain = dict()
        for cell in self.cell_name:
            self.histo_signal[cell] = dict()
            self.histo_gain[cell] = dict()

        try:
            self.HistFile.cd()
        except:
            rootfilename = 'histograms/histogram_cell_evolution.root' 
            self.initHistFile(rootfilename)
        self.HistFile.cd()


    def ProcessStart(self):
        global run_list
        ordered_list = sorted(run_list.getRunsOfType('Las'), key=lambda run: run.runNumber)
        for run in ordered_list:
            self.run_list.append(run)
            self.run_dict[run.runNumber] = []
            
            for cell in self.cell_name:
                histo_signal_name = 'histo_signal_cell_' + cell + '_' + repr(run)
                histo_signal_title = 'Signal_cell_' + cell + '_' + repr(run)
                histo_gain_name = 'histo_gain_cell_' + cell + '_' + repr(run)
                histo_gain_title = 'Gain_cell_' + cell + '_' + repr(run)
                self.histo_signal[cell][run] = ROOT.TH1F(histo_signal_name, histo_signal_title, 100, -20., +4.)
                self.histo_gain[cell][run] = ROOT.TH1F(histo_gain_name, histo_gain_title, 100, -20., +4.)
        

    def ProcessRegion(self, region):
        
        if len(region.GetNumber())==4:
            cell= region.GetCellName()

           
            [ros, module, channel, gain] = region.GetNumber(1)
            saturation_limits = [760., 12.] # in pC 
            underflow_limits = [4., 0.06]   # in pC Underflow limits

                
            for event in region.GetEvents():
                    
                if event.run.runType=='Las':
                    
                    if 'deviation' in event.data and 'Pisa_deviation' in event.data:
                    #if event.data.has_key('deviation'):

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

                    

                        #if (event.data['signal']<underflow_limits[gain]):  
                        #    continue

                        
                        
                        self.run_dict[event.run.runNumber].append(event)

        
    def ProcessStop(self):

        self.HistFile.cd()
        ordered_list = sorted(run_list.getRunsOfType('Las') , key=lambda run: run.runNumber)
        for run in ordered_list:

            stat = [stats() for x in range(41)]
            stat_pisa = [stats() for x in range(41)]
            mean= [0. for x in range(41)]
            rms= [1. for x in range(41)]
            mean_pisa = [0. for x in range(41)]
            rms_pisa = [1. for x in range(41)]
            
            mean_histo= [0. for x in range(41)]
            mean_err_histo = [0. for x in range(41)]
            entries_histo = [0. for x in range(41)]
            mean_pisa_histo = [0. for x in range(41)]
            mean_pisa_err_histo = [0. for x in range(41)]
            entries_pisa_histo = [0. for x in range(41)]

            for event in self.run_dict[run.runNumber]:
     
                [part_num, module, pmt, gain] = event.region.GetNumber(1)
                cell= event.region.GetCellName()

                if cell == 'D45': 
                    cell = 'D5'
                self.histo_signal[cell][event.run].Fill(event.data['deviation'])
                self.histo_gain[cell][event.run].Fill(event.data['Pisa_deviation'])                                            
                for i_cell in range(41):
                    if (self.cell_name[i_cell]==cell):
                        
                        x = event.data['deviation']
                        stat[i_cell].fill(x)


                        if ('Pisa_deviation' in event.data):
                            pisa_x = event.data['Pisa_deviation']
                            if (abs(pisa_x)< 100. ):
                                stat_pisa[i_cell].fill(pisa_x)
                            else:
                                print(pisa_x, part_num, module, pmt, gain, run.runNumber)
                        
            for cell in self.cell_name:
                self.histo_signal[cell][run].Write()
                self.histo_gain[cell][run].Write()
            
            for i_cell in range(41):
                
                if stat[i_cell].entries>1: 
                    mean[i_cell] = stat[i_cell].mean()
                    try:
                        rms[i_cell] = stat[i_cell].error()
                    except: 
                        rms[i_cell]=1.
                
                else:
                    mean[i_cell]=0.
                    rms[i_cell] = 1.

                if stat_pisa[i_cell].entries>1:
                    mean_pisa[i_cell] = stat_pisa[i_cell].mean()
                    try:
                        rms_pisa[i_cell] = stat_pisa[i_cell].error()
                    
                    except:
                        rms_pisa[i_cell]=1.
                else:
                    mean_pisa[i_cell] = 0.
                    rms_pisa[i_cell] = 1.

            for i_cell in range(41):
                cell = self.cell_name[i_cell]
                mean_histo[i_cell] = self.histo_signal[cell][run].GetMean()
                mean_err_histo[i_cell] = self.histo_signal[cell][run].GetMeanError()
                mean_pisa_histo[i_cell] = self.histo_gain[cell][run].GetMean()
                mean_pisa_err_histo[i_cell] = self.histo_gain[cell][run].GetMeanError()
                entries_histo[i_cell] = self.histo_signal[cell][run].GetEntries() 
                entries_pisa_histo[i_cell] = self.histo_gain[cell][run].GetEntries()
                
            run.data['cell_deviation_histo'] = mean_histo
            run.data['cell_deviation_err_histo'] = mean_err_histo
            run.data['gain_deviation_histo'] = mean_pisa_histo
            run.data['gain_deviation_err_histo'] = mean_pisa_err_histo

            run.data['cell_deviation']= mean
            run.data['cell_deviation_err'] = rms

    
            run.data['gain_deviation'] = mean_pisa
            run.data['gain_deviation_err'] = rms_pisa

            for i_cell in range(41):
                name = self.cell_name[i_cell]
                print("Run number: " , run.runNumber, name)
                print("Signal deviation: ", mean[i_cell], " +- " , rms[i_cell], " Entries: " , stat[i_cell].n())
                print("Signal deviation histo: ", mean_histo[i_cell], " +- ", mean_err_histo[i_cell], " Entries: ", entries_histo[i_cell])
                print("Gain deviation: ", mean_pisa[i_cell], " +- ", rms_pisa[i_cell], " Entries: ", stat_pisa[i_cell].n())
                print("Gain deviation histo: ", mean_pisa_histo[i_cell], " +- ", mean_pisa_err_histo[i_cell], " Entries: ", entries_pisa_histo[i_cell])
            
