############################################################ 
# Translate bundle of ntuples from specified period of time
#   Sam Meehan - April 2012
#
# Macro that finds all runs in a given date range and then
# feeds these runs into the translator serially
############################################################

##
#
#  EXAMPLE COMMAND to translate CIS ntuples between given dates if you already have gotten
#  the group of runs you want to translate : 
#
#  python macros/TranslateNTupleGroup.py --date 2011-01-01 --enddate 2011-02-01 --cis
#
#  if you have not already used the GetNTupleRuns.py command to make the above list of runs
#  then you must use the --getruns flag to run this command before translating
#
#  python macros/TranslateNTupleGroup.py --date 2011-01-01 --enddate 2011-02-01 --cis --getruns
#
#  To run these commands in the backgrounds to allow you to log off or clos your laptop, use
#  the nohup command as (without the "<>" carrots):
#
#  nohup <command_above> &> LOG &
#
#
#
import argparse
import os.path

parser = argparse.ArgumentParser(description='Macro used to get calibration \
                    runs for all systems')

parser.add_argument('--date', action='store', nargs=1, type=str, default='2012-01-01',
                    required=True, help='Select runs to use. Preferred formats: \
                    1) list of integers: [194834, 194733] \
                    2) starting date as a string (takes from there to present):\
                       \'YYYY-MM-DD\' \
                    3) runs X days, or X months in the past as string: \
                       \'-28 days\' or \'-2 months\' \
                    EX: --date 2011-10-01 or --date \'-28 days\' ')
                    
parser.add_argument('--enddate', action='store', nargs=1, type=str, default='',
                    help='Select the enddate for the runs you wish to use if you \
                    want to specify an interval in the past. Accepted format is \
                    \'YYYY-MM-DD\' EX: --enddate 2012-02-01')

parser.add_argument('--debug', action='store_true', default=False,
                    help='This is a switch that speeds computation time by only retrieving \
                    N-Tuple and Database information from the regions specified. \
                    NOTE: The plots produced when this option is selected will NOT \
                    HAVE the correct LASER corrections (which require the entire \
                    TileCal to be used).')
                    
parser.add_argument('--cis', action='store_true', default=False,
                    help='Set this if you want to show cis calibrations')
                    
parser.add_argument('--laser', action='store_true', default=False,
                    help='Set this if you want to show laser calibrations')
                    
parser.add_argument('--hv', action='store_true', default=False,
                    help='Set this if you want to show high voltage calibrations')
                    
parser.add_argument('--cesium', action='store_true', default=False,
                    help='Set this if you want to show cesium calibrations')
    
parser.add_argument('--getruns', action='store_true', default=False,
                    help='Set this if you need to run the macro to get the runs \
                    numbers for the dates you want to translate')
                    
                    

args=parser.parse_args()

date          = args.date[0]
if isinstance(args.enddate, list):
    enddate   = args.enddate[0] 
else:
    enddate   = args.enddate

debugflag = args.debug
    
if enddate:
    twoinput  = True
else:
    twoinput  = False
    
flag_cis    = args.cis
flag_laser  = args.laser
flag_hv     = args.hv
flag_cesium = args.cesium

flag_getruns = args.getruns

# Check to ensure you are running on dedicated pcata023 machine
machinename = os.uname()[1]
print 'Your machine is ',machinename
if machinename != 'pcata023':
    print '------------------------------------------------------------------------'
    print 'THIS PROGRAM MUST BE RUN ON pcata023. This is the dedicated TUCS machine. '
    print 'If you do not have access, email samuel.meehan@cern.ch.'
    print '<<<<<< Exiting >>>>>>'
    print '------------------------------------------------------------------------'
    sys.exit(0)
# make output directory if not already present
CommonDir = '/tucs/CommonNTuples'
cmd = 'mkdir '+CommonDir
os.system(cmd)


# Get all runs and put then in the Tucs/CommonNTupleOutput directory
if flag_getruns:
    getntuplelists = 'python macros/GetNTupleRuns.py --date '+str(date)+' --enddate '+str(enddate)+' --cis --laser --cesium --hv'
    print getntuplelists
    os.system(getntuplelists)


# open file with CIS ntuple list, loop over run numbers and feed each into translator
if flag_cis:
    print 'TRANSLATING CIS FILES'
    cis_file = open(CommonDir+'/CIS_runs',"r+")
    cis_runs = cis_file.readlines()
    for run in cis_runs:
        run = run.split('\n')[0]
        translate = 'python macros/Make_Common_NTuple.py --run '+str(run)+' --runtype \'CIS\' '
        print translate
        if not debugflag:
            os.system(translate)


# open file with Laser ntuple list, loop over run numbers and feed each into translator
if flag_laser:
    print 'TRANSLATING Laser FILES'
    las_file = open(CommonDir+'/Las_runs',"r+")
    las_runs = las_file.readlines()
    for run in las_runs:
        run = run.split('\n')[0]
        translate = 'python macros/Make_Common_NTuple.py --run '+str(run)+' --runtype \'Las\' '
        print translate
        if not debugflag:
            os.system(translate)    

# open file with High Voltage ntuple list, loop over run numbers and feed each into translator
if flag_hv:
    print 'TRANSLATING hv FILES'
    hv_file = open(CommonDir+'/HV_runs',"r+")
    hv_runs = hv_file.readlines()
    for run in hv_runs:
        run = run.split('\n')[0]
        translate = 'python macros/Make_Common_NTuple.py --run '+str(run)+' --runtype \'HV\' '
        print translate
        if not debugflag:
            os.system(translate) 

# open file with CIS ntuple list, loop over run numbers and feed each into translator
if flag_cesium:
    print 'TRANSLATING cesium FILES'
    cesium_file = open(CommonDir+'/cesium_runs',"r+")
    cesium_runs = cesium_file.readlines()
    for run in cesium_runs:
        run = run.split('\n')[0]
        translate = 'python macros/Make_Common_NTuple.py --run '+str(run)+' --runtype \'cesium\' '
        print translate
        if not debugflag:
            os.system(translate)



























