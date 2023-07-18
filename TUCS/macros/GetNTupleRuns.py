######################################################################
# Get Calibration Run Numbers - Sam Meehan
#  April 2012
#
# Macro that is run to get run numbers from time span specified
# in Use worker and prints run numbers out to file 
#
# This is mean to be run to produce a file for each calibration system
# that is to be read by ntuple to produce common ntuples for calibraton runs
#
# EXAMPLE: python macros/GetNTupleRuns.py --date 2011-01-01 --enddate 2011-02-01 --cis
#
######################################################################

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

parser.add_argument('--filter', action='store', nargs=1, type=str, default=' ',
                    help='Option for LASER. Defaults to \' \' ')

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
                    
                    

args=parser.parse_args()

date          = args.date[0]
filt_pos      = args.filter
if isinstance(args.enddate, list):
    enddate   = args.enddate[0] 
else:
    enddate   = args.enddate

if args.debug:
    region    = args.region
    
if enddate:
    twoinput  = True
else:
    twoinput  = False
    
flag_cis    = args.cis
flag_laser  = args.laser
flag_cesium = args.cesium
flag_hv  = args.hv

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals())

# Check to ensure you are running on dedicated pcata023 machine
machinename = os.uname()[1]
print machinename
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


# Find CIS files
if flag_cis:
    Use_CIS  = Use(run=date, run2=enddate, runType='CIS', TWOInput=twoinput)
    cis_runs = Use_CIS.GetRunList()
    print cis_runs
    
    cis_file = open(CommonDir+'/CIS_runs',"w+")
    for run in cis_runs:
        cis_file.write( str(run[0]) )
        cis_file.write( '\n' )
    cis_file.close()


# Find Laser files
if flag_laser:
    Use_LAS    = Use(run=date, run2=enddate, filter=filt_pos, runType='Las',TWOInput=twoinput)
    laser_runs = Use_LAS.GetRunList()
    print laser_runs
    
    laser_file = open(CommonDir+'/Las_runs',"w+")
    for run in laser_runs:
        laser_file.write( str(run[0]) )
        laser_file.write( '\n' )
    laser_file.close()
    
# Find High Voltage files - NOTE: these are just laser files but for uniformity we make it separate
if flag_hv:
    Use_LAS = Use(run=date, run2=enddate, filter=filt_pos, runType='Las',TWOInput=twoinput)
    hv_runs = Use_LAS.GetRunList()
    print hv_runs
    
    hv_file = open(CommonDir+'HV_runs',"w+")
    for run in hv_runs:
        hv_file.write( str(run[0]) )
        hv_file.write( '\n' )
    hv_file.close()


# Find Cesium files
if flag_cesium:
    Use_Cs        = Use(run=date, run2=enddate, runType='cesium',cscomment='',keepOnlyActive=True, TWOInput=twoinput)
    cesium_runs = Use_Cs.GetRunList()
    print cesium_runs
    
    cesium_file = open(CommonDir+'/cesium_runs',"w+")
    for run in cesium_runs:
        cesium_file.write( str(run[0]) )
        cesium_file.write( '\n' )
    cesium_file.close()

