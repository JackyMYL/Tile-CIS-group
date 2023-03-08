#!/usr/bin/env python
# Author : Rute Pedro (Inspired by Henric.py)
# Date   : July 2013
#
# This macro generates bitmaps per module containing the channel flags attributed with laser data

import os
import os.path
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
exec(open('src/laser/laserGetOpt.py').read(), globals()) 

# Laser Argument class
localArgParser=laserArgs(verbose=True)

# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--includeDQ', action='store_true', default=False,
                    arghelp='This is a switch that passes the include DQ flag to getLaserFlags.py. \
                    When it is selected the events already flagged by the Data Quality will be \
                    considered in the analysis. By default these events are discarded. \
                    Usage: --includeDQ')

localArgParser.add_local_arg('--flag', action='store', nargs='+', default='all',
                    arghelp='Specify the flag you want to study (default --flag all)\
                    --flag fast: will look for fast drifting channels\
                    --flag jump: will look for channels with gain jump\
                    --flag erratic: will look for channels with erratic gain\
                    --flag hl: will look for channels with uncompatible response to high and low gain runs\
                    NOTE with the last option we cannot specify a set of runs with unique gain in the --region argument')

localArgParser.add_local_arg('--expert', action='store_true', default=False,
                    arghelp='This is a switch that allows a local tileSqlite.db file\
                    to be used for the Las_REFs, and local laser ntuples to be used.\
                    The filename for the Las_REF file should be \'tileSqlite.db\' \
                    and path for the laser ntuples should be \'/data/ntuples/las\'')

localArgParser.add_local_arg('--mdebug', action='store_true', default=False,
                    arghelp='This is a switch that passes the memory debug flag to \
                    the Go.py module. The result is two plots detailing the memory \
                    consumption of this macro. The first is a plot that is the percent\
                    memory used as a function of time -- color coded by which worker \
                    is running during that time. The second is a histogram showing the \
                    total memory consumption used by each worker. These are all \
                    printed in the Tucs/ResourceLogs/ directory (which is created \
                    if not already in place). The plots, along with the supporting \
                    text files are categorized by the unique process ID of each instance \
                    this macro is called.')

# Get arguments from parser
localArgs     = localArgParser.args_from_parser()

mdebug        = localArgs.mdebug
includeDQ     = localArgs.includeDQ
flag          = localArgs.flag

if localArgs.expert:
    if not os.path.exists('/data/ntuples/las'):
        print ' \n \n WARNING: NO LOCAL LASER NTUPLES FOUND. USING NTUPLES ON /AFS/. \n \n'
    if not os.path.isfile('tileSqlite.db'):
        print ' \n \n WARNING: NO LOCAL TILESQLITE.DB FILE FOUND. USING COOL FOR LAS_REFS \n \n'

######################### BUILD GO LIST ########################################

Use_LAS       = Use(run=date, run2=enddate, filter=filt_pos, runType='Las', region=region,
                    TWOInput=twoinput)

if localArgs.expert and os.path.exists('/data/ntuples/las'):
   Read_Laser = ReadLaser(processingDir='/data/ntuples/las', diode_num_lg=0,diode_num_hg=0,  verbose=True)
   print '\n \n WARNING: USING LOCAL LASER NTUPLES \n \n'
else:
   Read_Laser = ReadLaser(diode_num_lg=0, diode_num_hg=0, verbose=True)
   


if localArgs.expert and os.path.isfile('tileSqlite.db'):
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

COOL_Cal_ChannelProblems  = ReadBadChFromCool(schema='OFL',
                                            tag='UPD4',
                                            Fast=True,
                                            storeADCinfo=True)

Laser_Fibre_Shifts        = getFiberShifts(n_sig=2.0, n_iter=5,verbose=False)
################################################################################

Go([ \
Use_LAS,                                     # BUILD LASER RUN LIST
Read_Laser,                                  # LOAD LASER EVENT NTUPLES
CleanLaser(),                                # CUT OUT BAD LASER EVENTS
COOL_Cal_Las,                                # LOAD LASER DATABASE CALIBRATIONS
COOL_Cal_ChannelProblems,                    # LOAD PROBLEMS FROM COOL
Laser_Fibre_Shifts,                          # GENERATE FIBRE LASER CORRECTIONS
getPMTShifts(),                              # GENERATE PMT LASER CORRECTIONS
getLaserFlags(region, includeDQ, plotdirectory=outputTag, flag=flag)],    # GET THE PMT LASER FLAGS
memdebug=mdebug)                             # TURNS ON/OFF MEMORY DEBUGGING
