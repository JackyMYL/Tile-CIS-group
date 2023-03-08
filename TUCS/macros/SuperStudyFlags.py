###########################################################################
# !/usr/bin/env python                                                    #
# Author : Jeff Shahinian <jeffrey.david.shahinian@cern.ch>               #
# Date   : October, 2013                                                  #
#                                                                         #
# This macro is used to identify and compare channels failing the Laser   #
# and CIS quality flags. It is a blatant ripoff of the existing macros    #
# that do this for their respective calibration system.                   #
#                                                                         #
#                                                                         #
###########################################################################

import os, sys
os.chdir(os.getenv('TUCS','.'))
sys.path.insert(0, 'src')
from oscalls import *
import Get_Consolidation_Date
import argparse
import itertools
import datetime

parser = argparse.ArgumentParser(description=
'Identifies channels failing the Laser and CIS \n \
quality flags.',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--calibsys', action='store', nargs=1, type=str, default='Both',
                    required=True, help='Select which calibration system(s) to look at.Options: \n \
1. --calibsys \'CIS\' \n \
2. --calibsys \'Laser\' \n \
3. --calibsys \'Both\' \n \
Defaults to \'Both\' \n ')

parser.add_argument('--date', action='store', nargs='+', type=str, default='2012-01-01',
                    required=True, help='Select runs to use. If you want to use \n \
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
                    help='Allows you to select runs to use \n \
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

parser.add_argument('--region', action='store', nargs='+', type=str, default=None,
                    required=True, help='Select the regions you wish to examine. Acceptable \n\
formatting is channels as they appear in the region.GetHash() \n\
format separated by spaces. Entire modules or barrels can be specified by \n\
leaving out the channel information or module and channel information \n\
respectively.  \n\
EX: --region LBA_m22 EBC_m02_c00 EBA \n\
would produce plots for every channel in LBA22, every channel \n\
in the EBA partition, and EBC02 channel 00. \n ' )
               
parser.add_argument('--output', action='store', nargs=1, type=str, required=True,
                    help='Name the output folder. It is a good idea to \n \
include the approximate date of the runs you \n \
are looking at. This will be a subdirectory \n \
in your plotting directory (generally ~/Tucs/plots/). \n \
Single quotes are only necessary for folders \n \
with a space in them. \n \
EX: --output OutPutFolder or --output \'Output Folder\' \n ')
                    
parser.add_argument('--cisflag', action='store', nargs=1, type=str, default=None,
                    help='Select one CIS Quality Flag you are interested in \n \
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
                    help='Select one or more COOL bad-channel bit you are \n \
interested in investigating. This must be a \n \
string enclosed in single quotes -- or for more \n \
than one they should be separated by a space. \n \
Typically CIS is interested in \'No CIS calibration\' \n \
or \'Bad CIS calibration\' COOL bits. \n ')
                   
parser.add_argument('--exclude', action='store_true', default=False,
                    help='This is a switch that should be used when \n \
investigating CIS Quality flags. When selected \n \
to be true, this macro will retrieve only \n \
calibrations that pass other flags.\n ')

parser.add_argument('--tstab', action='store', nargs=1, type=int, default=[50],
                    help='This is a switch with an additional argument. \n \
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
PLOTS, SET THRESHOLD TO GREATER THAN 100 \n ')

parser.add_argument('--caltype', action='store', nargs=1, type=str, default=['composite'],
                   help='Select the Calibration TYPE you wish to have \n \
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
                   help='Plot Printing Option. \n \
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
Defaults to Only_Chosen_Flag. \n \n ')

parser.add_argument('--maskingbits', action='store_true', default=False,
					help='CIS Channel Masking Option. \n \
This is an optional argument that default to False. \n \
If selected, the CISBitMapper.py worker will print a \n \
status bit history for channels failing one of the \n \
four following scenarios for more than 50%% of the runs \n \
selected by --date: \n \n \
1) Fails \'No Response\' flag \n \
2) Fails \'Outlier\' flag \n \
3) Fails \'DB Deviation\' flag \n \
4) Fails \'Low Chi2\', \'Large Injection RMS\', and \'Fail Likely Calib.\' \n \n \
If used, the --cisflag argument must be set to one of the \n \
flags listed above or \'all\'. If this option is left on False, \n \
CISBitMapper.py will create bit status history plots for the \n \
channels selected by the usual time stability controls (i.e., \n \
--cisflag, --printopt, --exclude, etc.) \n ')

parser.add_argument('--flaglist', action='store', nargs='+', type=str, default=False,
                    required=False, help='Use this option to locate channels failing multiple, user- \n \
selected, flags. Once entering the desired combination of \n \
flags, the macro will produce bitmap plots for channels that fail \n \
each of the selected flags for at least the threshold percentage of runs \n \
as determined by --tstab. Use the --timestab switch to produce \n \
the CIS time stability plots for these channels. \n \
EX: --flaglist \'DB Deviation\' \'Low Chi2\' \'Fail Max. Point\' \n ')

parser.add_argument('--timestab', action='store_true', default=False,
					help='This is an optional argument that defaults to False. \n\
If selected, CISBitMapper.py will create the time stability \n\
plots for for the same channels for which CISBitMapper.py \n \
prints a plot. There is no reason to use this option unless \n \
the --maskingbits option is used as well. \n \n ')

parser.add_argument('--preprocessing', action='store_true', default=False,
                    help='Use this switch to create a list of channels that \n\
should be automatically recalibrated during a \n\
reprocessing based on the date entered. Must be \n\
used with the ldate option.\n ')

parser.add_argument('--eventline', action='store', nargs='+', type=str, default='0',
                    required=False, help='Select a date at which to draw a vertical line on time stability plot. \n\
This date should correspond to some event of interest. \n\
This argument is not required. \n\
Argument format: \'YYYY-MM-DD\' \n\
EX: --eventline 2011-10-01 \n\
To draw the line at the consolidation date, use \'Consolidation\' \n\
EX: --eventline \'Consolidation\' \n ')

parser.add_argument('--eventlabel', action='store', nargs=1, type=str,default='0', required=False,
                    help='Use this to add a label next to the event line \n \
that identifies and decribes the event. \n \
This argument is not required. \n \
Enter the label as a string. \n \
EX: --eventlabel \'Module No.1 consolidated\' \n ')


#Arguments for Laser
parser.add_argument('--lasflag', action='store', nargs='+', type=str, default='all',
                    help='Specify the flag you want to study (default --flag all)\n \
--flag fast: will look for fast drifting channels\n \
--flag jump: will look for channels with gain jump\n \
--flag erratic: will look for channels with erratic gain\n \
--flag hl: will look for channels with uncompatible response to high and low gain runs\n \
--flag noResponse: will look for channels with no Laser response (currently not working) \n \
--flag all: will look for channels failing any of the flags \n \
NOTE with the hl option we cannot specify a set of runs with unique gain in the --region argument \n ')

parser.add_argument('--includeDQ', action='store_true', default=False,
                    help='This is a switch that passes the include DQ flag to getLaserFlags.py. \n\
When it is selected the events already flagged by the Data Quality will be \n\
considered in the analysis. By default these events are discarded. \n\
Usage: --includeDQ \n ')


parser.add_argument('--filter', action='store', nargs=1, type=str, default=' ',
                    help='Option for LASER. Defaults to \' \' \n ')

parser.add_argument('--debug', action='store_true', default=False,
                    help='This is a switch that speeds computation time by only retrieving \n\
N-Tuple and Database information from the regions specified. \n\
NOTE: The plots produced when this option is selected will NOT \n\
HAVE the correct LASER corrections (which require the entire \n\
TileCal to be used). \n')
                    
parser.add_argument('--expert', action='store_true', default=False,
                    help='This is a switch that allows a local tileSqlite.db file \n\
to be used for the Las_REFs, and local laser ntuples to be used.\n\
The filename for the Las_REF file should be \'tileSqlite.db\' \n\
and path for the laser ntuples should be \'/data/ntuples/las\' \n ')

parser.add_argument('--mdebug', action='store_true', default=False,
                    help='This is a switch that passes the memory debug flag to \n\
the Go.py module. The result is two plots detailing the memory \n\
consumption of this macro. The first is a plot that is the percent\n\
memory used as a function of time -- color coded by which worker \n\
is running during that time. The second is a histogram showing the \n\
total memory consumption used by each worker. These are all \n\
printed in the Tucs/ResourceLogs/ directory (which is created \n\
if not already in place). The plots, along with the supporting \n\
text files are categorized by the unique process ID of each instance \n\
this macro is called. \n ')

################################################################################################################################################
################################################################################################################################################
args=parser.parse_args()
calibsys = str(args.calibsys)

# Initialize CIS/Laser common variables:
selected_region = args.region

if len(args.date) == 1:
    runs = args.date[0]
elif len(args.date) == 2:
    runs = (args.date[1], args.date[0])
else:
    print '\
    --DATE HAS TOO MANY ARGUMENTS \n \
    USING ONLY THE FIRST'
    runs = args.date[0]

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
            print 'USING DATE OF CONSOLIDATION: %s' % runs
	# If date given to --maintdate, use runs between maintenance and date specified:    
        else:
            maint_date = Get_Consolidation_Date.GetConsDate(maint_region[2:-2])
            maint_date = datetime.datetime.strptime(maint_date, '%Y-%m-%d')
            maint_date = str(maint_date.strftime("%B %d, %Y"))
            runs  = (args.maintdate, maint_date)
            print 'USING DATE OF CONSOLIDATION: %s' % runs[1]
    else:
        print 'MODULE NOT CONSOLIDATED. IGNORING --MAINTDATE SWITCH'

mdebug = args.mdebug


#CIS Initialization:
if calibsys[2:-2] == 'CIS' or calibsys[2:-2] == 'Both':

    flaglist     = ['Digital Errors', 'Large Injection RMS', 'Low Chi2', 
                   'Fail Max. Point', 'Fail Likely Calib.', 'Next To Edge Sample', 
                   'Edge Sample', 'DB Deviation', 'No Response', 'Outlier', 'Unstable', 'all']

    caltype_list = ['measured', 'database', 'both', 'composite']

    print_list   = ['Print_All', 'Only_All_Flags', 'Only_Chosen_Flag']
    Print_All        = False
    Only_All_Flags   = False
    Only_Chosen_Flag = False

    Titling_Date         = args.output[0]
    ADC_Problems         = args.bflag
    Exclude_Other_Flags  = args.exclude
    PlotTimeStab         = float(args.tstab[0])/100
    Use_Calibration_Type = args.caltype[0]
    Print_Option         = args.printopt[0]
    Masking_Bits         = args.maskingbits
    BitMap_TimeStab      = args.timestab
    Preprocessing        = args.preprocessing
    event_line           = args.eventline[0] 
    event_label          = args.eventlabel[0]
    Flag_List            = args.flaglist

    if PlotTimeStab > 1:
        PlotTimeStab = False
        StabThreshold = False
    else:
        StabThreshold = PlotTimeStab
        PlotTimeStab  = True    

    if args.flaglist:
        for i in range(len(args.flaglist)):
            if args.flaglist[i] not in flaglist:
                print 'WARNING: AT LEAST ONE FLAG IN FLAG LIST IS NOT VALID. \n \
                SETTING FLAGLIST TO FALSE'
                args.flaglist = False


#################### For MapFlagFailure and SortFlag Modules ###################
    if args.cisflag:
        if args.cisflag[0] not in flaglist:
            print '\n \n \
    WARNING: SELECTED CIS QUALITY FLAG IS NOT IN THE ACCEPTED FLAG LIST. \n \
    DEFAULTING TO \'DB Deviation\' \n \n '
            flag = 'DB Deviation'
        flag     = args.cisflag[0]
    else:
        flag     = args.cisflag

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
            print '\n \n \
    WARNING: SELECTED CALIBRATION TYPE NOT IN ACCEPTED LIST. \n \
    DEFAULTING TO \'composite\'\n \n'
            Use_Calibration_Type = 'composite'
        if Print_Option == print_list[0]:
            Print_All = True
        elif Print_Option == print_list[1]:
            Only_All_Flags = True
        elif Print_Option == print_list[2]:
            Only_Chosen_Flag = True
        else:
            print '\n \n \
    WARNING: CHOSEN PRINT TYPE NOT IN ACCEPTED LIST. \n \
    DEFAULTING TO \'Only_Chosen_Flag\' \n \n'
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
            print "Please assign a date range associated with the files in the path list"
    else:
        if not ('StartingDate' in globals()) or not ('EndingDate' in globals()):
            StartingDate = ''
            EndingDate = ''
    if not 'Compare_Output_Files' in globals():
        Compare_Output_Files = False
    
    exec(open('src/load.py').read(), globals()) # don't remove this!
    
############### Building CIS Use List ##############################################
    cisbitmapper = CISBitMapper(all=Print_All, flagtype=flag, only_all_flags=Only_All_Flags,
                                only_chosen_flag=Only_Chosen_Flag, adc_problems=ADC_Problems,
                                plotdirectory=PlotDirectory, rundate=Titling_Date, only_good_events=Only_Good_Events,
                                maskingbits=Masking_Bits, printtimestab = BitMap_TimeStab,
                                cal_type=Use_Calibration_Type, ratio_threshold=StabThreshold, flaglist=Flag_List)

    if Print_Time_Stability:
        print 'PRINTING TIME STAB PLOTS'
        if Use_Calibration_Type == 'both':
            Use_Calibration_Type    = 'measured'
            Use_Calibration_Type_2  = 'database'
            print_time_stability    = TimeStability(all=Print_All, 
                                        plottimestab=PlotTimeStab, cal_type=Use_Calibration_Type,
                                        flagtype=flag, only_all_flags=Only_All_Flags,
                                        only_chosen_flag=Only_Chosen_Flag, plotdirectory=PlotDirectory,
                                        rundate=Titling_Date, exts=['eps'], only_good_events=Only_Good_Events,
                                        adc_problems=ADC_Problems, preprocessing=Preprocessing)
            print_time_stability_2  = TimeStability(all=Print_All, 
                                        plottimestab=PlotTimeStab, cal_type=Use_Calibration_Type_2,
                                        flagtype=flag, only_all_flags=Only_All_Flags,
                                        only_chosen_flag=Only_Chosen_Flag, plotdirectory=PlotDirectory,
                                        rundate=Titling_Date, exts=['eps'], only_good_events=Only_Good_Events,
                                        adc_problems=ADC_Problems)
        else:
            print_time_stability    = TimeStability(all=Print_All, 
                                        plottimestab=PlotTimeStab, cal_type=Use_Calibration_Type,
                                        flagtype=flag, only_all_flags=Only_All_Flags,
                                        only_chosen_flag=Only_Chosen_Flag, plotdirectory=PlotDirectory,
                                        rundate=Titling_Date, exts=['eps'], only_good_events=Only_Good_Events,
                                        adc_problems=ADC_Problems, preprocessing=Preprocessing, IOV=runs)
            print_time_stability_2  = None
    else:
        print_time_stability        = None
        print_time_stability_2      = None

    Read_CIS                    = ReadCIS()
    Clean_CIS                   = CleanCIS()
    More_Info                   = MoreInfo()
    CIS_Flag_Procedure_Modified = CISFlagProcedure_modified()
    CIS_Recalibrate_Procedure   = CISRecalibrateProcedure()

    Map_Flag_Failure = MapFlagFailure(exclude_other_flags=Exclude_Other_Flags, flagtype=flag, path1=FirstPath, 
                                      rundate=Titling_Date, from_studyflag=From_StudyFlag, plotdirectory=PlotDirectory,
                                      adc_problems=ADC_Problems, threshold=StabThreshold)

    Sort_Flag_Failure   = SortFlagFailure(flagtype=flag, rundate=Titling_Date,
                                          pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                                          compare_files=Compare_Output_Files)

    Sort_Flag_Failure_2 = SortFlagFailure(flagtype=flag, path1=FirstPath, rundate=Titling_Date,
                                          pathlist=Compare_PathList, startdate=StartingDate, enddate=EndingDate,
                                          compare_files=Compare_Output_Files)
    
# if using an SQLITE file, schema is 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2'
    readbchfromcool = ReadBadChFromCool(schema='OFL', tag='UPD4', Fast=True, storeADCinfo=True)
    readcalfromcool = ReadCalibFromCool(schema='OFL', runType='CIS', folder='CALIB/CIS', tag='UPD4')

    Use_CIS = Use(run=runs, runType='CIS', region=selected_region, preprocessing=Preprocessing)

################################################################################################################################################
################################################################################################################################################
# Laser Initialization
if calibsys[2:-2] == 'Laser' or calibsys[2:-2] == 'Both':

    #selected_region_las = []
    las_region          = ''
    filt_pos            = args.filter
    includeDQ           = args.includeDQ
    lasflag             = args.lasflag
    plotdirectory       = args.output[0]           

    #for dedug purposes use only part of the detector
    if args.debug:
        las_region = args.region    
    
    if args.expert:
        if not os.path.exists('/data/ntuples/las'):
            print ' \n \n WARNING: NO LOCAL LASER NTUPLES FOUND. USING NTUPLES ON /AFS/. \n \n'
        if not os.path.isfile('tileSqlite.db'):
            print ' \n \n WARNING: NO LOCAL TILESQLITE.DB FILE FOUND. USING COOL FOR LAS_REFS \n \n'

    exec(open('src/load.py').read(), globals()) # don't remove this!


######################### BUILD LASER USE LIST ########################################
    Use_LAS = Use(run=runs, filter=filt_pos, runType='Las', region=las_region)

    if args.expert and os.path.exists('/data/ntuples/las'):
       Read_Laser = ReadLaser(processingDir='/data/ntuples/las', diode_num_lg=0, diode_num_hg=0, verbose=True)
       print '\n \n WARNING: USING LOCAL LASER NTUPLES \n \n'
    else:
       Read_Laser = ReadLaser(diode_num_lg=0, diode_num_hg=0, verbose=True)
   


    if args.expert and os.path.isfile('tileSqlite.db'):
        print '\n \n WARNING: USING LOCAL SQLITE FILE FOR LAS_REFS \n \n'    
        COOL_Cal_Las  = ReadCalibFromCool(schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                                       folder='/TILE/OFL02/CALIB/CES',
                                       runType='Las_REF',
                                       tag='RUN2-HLT-UPD1-01', verbose=True)
    else:
        COOL_Cal_Las  = ReadCalibFromCool(schema='OFL',
                                       folder='CALIB/CES',
                                       runType='Las_REF',
                                       tag='UPD4', verbose=True)

    COOL_Cal_ChannelProblems  = ReadBchFromCool(schema='OFL',
                                                tag='UPD4',
                                                Fast=True,
                                                storeADCinfo=True)

    Laser_Fibre_Shifts        = getFiberShifts(n_sig=2.0, n_iter=5,verbose=False)

    Clean_Laser = CleanLaser()

    Get_PMT_Shifts = getPMTShiftsObsolete()

    Get_Laser_Flags = getLaserFlags(selected_region, includeDQ, plotdirectory=plotdirectory, flag=lasflag)
    
 
######################### BUILD GO LIST ########################################
if calibsys[2:-2] == 'CIS':
    Use_LAS                     = None
    Read_Laser                  = None
    Clean_Laser                 = None
    COOL_Cal_Las                = None
    COOL_Cal_ChannelProblems    = None
    Laser_Fibre_Shifts          = None
    Get_PMT_Shifts              = None
    Get_Laser_Flags             = None

if calibsys[2:-2] == 'Laser':
    Use_CIS                     = None
    Read_CIS                    = None
    Clean_CIS                   = None
    readbchfromcool             = None
    readcalfromcool             = None
    More_Info                   = None
    Map_Flag_Failure            = None
    CIS_Recalibrate_Procedure   = None
    Sort_Flag_Failure           = None
    Sort_Flag_Failure_2         = None
    print_time_stability        = None
    print_time_stability_2      = None
    CIS_Flag_Procedure_Modified = None
    cisbitmapper                = None
    # Define this variable to get inside the first laser 'Go' list in the case
    # where only Laser was specified with --calibsys:
    Preprocessing = True

if calibsys[2:-2] == 'Both':
    Super_Map_Flag            = SuperMapFlag(cis_flag=flag, las_flag=lasflag, plotdirectory=plotdirectory, region=selected_region)
else:
    Super_Map_Flag            = None


if Preprocessing:
    print 'We got a preprocessing going on!'
    Go([
        Use_CIS,\
        Read_CIS,\
        Clean_CIS, \
        readbchfromcool,\
        readcalfromcool,\
        More_Info,\
        Map_Flag_Failure,\
        CIS_Recalibrate_Procedure,\
        Sort_Flag_Failure,\
        print_time_stability],
        memdebug=mdebug)
    Go([
        Use_LAS,                  # BUILD LASER RUN LIST
        Read_Laser,               # LOAD LASER EVENT NTUPLES
        Clean_Laser,              # CUT OUT BAD LASER EVENTS
        COOL_Cal_Las,             # LOAD LASER DATABASE CALIBRATIONS
        COOL_Cal_ChannelProblems, # LOAD PROBLEMS FROM COOL
        Laser_Fibre_Shifts,       # GENERATE FIBRE LASER CORRECTIONS
        Get_PMT_Shifts,           # GENERATE PMT LASER CORRECTIONS
        Get_Laser_Flags,          # GET THE PMT LASER FLAGS
        Super_Map_Flag],          # MAP THE BAD CIS AND LASER CHANNELS
        memdebug=mdebug)          # TURNS ON/OFF MEMORY DEBUGGING
        
elif Masking_Bits:
    if flag == 'all':
        Go([
            Use_CIS,\
            Read_CIS,\
            Clean_CIS,\
            readbchfromcool,\
            readcalfromcool,\
            More_Info,\
            CIS_Flag_Procedure_Modified,\
            Map_Flag_Failure,\
            CIS_Recalibrate_Procedure,\
            Sort_Flag_Failure_2,\
            cisbitmapper],
            memdebug=mdebug)
        Go([
            Use_LAS,                  # BUILD LASER RUN LIST
            Read_Laser,               # LOAD LASER EVENT NTUPLES
            Clean_Laser,              # CUT OUT BAD LASER EVENTS
            COOL_Cal_Las,             # LOAD LASER DATABASE CALIBRATIONS
            COOL_Cal_ChannelProblems, # LOAD PROBLEMS FROM COOL
            Laser_Fibre_Shifts,       # GENERATE FIBRE LASER CORRECTIONS
            Get_PMT_Shifts,           # GENERATE PMT LASER CORRECTIONS
            Get_Laser_Flags,          # GET THE PMT LASER FLAGS
            Super_Map_Flag],          # MAP THE BAD CIS AND LASER CHANNELS
            memdebug=mdebug)          # TURNS ON/OFF MEMORY DEBUGGING

    else:
        Go([
            Use_CIS,\
            Read_CIS,\
            Clean_CIS,\
            readbchfromcool,\
            readcalfromcool,\
            More_Info,\
            Map_Flag_Failure,\
            CIS_Recalibrate_Procedure,\
            Sort_Flag_Failure,\
            cisbitmapper],
            memdebug=mdebug)
        Go([
            Use_LAS,                  # BUILD LASER RUN LIST
            Read_Laser,               # LOAD LASER EVENT NTUPLES
            Clean_Laser,              # CUT OUT BAD LASER EVENTS
            COOL_Cal_Las,             # LOAD LASER DATABASE CALIBRATIONS
            COOL_Cal_ChannelProblems, # LOAD PROBLEMS FROM COOL
            Laser_Fibre_Shifts,       # GENERATE FIBRE LASER CORRECTIONS
            Get_PMT_Shifts,           # GENERATE PMT LASER CORRECTIONS
            Get_Laser_Flags,          # GET THE PMT LASER FLAGS
            Super_Map_Flag],          # MAP THE BAD CIS AND LASER CHANNELS
            memdebug=mdebug)          # TURNS ON/OFF MEMORY DEBUGGING

elif Flag_List:
    if flag == 'all':
        Go([
            Use_CIS,\
            Read_CIS,\
            Clean_CIS,\
            readbchfromcool,\
            readcalfromcool,\
            More_Info,\
            CIS_Flag_Procedure_Modified,\
            Map_Flag_Failure,\
            CIS_Recalibrate_Procedure,\
            Sort_Flag_Failure_2,\
            cisbitmapper],
            memdebug=mdebug)
        Go([
            Use_LAS,                  # BUILD LASER RUN LIST
            Read_Laser,               # LOAD LASER EVENT NTUPLES
            Clean_Laser,              # CUT OUT BAD LASER EVENTS
            COOL_Cal_Las,             # LOAD LASER DATABASE CALIBRATIONS
            COOL_Cal_ChannelProblems, # LOAD PROBLEMS FROM COOL
            Laser_Fibre_Shifts,       # GENERATE FIBRE LASER CORRECTIONS
            Get_PMT_Shifts,           # GENERATE PMT LASER CORRECTIONS
            Get_Laser_Flags,          # GET THE PMT LASER FLAGS
            Super_Map_Flag],          # MAP THE BAD CIS AND LASER CHANNELS
            memdebug=mdebug)          # TURNS ON/OFF MEMORY DEBUGGING

    else:
        Go([
            Use_CIS,\
            Read_CIS,\
            Clean_CIS,\
            readbchfromcool,\
            readcalfromcool,\
            More_Info,\
            Map_Flag_Failure,\
            CIS_Recalibrate_Procedure,\
            Sort_Flag_Failure,\
            cisbitmapper],
            memdebug=mdebug)
        Go([
            Use_LAS,                  # BUILD LASER RUN LIST
            Read_Laser,               # LOAD LASER EVENT NTUPLES
            Clean_Laser,              # CUT OUT BAD LASER EVENTS
            COOL_Cal_Las,             # LOAD LASER DATABASE CALIBRATIONS
            COOL_Cal_ChannelProblems, # LOAD PROBLEMS FROM COOL
            Laser_Fibre_Shifts,       # GENERATE FIBRE LASER CORRECTIONS
            Get_PMT_Shifts,           # GENERATE PMT LASER CORRECTIONS
            Get_Laser_Flags,          # GET THE PMT LASER FLAGS
            Super_Map_Flag],          # MAP THE BAD CIS AND LASER CHANNELS
            memdebug=mdebug)          # TURNS ON/OFF MEMORY DEBUGGING

else:
    if flag == 'all':
        if FirstPath:
            print 'Entering loop 1'
            Go([
                Use_CIS,\
                Read_CIS,\
                Clean_CIS, \
                readbchfromcool,\
                readcalfromcool,\
                More_Info,\
                CIS_Flag_Procedure_Modified,\
                Map_Flag_Failure,\
                CIS_Recalibrate_Procedure,\
                Sort_Flag_Failure_2,\
                print_time_stability,\
                print_time_stability_2,\
                cisbitmapper],
                memdebug=mdebug)
            Go([
                Use_LAS,                  # BUILD LASER RUN LIST
                Read_Laser,               # LOAD LASER EVENT NTUPLES
                Clean_Laser,              # CUT OUT BAD LASER EVENTS
                COOL_Cal_Las,             # LOAD LASER DATABASE CALIBRATIONS
                COOL_Cal_ChannelProblems, # LOAD PROBLEMS FROM COOL
                Laser_Fibre_Shifts,       # GENERATE FIBRE LASER CORRECTIONS
                Get_PMT_Shifts,           # GENERATE PMT LASER CORRECTIONS
                Get_Laser_Flags,          # GET THE PMT LASER FLAGS
                Super_Map_Flag],          # MAP THE BAD CIS AND LASER CHANNELS
                memdebug=mdebug)          # TURNS ON/OFF MEMORY DEBUGGING
        
        else:
            print 'Entering loop 2'
            Go([
                Use_CIS,\
                Read_CIS,\
                Clean_CIS, \
                readbchfromcool,\
                readcalfromcool,\
                More_Info,\
                CIS_Flag_Procedure_Modified,\
                Map_Flag_Failure,\
                CIS_Recalibrate_Procedure,\
                Sort_Flag_Failure,\
                print_time_stability,\
                print_time_stability_2,\
                cisbitmapper],
                memdebug=mdebug)
            Go([
                Use_LAS,                  # BUILD LASER RUN LIST
                Read_Laser,               # LOAD LASER EVENT NTUPLES
                Clean_Laser,              # CUT OUT BAD LASER EVENTS
                COOL_Cal_Las,             # LOAD LASER DATABASE CALIBRATIONS
                COOL_Cal_ChannelProblems, # LOAD PROBLEMS FROM COOL
                Laser_Fibre_Shifts,       # GENERATE FIBRE LASER CORRECTIONS
                Get_PMT_Shifts,           # GENERATE PMT LASER CORRECTIONS
                Get_Laser_Flags,          # GET THE PMT LASER FLAGS
                Super_Map_Flag],          # MAP THE BAD CIS AND LASER CHANNELS
                memdebug=mdebug)          # TURNS ON/OFF MEMORY DEBUGGING

    else:
        if FirstPath:
            print 'Entering loop 3'
            Go([
                Use_CIS,\
                Read_CIS,\
                Clean_CIS, \
                readbchfromcool,\
                readcalfromcool,\
                More_Info,\
                Map_Flag_Failure,\
                CIS_Recalibrate_Procedure,\
                Sort_Flag_Failure_2,\
                print_time_stability,\
                print_time_stability_2,\
                cisbitmapper],
                memdebug=mdebug)
            Go([
                Use_LAS,                  # BUILD LASER RUN LIST
                Read_Laser,               # LOAD LASER EVENT NTUPLES
                Clean_Laser,              # CUT OUT BAD LASER EVENTS
                COOL_Cal_Las,             # LOAD LASER DATABASE CALIBRATIONS
                COOL_Cal_ChannelProblems, # LOAD PROBLEMS FROM COOL
                Laser_Fibre_Shifts,       # GENERATE FIBRE LASER CORRECTIONS
                Get_PMT_Shifts,           # GENERATE PMT LASER CORRECTIONS
                Get_Laser_Flags,          # GET THE PMT LASER FLAGS
                Super_Map_Flag],          # MAP THE BAD CIS AND LASER CHANNELS
                memdebug=mdebug)          # TURNS ON/OFF MEMORY DEBUGGING
        else:
            print 'Entering loop 4'
            Go([
                Use_CIS,\
                Read_CIS,\
                Clean_CIS, \
                readbchfromcool,\
                readcalfromcool,\
                More_Info,\
                Map_Flag_Failure,\
                CIS_Recalibrate_Procedure,\
                Sort_Flag_Failure,\
                print_time_stability,\
                print_time_stability_2,\
                cisbitmapper],
                memdebug=mdebug)
            Go([
                Use_LAS,                  # BUILD LASER RUN LIST
                Read_Laser,               # LOAD LASER EVENT NTUPLES
                Clean_Laser,              # CUT OUT BAD LASER EVENTS
                COOL_Cal_Las,             # LOAD LASER DATABASE CALIBRATIONS
                COOL_Cal_ChannelProblems, # LOAD PROBLEMS FROM COOL
                Laser_Fibre_Shifts,       # GENERATE FIBRE LASER CORRECTIONS
                Get_PMT_Shifts,           # GENERATE PMT LASER CORRECTIONS
                Get_Laser_Flags,          # GET THE PMT LASER FLAGS
                Super_Map_Flag],          # MAP THE BAD CIS AND LASER CHANNELS
                memdebug=mdebug)          # TURNS ON/OFF MEMORY DEBUGGING
