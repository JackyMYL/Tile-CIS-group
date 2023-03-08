#Coded by Gabriele Bertoli <gabriele.bertoli@physik.su.se> 21/08/2013

from workers.noise.NoiseWorker import NoiseWorker
from collections import defaultdict
from src.oscalls import *

from TileCalibBlobPython import TileCalibTools

class GetDigiNoiseData(NoiseWorker):
    '''Class to retireve the digital noise constats.

    This class will get for you the hfn and lfn data to be plotted in another class.'''

    def __init__(self, run, schema, folder, tag):

        self.initLog()
        self.initNoiseHistFile()

        self.type = 'physical'

        self.runs = sorted(run, key = int)

        self.schema = schema

        self.folder = folder

        self.tag = tag

        if "sqlite" in schema:
            splitname=schema.split("=")
            if not "/" in splitname[1]: 
                splitname[1]=os.path.join(getResultDirectory(), splitname[1])
                self.schema="=".join(splitname)


    def ProcessStart(self):
        '''Function to initialize all the variables.

        This function gets called immediatly before this worker gets sent data,
        so this function can be used to zero counters if you want to rerun the
        same worker many times.  After this function, regions start being passed
        to ProcessRegion()'''

        schema = self.schema

        folder = self.folder

        tag    = self.tag

        database = TileCalibTools.openDbConn(schema, 'READONLY')

        self.blob_reader = TileCalibTools.TileBlobReader(database, folder, tag)

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


            #FindZeroNoiseCells has a custom function to find
            #bad channels, if this is the case, skip the event

            # if 'bad_chan' in event.data:

            #     continue

            if '_t' in region.GetHash():

                partition = region.get_partition()
                mod       = region.get_module()

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

                part = {'LBA':1, 'LBC':2, 'EBA':3, 'EBC':4}

                if any('HGHG' for key in event.data):

                    gain = 1

                    blob = self.blob_reader.getDrawer(part[partition], int(mod) - 1, 
                                                      (event.run.runNumber, 0))

                    if channel_2 is not None:

                        event.data['hfnHGHG_db'] = (blob.getData(channel_1, gain, 1), 
                                                    blob.getData(channel_2, gain, 1))

                        event.data['lfnHGHG_db'] = (blob.getData(channel_1, gain, 2), 
                                                    blob.getData(channel_2, gain, 2))

                    else:
                
                        event.data['hfnHGHG_db'] = (blob.getData(channel_1, gain, 1), 
                                                    None)

                        event.data['lfnHGHG_db'] = (blob.getData(channel_1, gain, 2), 
                                                    None)



                # event.data['hfn_db'] = hfn_db
                # event.data['lfn_db'] = lfn_db


    def ProcessStop(self):
        '''Function to finalize things.

         This function gets called after all of the regions in the detector have
         been sent to ProcessRegion().  It is the last function called in this
         class.'''


        pass






