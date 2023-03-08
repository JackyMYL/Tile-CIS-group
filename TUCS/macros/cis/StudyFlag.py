#!/usr/bin/env python
# Author : Joshua Montgomery
# Date   : February 21, 2012
# """
# This macro is used to investigate which channels are failing
# a particular flag in the CISFlagProcedure.py worker.  It calls
# the worker MapFlagFailure.py, which creates a 2D histogram that
# shows the frequency with which each channel fails the flag.
# """

import os, sys
os.chdir(os.getenv('TUCS','.'))
sys.path.insert(0, 'src')
from oscalls import *
import Get_Consolidation_Date
import argparse
import itertools
import datetime

parser = argparse.ArgumentParser(description=
'Plots the time stability of ADC channels either selected \n \
by the user, or are characterized by one or more \n \
user-specified CIS quality flags or COOL ADC Bits. \n \
Channels fitting the user-specified criteria are also \n \
printed in text form, and two or more of those outputs \n \
can be compared to find the common channels.', 
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

parser.add_argument('--ldate', action='store', nargs='+', type=int, default=0,
                    help=
'Allows you to select runs to use \n \
by their actual run number. \n \
Run numbers should be separated by whitespace \n \
EX: --ldate 183009 183166 183367 \n ')

parser.add_argument('--maintdate', action='store', nargs = '?', type=str, const=True,
                    help = 'This is a switch to be used when you want to investigate \n\
the CIS behavior of modules/channels since the last time they were \n\
maintenanced. When used, the functions in Get_Consolidation_Date.py \n\
will be called to first determine if the module specified with --region \n\
has been consolidated. If it has, then the arguments given to --date will \n\
be overridden. Using this option without an argument will produce plots using runs \n\
between the consolidation date and the present. You can also give this option \n\
one argument, specifying the desired end date in the form \'Month DD, YYYY\'. \n\
EX: \n\
--maintdate uses runs between the cons. date and the present \n\
--maintdate \'November 05, 2013\' uses runs between the cons. date and November 05, 2013 \n\
NOTE: In its current form, this switch only works if only one module is specified \n\
with --region \n ')

parser.add_argument('--region', action='store', nargs='*', type=str, default='',
                    required=True, help=
'Select the regions you wish to examine. \n \
Acceptable formatting is channels as they appear \n \
in the region.GetHash() format separated by spaces. \n \
Entire modules or barrels can be specified by \n \
leaving out the channel information or module and \n \
channel information respectively.\n \n \
EX: --region LBA_m22 EBC_m02_c00 EBA \n \
would produce plots for every channel in LBA22, \n \
every channel in the EBA partition, \n \
and EBC02 channel 00.\n ')
                    
parser.add_argument('--output', action='store', nargs=1, type=str, required=True,
                    help=
'Name the output folder. It is a good idea to \n \
include the approximate date of the runs you \n \
are looking at. This will be a subdirectory \n \
in your plotting directory (generally ~/Tucs/plots/). \n \
Single quotes are only necessary for folders \n \
with a space in them. \n \
EX: --output OutPutFolder or --output \'Output Folder\' \n ')
                    
parser.add_argument('--qflag', action='store', nargs=1, type=str, default=None,
                    help=
'Select one CIS Quality Flag you are interested in \n \
investigating. This can be one of 10 flags which \n \
should be a string enclosed in single quotes. \n \
Quality flags should be one of the following: \n \
\'Digital Errors\' \n \
\'Large Injection RMS\' \n \
\'Low Chi2\'\n \
\'Fail Max. Point\' \n \
\'Fail Likely Calib.\' \n \
\'Next To Edge Sample\' \n \
\'Edge Sample\' \n \
\'DB Deviation\' \n \
\'No Response\' \n \
\'Outlier\' \n \
\'Unstable\' \n \
\'all\' \n ')



parser.add_argument('--bflag', action='store', nargs='+', type=str, default=None,
                    help=
'Select one or more COOL bad-channel bit you are \n \
interested in investigating. This must be a \n \
string enclosed in single quotes -- or for more \n \
than one they should be separated by a space. \n \
Typically CIS is interested in \'No CIS calibration\' \n \
or \'Bad CIS calibration\' COOL bits. \n ')
                    
parser.add_argument('--exclude', action='store_true', default=False,
                    help=
'This is a switch that should be used when \n \
investigating CIS Quality flags. When selected \n \
to be true, this macro will retrieve only \n \
calibrations that pass other flags.\n ')

parser.add_argument('--tstab', action='store', nargs=1, type=int, default=[50],
                    help=
'This is a switch with an additional argument. \n \
It defaults to being selected, and prints \n \
time stability plots in units of ADC counts per pC \n \
for each ADC channel in either the selected region, \n \
or the regions caught by the specified flags. \n \
THE argument following flag is for the threshold: \n \
Enter an integer between 0 and 100 to indicate the \n \
threshold percentage of runs that a channel must \n \
fail to be printed out in the time \n \
stability plots and text outputs. The default \n \
value is 50%% \n \
NOTE: TO PRINT NO TIME STABILITY \n \
PLOTS, SET THRESHOLD TO GREATER THAN 100')

parser.add_argument('--caltype', action='store', nargs=1, type=str, default=['composite'],
                   help=
'Select the Calibration TYPE you wish to have \n \
plotted on the Time Stability plot. \n \
Acceptable arguments are: \n \
\'measured\' \n \
\'database\'\n \
\'both\' \n \
\'composite\' \n \
MEASURED only uses calibration values from CIS \n \
scans on /afs/. \n \
DATABASE only uses values stored in the COOL database. \n \
BOTH prints both of the above sets of plots. \n \
COMPOSITE prints one set of plots with both measured \n \
and database values plotted on the same canvas. \n \
Default is set to composite. \n ')
                   
parser.add_argument('--printopt', action='store', nargs=1, type=str, default=['Only_Chosen_Flag'],
                   help=
'Plot Printing Option. \n \
The following are accepted arguments: \n \
\'Print_All\' \n \
\'Only_All_Flags\' \n \
\'Only_Chosen_Flag\' \n \
Print_All will plot every channel in the \n \
--region option. \n \
Only_All_Flags will print every channel failing \n \
ANY of the CIS Quality Flags in --region. \n \
Only_Chosen_Flag will only print out channels in \n \
--region \n failing the specified flag for at \n \
least 50%% of the events being inspected. \n \
Defaults to Only_Chosen_Flag. \n \n')

parser.add_argument('--maskingbits', action='store_true', default=False,
					help=
'CIS Channel Masking Option. \n \
This is an optional argument that default to False. \n \
If selected, the CISBitMapper.py worker will print a \n \
status bit history for channels failing one of the \n \
four following scenarios for more than 50%% of the runs \n \
selected by --date: \n \n \
1) Fails \'No Response\' flag \n \
2) Fails \'Outlier\' flag \n \
3) Fails \'DB Deviation\' flag \n \
4) Fails \'Low Chi2\', \'Large Injection RMS\', and \'Fail Likely Calib.\' \n \n \
If used, the --qflag argument must be set to one of the \n \
flags listed above or \'all\'. If this option is left on False, \n \
CISBitMapper.py will create bit status history plots for the \n \
channels selected by the usual time stability controls (i.e., \n \
--qflag, --printopt, --exclude, etc.) \n ')

parser.add_argument('--flaglist', action='store', nargs='+', type=str, default=False,
                    required=False, help=
'Use this option to locate channels failing multiple, user- \n \
selected, flags. Once entering the desired combination of \n \
flags, the macro will produce bitmap plots for channels that fail \n \
each of the selected flags for at least the threshold percentage of runs \n \
as determined by --tstab. When using this option, the flag specified with the \n \
--qflag argument must be one of the flags in the list given to --flaglist \n \
Use the --timestab switch to produce the CIS time stability plots for \n \
these channels. \n \
EX: --flaglist \'DB Deviation\' \'Low Chi2\' \'Fail Max. Point\' \n ')

parser.add_argument('--timestab', action='store_true', default=False,
					help=
'This is an optional argument that defaults to False. \n\
If selected, CISBitMapper.py will create the time stability \n\
plots for for the same channels for which CISBitMapper.py \n \
prints a plot. There is no reason to use this option unless \n \
the --maskingbits option is used as well. \n \n')

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

parser.add_argument('--preprocessing', action='store_true', default=False,
                    help=
'Use this switch to create a list of channels that \n\
should be automatically recalibrated during a \n\
reprocessing based on the date entered. Must be \n\
used with the ldate option.\n ')

parser.add_argument('--eventline', action='store', nargs='+', type=str, default='0',
                    required=False, help=
'Select a date at which to draw a vertical line on time stability plot. \n\
This date should correspond to some event of interest. \n\
You may make many such lines \n\
This argument is not required. \n\
Argument format: \'YYYY-MM-DD\' \n\
EX: --eventline 2011-10-01 \n\
EX: --eventline \'2016-02-12\' \'2016-02-18\'\n\
To draw the line at the consolidation date, use \'Consolidation\' \n\
EX: --eventline \'Consolidation\' \n ')

parser.add_argument('--eventlabel', action='store', nargs='+', type=str,default='0', required=False,
                    help=
'Use this to add a label next to the event line \n \
that identifies and decribes the event. \n \
This argument is not required. \n \
Enter the label as a string. \n \
EX: --eventlabel \'Module No.1 consolidated\' \n ')

parser.add_argument('--meandevthreshold', action='store', nargs=1, type=str,default='0', required=False,
                    help=
'Use this to select the threshold required\n \
for the \'Mean Deviation\' TUCS flag. \n \
Runs with measured CIS constants that differ\n \
by more than this value from an ADC\'s measured\n \
CIS constant average will fail this flag. \' \n ')

parser.add_argument('--runofinterest', action='store', nargs='+', type=str,default='0', required=False,
		help=
'Use this to highlight certain runs that are\n \
of interest in the TimeStability plot. Label them by run number.\n \
Runs not found will be skipped without warning.\n \
This argument is not required\n \
Ex: --runofinterest \'292829\' \'293030\' \'293029\' \' \n ')
parser.add_argument('--maxmin', action='store_true', required=False)



args=parser.parse_args()

flaglist     = ['Digital Errors', 'Large Injection RMS', 'Low Chi2', 'Mean Deviation',
                'Fail Max. Point', 'Fail Likely Calib.', 'Next To Edge Sample', 'Stuck Bit',
                'Edge Sample', 'DB Deviation', 'No Response', 'Outlier', 'Unstable', 'all']

caltype_list = ['measured', 'database', 'both', 'composite']

print_list   = ['Print_All', 'Only_All_Flags', 'Only_Chosen_Flag']
Print_All        = False
Only_All_Flags   = False
Only_Chosen_Flag = False

if len(args.date) == 1:
    runs             = args.date[0]
elif len(args.date) == 2:
    runs             = (args.date[1], args.date[0])
else:
    print('\
    --DATE HAS TOO MANY ARGUMENTS \n \
    USING ONLY THE FIRST')
    runs             = args.date[0]

    
selected_region      = args.region
Titling_Date         = args.output[0]
ADC_Problems         = args.bflag
Exclude_Other_Flags  = args.exclude
PlotTimeStab         = float(args.tstab[0])/100
Use_Calibration_Type = args.caltype[0]
Print_Option         = args.printopt[0]
Masking_Bits         = args.maskingbits	
BitMap_TimeStab      = args.timestab
mdebug               = args.mdebug
Preprocessing        = args.preprocessing
event_line           = args.eventline 
event_label          = args.eventlabel
Flag_List            = args.flaglist
roilist              = args.runofinterest
maxmin               = args.maxmin
#MeanDevThresh        = float(args.meandevthreshold[0])



if args.meandevthreshold != '0':
    MeanDevThresh = float(args.meandevthreshold[0])
else:
    MeanDevThresh = 0.005
if PlotTimeStab > 1:
    PlotTimeStab = False
    StabThreshold = False
else:
    StabThreshold = PlotTimeStab 
    PlotTimeStab  = True
if args.ldate:
    runs = args.ldate

# Override the --date and --ldate arguments if the --maintdate option is used
if args.maintdate:
        maint_region = str(selected_region)
        maint_status = Get_Consolidation_Date.IsModCons(maint_region[2:-2])
        if maint_status == True:
            # If no argument given to --maintdate, use runs between maintenance and present:
            if isinstance(args.maintdate, bool):
                runs = Get_Consolidation_Date.GetConsDate(maint_region[2:-2])
                print('USING DATE OF CONSOLIDATION: %s' % runs)
            # If date given to --maintdate, use runs between maintenance and date specified:    
            else:
                maint_date = Get_Consolidation_Date.GetConsDate(maint_region[2:-2])
                maint_date = datetime.datetime.strptime(maint_date, '%Y-%m-%d')
                maint_date = str(maint_date.strftime("%B %d, %Y"))
                runs  = (args.maintdate, maint_date)
                print('USING DATE OF CONSOLIDATION: %s' % runs[1])
        else:
            print('MODULE NOT CONSOLIDATED. IGNORING --MAINTDATE SWITCH')

if args.flaglist:
    for i in range(len(args.flaglist)):
        if args.flaglist[i] not in flaglist:
            print('WARNING: AT LEAST ONE FLAG IN FLAG LIST IS NOT VALID. \n \
            SETTING FLAGLIST TO FALSE')
            args.flaglist = False


#################### For MapFlagFailure and SortFlag Modules ###################
if args.qflag:
    if args.qflag[0] not in flaglist:
        print('\n \n \
WARNING: SELECTED CIS QUALITY FLAG IS NOT IN THE ACCEPTED FLAG LIST. \n \
DEFAULTING TO \'DB Deviation\' \n \n ')
        flag = 'DB Deviation'
    flag     = args.qflag[0]
else:
    flag     = args.qflag

if not flag and ADC_Problems:
    adc_title = str()
    if len(ADC_Problems) > 1:
        adc_seps = []            
        for xiter in range(len(ADC_Problems)):
            adc_seps.append('_')
        adczip = zip(ADC_Problems, adc_seps)
        titlechain = itertools.chain.from_iterable(adczip)
        flag     = 'ADC_{0}'.format(adc_title.join(list(titlechain))).replace(' ', '_')
    else:
        flag     = 'ADC_{0}'.format(ADC_Problems[0]).replace(' ', '_')

if not flag and not ADC_Problems:
    raise Exception('\
\n \n ERROR: YOU MUST SELECT AT LEAST ONE COOL BIT OR CIS QUALITY FLAG.\n \
THIS IS GOING TO FAIL. \n')

########################### For TimeStability Module ###########################

if PlotTimeStab:
    Print_Time_Stability = True
    if Use_Calibration_Type not in caltype_list:
        print('\n \n \
WARNING: SELECTED CALIBRATION TYPE NOT IN ACCEPTED LIST. \n \
DEFAULTING TO \'composite\'\n \n')
        Use_Calibration_Type = 'composite'
    if Print_Option == print_list[0]:
        Print_All = True
    elif Print_Option == print_list[1]:
        Only_All_Flags = True
    elif Print_Option == print_list[2]:
        Only_Chosen_Flag = True
    else:
        print('\n \n \
WARNING: CHOSEN PRINT TYPE NOT IN ACCEPTED LIST. \n \
DEFAULTING TO \'Only_Chosen_Flag\' \n \n')
        Print_Option = 'Only_Chosen_Flag'
else:
    Print_Time_Stability = False
    
################################################################################
# THIS IS KIND OF A POINTLESS UTILITY. 
# IT WOULD BE NICE TO TURN IT INTO 
# SOMETHING THAT ALLOWS PLOT RANGES TO BE SET
Only_Good_Events = False 
################################################################################

###################### For General Purposes Function ###########################
From_StudyFlag = True
fail_chan_list = []
PlotDirectory = 'StudyFlag' 
################################################################################



#EXPERT UTILITY (MAYBE I WILL WORK THIS INTO ARGPARSE. BUT IT IS SO RARELY USED...
'''
Would you like to compare two data files? They can be in either the standard output format of this SortFlagFailure
or of MapFlagFailure.
If so enter the path of the slimmed files and the date associated with the runs
they use as strings.
To use as the first data file the output of this macro, do not assign the first path
variable. If the first rundate is left unassigned, the current date will be automatically
used. A secondpath_date is required to use this option.
''' 
Compare_Output_Files = False

FirstPath = ''
#Compare_PathList = ['/afs/cern.ch/user/j/jmontgom/public/flaglogs/01_05_2011/01_05_2011_txt/{0}/{0}_slimmed_tot.log'.format(flag),
#'/afs/cern.ch/user/j/jmontgom/public/flaglogs/01_06_2011/01_06_2011_txt/{0}/{0}_slimmed_tot.log'.format(flag)]
#Compare_PathList = [os.path.join(getResultDirectory(),'flaglogs/01_05_2011/01_05_2011_txt/{0}/{0}_slimmed_tot.log'.format(flag)),
#os.path.join(getResultDirectory(),'flaglogs/01_06_2011/01_06_2011_txt/{0}/{0}_slimmed_tot.log'.format(flag))]

#StartingDate = ''
#EndingDate   = ''

if not 'Compare_PathList' in globals():
    Compare_PathList = ['']
if Compare_PathList[0]:
    if not ('StartingDate' in globals()) or not ('EndingDate' in globals()) :
        print("Please assign a date range associated with the files in the path list")
else:
    if not ('StartingDate' in globals()) or not ('EndingDate' in globals()):
        StartingDate = ''
        EndingDate = ''
if not 'Compare_Output_Files' in globals():
    Compare_Output_Files = False
    
################################################################################
exec(open('src/load.py').read(), globals())
############### Building Use List ##############################################
cisbitmapper = CISBitMapper(all=Print_All, flagtype=flag, only_all_flags=Only_All_Flags,
                            only_chosen_flag=Only_Chosen_Flag, adc_problems=ADC_Problems,
                            plotdirectory=PlotDirectory, rundate=Titling_Date, only_good_events=Only_Good_Events,
                            maskingbits=Masking_Bits, printtimestab = BitMap_TimeStab,
                            cal_type=Use_Calibration_Type, ratio_threshold=StabThreshold, flaglist=Flag_List)

if Print_Time_Stability:
    print('PRINTING TIME STAB PLOTS')
    if Use_Calibration_Type == 'both':
        Use_Calibration_Type    = 'measured'
        Use_Calibration_Type_2  = 'database'
        print_time_stability    = TimeStability(all=Print_All, 
                                    plottimestab=PlotTimeStab, cal_type=Use_Calibration_Type,
                                    flagtype=flag, only_all_flags=Only_All_Flags,
                                    only_chosen_flag=Only_Chosen_Flag, plotdirectory=PlotDirectory,
                                    rundate=Titling_Date, exts=['png'], only_good_events=Only_Good_Events,
                                    adc_problems=ADC_Problems, preprocessing=Preprocessing)
        print_time_stability_2  = TimeStability(all=Print_All, 
                                    plottimestab=PlotTimeStab, cal_type=Use_Calibration_Type_2,
                                    flagtype=flag, only_all_flags=Only_All_Flags,
                                    only_chosen_flag=Only_Chosen_Flag, plotdirectory=PlotDirectory,
                                    rundate=Titling_Date, exts=['png'], only_good_events=Only_Good_Events,
                                    adc_problems=ADC_Problems)
    else:
        print_time_stability    = TimeStability(all=Print_All, 
                                    plottimestab=PlotTimeStab, cal_type=Use_Calibration_Type,
                                    flagtype=flag, only_all_flags=Only_All_Flags,
                                    only_chosen_flag=Only_Chosen_Flag, plotdirectory=PlotDirectory,
                                    rundate=Titling_Date, exts=['png'], only_good_events=Only_Good_Events,
                                    adc_problems=ADC_Problems, preprocessing=Preprocessing, IOV=runs)
        print_time_stability_2  = None
else:
    print_time_stability        = None
    print_time_stability_2      = None
    
stuckbithist = StuckBitHistory(only_chosen_flag=Only_Chosen_Flag, only_all_flags=Only_All_Flags, flagtype=flag, plotdirectory=PlotDirectory)
    
# if using an SQLITE file, schema is 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2'
readbchfromcool = ReadBadChFromCool(schema='OFL', tag='UPD4', Fast=True, storeADCinfo=True)
readcalfromcool = ReadCalibFromCool(schema='OFL', runType='CIS', folder='CALIB/CIS', tag='UPD4', data = 'DATA', meandev_threshold = MeanDevThresh)

u = Use(run=runs, runType='CIS', region=selected_region, preprocessing=Preprocessing)

if Preprocessing:
    print('We got a preprocessing going on!')
    print('\nIn Loop 1\n')
    Go([
        u,\
        ReadCIS(),\
        CleanCIS(), \
        readbchfromcool,\
        readcalfromcool,\
        MoreInfo(),\
        MapFlagFailure(exclude_other_flags=Exclude_Other_Flags, flagtype=flag, path1=FirstPath, 
                       rundate=Titling_Date, from_studyflag=From_StudyFlag, plotdirectory=PlotDirectory,
                       adc_problems=ADC_Problems, threshold=StabThreshold),\
        CISRecalibrateProcedure(),\
        SortFlagFailure(flagtype=flag, rundate=Titling_Date,
                        pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                        compare_files=Compare_Output_Files),\
        print_time_stability,\
	stuckbithist],
        memdebug=mdebug)
        
elif Masking_Bits:
    if flag == 'all':
        print('\nIn Loop 2\n')
        Go([
            u,\
            ReadCIS(),\
            CleanCIS(),\
            readbchfromcool,\
            readcalfromcool,\
            MoreInfo(),\
            CISFlagProcedure_modified(),\
            MapFlagFailure(exclude_other_flags=Exclude_Other_Flags, flagtype=flag, path1=FirstPath,
                           rundate=Titling_Date, from_studyflag=From_StudyFlag, plotdirectory=PlotDirectory,
                           adc_problems=ADC_Problems, threshold=StabThreshold),\
            CISRecalibrateProcedure(),\
            SortFlagFailure(flagtype=flag, path1=FirstPath, rundate=Titling_Date,
                            pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                            compare_files=Compare_Output_Files),\
            cisbitmapper,\
	    stuckbithist],
            memdebug=mdebug)

    else:
        print('\nIn Loop 3\n')
        Go([
            u,\
            ReadCIS(),\
            CleanCIS(),\
            readbchfromcool,\
            readcalfromcool,\
            MoreInfo(),\
            MapFlagFailure(exclude_other_flags=Exclude_Other_Flags, flagtype=flag, path1=FirstPath, 
                           rundate=Titling_Date, from_studyflag=From_StudyFlag, plotdirectory=PlotDirectory,
                       adc_problems=ADC_Problems, threshold=StabThreshold),\
            CISRecalibrateProcedure(),\
            SortFlagFailure(flagtype=flag, rundate=Titling_Date,
                            pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                            compare_files=Compare_Output_Files),\
            cisbitmapper,\
	    stuckbithist],
            memdebug=mdebug)

elif Flag_List:
    if flag == 'all':
        print('\nIn Loop 4\n')
        Go([
            u,\
            ReadCIS(),\
            CleanCIS(),\
            readbchfromcool,\
            readcalfromcool,\
            MoreInfo(),\
            CISFlagProcedure_modified(),\
            MapFlagFailure(exclude_other_flags=Exclude_Other_Flags, flagtype=flag, path1=FirstPath,
                           rundate=Titling_Date, from_studyflag=From_StudyFlag, plotdirectory=PlotDirectory,
                           adc_problems=ADC_Problems, threshold=StabThreshold),\
            CISRecalibrateProcedure(),\
            SortFlagFailure(flagtype=flag, path1=FirstPath, rundate=Titling_Date,
                            pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                            compare_files=Compare_Output_Files),\
            cisbitmapper,\
	    stuckbithist],
            memdebug=mdebug)

    else:
        print('\nIn Loop 5\n')
        Go([
            u,\
            ReadCIS(),\
            CleanCIS(),\
            readbchfromcool,\
            readcalfromcool,\
            MoreInfo(),\
            MapFlagFailure(exclude_other_flags=Exclude_Other_Flags, flagtype=flag, path1=FirstPath, 
                           rundate=Titling_Date, from_studyflag=From_StudyFlag, plotdirectory=PlotDirectory,
                       adc_problems=ADC_Problems, threshold=StabThreshold),\
            CISRecalibrateProcedure(),\
            SortFlagFailure(flagtype=flag, rundate=Titling_Date,
                            pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                            compare_files=Compare_Output_Files),\
            cisbitmapper,\
	    stuckbithist],
            memdebug=mdebug)

else:
    if flag == 'all':
        if FirstPath:
            print('\nIn Loop 6\n')
            #print 'Entering loop 1'
            Go([
                u,\
                ReadCIS(),\
                CleanCIS(), \
                readbchfromcool,\
                readcalfromcool,\
                MoreInfo(),\
                CISFlagProcedure_modified(),\
                MapFlagFailure(exclude_other_flags=Exclude_Other_Flags, flagtype=flag, path1=FirstPath,
                               rundate=Titling_Date, from_studyflag=From_StudyFlag, plotdirectory=PlotDirectory, 
                               adc_problems=ADC_Problems, threshold=StabThreshold),\
                CISRecalibrateProcedure(),\
                SortFlagFailure(flagtype=flag, path1=FirstPath, rundate=Titling_Date,
                                pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                                compare_files=Compare_Output_Files),\
                print_time_stability,\
                print_time_stability_2,\
                cisbitmapper,\
	        stuckbithist],
                memdebug=mdebug)
        
        else:
            #print 'Entering loop 2'
            print('\nIn Loop 7\n')
            Go([
                u,\
                ReadCIS(),\
                CleanCIS(), \
                readbchfromcool,\
                readcalfromcool,\
                MoreInfo(),\
                CISFlagProcedure_modified(),\
                MapFlagFailure(exclude_other_flags=Exclude_Other_Flags, flagtype=flag, path1=FirstPath,
                           rundate=Titling_Date, from_studyflag=From_StudyFlag, plotdirectory=PlotDirectory,
                           adc_problems=ADC_Problems, threshold=StabThreshold),\
                CISRecalibrateProcedure(),\
                SortFlagFailure(flagtype=flag, rundate=Titling_Date,
                        pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                            compare_files=Compare_Output_Files),\
                print_time_stability,\
                print_time_stability_2,\
                cisbitmapper,\
	        stuckbithist],
                memdebug=mdebug)

    else:

        if FirstPath:
            #print 'Entering loop 3'
            print('\nIn Loop 8\n')
            Go([
                u,\
                ReadCIS(),\
                CleanCIS(), \
                readbchfromcool,\
                readcalfromcool,\
                MoreInfo(),\
                MapFlagFailure(exclude_other_flags=Exclude_Other_Flags, flagtype=flag, path1=FirstPath,
                           rundate=Titling_Date, from_studyflag=From_StudyFlag, plotdirectory=PlotDirectory,
                               adc_problems=ADC_Problems, threshold=StabThreshold),\
                CISRecalibrateProcedure(),\
                SortFlagFailure(flagtype=flag, path1=FirstPath, rundate=Titling_Date,
                                pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                                compare_files=Compare_Output_Files),\
                print_time_stability,\
                print_time_stability_2,\
                cisbitmapper,\
	        stuckbithist],
                memdebug=mdebug)
        else:
            print('\nIn Loop 9\n')
            #print 'Entering loop 4'
            Go([
                u,\
                ReadCIS(),\
                CleanCIS(), \
                readbchfromcool,\
                readcalfromcool,\
                MoreInfo(),\
                MapFlagFailure(exclude_other_flags=Exclude_Other_Flags, flagtype=flag, path1=FirstPath, 
                           rundate=Titling_Date, from_studyflag=From_StudyFlag, plotdirectory=PlotDirectory,
                               adc_problems=ADC_Problems, threshold=StabThreshold),\
                CISRecalibrateProcedure(),\
                SortFlagFailure(flagtype=flag, rundate=Titling_Date,
                            pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                                compare_files=Compare_Output_Files),\
                print_time_stability,\
                print_time_stability_2,\
                cisbitmapper,\
	        stuckbithist],
                memdebug=mdebug)

