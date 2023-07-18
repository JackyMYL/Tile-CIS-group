#!/usr/bin/env python
# @author:  Marco
# @date:    2012-07-13
# @purpose: generate relevant plots for potential HV changes
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/laser/laserGetOpt.py').read(), globals())
exec(open('src/load.py').read(), globals()) # don't remove this!

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
newArg=localArgs.newArg

runs = '2014-10-01'
enddate = '2014-10-10'
# DEFINE PROCESSORS
processors = [ Use(runs,run2=enddate,filter=filt_pos,runType='Las', region=region, TWOInput=twoinput) ]
if os.path.exists('/data/ntuples/las'):
    b = ReadLaser(processingDir='/data/ntuples/las',diode_num_lg=0, diode_num_hg=0, verbose=True)
else:
    b = ReadLaser(diode_num_lg=0, diode_num_hg=0)
processors.append( b )
processors.append( CleanLaser() )
processors.append( ReadBadChFromCool( schema='OFL',
                                    tag='UPD4',
                                    Fast=True,
                                    storeADCinfo=True ) )
processors.append( ReadCalibFromCool( schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                                    folder='/TILE/OFL02/CALIB/CES',
                                    runType = 'Las_REF',
                                    tag = 'RUN2-HLT-UPD1-01',
                                    verbose=True) )
#processors.append( ReadCalibFromCool( schema='OFL',
#                                    folder='CALIB/CES',
#                                    runType = 'Las_REF',
#                                    tag = 'UPD1',
#                                    verbose=True) )


use_optics = True
if use_optics:
    processors.append( getGlobalShiftsDirect(siglim=2.0, n_iter=3, verbose=True) )
    processors.append( getFiberShiftsDirect(siglim=1.0, n_iter=3, verbose=True) )
    processors.append( getPMTShiftsDirect() )
    processors.append( getBadChannels() )

# GENERATE PLOTS
if region == None:
    region=''

for part in [EBA, EBC]:#, LBA, LBC]:
    processors.append(  do_possible_HV_increase(part=part, chan= 0) ) # E3 or MBTS
    processors.append(  do_possible_HV_increase(part=part, chan= 1) ) # E4
    #processors.append(  do_possible_HV_increase(part=part, chan= 2) ) # D4
    #processors.append(  do_possible_HV_increase(part=part, chan= 3) ) # D4
    #processors.append(  do_possible_HV_increase(part=part, chan= 5) ) # C10
    #processors.append(  do_possible_HV_increase(part=part, chan= 6) ) # C10
    #processors.append(  do_possible_HV_increase(part=part, chan= 12) ) # E1
    #processors.append(  do_possible_HV_increase(part=part, chan= 13) ) # E2

    #processors.append(  do_map_HV_increase(part=part) )

    #processors.append(  get_lowest_laser_signals(part=part,number=10, cells=[1,2]  ) )
    #processors.append(  get_lowest_laser_signals(part=part,number=150, cells=[] ) )
    #processors.append(  get_lowest_laser_signals(part=part,number=200, cells=[1,2] ) )

    #processors.append(  get_highest_laser_signals(part=part,number=10, cells=[1,2]  ) )
    #processors.append(  get_highest_laser_signals(part=part,number=150, cells=[] ) )
    #processors.append(  get_highest_laser_signals(part=part,number=200, cells=[1,2] ) )

    #processors.append(  do_mod_plot(limit=10,part=part,doEps=False,doSig=True) )
    #processors.append(  do_mod_plot(limit=10,part=part,doEps=True,doSig=False) )

Go (processors)
