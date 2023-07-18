#!/usr/bin/env python

import os, sys

'''
This macro fills a tileSqlite (noise in channels) with data or Monte Carlo in units of ADC counts.
For MC it's not so useful, because only Ped, HFN, LFN are provided and not two-Gaussian parameters
'''

args = sys.argv[1:]

if not args or len(args)<2:
    print 'usage: ', sys.argv[0], 'lower_iov run_number file(can be empty) UseData(default is True) inputTag(default is RUN2-UPD1-01) outputTag(default=inputTag)'
    print 'for example:  MakeDigiNoise.py 354321 355007'
    print '         or:  MakeDigiNoise.py 310000 355007 "" False TwoGauss-22 TwoGauss-23'
    sys.exit(1)

# define the region in which this is performed:
# possible syntax:
# '' means everything
# 'LBA'  partition;
# 'LBA25'
# 'LBA25_c5'
selected_region = ''

#minDate = 2011-04-01
#maxDate = 2011-06-30
#runList = getRuns(minDate,maxDate,False)

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

dbTag = args[4] if len(args)>4 else 'RUN2-HLT-UPD1-01' if useData else 'TwoGauss-22'
myTag = args[5] if len(args)>5 else dbTag

print "Running",sys.argv[0],"with parameters:", lower_iov, runNumber, filename+pedNr if len(filename+pedNr)>0 else repr(''),\
       useData, dbTag if len(args)>4 else repr(''), myTag if len(args)>5 else repr('')

if useData:
    myConn = 'CONDBR2' #data
    myTagAC = 'RUN2-HLT-UPD1-01' #?
    outputSQLiteFile = 'tile_noise_%d_%d.sqlite' % (lower_iov, runNumber) # file will be created in $TUCSRESULTS directory
else:
    myConn = 'OFLP200' #MC
    myTagAC = 'COM-03' #?
    outputSQLiteFile = 'tile_noise_mc_%d_%d_%s.sqlite' % (lower_iov, runNumber, myTag) # file will be created in $TUCSRESULTS directory

# just to guarantee that additional restart in src/load.py works
__file__ = os.path.realpath(__file__)

os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) #don't remove

processlist = [
    Use(run = runNumber, runType = 'Ped', region = selected_region, verbose = True, keepOnlyActive = False),
    ReadDigiNoiseDB(useSqlite = False, folderTag = dbTag, folderTagAC = myTagAC, dbConn = myConn, load_autocr = False),
    ReadDigiNoiseFile(processingDir = filename, pedNr=pedNr, load_autocr = False),
    PatchBadValues(runType = 'Ped', type = 'readout', standard_p = 'hfn'),
    NoiseVsDB(parameter='digi', savePlot=True, load_autocr = False),
    WriteDigiNoiseDB(offline_iov_beg=(lower_iov,0), offline_iov_end = (-1,MAXLBK),
                     folderTagAC = myTagAC, folderTag = myTag, dbConn = myConn, load_autocr = False, sqlfn=outputSQLiteFile)]

g = Go(processlist,withMBTS=True,withSpecialMods=True, RUN2=True)
