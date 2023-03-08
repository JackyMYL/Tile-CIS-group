#!/usr/bin/env python
# Author: Joshua Montgomery <Joshua.Montgomery@gmail.com>
#
# This creates the CIS public plot that shows the channel deviation after
# many months.  
#
# October 31, 2011
#

import argparse

parser = argparse.ArgumentParser(description=
'This CIS Macro generates all of the current CIS \n \
Public Plots. Including most history plots. \n',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--date', action='store', nargs='+', type=str, default='2012-01-01',
                    required=True, help=
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
    
parser.add_argument('--listdate', action='store', nargs='+', type=int, default=0,
                    help=
'Allows you to select runs to use \n \
by their actual run number. \n \
Run numbers should be separated by whitespace \n \
EX: --listdate 183009 183166 183367 \n ')

parser.add_argument('--ndate', action='store', nargs='+', type=str, default=[''],
                    help=
  'Select a second set of runs to use. \n \
NOTE:  Earlier runs should be \'--date\' \n \
or \'--listdate\', while more recent runs \n \
should be \'--ndate\' or \'secondlistdate\'. \n \
This is necessary to make the History Plots \n \
Preferred formats are identical to --date. \n \n')

parser.add_argument('--secondlistdate', action='store', nargs='+', type=int, default=0,
                    help=
'Allows you to select runs to use \n \
for the second set of runs \n \
by their actual run number. \n \
Run numbers should be separated by whitespace \n \
EX: --ldate 183009 183166 183367. \n \n')

parser.add_argument('--region', action='store', nargs='*', type=str, default='',
                    help=
' NOTE: IT IS VERY UNLIKELY YOU WISH TO \n \
RUN THIS MACRO ON ANYTHING LESS THAN THE \n \
ENTIRE DETECTOR. DEFAULTS TO '' \n \
Select the regions you wish to examine. \n \
Acceptable formatting is channels as they appear \n \
in the region.GetHash() format separated by spaces. \n \
Entire modules or barrels can be specified by \n \
leaving out the channel information or module and \n \
channel information respectively.\n \n \
EX: --region LBA_m22 EBC_m02_c00 EBA \n \
would produce plots for every channel in LBA22, \n \
every channel in the EBA partition, \n \
and EBC02 channel 00. \n ')

parser.add_argument('--history', action='store', nargs=2, type=float,
                    default=False,
                    help=
'This flag will print both history plots: \n \
1) Shows the public plot of the percentage \n \
change of individual channels CIS constants \n \
in the entire detector between the two dates \n \
specified. This is two histograms. \n \
2) Makes 8 2D Histograms, one for each gain in \n \
each partition of the detector, showing the \n \
percentage change in CIS constants by region \n \
in the partitions. \n \
For this to run it needs both --date AND \n \
--ndate to be specified. \n \
The arguments following this flag allow you \n \
to set the min and max for the Z axis \n \
in the 2D histograms. I would recommend \n \
starting with -0.5 and 0.5. \n \
EX: --history -0.5 0.5 \n \n')

parser.add_argument('--cmap', action='store_true', default=False,
                    help=
'This switch will generate Calibration Constant \n \
maps for every partition and gain. Similar to the \n \
--history option except it uses only the runs \n \
specified by --date and the scale is in absolute units. \n \
At the moment this is just a boolean, and the scale is \n \
determined automatically in the worker. \n \n')

parser.add_argument('--flagplots', action='store_true', default = False,
                    help=
'This switch will use the the FlagPlots.py \n \
worker to generate time-stamped performance plots showing \n \
the number of ADC\'s failing select TUCS Quality Flags\n \
for each run over the specific run period. \n \n')

parser.add_argument('--coolplots', action='store_true', default = False,
                    help=
'This switch will use the the CoolPlots.py \n \
worker to generate time-stamped plots showing \n \
the number of ADC\'s with select COOL database satuses\n \
for each run over the specific run period. \n \n')

parser.add_argument('--rmsplots', action='store_true', default = False,
                    help=
'This switch will use the the RMSPlots.py \n \
worker to generate histograms regarding the \n \
time period specific CIS constant RMS and RMS/mean\n \
of all channels in the detector. \n \n')

parser.add_argument('--gcals', action='store_true', default=False,
                    help=
'This switch generates two histograms showing \n \
the global calibration distributions in high \n \
and low gain for the entire detector over the \n \
runs specified with --date. \n \
It defaults to False and needs no arguments. \n \n')

parser.add_argument('--tune', action='store_true',
                    default=False,
                    help=
'This switch generates plots from both \n \
the tune_rms_chi2 and tune_maxpoint_likelycalib \n \
worker modules. This is very computationally intensive \n \
and somewhat depreciated it. It generates the plots \n \
and histograms used to determine the cuts for the \n \
Large Injection RMS, Low Chi2, Max. Point, and \n \
Likely Calibration quality flags. \n \n')

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

parser.add_argument('--mean', action='store_true', default=False,
                    help=
'Creates a plot of the run by run mean of the \n\
calibration constants for the entire detector. \n\
The plot also displays a single channel for \n\
comparison whose constant is within one half \n\
of a standard deviation of the mean. \n \n')

parser.add_argument('--lowmem', action='store_true', default=False,
                    help=
'For really really long run selections, use the lowmem \n\
option.Most of these plotting tools were not really designed \n\
to run over more than 4 months of info but they should \n\
be able to handle at least a year. \n')

parser.add_argument('--datelabel', action='store', nargs='+', type=str, default='\t',
                     help=
'write a label for the date range on the plot \n')

parser.add_argument('--rmruns', action='store_true',  default=False,
                     help=
'remove runs if necessary for creating CIS Public Plots. Runs to remove can \n\
 be listed in the specified section within this macro \n')

args = parser.parse_args()

rm_bad_runs = args.rmruns

datelabel = args.datelabel[0]

if len(args.date) == 1:
    runs                  = args.date[0]
elif len(args.date) == 2:
    runs                  = (args.date[1], args.date[0])
else:
    print('\
    --DATE HAS TOO MANY ARGUMENTS \n \
    USING ONLY THE FIRST')
    runs                  = args.date[0]
    
if len(args.ndate) == 1:
    runs2                 = args.ndate[0]
elif len(args.date) == 2:
    runs2                 = (args.ndate[1], args.ndate[0])
else:
    print('\
    --NDATE HAS TOO MANY ARGUMENTS \n \
    USING ONLY THE FIRST')
    runs2                 = args.ndate[0]

selected_region           = args.region
Calib_Const_Regions       = args.cmap
Calibration_Distributions = args.gcals
Tune_RMS_Chi2             = args.tune
Tune_MaxPoint_LikelyCalib = args.tune
mdebug                    = args.mdebug
lowmem                    = args.lowmem
    

if args.mean:
    Detector_Stability = True
    
    if len(args.date) == 1:
        from_date = args.date[0]
        to_date = ''
        
    if len(args.date) == 2:
        from_date = args.date[0]
        to_date = args.date[1]

else:
    Detector_Stability = False


if args.history:
    Hist_Percent_Public  = True
    Hist_Percent_Regions = True
    SetScaleMin          = args.history[0]
    SetScaleMax          = args.history[1]
    if not runs2 and not args.secondlistdate:
        raise Exception('\n \
        argument: --HISTORY REQUIRES TWO RUN INTERVALS/DATES \n \
        TO BE SELECTED. TRY AGAIN ;)')
    
    
else:
    Hist_Percent_Public  = False
    Hist_Percent_Regions = False
    
if args.flagplots:
    Flag_Plot = True
else:
    Flag_Plot = False

if args.coolplots:
    Cool_Plot = True
else:
    Cool_Plot = False

if args.rmsplots:
    RMS_Plot = True
else:
    RMS_Plot = False

if args.listdate:
    runs  = args.listdate
if args.secondlistdate:
    runs2 = args.secondlistdate


import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!


"""
step 4
dump debug information
"""
debug = False

#
#  Experts only below.
#

macros_2run_interval = [Hist_Percent_Public, Hist_Percent_Regions] ## This list is for easy addition of other two-run macros

macros_DB_check = [Calibration_Distributions, Tune_RMS_Chi2, Tune_MaxPoint_LikelyCalib, Detector_Stability]

getscans = None # initialize for multiple macro uses


if debug:
    pr = Print()
    s = SaveTree()
else:
    pr = None
    s = None
    
## Logic ##

if Detector_Stability:
    detectortimestability = DetectorTimeStability(dateLabel=datelabel,mindate=from_date, maxdate=to_date)
else:
    detectortimestability            = None
    
if Hist_Percent_Public:
    hist_percent_public = HistoryPlot('CIS',dateLabel=datelabel)
else:
    hist_percent_public = None

if Hist_Percent_Regions:
    hist_percent_regions = HistPlotRegions('CIS', setmax=SetScaleMax, setmin=SetScaleMin)
else:
    hist_percent_regions = None

if Calib_Const_Regions:
    calib_const_regions = CISConstantRegions()
else:
    calib_const_regions = None

if Flag_Plot:
    flag_plots = FlagPlots()
else:
    flag_plots = None

if Cool_Plot:
    cool_plots = CoolPlots()
else:
    cool_plots = None

if RMS_Plot:
    rms_plots = RMSPlots(dateLabel=datelabel)
else:
    rms_plots = None

if Calibration_Distributions:
    calibration_distributions = CalibDist(dateLabel=datelabel)
else:
    calibration_distributions = None
    
if lowmem:
    cis_recalibrate_procedure = CISRecalibrateProcedure_Modified(all=True)
else:
    cis_recalibrate_procedure = CISRecalibrateProcedure(all=True)
     
if Tune_RMS_Chi2:
   tune_rms_chi2 = TuneCuts(probbad=True) ## Don't change this from True ...keeping it as a switch for now.
else:
   tune_rms_chi2 = None

if Tune_MaxPoint_LikelyCalib:
   tune_maxpoint_likelycalib = TuneCutsMaxPointLikelyCalib()
else:
   tune_maxpoint_likelycalib = None

if Tune_MaxPoint_LikelyCalib or Tune_RMS_Chi2:
    getscans = GetScans(all=True)

# Normal  
readbchfromcool = ReadBadChFromCool(schema='OFL', tag='UPD4', Fast=True, storeADCinfo=True)
readcalfromcool = ReadCalibFromCool(schema='OFL', runType='CIS', folder='CALIB/CIS', tag='UPD4', data = 'DATA')

#if Flag_Plot:
#    readbchfromcool = ReadBadChFromCool(schema='OFL', tag='UPD4', Fast=False, storeADCinfo=True)

readbchfromcool = ReadBadChFromCool(schema='OFL', tag='UPD4', Fast=True, storeADCinfo=True)

# Use for normal CIS updates
#readcalfromcool = ReadCalibFromCool(schema='OFL', runType='CIS', folder='CALIB/CIS', tag='UPD1', data = 'DATA',meandev_threshold = updateThreshold)

# Use for reprocessing as instructed by Sasha Solodkov
# readcalfromcool = ReadCalibFromCool(schema='sqlite://;schema=tileSqlite_first_IOV.db;dbname=CONDBR2', runType='CIS', 
#                                    folder='CALIB/CIS', tag='RUN2-HLT-UPD1-00', data = 'DATA')

################## Parse what runs is set to ###########################
u1 = Use(run=runs, runType='CIS')

####START OF OPTIONAL RUN REMOVAL --Andrew, 2018 ###########
print(rm_bad_runs)
if rm_bad_runs:
    badruns = []

    run_numbers = [run[0] for run in u1.runs]
    print("Run Numbers:", run_numbers)
    step = 1  #set i so that only every ith run number is used, default 1 uses every run.
    every_ith_run_number = run_numbers[0::step]
    to_remove = []


    print("Every ith run:", every_ith_run_number)
    #this for loop omits every run except those in every_ith_run_number list
    for run in u1.runs:

        if run[0] not in every_ith_run_number:
            to_remove.append(run[0])
    to_remove += badruns
    u1.RemoveBadRuns(to_remove)
    print("Runs After Removal")
    for run in u1.runs:
	    print(run)

##### END OF OPTION RUN REMOVAL--Andrew, 2018  #############

if 'runs2' in globals():
    u2 = Use(run=runs2, runType='CIS', region=selected_region)
#########################################################################

use_two_run_interval = False
database_check = False
for macro in macros_2run_interval:
    if macro:
        use_two_run_interval = True

for macro in macros_DB_check:
    if macro:
        database_check = True


### building The Go lists ##
if use_two_run_interval:
    Go([\
        u1,\
        ReadCIS(),\
        CleanCIS(),\
        readbchfromcool,\
        readcalfromcool,\
        CISFlagProcedure_modified(dbCheck=database_check),\
        getscans,\
        cis_recalibrate_procedure,\
        pr,\
        hist_percent_public,\
        hist_percent_regions,\
        calib_const_regions,\
        flag_plots,\
        cool_plots,\
        rms_plots,\
        calibration_distributions,\
        tune_rms_chi2,\
        tune_maxpoint_likelycalib,\
        Clear(),\
        u2,\
        ReadCIS(),\
        CleanCIS(),\
        readbchfromcool,\
        readcalfromcool,\
        CISFlagProcedure_modified(dbCheck=database_check),\
        hist_percent_public,\
        hist_percent_regions,\
        pr,\
        s],
        memdebug=mdebug)
        #RUN2=True)
else:
    Go([\
        u1,\
        ReadCIS(),\
        CleanCIS(),\
        readbchfromcool,\
        readcalfromcool,\
        CISFlagProcedure_modified(dbCheck=database_check),\
        getscans,\
#        cis_recalibrate_procedure,\
        hist_percent_public,\
        hist_percent_regions,\
        calib_const_regions,\
        flag_plots,\
        cool_plots,\
        rms_plots,\
        calibration_distributions,\
        tune_rms_chi2,\
        tune_maxpoint_likelycalib,\
        detectortimestability,\
        pr,\
        s],
        memdebug=mdebug)
       # RUN2=True)


#Go([\
#    u1,\
#    ReadCIS(),\
#    CleanCIS(),\
#    readbchfromcool,\
#    readcalfromcool,\
#    CISFlagProcedure_modified(dbCheck=database_check),\
#    getscans,\
#    CISRecalibrateProcedure(all=True),\
#    calibration_distributions,\
#    detectortimestability,\
#    pr,\
#    s],
#    memdebug=mdebug)

