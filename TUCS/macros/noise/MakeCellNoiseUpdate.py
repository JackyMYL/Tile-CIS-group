#!/usr/bin/env python

import os, sys

os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) #don't remove

import _NoiseCommon

'''
This macro fills a caloSqlite (cell noise) with data or MC in MeV units.
'''

# handle arguments
argparser = argparse.ArgumentParser(description='Produce new cell noise calibration constants')

argparser.add_argument('--verbose', required=False, default=False, action='store_true',
                       help='Verbose output', dest='verbose')
# Input arguments
argparser.add_argument('--run', required=True,
                       type=int, help='Specify the run to compare to DB', dest='run')

argparser.add_argument('--db_compare_run', required=False, default=None,
                       type=int, help='Specify the DB comparison run, also the start of the IoV', dest='dbCompareRun')

argparser.add_argument('--input_file_name', required=False, default='',
                       type=str, help='Override input file name', dest='inputFileName')

argparser.add_argument('--pedestal_number', required=False, default='',
                       type=str, help='Pedestal number in the file name', dest='pedestalNumber')

argparser.add_argument('--db_input_file', required=False, default='caloSqlite_in.db',
                       type=str, help='Sqlite file for comparison', dest='dbInputFile')

argparser.add_argument('--db_input_tag', required=False, default=None,
                       type=str, help='COOL input tag', dest='dbInputTag')

# Output arguments
argparser.add_argument('--db_output_file', required=False, default='',
                       type=str, help='Output Sqlite file', dest='dbOutputFile')

argparser.add_argument('--db_output_tag', required=False, default=None,
                       type=str, help='COOL output tag', dest='dbOutputTag')

# Process arguments
do_mc_grp = argparser.add_mutually_exclusive_group(required=False)
do_mc_grp.add_argument('--do_mc', action='store_true',
                       help='Do MC/Data', dest='doMC')
do_mc_grp.add_argument('--do_data', action='store_false',
                       help='Do MC/Data', dest='doMC')
argparser.set_defaults(doMC=False)

patch_bad_grp = argparser.add_mutually_exclusive_group(required=False)
patch_bad_grp.add_argument('--patch_bad_values', action='store_true',
                           help='Apply patch to bad values from data', dest='patchBadValues')
patch_bad_grp.add_argument('--do_not_patch_bad_values', action='store_false',
                           help='Do not apply patch to bad values from data', dest='patchBadValues')
argparser.set_defaults(patchBadValues=False)

# DB arguments
use_sqlite_grp = argparser.add_mutually_exclusive_group(required=False)
use_sqlite_grp.add_argument('--db_use_sqlite', action='store_true',
                            help='Use Sqlite database for comparison', dest='dbUseSqlite')
use_sqlite_grp.add_argument('--db_use_oracle', action='store_false',
                            help='Use Oracle database for comparison', dest='dbUseSqlite')
argparser.set_defaults(dbUseSqlite=False)

# Parse the arguments
args = argparser.parse_args()

if args.dbUseSqlite and not args.dbInputFile:
    print( "Error: option --db_input_file required when comparing to SQLite file")
    exit(1)

selected_region = ''
# run number for start of IOV in DB
lower_iov = args.dbCompareRun if args.dbCompareRun else args.run 
# run number to process (and to retrieve from runInfo DB)
runNumber = args.run

# data/MC flag
# if True - prepare DB for data
# otherwise - prepare DB for MC
useData = not args.doMC

# sqlite/Oracle flag
# if True read old constants from sqlite file caloSqlite_in.db
# otherwise read old constants from Oracle directly
# Note that input and output sqlite files are different
useSqlite = args.dbUseSqlite

# Default values
if useData == True:
    myConn='CONDBR2'
    dbTag = 'RUN2-UPD4-19'
    myTag = 'RUN2-UPD4-19'
    dbRun = lower_iov # will use the same runNumber for input and output DB
else:
    myConn = 'OFLP200'
    dbTag = 'OF2-07'
    myTag = 'OF2-08'
    dbRun = lower_iov # will use the same runNumber for input and output DB

if args.dbInputTag:
    print("Overriding default input tag '%s' with '%s'" % (dbTag, args.dbInputTag))
    dbTag = args.dbInputTag

if args.dbOutputTag:
    print("Overriding default output tag '%s' with '%s'" % (myTag, args.dbOutputTag))
    myTag = args.dbOutputTag

insqlfn = args.dbInputFile
outsqlfn = ('tile_cell_noise_%d.sqlite' % runNumber) if not args.dbOutputFile else args.dbOutputFile

print( "Running: %s" % sys.argv[0])
print( "Run number: %d" % runNumber)
print( "IOV start: %d" % lower_iov)
print( "Use data: %s" % str(useData))
print( "Use sqlite: %s" % str(useSqlite))
print( "In SQLite file: %s" % (insqlfn if useSqlite else  '-'))
print( "Out SQLite file: %s" % outsqlfn)
print( "DB conn: %s" % myConn)
print( "DB in tag: %s" % dbTag)
print( "DB out tag: %s" % myTag)
print( "DB comparison run: %d" % dbRun)
print( "Patch bad values: %s" % str(args.patchBadValues))

processlist = [
    Use(run=runNumber, runType='Ped', type='physical', region=selected_region, verbose=args.verbose, keepOnlyActive=False),
    ReadCellNoiseDB(useSqlite=useSqlite, folderTag=dbTag, dbConn=myConn, sqlfn=insqlfn, runNumber=dbRun), # reading from Oracle
    # Usual processingDir, put full path to the file if want to read from non-standard dir
    ReadCellNoiseFile(processingDir=args.inputFileName, pedNr=args.pedestalNumber)
    ]

# For MC:
if args.patchBadValues:
    processlist.append(PatchBadValues(runType='Ped', type='physical', standard_p='cellsigma1', RUN2=True))

# if NoiseVsDB is used, runType in WriteCellNoiseDB should be PedUpdate
# if NoiseVsDB is commented out, runType in WriteCellNoiseDB should be Ped
processlist.extend([
    NoiseVsDB(parameter='cell', savePlot=True, updateAll=True, RUN2=True),
    WriteCellNoiseDB(runType='PedUpdate', offline_iov_beg=(lower_iov,0), offline_iov_end=(-1,MAXLBK), folderTag=myTag, dbConn=myConn, sqlfn=outsqlfn, ngains=4)
    ])

g = Go(processlist, withMBTS=True, withSpecialMods=True, RUN2=True)
