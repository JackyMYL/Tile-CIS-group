#Coded by Gabriele Bertoli <gabriele.bertoli@physik.su.se> 21/08/2013

from workers.noise.NoiseWorker import NoiseWorker
from collections import defaultdict
import os, sys, math

# LIB_PATH = os.path.abspath(os.path.join("scripts/"))
# sys.path.insert(0, LIB_PATH)

#from cell_index import get_cellName

def prev_next(iterable):
    '''Function to get previous, current and next run.

    This generator will give the previous, the current and the next run to allow operations on them.'''

    iterator = iter(iterable)

    prev = iterable[0]

    next(iterator)
    
    current = next(iterator)

    for next_el in iterator:

        yield (prev, current, next_el)

        prev, current = current, next_el

    yield (prev, current, None)


def rms_effective(sigma_1, sigma_2, R):
    '''Function to calculate the RMS_eff.

    This Function calculates the RMS_eff and return it.'''

    return math.sqrt((1 - R) * sigma_1**2 + R * sigma_2**2)


class TimeDependencePlots(NoiseWorker):
    '''Class to draw time dependence plots.
    
    This class will draw time dependence plots for arbitrary number of run numbers of the noise.'''

    def __init__(self, run):

        self.initLog()
        self.initNoiseHistFile()

        NoiseWorker.__init__(self)
        
        self.runs = sorted(run, key = int)

        self.partition   = ('LBA', 'LBC', 'EBA', 'EBC')
        self.gain        = ('HGHG', ) #('LGLG', 'LGHG', 'HGLG', 'HGHG')

        self.type = 'physical'

        self.graph_names = []
        self.graph_key   = []
        
        self.graphs = {}

        self.canvas = {}


    def ProcessStart(self):
        '''Function to initialize all the variables.

        This function gets called immediatly before this worker gets sent data,
        so this function can be used to zero counters if you want to rerun the
        same worker many times.  After this function, regions start being passed
        to ProcessRegion()'''

        titles = []

        for part in self.partition:
            for module in range(65):
                for channel in range(48):
                    for gain in self.gain:

                        name  = 'RMS_%s_%02d_%s_%s' % (part, module, channel, gain)
                        title = ('RMS Over RMS First Run For %s Mod %s Ch %s in %s' 
                                 % (part, module, channel, gain))
                        key   = 'RMS_%s_%02d_%s_%s' % (part, module, channel, gain)

                        self.graph_names.append(name)
                        titles.append(title)
                        self.graph_key.append(key)

                        name  = 'Calib_%s_%02d_%s_%s' % (part, module, channel, gain)
                        title = ('Calib Const Over Calib Const First Run For %s Mod %s Ch %s in %s' 
                                 % (part, module, channel, gain))
                        key   = 'Calib_%s_%02d_%s_%s' % (part, module, channel, gain)

                        self.graph_names.append(name)
                        self.graph_key.append(key)
                        titles.append(title)

                        name  = 'RMS_EFF_%s_%02d_%s_%s' % (part, module, channel, gain)
                        title = ('RMS Effective Over RMS For %s Mod %s Ch %s in %s' 
                                 % (part, module, channel, gain))
                        key   = 'RMS_EFF_%s_%02d_%s_%s' % (part, module, channel, gain)

                        self.graph_names.append(name)
                        self.graph_key.append(key)
                        titles.append(title)

                        name  = 'BAD_%s_%02d_%s_%s' % (part, module, channel, gain)
                        title = ('BAD Status For %s Mod %s Ch %s in %s' 
                                 % (part, module, channel, gain))
                        key   = 'BAD_%s_%02d_%s_%s' % (part, module, channel, gain)

                        self.graph_names.append(name)
                        self.graph_key.append(key)
                        titles.append(title)

                        name  = 'HFN_%s_%02d_%s_%s' % (part, module, channel, gain)
                        title = ('HFN For %s Mod %s Ch %s in %s' 
                                 % (part, module, channel, gain))
                        key   = 'HFN_%s_%02d_%s_%s' % (part, module, channel, gain)

                        self.graph_names.append(name)
                        self.graph_key.append(key)
                        titles.append(title)

                        name  = 'LFN_%s_%02d_%s_%s' % (part, module, channel, gain)
                        title = ('LFN For %s Mod %s Ch %s in %s' 
                                 % (part, module, channel, gain))
                        key   = 'LFN_%s_%02d_%s_%s' % (part, module, channel, gain)

                        self.graph_names.append(name)
                        self.graph_key.append(key)
                        titles.append(title)

        
        for i in range(len(self.graph_names)):

            name  = self.graph_names[i]
            self.graph_names[i] = ROOT.TGraph()
            self.graph_names[i].SetName(name)
            self.graph_names[i].SetTitle(titles[i])

            
        self.graphs = dict((key, value) for key, value in zip(self.graph_key, self.graph_names))



    def ProcessStop(self):
        '''Function to finalize things.

         This function gets called after all of the regions in the detector have
         been sent to ProcessRegion().  It is the last function called in this
         class.'''

        # for i in range(len(self.graph_names)):
           
        #     if self.graph_names[i].GetN():
                
        #         self.graph_names[i].GetXaxis().SetLimits(self.runs[0], self.runs[-1])
        #         self.graph_names[i].GetXaxis().SetTitle("RUN Number")
        #         self.graph_names[i].GetYaxis().SetTitle("RMS Over RMS First Run")
        #         self.graph_names[i].Write()


        for i in self.canvas:

            rms_graph          = self.canvas[i][0]
            calib_graph_ch1    = self.canvas[i][1]
            rms_eff_graph      = self.canvas[i][2]
            bad_ch1_graph      = self.canvas[i][3]
            hfn_hghg_graph_ch1 = self.canvas[i][4]
            lfn_hghg_graph_ch1 = self.canvas[i][5]
            channel_1          = self.canvas[i][6]
            
            title = 'RMS/RMS_0, CAL/CAL_0 For ' + i
            
            c = ROOT.TCanvas(i, title, 900, 600)

            rms_graph.SetMaximum(4)
            rms_graph.SetMinimum(-1)
            rms_graph.GetXaxis().SetTitle("Run Number")
            rms_graph.GetYaxis().SetTitle("Relative Change")
            rms_graph.GetXaxis().SetNdivisions(3)
            rms_graph.SetMarkerStyle(24)
            rms_graph.SetMarkerColor(3)
            rms_graph.SetLineColor(3)

            part = rms_graph.GetTitle().split()[6]
            mod  = rms_graph.GetTitle().split()[8]
            chan = rms_graph.GetTitle().split()[10]

            cell = self.get_cellName(part, mod, chan)

            rms_graph.SetTitle("Cell Noise Difference For %s%s %s" 
                               % (part, mod, cell))

            rms_graph.Draw("ALP")
                
            calib_graph_ch1.SetMarkerStyle(25)
            calib_graph_ch1.SetMarkerColor(2)
            calib_graph_ch1.SetLineColor(2)
            calib_graph_ch1.Draw("LP")

            bad_ch1_graph.SetMarkerStyle(25)
            bad_ch1_graph.SetMarkerColor(1)
            bad_ch1_graph.Draw("P")

            rms_eff_graph.SetMarkerStyle(30)
            rms_eff_graph.SetMarkerColor(6)
            rms_eff_graph.SetLineColor(6)
            rms_eff_graph.Draw("LP")

            hfn_hghg_graph_ch1.SetMarkerStyle(27)
            hfn_hghg_graph_ch1.SetMarkerColor(46)
            hfn_hghg_graph_ch1.SetLineColor(46)
            hfn_hghg_graph_ch1.Draw("LP")

            lfn_hghg_graph_ch1.SetMarkerStyle(32)
            lfn_hghg_graph_ch1.SetMarkerColor(7)
            lfn_hghg_graph_ch1.SetLineColor(7)
            lfn_hghg_graph_ch1.Draw("LP")
                
            line = ROOT.TLine()
                
            line.SetLineStyle(2)
            line.DrawLine(182412, 4, 182412, -1)
            line.DrawLine(183561, 4, 183561, -1)
            line.DrawLine(184000, 4, 184000, -1)
            line.DrawLine(185190, 4, 185190, -1)
            line.DrawLine(186887, 4, 186887, -1)
            line.DrawLine(187128, 4, 187128, -1)
            line.DrawLine(188643, 4, 188643, -1)
            line.DrawLine(190052, 4, 190052, -1)
            line.DrawLine(190458, 4, 190458, -1)
            line.DrawLine(191164, 4, 191164, -1)
            line.DrawLine(192239, 4, 192239, -1)
            line.DrawLine(193255, 4, 193255, -1)
            line.DrawLine(193776, 4, 193776, -1)
                
            leg = ROOT.TLegend(0.18, 0.7, 0.37, 0.93)
                
            leg.SetFillColor(0)
            leg.SetBorderSize(4)
            leg.AddEntry(rms_graph, "Cell Noise", "pl")
            leg.AddEntry(calib_graph_ch1, "Calib (Ch %s)" % channel_1, "pl")
            leg.AddEntry(rms_eff_graph, "Cell Noise / RMS Effective", "pl")
            leg.AddEntry(hfn_hghg_graph_ch1, "HFN (Ch %s)" % channel_1, "pl")
            leg.AddEntry(lfn_hghg_graph_ch1, "LFN (Ch %s)" % channel_1, "pl")
            leg.AddEntry(bad_ch1_graph, "Bad Channel (Ch %s)" % channel_1, "p")
                        
            if len(self.canvas[i]) == 12:
                
                channel_2          = self.canvas[i][7]
                bad_ch2_graph      = self.canvas[i][8]
                calib_graph_ch2    = self.canvas[i][9]
                hfn_hghg_graph_ch2 = self.canvas[i][10]
                lfn_hghg_graph_ch2 = self.canvas[i][11]

                hfn_hghg_graph_ch2.SetMarkerStyle(30)
                hfn_hghg_graph_ch2.SetMarkerColor(8)
                hfn_hghg_graph_ch2.SetLineColor(8)
                hfn_hghg_graph_ch2.Draw("LP")

                lfn_hghg_graph_ch2.SetMarkerStyle(31)
                lfn_hghg_graph_ch2.SetMarkerColor(9)
                lfn_hghg_graph_ch2.SetLineColor(9)
                lfn_hghg_graph_ch2.Draw("LP")

                calib_graph_ch2.SetMarkerStyle(26)
                calib_graph_ch2.SetMarkerColor(4)
                calib_graph_ch2.SetLineColor(4)
                calib_graph_ch2.Draw("LP")

                bad_ch2_graph.SetMarkerStyle(26)
                bad_ch2_graph.SetMarkerColor(1)
                bad_ch2_graph.Draw("P")

                leg.AddEntry(calib_graph_ch2, "Calib (Ch %s)" % channel_2, "pl")
                leg.AddEntry(hfn_hghg_graph_ch2, "HFN (Ch %s)" % channel_2, "pl")
                leg.AddEntry(lfn_hghg_graph_ch2, "LFN (Ch %s)" % channel_2, "pl")
                leg.AddEntry(bad_ch2_graph, "Bad Channel (Ch %s)" % channel_2, "p")               
            
            leg.Draw()    

            c.Write()
                
    def ProcessRegion(self, region):
        '''Function to do the actual calculations.

        This function compute the quantities to be plotted, in the macro that
        calls this worker you can specify a list of run numbers [first_run,
        second_run]. This function is called once for each event in the list,
        for instance once for [first_run:first_event, second_run:second_event]
        ... [first_run:last_event, second_run:last_event]'''

        runs_data = {}
        rms_first_run = defaultdict(list)
        
        calib_constant_hg = {}

        hfn_hghg = {}
        lfn_hghg = {}

        
        # If there are no events in the region, do nothing

        if (not region.GetEvents()): 

            return

        
        for event in sorted(region.GetEvents(), key = lambda event: event.run.runNumber):

            # and only look at noise runs

            if event.run.runType != 'Ped':

                continue

            #Skip bad channels (if the channel was bad in one run it
            #will be skipped from the whole analysis)

            # if 'bad_chan' in event.data:

            #     continue

            # _t stands for tower and has to be present in the
            # hash to get the right data.

            if '_t' not in region.GetHash():

                continue


            run = str(event.run).split(",")[0]

            partition = region.get_partition()
            module    = region.get_module()

            # Get channel number from tower.

            channel_1 = region.GetChannels(useSpecialEBmods = True)[0]

            # Set dummy value for channel_2 if the cell
            # has only one channel

            channel_2 = None

            # If channel_2 exists assign its right number.

            if(len(region.GetChannels(True)) == 2):

                channel_2 = region.GetChannels(True)[1]

            # For D0 cell channel -1 is the zero channel
            # of LBC 

            if(channel_1 == -1 and channel_2 == 0):

                channel_1 = 0
                channel_2 = None


            calib_constant_hg[run] = event.data['cal_constantHG']

            hfn_hghg[run] = event.data['hfnHGHG_db']
            lfn_hghg[run] = event.data['lfnHGHG_db']

            if(int(run) == self.runs[0]):

                calib_first_run = calib_constant_hg[run]

                hfn_first_run = hfn_hghg[run]
                lfn_first_run = lfn_hghg[run]

            for gain in self.gain:

                if(channel_2 is None and (gain == 'HGLG' or gain == 'LGHG')):

                    continue

                cell_rms = event.data["cellnoise" + gain + "_db"]

                sigma1   = event.data["cellsigma1" + gain + "_db"]

                sigma2   = event.data["cellsigma2" + gain + "_db"]

                cell_r   = event.data["cellnorm" + gain + "_db"]


                rms_eff = rms_effective(sigma1, sigma2, cell_r)

                if 'bad_chan' in event.data:

                    runs_data[str(run) + gain] = (cell_rms, cell_rms / rms_eff,
                                                  True)
                    
                else:

                    runs_data[str(run) + gain] = (cell_rms, cell_rms / rms_eff,
                                                  False)

                if(int(run) == self.runs[0]):

                    rms_first_run[gain].append((region.GetHash(), cell_rms))

                # print "1111111111"
                # print region.GetHash()
                # print "runs_data: ", runs_data
                # print "----------"

            all_keys = [str(r) + g for r in self.runs for g in self.gain]


            if all([k in runs_data for k in all_keys]):

                for prev_run, this_run, next_run in prev_next(self.runs):

                    for gain in self.gain:

                        this_run_key = str(this_run) + gain
                        prev_run_key = str(prev_run) + gain

                        this_run_rms = runs_data[this_run_key][0]
                        prev_run_rms = runs_data[prev_run_key][0]

                        #print "this run: ", this_run_key, this_run_rms
                        #print "prev run: ", prev_run_key, prev_run_rms

                        rms_difference = this_run_rms - prev_run_rms

                        #print "rms_difference: ", rms_difference

                        if(partition == 'LBA' and (int(module) == 22 or int(module) == 24)):

                            continue

                        if(abs(rms_difference) / 100. > .1):

                            continue

                        if( .05 < abs(rms_difference) / 100. < .1):

                            for i in rms_first_run[gain]:

                                if i[0] == region.GetHash():

                                    first_run_rms = i[1]

                            graph_id = "%s_%s_%s_%s" % (partition, module, channel_1, gain)

                            rms_graph          = self.graphs['RMS_' + graph_id]
                            bad_ch1_graph      = self.graphs['BAD_' + graph_id]
                            rms_eff_graph      = self.graphs['RMS_EFF_' + graph_id]
                            calib_graph_ch1    = self.graphs['Calib_' + graph_id]
                            hfn_hghg_graph_ch1 = self.graphs['HFN_' + graph_id]
                            lfn_hghg_graph_ch1 = self.graphs['LFN_' + graph_id]

                            data = [(run, runs_data[str(run) + gain][0] / first_run_rms) 
                                    for run in self.runs]

                            for point, (run, data) in enumerate(data):

                                rms_graph.SetPoint(point, run, data)


                            rms_eff_data = [(run, runs_data[str(run) + gain][1])
                                            for run in self.runs]

                            for point, (run, data) in enumerate(rms_eff_data):

                                rms_eff_graph.SetPoint(point, run, data)

                            hfn_first_run_ch1, hfn_first_run_ch2 = hfn_first_run

                            hfn_hghg_data = [(run, hfn_hghg[str(run)][0] / hfn_first_run_ch1)
                                             for run in self.runs]

                            for point, (run, data) in enumerate(hfn_hghg_data):

                                hfn_hghg_graph_ch1.SetPoint(point, run, data)

                            lfn_first_run_ch1, lfn_first_run_ch2 = lfn_first_run

                            lfn_hghg_data = [(run, lfn_hghg[str(run)][0] / lfn_first_run_ch1)
                                             for run in self.runs]

                            for point, (run, data) in enumerate(lfn_hghg_data):

                                lfn_hghg_graph_ch1.SetPoint(point, run, data)

                            #Generate the Graph for first channel calibration constant
                                
                            calib_first_run_ch1, calib_first_run_ch2 = calib_first_run
                            
                            calib_data = [(run, calib_constant_hg[str(run)][0] / calib_first_run_ch1) 
                                          for run in self.runs]


                            bad_ch_data = [(run, calib_constant_hg[str(run)][0] / calib_first_run_ch1) 
                                           for run in self.runs if runs_data[str(run) + gain][2]]

                            for point, (run, data) in enumerate(bad_ch_data):
                                
                                bad_ch1_graph.SetPoint(point, run, data)
                                    
                            # print "data: ", runs_data, data, gain
                            # print "CC: ", cell, calib_first_run_ch1, calib_first_run_ch2, calib_first_run 
                            # print graph_id
                            # print "22222222222"


                            for point, (run, calib_data) in enumerate(calib_data):

                                calib_graph_ch1.SetPoint(point, run, calib_data)


                            #Generate the Graph for second channel calibration constant

                            if channel_2 is not None:

                                calib_data = [(run, calib_constant_hg[str(run)][1] / calib_first_run_ch2) 
                                              for run in self.runs]

                                hfn_hghg_data = [(run, hfn_hghg[str(run)][1] / hfn_first_run_ch2)
                                                 for run in self.runs]

                                lfn_hghg_data = [(run, lfn_hghg[str(run)][1] / lfn_first_run_ch2)
                                                 for run in self.runs]

                                bad_ch_data = [(run, calib_constant_hg[str(run)][1] / calib_first_run_ch2) 
                                               for run in self.runs if runs_data[str(run) + gain][2]]


                                graph2_id = "%s_%s_%s_%s" % (partition, module, channel_2, gain)

                                calib_graph_ch2    = self.graphs['Calib_' + graph2_id]
                                hfn_hghg_graph_ch2 = self.graphs['HFN_' + graph2_id]
                                lfn_hghg_graph_ch2 = self.graphs['LFN_' + graph2_id]
                                bad_ch2_graph       = self.graphs['BAD_' + graph2_id]


                                for point, (run, data) in enumerate(bad_ch_data):
                                
                                    bad_ch2_graph.SetPoint(point, run, data)

                                for point, (run, calib_data) in enumerate(calib_data):

                                    calib_graph_ch2.SetPoint(point, run, calib_data)

                                for point, (run, data) in enumerate(hfn_hghg_data):

                                    hfn_hghg_graph_ch2.SetPoint(point, run, data)

                                for point, (run, data) in enumerate(lfn_hghg_data):

                                    lfn_hghg_graph_ch2.SetPoint(point, run, data)


                            if channel_2 is None:

                                self.canvas[graph_id] = (rms_graph, 
                                                         calib_graph_ch1, 
                                                         rms_eff_graph, 
                                                         bad_ch1_graph,                                                      
                                                         hfn_hghg_graph_ch1, 
                                                         lfn_hghg_graph_ch1,
                                                         channel_1)

                            else:

                                self.canvas[graph_id] = (rms_graph, 
                                                         calib_graph_ch1,
                                                         rms_eff_graph, 
                                                         bad_ch1_graph,
                                                         hfn_hghg_graph_ch1,
                                                         lfn_hghg_graph_ch1,
                                                         channel_1,
                                                         channel_2,
                                                         bad_ch2_graph,
                                                         calib_graph_ch2, 
                                                         hfn_hghg_graph_ch2, 
                                                         lfn_hghg_graph_ch2)
