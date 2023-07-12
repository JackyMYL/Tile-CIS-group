import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(),globals()) #don't remove

args = sys.argv[1:]

if not args:
    
    print 'usage: ', sys.argv[0], 'run_number'
    sys.exit(1)

selected_region = ''
runNumber = map(int,args)
#filename  = args[1]
myConn = 'CONDBR2' #data
#myConn = 'OFLP200' #MC
#myTag = 'PileUp-Dt75-OFC0-HVCorr'
#myTag = 'PileUp-Dt75-OFC0-HVCorr-02'
myTag = 'RUN2-UPD1-00' # often used for data

#Parameters for ReadBchFromColl

bad_channel_db = ('sqlite://;schema=/afs/cern.ch/user/t/tilecali/w0/'
                  'sqlfiles/BadChan/tileSqlite_2011.db;dbname=CONDBR2')

bad_channel_folder = '/TILE/OFL02/STATUS/ADC'

bad_channel_tag = 'TileOfl02StatusAdc-RUN2-UPD4-08'

readbchfromcool = GetBadChannel(run = runNumber, schema = bad_channel_db, 
                                    folder = bad_channel_folder, tag = bad_channel_tag)

#Parameters for ReadCalFromCool



ces_schema = ('sqlite://;schema=/afs/cern.ch/user/t/tilecali/w0/'
              'sqlfiles/Cesium/tileSqlite_Ces_2011.db;dbname=CONDBR2')

ces_folder = '/TILE/OFL02/CALIB/CES'

ces_tag    = 'TileOfl02CalibCes-RUN2-HLT-UPD1-01'


cis_schema = ('sqlite://;schema=/afs/cern.ch/user/t/tilecali/w0/'
              'sqlfiles/CIS/tileSqlite_CIS_2011_reprocessing.db;dbname=CONDBR2')

cis_folder = '/TILE/OFL02/CALIB/CIS/LIN'

cis_tag    = 'TileOfl02CalibCisLin-RUN2-UPD4-08'

las_schema = ('sqlite://;schema=/afs/cern.ch/user/t/tilecali/w0/'
              'sqlfiles/Laser/tileSqlite_allcst2011.db;dbname=CONDBR2')

las_folder = '/TILE/OFL02/CALIB/LAS/LIN'

las_tag    = 'TileOfl02CalibLasLin-RUN2-HLT-UPD1-00'

calib_schema = [ces_schema, cis_schema, las_schema]
calib_folder = [ces_folder, cis_folder, las_folder]
calib_tag    = [ces_tag, cis_tag, las_tag]


readcalfromcool = GetCalibConstants(run = runNumber, schema = calib_schema, 
                                    folder = calib_folder, tag = calib_tag)

digi_schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2'

digi_folder = '/TILE/OFL02/NOISE/SAMPLE'

digi_tag    = 'TileOfl02NoiseSample-RUN2-HLT-UPD1-01'

readdigifromcool = GetDigiNoiseData(run = runNumber, schema = digi_schema, 
                                    folder = digi_folder, tag = digi_tag)



processlist = [
    Use(run = runNumber, runType = 'Ped', type = 'physical', 
        region = selected_region, verbose = True, keepOnlyActive = True),
    #ReadCellNoiseFile(processingDir = filename),
    ReadCellNoiseDB(useSqlite = True, dbFile = 'caloSqlite.db', 
                    folderTag = myTag, dbConn = myConn),
    readbchfromcool, 
    readcalfromcool,
    readdigifromcool,
    FindZeroNoiseCells(run = runNumber),
    # ReadDigiNoiseDB(useSqlite = True, dbFile = 'tileSqlite.db', 
    #                 folderTag = 'RUN2-HLT-UPD1-01', dbConn = 'CONDBR2',
    #                 folderTagAC = 'RUN2-HLT-sUPD1-01'),
    TimeDependencePlots(run = runNumber)]
    #DigiTimeDependencePlots(run = runNumber)]

g = Go(processlist, withMBTS=True, withSpecialMods = True)
