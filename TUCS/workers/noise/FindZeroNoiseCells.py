from workers.noise.NoiseWorker import NoiseWorker
import os, ROOT

class FindZeroNoiseCells(NoiseWorker):
    '''Class to create Module Channel map of zero noise cells.

    This class will create a map of zero noise cells.'''

    def __init__(self, run):

        self.initLog()
        self.initNoiseHistFile()

        self.runs = run

        self.gain        = ('LGLG', 'LGHG', 'HGLG', 'HGHG')

        self.type = 'physical'

        self.histo_names  = []
        self.histo_titles = []
        self.histo_keys   = []

        self.histograms   = {}


    def ProcessStart(self):
        '''Function to initialize all the variables.

        This function gets called immediatly before this worker gets sent data,
        so this function can be used to zero counters if you want to rerun the
        same worker many times.  After this function, regions start being passed
        to ProcessRegion()'''


        labels = ('RMS', 'pileup', 'sigma1', 'sigma2', 'R')
        partition   = ('LBA', 'LBC', 'EBA', 'EBC')
        sample      = ('A', 'BC', 'D', 'E')



        #/--------------** Zero Noise Cells Histograms **--------------\

        # Dynamically generate name title and key for the histograms.

        for part in partition:
            for gain in self.gain:
                for samp in sample:
                    for run in self.runs:
                        for label in labels:

                            if (label == 'RMS'):

                                name  = ("h_%s_Zero_RMS_NoiseIn_%s_%s_%s" 
                                         % (part, gain, samp, run))

                                title = ("Zero RMS Noise Cells In %s %s cell in %s" 
                                         % (part, samp, gain))

                                key   = ("%s_%s_%s_%s_%s" 
                                         % (part, samp, gain, run, label))

                            if (label == 'pileup'):

                                name  = ("h_%s_Zero_Pileup_NoiseIn_%s_%s_%s" 
                                         % (part, gain, samp, run))

                                title = ("Zero Pileup Noise Cells In %s %s cell in %s" 
                                         % (part, samp, gain))

                                key   = ("%s_%s_%s_%s_%s" 
                                         % (part, samp, gain, run, label))

                            if (label == 'sigma1'):

                                name  = ("h_%s_Zero_Sigma1_NoiseIn_%s_%s_%s" 
                                         % (part, gain, samp, run))

                                title = ("Zero Sigma1 Noise Cells In %s %s cell in %s" 
                                         % (part, samp, gain))

                                key   = ("%s_%s_%s_%s_%s" 
                                         % (part, samp, gain, run, label))

                            if (label == 'sigma2'):

                                name  = ("h_%s_Zero_Sigma2_NoiseIn_%s_%s_%s" 
                                         % (part, gain, samp, run))

                                title = ("Zero Sigma2 Noise Cells In %s %s cell in %s" 
                                         % (part, samp, gain))

                                key   = ("%s_%s_%s_%s_%s" 
                                         % (part, samp, gain, run, label))

                            if (label == 'R'):

                                name  = ("h_%s_Zero_R_NoiseIn_%s_%s_%s" 
                                         % (part, gain, samp, run))

                                title = ("Zero R Noise Cells In %s %s cell in %s" 
                                         % (part, samp, gain))

                                key   = ("%s_%s_%s_%s_%s" 
                                         % (part, samp, gain, run, label))

                    
                            self.histo_names.append(name)
                            self.histo_titles.append(title)
                            self.histo_keys.append(key)


        # Initialize the histograms.
                    
        for i in range(len(self.histo_names)):

            self.histo_names[i] = ROOT.TH2D(self.histo_names[i], 
                                            self.histo_titles[i], 
                                            64, .5, 64.5, 48, -.5, 47.5)

        # Generate a dictionary for the histograms with the key
        # generated above.

        self.histograms = dict((x, y) for x, y in 
                               zip(self.histo_keys, self.histo_names))

        #----------------------------------------------------------------------



    def ProcessStop(self):
        '''Function to finalize things.

         This function gets called after all of the regions in the detector have
         been sent to ProcessRegion().  It is the last function called in this
         class.'''

        # Write the histograms.

        for i in range(len(self.histo_names)):
            
            self.histo_names[i].GetXaxis().SetTitle('Module Number')
            self.histo_names[i].GetYaxis().SetTitle('Channel Number')

            if not (self.histo_names[i].GetEntries() == 0):

                self.histo_names[i].Write()



    def ProcessRegion(self, region):
        '''Function to do the actual calculations.

        This function compute the quantities to be plotted, in the macro that
        calls this worker you can specify a list of run numbers [first_run,
        second_run]. This function is called once for each event in the list,
        for instance once for [first_run:first_event, second_run:second_event]
        ... [first_run:last_event, second_run:last_event]'''
        
        # If there are no events in the region, do nothing

        if (not region.GetEvents()): 
            
            return

        for event in region.GetEvents():

            # and only look at noise runs

            if event.run.runType != 'Ped':

                continue

            # _t stands for tower and has to be present in the
            # hash to get the right data.
                    
            if '_t' not in region.GetHash():

                continue

            # Skip bad channels.

            if 'bad_chan' in event.data:

                continue

            run = int(str(event.run).split(",")[0])

            # Get cell informations.

            cell_hash = region.GetHash().split("_")

            partition = region.get_partition()
            module    = region.get_module()
            sample    = cell_hash[3][1:]

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

            # Fill the histograms and printout some
            # values.

            def fill_histo(histo_id, data):
                '''Function to fill the histograms.

                This function will fill the histograms.'''

                self.histograms[histo_id].SetBinContent(int(module), int(channel_1) + 1, data)

                if channel_2 is not None:

                    self.histograms[histo_id].SetBinContent(int(module), int(channel_2) + 1, data) 


            for gain in self.gain:

                # If cell has only one channel keep only HGHG
                # LGLG tags

                if(channel_2 == None and (gain == 'HGLG' or gain == 'LGHG')):

                    continue

                cell_rms    = event.data["cellnoise" + gain + "_db"]

                cell_pileup = event.data["pilenoise" + gain + "_db"]

                cell_sigma1 = event.data["cellsigma1" + gain + "_db"]

                cell_sigma2 = event.data["cellsigma2" + gain + "_db"]

                cell_r      = event.data["cellnorm" + gain + "_db"]

                cell_id = partition + str(module) + '_' + str(channel_1)
                

                if cell_id == 'LBA22_47':

                    print(run, partition, module, channel_1, channel_2, cell_sigma1, cell_sigma2, cell_sigma1 / cell_sigma2)

                cell_id = partition + str(module) + '_' + str(channel_2)

                if cell_id == 'LBA22_47':

                    print(run, partition, module, channel_1, channel_2, cell_sigma1, cell_sigma2, cell_sigma1 / cell_sigma2)


                if (cell_rms == 0):

                    # Construct the correct histo id for
                    # the dictionary.

                    histo_id = "%s_%s_%s_%s_RMS" % (partition, sample, gain, str(run))

                    # Print useful values.

                    print("Zero RMS", partition, module, region.GetChannels(True), sample, gain, run)

                    # Assign a dummy value to show zero
                    # noise cells

                    cell_rms    = 10

                    # Fill the histos.

                    fill_histo(histo_id, cell_rms)


                if (cell_pileup == 0):

                    histo_id = "%s_%s_%s_%s_pileup" % (partition, sample, gain, str(run))

                    print("Zero Pileup", partition, module, region.GetChannels(True), sample, gain, run)

                    cell_pileup = 10

                    fill_histo(histo_id, cell_pileup)


                if (cell_sigma1 == 0):

                    histo_id = "%s_%s_%s_%s_sigma1" % (partition, sample, gain, str(run))

                    print("Zero Sigma1", partition, module, region.GetChannels(True), sample, gain, run)

                    cell_sigma1 = 10

                    fill_histo(histo_id, cell_sigma1)


                if (cell_sigma2 == 0):

                    histo_id = "%s_%s_%s_%s_sigma2" % (partition, sample, gain, str(run))

                    print("Zero Sigma2", partition, module, region.GetChannels(True), sample, gain, run)

                    cell_sigma2 = 10

                    fill_histo(histo_id, cell_sigma2)


                if (cell_r == 0):

                    histo_id = "%s_%s_%s_%s_R" % (partition, sample, gain, str(run))

                    print("Zero R", partition, module, region.GetChannels(True), sample, gain, run)

                    cell_r = 10

                    fill_histo(histo_id, cell_r)

        return region

