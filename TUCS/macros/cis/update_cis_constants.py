#!/usr/bin/env python
# Author:   Christopher Tunnell  <tunnell@hep.uchicago.edu>
# Updated:  Andrew Hard          <ahard@uchicago.edu>
#
# Create an SQLite file with new CIS constants. This should be perfomed 
# following maintenance periods, after modules are unmasked, or when large 
# numbers of channels are failing the 1% deviation flag in the CIS procedure. 
# To target specific channels, change the conditions in the CISFlagProcedure.py
# or WriteDB.py workers.
#
# April 11, 2011
#
# Modified: Joshua Montgomery <Joshua.J.Montgomery@gmail.com>
#
# Can now be run directly from the command line, like the rest of CIS.
#
# March 05, 2012

import argparse
import os.path
import itertools
import gc

parser = argparse.ArgumentParser(description=
'Creates the tileSqlite.db file to update the \n \
CIS Constants in the COOL Calibration database \n \
(the cis lin folder).',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--date', action='store', nargs='+', type=str, default=['-28 days'],
                    help=
'Select runs to use. If you want to use \n\
a list of run numbers instead, use --ldate. \n\
You have to select SOMETHING for --date, \n\
but it is irrelevant if --ldate is used \n\
(There is probably a better way about that) \n\
NOTE: Default for performing channel updates \n\
is \'- 28 days\' \n\
Preferred formats: \n\
1) starting date as a string (takes from there \n\
to present). EX: \'YYYY-MM-DD\' \n\
2) runs X days, or X months in the past as string: \n\
   \'-28 days\' or \'-2 months\' \n\
3) All of the runs between two dates. \n\
   This should use two arguments \n\
   each of this form: \'Month DD, YYYY\' \n\
EX: --date 2011-10-01 or --date \'-28 days\' \n\
    --date \'January 01, 2011\' \'February 11, 2011\' \n ')


parser.add_argument('--ldate', action='store', nargs='+', type=int, default=0,
                    help=
'Allows you to select runs to use \n \
by their actual run number. \n \
Run numbers should be separated by whitespace \n\
EX: --ldate 183009 183166 183367 \n ')


parser.add_argument('--maintregions', action='store', nargs='*', type=str, default='',
                    help=
'Select the regions of the detector which \n \
have received maintenance, or otherwise \n\
are targeted for recalibartion. \n\
Acceptable formatting is channels as they appear \n\
in the region.GetHash() format separated by spaces. \n\
Entire modules or barrels can be specified by \n\
leaving out the channel information or module and \n\
channel information respectively.\n \n\
EX: --region LBA_m22 EBC_m02_c00 EBA \n\
would produce plots for every channel in LBA22, \n\
every channel in the EBA partition, \n\
and EBC02 channel 00.\n ')

parser.add_argument('--default', action='store_true', default=False,
                    help=
'This option helps target the recalibration procedure in \n\
workers/cis/CISRecalibrateProcedure.py (line 274). If selected \n\
It will target channels with default calibrations for a \n\
recalibration. This can be used in conjunction with --maintregions \n\
and --deviation. This is sort of a sledgehammer of a tool \n\
and I prefer instead to use StudyFlag.py to look for channels \n\
which the COOL bit (--bflag) of \'No CIS calibration\' and then \n\
evaluate each of them individually. That way I can compile a \n\
more controlled list, and then drop that into the --maintregions \n\
flag. \n \n')

parser.add_argument('--deviation', action='store_true', default=False,
                    help=
'This option helps target the recalibration procedure in \n\
workers/cis/CISRecalibrateProcedure.py (line 274). If selected \n\
It will target channels with deviations from their DB values. \n\
This can be used in conjunction with --maintregions \n\
and --default. This is sort of a sledgehammer of a tool \n\
and I prefer instead to use StudyFlag.py to look for channels \n\
which the COOL bit (--bflag) of \'Bad CIS calibration\' or the --qflag \n\
of \'DB Deviation\' and then evaluate each of them individually. \n\
That way I can compile a more controlled list, and then drop \n\
that into the --maintregions flag. \n \n')

parser.add_argument('--forcedregions', action='store', nargs='*', type=str, default='',
                    help=
'Select the regions of the detector which \n\
have received maintenance, or otherwise \n\
are targeted for recalibartion. \n\
Acceptable formatting is channels as they appear \n\
in the region.GetHash() format separated by spaces. \n\
Entire modules or barrels can be specified by \n\
leaving out the channel information or module and \n\
channel information respectively.\n \n\
EX: --region LBA_m22 EBC_m02_c00 EBA \n\
would produce plots for every channel in LBA22, \n\
every channel in the EBA partition, \n\
and EBC02 channel 00.\n \n')

parser.add_argument('--recalALL', action='store_true', default=False,
                    help=
'Be Careful With This Switch! \n\
Selecting it will create a tileSqlite.db file \n\
with new calibrations for EVERY CHANNEL in the \n\
detector. Most calibration updates should be \n\
targeted to unmasked, repaired, or outlier channels. \n\
This is referenced in the CISRecalibrateProcedure.py \n\
worker. Inspecting these Sqlite files can \n\
be instructive, but it is crucial that they \n\
not be mistakenly uploaded to the COOL Database! \n \n')


parser.add_argument('--mdebug', action='store_true', default=False,
                    help=
'This is a switch that passes the memory debug flag to \n\
the Go.py module. The result is two plots detailing \n\
the memory consumption of this macro. The first is a \n\
plot that is the percent memory used as a function of \n\
time -- color coded by which worker is running during \n\
that time. The second is a histogram showing the \n\
total memory consumption used by each worker. These are \n\
all printed in the Tucs/ResourceLogs/ directory \n\
(which is created if not already in place). The plots, \n\
along with the supporting text files are categorized \n\
by the unique process ID of each instance this macro is \n\
called.\n \n')


parser.add_argument('--iov', action='store', nargs=1, type=int, default=0, help=
'This allows the user to manually set the starting IOV for \n\
CIS recalibrations. In order to avoid a back-insertion error, \n\
the start of the new IOV must be later than the start of the \n\
previous one. Must be in the form of a six-digit run number \n \n')

parser.add_argument('--defaulttargets', action='store', nargs='*', type=str, default='',
                    help=
"Enter channels that have been selected for defaulting. \n\
Normally should only be used in tandem with the reprocessing \n\
option below. For quotidian CIS constant updates, default \n\
channels are determined automatically by the CIS recalibrate \n\
procedure worker. Note the difference between this option adn...\n \n")

parser.add_argument('--reprocessing', action='store', default=False, help=
"This is a switch that disables the CopyDBConstants.py worker. \n\
Instead, WriteDB.py will create a new IOV to a local SQLite \n\
file named tileSqlite.db. This switch defaults to 'False' since \n\
since default CIS recalibrations ought to copy calibration \n\
constants from COOL. \n \n")

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
    
recalibrate_all      = args.recalALL
mdebug               = args.mdebug
maintenanced_modules = args.maintregions
default              = args.default
deviation            = args.deviation
forced               = args.forcedregions
forced_regions       = []
iov                  = args.iov
reprocessing         = args.reprocessing
defaulttargets       = args.defaulttargets

if iov != 0:
	iovstart = iov[0]
	print iovstart	
	
if maintenanced_modules:
    MaintSel = True
else:
    MaintSel = False

if forced:
    displaystr = '\n '
    for el in forced:
        displaystr = displaystr+'**'+str(el)+'\n '
#        if el not in maintenanced_modules:
#            raise Exception('\n \
#            ALL FORCED CHANNELS MUST ALSO BE MEMBERS OF THE \n \
#            MAINTENANCED MODULES LIST.')
            
    response = False
    answered = False
    prompt   = ' \n \
    You have chosen to FORCE the recalibration of the following channels: \n \
    {0} \n \
    DO NOT PROCEED UNLESS THE FOLLOWING HAVE BEEN SATISFIED: \n \n \
    1) YOU HAVE A GOOD PHYSICAL REASON FOR DOING THIS \n \
       Note that this is bypassing IMPORTANT QUALITY CHECKS for the events \n \
       in the selected channels. \n \
    2) DO NOT use this option just because entering channels \n \
       into the maintenance module argument did not have the desired outcome. \n \
    3) BEFORE USING THIS OPTION inspect the plots for these channels using: \n \
          i) StudyFlag.py to look for unreasonable noise or recent shifts \n \
         ii) Combined_Calib_Response.py to cross-check with other systems \n \
        iii) The Detector Ocupancy Plots as final confirmation that the \n \
             abnormal calibration values are real and effect physics \n \n \
       THESE STEPS ARE IMPORTANT in determining whether the CIS values are \n \
       legitimate and should be used DESPITE failing quality flags. \n \n \
    Do you wish to force these channels? [y]/[n] \n'.format(displaystr)
    
    while not answered:
        response = raw_input(prompt)
        if response not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        elif response == 'y' or ans == 'Y':
            response = True
            answered = True
        elif response == 'n' or ans == 'N':
            response = False
            answered = True
    
    if response:
        for region in forced:
            forced_regions.append('TILECAL_{0}'.format(region))
    elif not response:
        forced_regions = []

    print 'Forced Regions: ', forced_regions
    
    
#################### USER INPUT SCARING THEM ###################################
############# DELETE ENTRIES IF USER CHANGES MIND ##############################

#
# Experts only below.
#
import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
details = False
debug = False

use = Use(run=runs, useDateProg=True, runType='CIS', verbose=False)
readcis = ReadCIS()

readbchfromcool = ReadBadChFromCool(schema='OFL', folder='/TILE/OFL02/STATUS/ADC', tag='UPD1', Fast=True)
readcalfromcool = ReadCalibFromCool(schema='OFL', runType='CIS', folder='CALIB/CIS', tag='UPD1')


# This list will determine which channels are recalibrated in WriteDB.py using the information from CISRecalibrateProcedure.py
list_of_targets = []

if not globals().has_key('selected_region'):
    selected_region = ''

if details:
    plotmodulechannel = PlotModuleChannel(runType1='CIS', parameter1='calibratableRegion', text1='Low-gain', invert1=True,\
                          runType2='CIS', parameter2='calibratableRegion', text2='High-gain', invert2=True)
    compareprocedures = CompareProcedures('CIS')
    getscans          = GetScans()
    showcisscans      = ShowCISSCans()
else:
    plotmodulechannel = compareprocedures = getscans = showcisscans = None

if debug:
    debugprint = Print()
    debugsavetree = SaveTree()
else:
    debugprint = debugsavetree = None

if iov == 0:
    writedb = CISWriteDB(forcedreg = forced_regions)
else:
    writedb = CISWriteDB(forcedreg = forced_regions, runNumber = iovstart)
    print 'using IOV=%s' % iovstart

if reprocessing:
    writedb = CISWriteDB(forcedreg = forced_regions, runNumber = iovstart, 
                      reprocessingstep = reprocessing, deftargets=defaulttargets)
    print 'Reprocessing step {0} commencing, using IOV={1}'.format(reprocessing, iovstart)
elif iov==0:
    writedb = CISWriteDB(forcedreg = forced_regions)
else:
    writedb = CISWriteDB(forcedreg = forced_regions, runNumber = iovstart)
    print 'using IOV=%s' % iovstart

if reprocessing:
    Go([use,\
        SelectRegion(selected_region),\
        readcis,\
        CleanCIS(),\
        readbchfromcool,\
        readcalfromcool,\
        CISRecalibrateProcedure(all=recalibrate_all, forced=forced_regions, MReg=MaintSel,
                                Defaults=default, Deviations=deviation),\
        CISFlagProcedure_modified(dbCheck=False),\
        plotmodulechannel,\
        IsEntireModuleBad(),\
        IsEntirePartitionBad(),\
        plotmodulechannel,\
        compareprocedures,\
        getscans,\
        showcisscans,\
        writedb,\
        debugprint,\
        debugsavetree],
        memdebug=mdebug)
        
else:
    Go([use,\
        SelectRegion(selected_region),\
        readcis,\
        CleanCIS(),\
        readbchfromcool,\
        readcalfromcool,\
        CISRecalibrateProcedure(all=recalibrate_all, forced=forced_regions, MReg=MaintSel,
                                Defaults=default, Deviations=deviation),\
        CISFlagProcedure_modified(dbCheck=False),\
        plotmodulechannel,\
        IsEntireModuleBad(),\
        IsEntirePartitionBad(),\
        plotmodulechannel,\
        compareprocedures,\
        getscans,\
        showcisscans,\
        CopyDBConstants('CIS', recreate=True),\
        writedb,\
        debugprint,\
        debugsavetree],
        memdebug=mdebug)
        


