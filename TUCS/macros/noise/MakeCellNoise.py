#!/usr/bin/env python

import os, sys
'''
This macro fills a caloSqlite (cell noise) with data or MC in MeV units.
'''

args = sys.argv[1:]

if not args or len(args)<2:
    print 'usage: ', sys.argv[0], 'lower_iov run_number file(can be empty) UseData(default is True) UseSqlite(default is False) PatchBadValues(default is "not UseData") inputTag(default is RUN2-UPD1-00) outputTag(default=inputTag)'
    print 'for example:  MakeCellNoise.py 354321 355007'
    print '         or:  MakeCellNoise.py 310000 310000 RawCh_NoiseCalib_0_310000_Phys.root False False True OF2-15 OF2-17'
    sys.exit(1)

# define the region in which this is performed:
# possible syntax:
# '' means everything
# 'LBA'  partition;
# 'LBA25'
# 'LBA25_c5'
selected_region = ''

lower_iov = int(args[0]) # run number for start of IOV in DB
runNumber = int(args[1]) # run number to process (and to retrieve from runInfo DB)

filename  = args[2] if len(args)>2 else '' # root file to read, if it has non-standard name or in non-standard directory
if filename.isdigit(): # if filename is integer assume that it's version number for given ped run
    pedNr = filename
    filename  = ''
else:
    pedNr = ''

# data/MC flag
# if True - prepare DB for data
# otherwise - prepare DB for MC
useData = len(args)<4 or args[3][0] in ['t', 'T', '1', 'y', 'Y' ]
if useData:
    dbRun = lower_iov  # will use the same runNumber for input and output DB
else:
    dbRun = runNumber  # will take constants from input DB for this run number
    runNumber = 355007 # jusr arbitrary pedestal run number, it's not important for MC update

# sqlite/Oracle flag
# if True read old constants from sqlite file caloSqlite_in.db
# otherwise read old constants from Oracle directly
# Note that input and output sqlite files are different
# Name of input file can be also provided as 5th parameter instead of "True"
useSqlite = len(args)>4 and args[4][0] in ['t', 'T', '1', 'y', 'Y' ]
insqlfn='caloSqlite_in.db'
if len(args)>4:
    nm=args[4]
    if "db" in nm or "ql" in nm:  # if 5th parameter contains db or sql
        insqlfn=nm                # it is assumed to be name of sqlite file with cell noise
        useSqlite=True            # so, this file is used as input

# if patchBadValues is set to true, all zero noise values
# are replaced by detector-average for the same cell type
# Default is True for MC and False for data
if len(args)>5:
    patchBadValues = args[5][0] in ['t', 'T', '1', 'y', 'Y' ]
else:
    patchBadValues = not useData

dbTag = args[6] if len(args)>6 else 'RUN2-UPD1-00'
myTag = args[7] if len(args)>7 else dbTag

print "Running",sys.argv[0],"with parameters:", lower_iov, runNumber, filename+pedNr if len(filename+pedNr)>0 else repr(''),\
       useData, useSqlite, patchBadValues, dbTag if len(args)>6 else repr(''), myTag if len(args)>7 else repr('')

if useData == True:
    myConn='CONDBR2'
    outsqlfn='tile_cell_noise_%d.sqlite' % runNumber
else:
    if dbTag == myTag:
        print 'For MC input tag and output tag should be different, please specify them as 7th and 8th parameter'
        sys.exit(1)
    myConn = 'OFLP200'
    outsqlfn='tile_cell_noise_mc_%d_%s.sqlite' % (lower_iov, myTag)

# just to guarantee that additional restart in src/load.py works
__file__ = os.path.realpath(__file__)

os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) #don't remove

processlist = [
    Use(run=runNumber,runType='Ped',type='physical',region=selected_region,verbose=True,keepOnlyActive=False),
    ReadCellNoiseDB(useSqlite=useSqlite,folderTag=dbTag,dbConn=myConn,sqlfn=insqlfn,runNumber=dbRun), # reading from Oracle
    ReadCellNoiseFile(processingDir = filename, pedNr=pedNr)] #Usual processingDir, put full path to the file if want to read from non-standard dir
if patchBadValues:
    processlist += [PatchBadValues(runType='Ped',type='physical',standard_p='cellsigma1',RUN2=True)]
processlist += [
    NoiseVsDB(parameter='cell',savePlot=True,updateAll=True,RUN2=True),
    WriteCellNoiseDB(runType='PedUpdate',offline_iov_beg=(lower_iov,0),offline_iov_end=(-1,MAXLBK),folderTag=myTag,dbConn=myConn,sqlfn=outsqlfn,ngains=4)]
# if NoiseVsDB is used, runType in WriteCellNoiseDB should be PedUpdate
# if NoiseVsDB is commented out, runType in WriteCellNoiseDB should be Ped

g = Go(processlist,withMBTS=True,withSpecialMods=True,RUN2=True)
