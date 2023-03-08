#Coded by Gabriele Bertoli <gabriele.bertoli@physik.su.se> 21/08/2013

from workers.noise.NoiseWorker import NoiseWorker

from TileCalibBlobPython import TileCalibTools
#from TileCalibBlobObjs.Classes import *
from src.oscalls import *

class GetCalibConstants(NoiseWorker):
    '''Class to retireve the calibration constants.

    This class will get for you the calibration constants from the databases.'''

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

        self.ces_blob_reader = None
        self.cis_blob_reader = None
        self.las_blob_reader = None


    def ProcessStart(self):
        '''Function to initialize all the variables.

        This function gets called immediatly before this worker gets sent data,
        so this function can be used to zero counters if you want to rerun the
        same worker many times.  After this function, regions start being passed
        to ProcessRegion()'''

        ces_schema = self.schema[0]

        ces_folder = self.folder[0]

        ces_tag    = self.tag[0]

        ces_db = TileCalibTools.openDbConn(ces_schema, 'READONLY')

        self.ces_blob_reader = TileCalibTools.TileBlobReader(ces_db, ces_folder, ces_tag)

        cis_schema = self.schema[1]
                                
        cis_folder = self.folder[1]
                                
        cis_tag    = self.tag[1]

        cis_db = TileCalibTools.openDbConn(cis_schema, 'READONLY')

        self.cis_blob_reader = TileCalibTools.TileBlobReader(cis_db, cis_folder, cis_tag)

        las_schema = self.schema[2]
                                
        las_folder = self.folder[2]
                                
        las_tag    = self.tag[2]
        
        las_db = TileCalibTools.openDbConn(las_schema, 'READONLY')

        self.las_blob_reader = TileCalibTools.TileBlobReader(las_db, las_folder, las_tag)

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

            # _t stands for tower and has to be present in the
            # hash to get the right data.

            if '_t' not in region.GetHash():

                continue

            run       = str(event.run).split(",")[0]
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

            part = {'LBA':1, 'LBC':2, 'EBA':3, 'EBC':4}

            ces_drawer = self.ces_blob_reader.getDrawer(part[partition], 
                                                        int(module) - 1, 
                                                        (int(run), 0))

            cis_drawer = self.cis_blob_reader.getDrawer(part[partition], 
                                                        int(module) - 1, 
                                                        (int(run), 0))

            las_drawer = self.las_blob_reader.getDrawer(part[partition], 
                                                        int(module) - 1, 
                                                        (int(run), 0))

            if channel_2 is not None:

                ces_const_hg = (ces_drawer.getData(channel_1, 1, 0), 
                                ces_drawer.getData(channel_2, 1, 0))

                cis_const_hg = (cis_drawer.getData(channel_1, 1, 0),
                                cis_drawer.getData(channel_2, 1, 0))

                las_const_hg = (las_drawer.getData(channel_1, 1, 0),
                                las_drawer.getData(channel_2, 1, 0))


                product = (ces_const_hg[0] * cis_const_hg[0] * las_const_hg[0],
                           ces_const_hg[1] * cis_const_hg[1] * las_const_hg[1])

                event.data['cal_constantHG'] = (1 / product[0], 1 / product[1])

            else:

                ces_const_hg = (ces_drawer.getData(channel_1, 1, 0), 
                                None)

                cis_const_hg = (cis_drawer.getData(channel_1, 1, 0),
                                None)

                las_const_hg = (las_drawer.getData(channel_1, 1, 0),
                                None)

                product = (ces_const_hg[0] * cis_const_hg[0] * las_const_hg[0],
                           None)

                event.data['cal_constantHG'] = (1 / product[0], None)


    def ProcessStop(self):
        '''Function to finalize things.

         This function gets called after all of the regions in the detector have
         been sent to ProcessRegion().  It is the last function called in this
         class.'''


        pass
