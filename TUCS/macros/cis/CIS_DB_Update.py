#!/usr/bin/env python
#
# Author : Grey Wilburn
# Date   : September 2014
#
#"""
#This macro calculates updated CIS DB constants
#and puts them into an SQLite file called
#results/tilesqlite.db
#"""

import argparse
import itertools
import sys
import os
os.chdir(os.getenv('TUCS','.'))
sys.path.insert(0, 'src')
#import Get_Consolidation_Date
import datetime


#################################################################

parser = argparse.ArgumentParser(description=
'recalibrates the database CIS constant value in the region \n \
specified by the user. Uses h3000 data in calculating the \n \
database constant values. Default values SHOULD be an added \n \
functionality once this code is used in reality.',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--updateThreshold', action='store',default=0.005,required=False,
                    help='Update threshold is nominally 0.5% (updateThreshold=0.005)\
                        If you want to change it, enter a different value. \
                            For example, updateThreshold=0.0  will force a change on every channel'  )

parser.add_argument('--runWindow', action='store',type=int,default=10,required=False,
help='Change run_window parameter for MultipleIOV processing if necessary. Enter an integer')

parser.add_argument('--date', action='store', nargs='+', type=str, default='2012-01-01',
                    required=True, #No longer a required argument 
                     help=
  'Select runs to use. If you want to use \n \
a list of run numbers instead, use --ldate. \n \
You have to select SOMETHING for --date, \n \
but it is irrelevant if --ldate is used \n \
(There is probably a better way about that) \n \
Preferred formats: \n \
1) starting date as a string (takes from there \n \
to present). EX: \'YYYY-MM-DD\' \n \
2) runs X days, or X months in the past as string: \n \
   \'-28 days\' or \'-2 months\' \n \
3) All of the runs between two dates. \n \
   This should use two arguments \n \
   each of this form: \'Month DD, YYYY\' \n \
EX: --date 2011-10-01 or --date \'-28 days\' \n \
    --date \'January 01, 2011\' \'February 11, 2011\' \n ')

parser.add_argument('--ldate', action='store', nargs='+', type=int, default=0,
                    help=
'Allows you to select runs to use \n \
by their actual run number. \n \
Run numbers should be separated by whitespace \n \
EX: --ldate 183009 183166 183367 \n ')


parser.add_argument('--region', action='store', nargs='*', type=str, default='',
                    required=False, help=
'Select the regions you wish to examine. \n \
Acceptable formatting is channels as they appear \n \
in the region.GetHash() format separated by spaces. \n \
Entire modules or barrels can be specified by \n \
leaving out the channel information or module and \n \
channel information respectively.\n \n \
EX: --region LBA_m22 EBC_m02_c00 EBA \n \
would produce plots for every channel in LBA22, \n \
every channel in the EBA partition, \n \
and EBC02 channel 00. Channels in this region \n \
will be recalibrated using measured constants stored \n \
in the h3000 ntuples. \n ')

parser.add_argument('--mdebug', action='store_true', default=False,
                    help=
'This is a switch that passes the memory debug flag to \n\
the Go.py module. THe result is two plots detailing \n\
the memory consumption of this macro. The first is a \n\
plot that is the percent memory used as a function of \n\
time -- color coded by which worker is running during \n\
that time. The second is a histogram showing the \n\
total memory consumption used by each worker. These are \n\
all printed in the Tucs/ResourceLogs/ directory \n\
(which is created if not already in place). The plots, \n\
along with the supporting text files are categorized \n\
by the unique process ID of each instance this macro \n\
is called. \n\n')

parser.add_argument('--multipleiov', action='store_true', default=False,
                    help=
'This is a switch that activates the creation of  \n\
an SQL file with multiple IOV\'s. \n\n')


parser.add_argument('--recalALL', action='store_true', default=False,
                    help=
'this is a switch that produces new cis constants \n\
for every tilecal adc. it should never be used casually. \n\
it is most commonly used after the detector comes online\n\
after a shutdown, or after a  serious maintenance problem. \n\
only use if you know what you are doing and have permission \n\
from a. solodkov (sanya.solodkov@cern.ch)  \n\n')

args=parser.parse_args()

#################################################################
# Does not require date input (can use --ldate instead)
if args.date:
    if len(args.date) == 1:
        runs             = args.date[0]
    elif len(args.date) == 2:
        runs             = (args.date[1], args.date[0])
    else:
        print('\
        --DATE HAS TOO MANY ARGUMENTS \n \
        USING ONLY THE FIRST')
        runs             = args.date[0]
if args.updateThreshold:
    updateThreshold = float(args.updateThreshold)
else:
    updateThreshold = 0.005
print("updateThreshold=",updateThreshold)

if args.multipleiov:
	multipleiov = True
else:
	multipleiov = False

if args.runWindow:
    runWindow = args.runWindow
else:
    runWindow = False
print("runWindow={%f}"%runWindow)
if multipleiov and not runWindow:
    ValueError("You have not declared a runWindow interval size even though you want multipleIOV reprocessing. Use --runWindow 10, for example.")

if args.recalALL:
	recalall = True
else:
	recalall = False

if args.ldate:
    runs = args.ldate

if args.region:
	selected_region      = args.region
mdebug               = args.mdebug

#Do NOT remove this line!
#py2 version: exec(open('src/load.py').read(), globals())
exec(open("src/load.py").read(), globals())


## The update threshold can be changed here. # Make this a command-line option in the future
# updateThreshold = 0.00
#updateThreshold = 0.0 # Use for first_iov when doing reprocessing to get baseline values for each


## When you want to read a local sqlite file for reprocessing or another reason, 
## uncomment the second 'readcalfromcool' option and use that instead of the first one. 
readbchfromcool = ReadBadChFromCool(schema='OFL', tag='UPD4', Fast=True, storeADCinfo=True)

# Use for normal CIS updates
readcalfromcool = ReadCalibFromCool(schema='OFL', runType='CIS', folder='CALIB/CIS', tag='UPD1', data = 'DATA',meandev_threshold = updateThreshold)

# Use for reprocessing as instructed by Sasha Solodkov
#readcalfromcool = ReadCalibFromCool(schema='sqlite://;schema=tileSqlite_first_IOV.db;dbname=CONDBR2', runType='CIS', 
#                                    folder='CALIB/CIS', tag='RUN2-HLT-UPD1-00', data = 'DATA',meandev_threshold = updateThreshold)
#readcalfromcool = ReadCalibFromCool(schema='sqlite://;schema=./results/tileSqlite.db;dbname=CONDBR2', runType='CIS', folder='/TILE/OFL02/CALIB/CIS/LIN', tag='RUN2-UPD4-09')

stuckbit = StuckBitHistory(DBUpdate = True, only_all_flags = False, only_chosen_flag = False)

print(runs)
if args.region:
	u = Use(run=runs, runType='CIS', region=selected_region, preprocessing=False)
else:
	u = Use(run=runs, runType='CIS', preprocessing=False)

#HELLO I AM NEW AND ALSO A TESTS
thr = SetLowCISThreshold(run_window = 10, threshold = updateThreshold)

## For the CalculateDBCIS worker, 'run_window' is the number of runs with higher than threshold
##deviation after which the CIS constant will be updated.
cdb = CalculateDBCIS( run_window = runWindow, threshold = updateThreshold)
#changed run window from 10 -> 2, i think this may be qhy some channels r not updating

if multipleiov:
	writedb = WriteDBMultipleIOV(multiple_iov = True, recalALL = recalall)
	sqlo = SQLOutput(single_iov = False, recalALL = recalall)
	updateneeded = Update_Needed(multiple_iov = True, recalALL = recalall, threshold = updateThreshold)
else:
	writedb = WriteDBMultipleIOV(multiple_iov = False, recalALL = recalall)
	sqlo = SQLOutput(single_iov = True, recalALL = recalall)
	updateneeded = Update_Needed(multiple_iov = False, recalALL = recalall, threshold = updateThreshold)



#################################################################

Go([
	u,\
        ReadCIS(),\
        CleanCIS(), \
        readbchfromcool,\
        readcalfromcool,\
        MoreInfo(),\
        thr,\
        cdb,\
        updateneeded,\
        writedb,\
	sqlo,\
        stuckbit], 
        memdebug=mdebug)

