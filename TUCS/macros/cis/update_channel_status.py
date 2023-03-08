#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# This is a script intended to provide summary status information about the
# CIS system in the form of a channel status bit.  This does NOT update the
# database directly.  Instead, it creates a local SQLite file.
# March 04, 2009
#
# Modified: Dave Hollander <daveh@uchicago.edu>
# May 28, 2010
#
# Modified: Joshua Montgomery <Joshua.J.Montgomery@gmail.com>
# Can now be run directly from the command line, like the rest of CIS.
# March 05, 2012

import argparse
import itertools


parser = argparse.ArgumentParser(description=
'Creates two tileSqlite.db files for the COOL Bad \n \
Channel Database. One for the UPD4 folder, and another \n \
for the UPD1 folder. Both contain identical information. \n \
NOTE: if you attempt to update the database using these \n \
files and the attempt fails (usually saying you dont have \n \
permission to change certain bits) it means that either \n \
somebody submitted an update between when you ran this \n \
and when you attempted to submit the Sqlite files, OR \n \
that the databases are unsynchronized. Somebody updated \n \
UPD4 without updating UPD1 or vise versa. Check the COOL \n \
elog to find when the unsynch happened, and email the person \n \
responsible. \n ',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--date', action='store', nargs='+', type=str, default=['-28 days'],
                    help=
'Select runs to use. If you want to use \n \
a list of run numbers instead, use --ldate. \n \
You have to select SOMETHING for --date, \n \
but it is irrelevant if --ldate is used \n \
(There is probably a better way about that) \n \
NOTE: Default for performing channel updates \n \
is \'- 28 days\' \n \
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
                    help=
'NOTE: There is virtually no reason \n \
to use anything but the whole detector \n \
when generating Channel Updates! \n \
Unless you are sure you know what you are \n \
doing, do not use this flag! \n \
\n \
Select the regions you wish to examine. \n \
Acceptable formatting is channels as they appear \n \
in the region.GetHash() format separated by spaces. \n \
Entire modules or barrels can be specified by \n \
leaving out the channel information or module and \n \
channel information respectively.\n \n \
EX: --region LBA_m22 EBC_m02_c00 EBA \n \
would produce plots for every channel in LBA22, \n \
every channel in the EBA partition, \n \
and EBC02 channel 00.\n ')


parser.add_argument('--usescans', action='store_true', default=False,
                    help=
'This is a switch that turns on functionality \n \
which looks at individual CIS scans for selected \n \
runs. be mindful that this will load in CIS \n \
scans for each channel for each run. \n \
This can be slow if you selected the whole \n \
detector and many runs.\n ')

parser.add_argument('--addwikipt', action='store_true', default=False,
                    help=
'If this switch is selected a new line will \n \
be added to the text file used to generate the \n \
performance plots found in the Public_Super_Macro. \n \
In general you want this to be false until you \n \
are sure you will be using the output tileSqlite.db \n \
files to update the COOL DB... we want the Performance \n \
plots to mirror the information contained in that DB. \n \
Default is False. \n \n')

parser.add_argument('--FORCEIOV', action='store', nargs=1, type=int, default=[0],
                    help=
'The COOL DB has a strict control over the IOVs you are \n \
allowed to effect change in with the UPD4 tagged folder. \n \
CIS doesnt really care as long as they are in the \n \
calibration loop, since we are only ever updating status \n \
for the present and future...never reprocessing \n \
status from the past. Right now the code somewhat intelligently \n \
GUESSES what IOV within the calibration loop to use. This \n \
almost always works. However, it is possible for somebody \n \
to have very recently submitted an update that overlaps \n \
with the chosen IOV. When this happens the COOL ROBOT \n \
may bump out complaining about back-insertion or wrong IOV. \n \
If this happens, log into the ROBOT, note the run number shown \n \
in the top left of the screen, and pick a number higher than that \n \
(or between the two numbers shown). It should also be higher \n \
than the one the program chose (which can be found by looking at \n \
the COOL Error log or the standard out of this program). \n \
Enter this integer after this flag, and it \n \
will replace the one automically used. \n \n')


parser.add_argument('--mdebug', action='store_true', default=False,
                    help=
'This is a switch that passes the memory debug flag to \n \
the Go.py module. The result is two plots detailing \n \
the memory consumption of this macro. The first is a \n \
plot that is the percent memory used as a function of \n \
time -- color coded by which worker is running during \n \
that time. The second is a histogram showing the \n \
total memory consumption used by each worker. These are \n \
all printed in the Tucs/ResourceLogs/ directory \n \
(which is created if not already in place). The plots, \n \
along with the supporting text files are categorized \n \
by the unique process ID of each instance this macro is called. \n')

args=parser.parse_args()

if len(args.date) == 1:
    runs             = args.date[0]
elif len(args.date) == 2:
    runs             = (args.date[1], args.date[0])
else:
    print '\
    --DATE HAS TOO MANY ARGUMENTS \n \
    USING ONLY THE FIRST'
    runs             = args.date[0]

if args.ldate:
    runs = args.ldate

selected_region      = args.region
useScans             = args.usescans
showAll              = True
add_wiki_data_point  = args.addwikipt
mdebug               = args.mdebug
Forced_IOV           = args.FORCEIOV[0]

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) 
from src.oscalls import *

startdir    = getPlotDirectory()
editdir     = startdir.split('/')
plotindex   = editdir.index('plots')
newstartdir = editdir[:plotindex]
newdir = []
for entry in newstartdir:
    newdir.append(entry)
newdir.append('Performance_Plot_Data')
PerfDir  = '/'.join(newdir)
createDir(PerfDir)
if add_wiki_data_point:
    add_wiki_data_point = PerfDir
else:
    add_wiki_data_point = False
#  Experts only below.
#

u = Use(run=runs, runType='CIS', region=selected_region)


if useScans:
    gs2 = GetScans(all=showAll)
    scs = ShowCISScans(all=showAll)
else:
    gs2 = None
    scs = None
    
readbchfromcool = ReadBadChFromCool(schema='OFL', tag='UPD4', Fast=True)
readcalfromcool = ReadCalibFromCool(schema='OFL', runType='CIS', folder='CALIB/CIS', tag='UPD4')


# Use the whole detector if no selected region is specified
if not globals().has_key('selected_region'):
    selected_region = ''

print 'Dumping plots for %s' % selected_region
#Go([u,\
#    ReadCIS(),\
#    CleanCIS(), \
#    readbchfromcool,\
#    readcalfromcool,\
#    CISFlagProcedure_modified(add_data_point=add_wiki_data_point),\
#    CISRecalibrateProcedure(),\
#    gs2,\
#    scs,\
#    CopyLocalChanStat(CISIOV=Forced_IOV),\
#    WriteChanStat(),\
#    Change_UPD_tag()],
#    memdebug=mdebug)

Go([u,\
    ReadCIS(),\
    CleanCIS(),\
    readbchfromcool,\
    readcalfromcool,\
    CISFlagProcedure_modified(add_data_point=add_wiki_data_point),\
    CISRecalibrateProcedure(),\
    gs2,\
    scs,\
    CopyLocalChanStat(CISIOV=Forced_IOV),\
    WriteChanStat(),\
    CopyLocalChanStatUPD1(CISIOV=Forced_IOV),\
    WriteChanStatUPD1()],
    memdebug=mdebug)
