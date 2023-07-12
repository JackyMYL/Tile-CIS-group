from src.GenericWorker import GenericWorker
import os
import ROOT
import datetime

class UseDB(GenericWorker):
    '''
    Add runs from DB
    '''

    def __init__(self, output, first_run, last_run, use_sqlite, db_conn, db_file, db_folder_tag, run_type='Ped', verbose=False, regions=None, exclude_regions=None, ped_low=5.0):
        self.m_output = output
        self.m_first_run = first_run
        self.m_last_run = last_run
        self.m_run_type = run_type
        self.m_verbose = verbose
        self.m_use_sqlite = use_sqlite
        self.m_db_conn = db_conn
        self.m_db_file = db_file
        self.m_db_folder_tag = db_folder_tag
        self.m_db = None
        self.m_blob_reader = None
        self.m_db_objects = {}
        self.m_regions = regions
        self.m_exclude_regions = exclude_regions
        self.m_all_runs = set()
        self.m_ped_low = ped_low

    # ---- Implementation of Worker ----

    def ProcessStart(self):
        # Open up a DB connection
        if self.m_use_sqlite:
            if not os.path.exists(self.m_db_file):
                self.m_output.print_log('ERROR UseDB: Failed to find SQLite: %s' % self.m_db_file)
                exit
            self.m_db = TileCalibTools.openDb('SQLITE', self.m_db_conn, 'READONLY', sqlfn=self.m_db_file)
            self.m_output.print_log('UseDB: Opened file %s ' % self.m_db_file)
        else:
            self.m_db = TileCalibTools.openDb('ORACLE', self.m_db_conn, 'READONLY', "COOLOFL_TILE")
            self.m_output.print_log('UseDB: Opened DB connection %s ' % self.m_db_conn)

        if not self.m_db:
            self.m_output.print_log('UseDB" Failed to open a connection to the COOL database')
        else:
            folderDigi      = TileCalibTools.getTilePrefix(True,True)+'NOISE/SAMPLE'
            tagDigi = TileCalibTools.getFolderTag(self.m_db, folderDigi, self.m_db_folder_tag)
            
            self.m_output.print_log('UseDB: Using folder: %s with tag: %s' % (folderDigi, tagDigi))
            self.m_blob_reader = TileCalibTools.TileBlobReader(self.m_db, folderDigi, tagDigi)

    def ProcessStop(self):
        if self.m_db:
            self.m_db.closeDatabase()
        global Use_run_list
        Use_run_list = sorted(self.m_all_runs)
        self.m_output.print_log('UseDB: Run list %s' % Use_run_list)
        
    def ProcessRegion(self, region):
        rhash = region.GetHash()
        if 'gain' not in rhash:
            return

        if self.m_regions:
            do_include = False
            for r in self.m_regions:
                if r in rhash:
                    do_include = True
                    continue
            if not do_include:
                return
        
        if self.m_exclude_regions:
            for r in self.m_exclude_regions:
                if r in rhash:
                    return

        # Get indices 
        [part, mod, chan, gain] = region.GetNumber()

        # Get information about the DB objects, i.e. their IOV
        db_key = '%d_%d' % (part, mod-1)
        if db_key not in self.m_db_objects:
            # Get all DB objects from firstRun to lastRun
            objs = self.m_blob_reader.getDBobjsWithinRange(ros=part, drawer=mod-1, point1inTime=(self.m_first_run,0), point2inTime=(self.m_last_run,0))            
            self.m_db_objects[db_key] = [(TileCalibTools.runLumiFromCoolTime(dbo.get().since())[0], TileCalibTools.runLumiFromCoolTime(dbo.get().until())[0]) for dbo in objs]

        # Create an event for each run
        dbObjs = self.m_db_objects[db_key]
        
        if self.m_verbose:
            self.m_output.print_log("UseDB: region %s" % rhash)

        for run_number, run_number_until in dbObjs:
            run = Run(run_number, self.m_run_type, 0, {})

            self.m_all_runs.add(run_number)

            event = Event(run, {})
            blob = self.m_blob_reader.getDrawer(part, mod-1, (run_number, 0))
            event.data['run_number_until_db'] = run_number_until
            event.data['ped_db']   = blob.getData(chan, gain, 0)
            event.data['hfn_db']   = blob.getData(chan, gain, 1)
            event.data['lfn_db']   = blob.getData(chan, gain, 2)
            try:
                event.data['hfnsigma1_db']   = blob.getData(chan, gain, 3) 
            except:
                event.data['hfnsigma1_db'] = 0
            try:
                event.data['hfnsigma2_db']   = blob.getData(chan, gain, 4) 
            except:
                event.data['hfnsigma2_db']   = 0
            try:
                event.data['hfnnorm_db']   = blob.getData(chan, gain, 5) 
            except:
                event.data['hfnnorm_db']   = 0
                
            region.AddEvent(event)
            if event.data['ped_db'] < self.m_ped_low:
                self.m_output.print_log("ERROR Zero/small pedestal for ADC: %s run: %d pedestal: %f" % (rhash, run_number, event.data['ped_db']))
            if self.m_verbose:
                self.m_output.print_log("run: %d -> %d pedestal: %s" % (run_number, run_number_until, event.data['ped_db']))

