#!/usr/bin/env python

import os,sys
'''
This macro converts cell noise to digi(sample) noise and creates sqlite file for MC
'''

args = sys.argv[1:]

if not args:
    print 'usage: ', sys.argv[0], 'lower_iov run_number file(can be empty) CellNoiseFromDB(default is False) DigiNoiseFromDB(default is False)'
    print 'for example:  make2gausDigi.py 282483 287203 RawCh_NoiseCalib_1_287203_Ped.root False False'
    print '         or:  make2gausDigi.py 310000 354121'
    print '         or:  make2gausDigi.py 310000 355007 X True True'
    print 'in last example ped run number (355007) is simply used to select corresponding IOV in COOL DB'
    sys.exit(1)

# define the region in which this is performed:
# possible syntax:
# '' means everything
# 'LBA'  partition;
# 'LBA25'
# 'LBA25_c5'
selected_region = ''

# IOV in sqlite file for MC you are building
# normally should be one of those mentioned at
# https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/ConditionsRun1RunNumbers
lower_iov = int(args[0])

# pedestal run number (DQ leader should tell which file to use for a good calibration set)
# or run number from desired IOV in COOL DB for data (but still, valid pedestal run number)
runNumber = int(args[1])
dbRun = runNumber # used only if cellNoiseFromDB=True or digiNoiseFromDB=True

filename  = args[2] if len(args)>2 else '' # root file to read, if it has non-standard name or in non-standard directory
if filename.isdigit(): # if filename is integer assume that it's version number for given ped run
    pedNr = filename
    filename  = ''
else:
    pedNr = ''
digiNoiseFile = filename.replace("RawCh","Digi") # normally digi noise is taken from Digi_NoiseCalib*.root

# read input noise values from DB for data or directly from ROOT files 
cellNoiseFromDB=len(args)>3 and args[3][0] in ['t', 'T', '1', 'y', 'Y' ]
digiNoiseFromDB=len(args)>4 and args[4][0] in ['t', 'T', '1', 'y', 'Y' ]

caloSQLiteFile=None
if len(args)>3:
    nm=args[3]
    if "db" in nm or "ql" in nm:  # if 4th parameter contains db or sql
        caloSQLiteFile=nm         # it is assumed to be name of sqlite file with cell noise
        caloNoiseFromDB=True      # so, this file is used as input

digiSQLiteFile=None
if len(args)>4:
    nm=args[4]
    if "db" in nm or "ql" in nm:  # if 5th parameter contains db or sql
        digiSQLiteFile=nm         # it is assumed to be name of sqlite file with digi noise
        digiNoiseFromDB=True      # so, this file is used as input

doSingleGaus = False
doCheckValues = True
doWriteDB = True

# CHANGE ME:
# following parameters should be adjusted for every MC production
# check what are the most recent tags in MC COOL DB

# tag for bad channel lisf in MC DB
badTAG = args[5] if len(args)>5 else 'IOVDEP-12'

# tag for cesium constants in MC DB
cesiumTag = args[6] if len(args)>6 else 'SIM-09'

# tags for old noise and ACM in MC DB
noiseTAG = args[7] if len(args)>7 else 'TwoGauss-21'
acTAG = 'COM-03'

# output noise tag
noiseTAGOut = args[8] if len(args)>8 else 'TwoGauss-22'

quote = lambda x: " ".join([y if len(y)>0 else repr('') for y in x])
print "Running",sys.argv[0],"with parameters:", quote(args)

suffix="2gauss"
outputSQLiteFile = 'tile_noise_mc%s_%d_%d_%s.sqlite' % (suffix, lower_iov, runNumber, noiseTAGOut) # file will be created in $TUCSRESULTS directory
outputROOTFile = os.getenv('PWD') + '/tile_mc_noise_input_%d_%s.root' % (runNumber, suffix) # file will be created in current directory
outputLogFile = os.getenv('PWD') + '/tile_mc_noise_log_%d_%s.txt' % (runNumber, suffix) # file will be created in current directory

# just to guarantee that additional restart in src/load.py works
__file__ = os.path.realpath(__file__)

os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

sys.path.insert(0, 'macros/noise')
import _NoiseCommon
output = _NoiseCommon.NoiseOutput(outputLogFile, outputROOTFile, None)

output.print_log("Reading calibration IOV: %d tag for Cesium: %s " % (lower_iov, cesiumTag))
output.print_log("Do single gaus: %s " % (str(doSingleGaus)))

processList = [
    Use(run=runNumber,runType='all',type='physical',region=selected_region,verbose=True,keepOnlyActive=False),
    CheckSpecialChannels(data='MC', runNumber=lower_iov),
]

if caloSQLiteFile is not None:
    output.print_log("Read Cell noise from sqlite file %s" % caloSQLiteFile)
    processList += [
        ReadCellNoiseDB(useSqlite=True,sqlfn=caloSQLiteFile, dbConn='CONDBR2',folderTag='UPD1') # reading latest cell noise from sqlite
    ]
elif cellNoiseFromDB:
    output.print_log("Read Cell noise from COOL DB")
    processList += [
        ReadCellNoiseDB(useSqlite=False,dbConn='CONDBR2',runNumber=dbRun,folderTag='UPD4') # reading old cell noise from Oracle
    ]
else:
    output.print_log("Read Cell noise from file %s" % filename)
    processList += [
        ReadCellNoiseFile(processingDir = filename, pedNr=pedNr, Read2Gaus=(not doSingleGaus), Make2GausEqual1Gaus=doSingleGaus), #Usual processingDir, put full path to the file if want to read from non-standard dir
    ]

processList += [
    PatchBadValues(runType='Ped', type='physical', standard_p='cellsigma1', useDbValues=cellNoiseFromDB, RUN2=True, maxgain=4 if cellNoiseFromDB else 6)
]

if digiSQLiteFile is not None:
    output.print_log("Read Digi noise from sqlite file %s" % digiSQLiteFile)
    processList += [
        ReadDigiNoiseDB(useSqlite=True,dbFile=digiSQLiteFile,dbConn='CONDBR2',folderTag='UPD1',folderTagAC='UPD1',load_autocr=True) # reading latest digi noise from sqlite
    ]
elif digiNoiseFromDB:
    output.print_log("Read Digi noise from COOL DB")
    processList += [
        ReadDigiNoiseDB(useSqlite=False,dbConn='CONDBR2',IOVRun=dbRun,folderTag='UPD4',folderTagAC='UPD4',load_autocr=True) # reading old digi noise from Oracle
    ]
else:
    output.print_log("Read Digi noise from file %s" % digiNoiseFile)
    processList += [
        ReadDigiNoiseFile(processingDir = digiNoiseFile, pedNr=pedNr, load_autocr=True), #Usual processingDir, put full path to the file if want to read from non-standard dir
        #NoiseVsDB(parameter='digi', savePlot=True, load_autocr = False),
    ]

processList += [
    PatchBadValues(runType='Ped', type='readout', standard_p='hfn', useDbValues=digiNoiseFromDB, RUN2=True, maxval=8)
]
processList += [
    PatchBadValues(runType='Ped', type='readout', standard_p='ped', useDbValues=digiNoiseFromDB, RUN2=True, minval=10, maxval=100)
]

processList += [EnableCalibration(),
    ReadBadChFromCool(schema='OFL', Fast=True,         storeADCinfo=True,  tag=badTAG,   data='MC', runNumber=lower_iov),
    ReadCalibFromCool(schema='OFL', runType='CIS',     folder='CALIB/CIS', tag='COM-00', data='MC', runNumber=lower_iov),
    ReadCalibFromCool(schema='OFL', runType='Las_LIN', folder='CALIB/LAS', tag='COM-00', data='MC', runNumber=lower_iov),
    ReadCalibFromCool(schema='OFL', runType='cesium',  folder='CALIB/CES', tag=cesiumTag,data='MC', runNumber=lower_iov, verbose=True),
    ReadCalibFromCool(schema='OFL', runType='emscale', folder='CALIB/EMS', tag='COM-00', data='MC', runNumber=lower_iov)]

processList += [
    MarkBadCells(output),
    MakeDigi2Gaus(digiFromDB=digiNoiseFromDB,cellFromDB=cellNoiseFromDB, LGscale=1.0, HGscale=1.0, output=output), # RUN2=True
    PlotDigiNoise(runNumber=runNumber, runType='PedUpdate', output=output)]

if doCheckValues:
    processList += [
        ReadDigiNoiseDB(useSqlite=False,dbConn='OFLP200',folderTag=noiseTAG,folderTagAC=acTAG,load_autocr=True),
        PedestalCompare2DB(hgThresholds=[0.5, 0.05, 0.05, 0.05,  0.05],
                           lgThresholds=[0.5, 0.05, 0.05, 0.05,  0.05],
                           isRelativeThreshold =[False, True, True, True, True],
                           verbose=True, 
                           attributes=['ped', 'lfn', 'hfn', 'hfnsigma1', 'hfnsigma2'], 
                           dbAttributes=['ped_db', 'lfn_db', 'hfn_db', 'hfnsigma1_db', 'hfnsigma2_db'], 
                           maskBad=False,
                           output=output,
                           createUpdateEvent=False, runTypeUpdate='PedUpdate', runTypeDB='Ped',
                           onlyWriteUpdated=True,
                           hgLargeDiffThresholds=[30, 0.30, 0.30, 0.30, 0.30],
                           lgLargeDiffThresholds=[30, 0.30, 0.30, 0.30, 0.30],
                           absurdValThresholds=[500, 8, 8, 8, 8])]

if doWriteDB:
    processList += [
        WriteDigiNoiseDB(runType='PedUpdate',folderTag=noiseTAGOut, folderTagAC=acTAG, offline_iov_beg=(lower_iov,0), 
                         offline_iov_end = (-1,MAXLBK), dbConn='OFLP200', load_autocr = False, sqlfn=outputSQLiteFile)]

g = Go(processList,withMBTS=True,withSpecialMods=True,RUN2=True)


output.close()
