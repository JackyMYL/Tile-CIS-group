from workers.noise.NoiseWorker import NoiseWorker
from src.oscalls import *

class GetBadChannel(NoiseWorker):
    '''Class to get bad channels from the database

    This class will get the bad channels for you.'''

    def __init__(self, run, schema, folder, tag):
 
        NoiseWorker.__init__(self)

        self.initLog()
        self.initNoiseHistFile()

        self.runs = run

        self.type = 'physical'

        self.schema = schema

        self.folder = folder
   
        self.tag = tag

        self.bad_chan_list = {}


    def read_bad_chan(self, run):
        '''Function to read bad channels from a list.

        This function explioit the script RreadBchFromCool to 
        create a file containing the list of bad channels.'''

        filename = os.path.join(getResultDirectory(),"bad_chan_list_" + str(run))

        bad_chan_list = []

        bad_chan_db = self.schema

        bad_chan_folder = self.folder
        
        bad_chan_tag = self.tag

        try:
            
            with open(filename): 
                
                pass

        except IOError:

            print("Creating Bad Channel File...")

            os.system("ReadBchFromCool.py --schema=\"" + bad_chan_db + 
                      "\" --folder=\"" + bad_chan_folder + "\" --tag=\"" + 
                      bad_chan_tag + "\" --run=" + str(run) + " > " + filename)

        # Open the file and store the lines in a list.

        with open(filename) as _file:

            content = _file.readlines()

        # Get the information from the list and create a tuple.

        for i in content:
            
            partition = i.split()[0][:3]
            module    = i.split()[0][3:]
            channel   = i.split()[1]
            gain      = i.split()[2]

            bad_chan_list.append((partition, module, channel, gain))

        return bad_chan_list


    def is_bad_chan(self, partition, module, channel, run):
        '''Function to check if a channel is in the bad channel list.

        This Function checks if a channel is in the bad channel list.'''
        
        for gain in range(2):

            return ((partition, module, str(channel), str(gain)) 
                    in self.bad_chan_list[run])

            

    def ProcessStart(self):
        '''Function to initialize all the variables.

        This function gets called immediatly before this worker gets sent data,
        so this function can be used to zero counters if you want to rerun the
        same worker many times.  After this function, regions start being passed
        to ProcessRegion()'''

        for run in self.runs:

            self.bad_chan_list[run] = self.read_bad_chan(run)

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

            run = int(str(event.run).split(",")[0])

            # Get cell informations.

            cell_hash = region.GetHash().split("_")

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

            # Add entry for bad channels.

            if self.is_bad_chan(partition, module, channel_1, run):

                event.data['bad_chan'] = True

            if channel_2 is not None and self.is_bad_chan(partition, module, channel_2, run):

                event.data['bad_chan'] = True


    def ProcessStop(self):
        '''Function to finalize things.

         This function gets called after all of the regions in the detector have
         been sent to ProcessRegion().  It is the last function called in this
         class.'''


        pass
