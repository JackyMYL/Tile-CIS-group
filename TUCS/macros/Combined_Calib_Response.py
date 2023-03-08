#!/usr/bin/env python
# Author : Joshua Montgomery (Inspired by Henric.py)
# Date   : February 17, 2012
#
# This macro generates plots comparing the fractional response of a TileCal Channel
# as measured by the Laser, Cesium, and Charge Injection Systems

import argparse
import os.path

parser = argparse.ArgumentParser(description='Plots channel response as measured \
                    by Laser, High Voltage, Cesium, and Charge Injection combined')

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

parser.add_argument('--region', action='store', nargs='+', type=str, default=None,
                    required=True, help='Select the regions you wish to examine. Acceptable \
                    formatting is channels as they appear in the region.GetHash() \
                    format separated by spaces. Entire modules or barrels can be specified by \
                    leaving out the channel information or module and channel information \
                    respectively.  \
                    EX: --region LBA_m22 EBC_m02_c00 EBA \
                    would produce plots for every channel in LBA22, every channel \
                    in the EBA partition, and EBC02 channel 00.')

parser.add_argument('--output', action='store', nargs=1, type=str, default=None,
                    help='Name the output folder. This will be a subdirectory in \
                    your plotting directory (generally ~/Tucs/plots/) \
                    Single quotes are only necessary for folders with a space \
                    in them. EX: --output OutPutFolder or --output \'Output Folder\' ')

parser.add_argument('--filter', action='store', nargs=1, type=str, default=' ',
                    help='Option for LASER. Defaults to \' \' ')

parser.add_argument('--debug', action='store_true', default=False,
                    help='This is a switch that speeds computation time by only retrieving \
                    N-Tuple and Database information from the regions specified. \
                    NOTE: The plots produced when this option is selected will NOT \
                    HAVE the correct LASER corrections (which require the entire \
                    TileCal to be used).')
                    
parser.add_argument('--expert', action='store_true', default=False,
                    help='This is a switch that allows a local tileSqlite.db file\
                    to be used for the Las_REFs, and local laser ntuples to be used.\
                    The filename for the Las_REF file should be \'tileSqlite.db\' \
                    and path for the laser ntuples should be \'/data/ntuples/las\'')

parser.add_argument('--mdebug', action='store_true', default=False,
                    help='This is a switch that passes the memory debug flag to \
                    the Go.py module. The result is two plots detailing the memory \
                    consumption of this macro. The first is a plot that is the percent\
                    memory used as a function of time -- color coded by which worker \
                    is running during that time. The second is a histogram showing the \
                    total memory consumption used by each worker. These are all \
                    printed in the Tucs/ResourceLogs/ directory (which is created \
                    if not already in place). The plots, along with the supporting \
                    text files are categorized by the unique process ID of each instance \
                    this macro is called.')

args=parser.parse_args()

mdebug        = args.mdebug
region        = ''
plot_regions  = args.region
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
    
if not args.output:
    OutFolder = args.output
else:
    OutFolder = args.output[0]
    
if args.expert:
    if not os.path.exists('/data/ntuples/las'):
        print ' \n \n WARNING: NO LOCAL LASER NTUPLES FOUND. USING NTUPLES ON /AFS/. \n \n'
    if not os.path.isfile('tileSqlite.db'):
        print ' \n \n WARNING: NO LOCAL TILESQLITE.DB FILE FOUND. USING COOL FOR LAS_REFS \n \n'

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

######################### BUILD GO LIST ########################################

Use_LAS       = Use(run=date, run2=enddate, filter=filt_pos, runType='Las', region=region,
                    TWOInput=twoinput)

Use_Cs        = Use(run=date, run2=enddate, runType='cesium', region=region,
                       cscomment='',keepOnlyActive=True, TWOInput=twoinput)

Use_CIS       = Use(run=date, run2=enddate, runType='CIS', region=plot_regions,
                    TWOInput=twoinput)

if args.expert and os.path.exists('/data/ntuples/las'):
   Read_Laser = ReadLaser(processingDir='/data/ntuples/las', diode_num_lg=0, diode_num_hg=0, verbose=True)
   print '\n \n WARNING: USING LOCAL LASER NTUPLES \n \n'
else:
   Read_Laser = ReadLaser(diode_num_lg=0,diode_num_hg=0, verbose=True)
   


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

                                   
COOL_Cal_Int  = ReadCalibFromCool(runType='integrator',
                                   schema='OFL',
                                   folder='INTEGRATOR',
                                   tag='UPD4')
                                   
COOL_Cal_Cs   = ReadCalibFromCool(runType='cesium',
                                   schema='OFL',
                                   folder='CALIB/CES',
                                   tag='UPD4')

COOL_Cal_CIS  = ReadCalibFromCool(runType='CIS',
                                   schema='OFL', 
                                   folder='CALIB/CIS',
                                   tag='UPD4')

COOL_Cal_ChannelProblems  = ReadBadChFromCool(schema='OFL',
                                            tag='UPD4',
                                            Fast=True,
                                            storeADCinfo=True)
                                   
Laser_Global_Shifts       = getGlobalShiftsDirect(siglim=2.0,n_iter=3,verbose=True)

Laser_Fibre_Shifts        = getFiberShiftsDirect(siglim=1.0, n_iter=3,verbose=True)

Combined_Plotting_Utility = LasCsCIS_plots(Region=plot_regions, plotdirectory=OutFolder)

################################################################################

Go([ \
Use_LAS,                                     # BUILD LASER RUN LIST
Use_Cs,                                      # BUILD CESIUM RUN LIST
Use_CIS,                                     # BUILD CIS RUNS LIST
Read_Laser,                                  # LOAD LASER EVENT NTUPLES
CleanLaser(),                                # CUT OUT BAD LASER EVENTS
ReadCIS(),                                   # LOAD CIS EVENT NTUPLES
CleanCIS(),                                  # CUT OUT FAILED INJECTIONS
ReadCsFile(normalize=True, verbose=False),   # LOAD CESIUM EVENT NTUPLES
COOL_Cal_Las,                                # LOAD LASER DATABASE CALIBRATIONS
COOL_Cal_Int,                                # LOAD INTEGRATOR DB CALIBRATIONS
COOL_Cal_Cs,                                 # LOAD CESIUM DB CALIBRATIONS
COOL_Cal_CIS,                                # LOAD CIS DATABASE CALIBRATIONS
COOL_Cal_ChannelProblems,                    # LOAD PROBLEMS FROM COOL
Laser_Global_Shifts,                         # GENERATE GLOBAL LASER CORRECTIONS
Laser_Fibre_Shifts,                          # GENERATE FIBRE LASER CORRECTIONS
getPMTShiftsDirect(),                              # GENERATE PMT LASER CORRECTIONS
Combined_Plotting_Utility],                  # MAKE THE PLOTS
memdebug=mdebug)                             # TURNS ON/OFF MEMORY DEBUGGING
