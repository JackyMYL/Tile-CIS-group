#!/usr/bin/env python
# Atuh: Henric
# date: A long time ago
# @purpose: makes nice laser timing plot
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8
#2345678901234567890123456789012345678901234567890123456789012345678901234567890


import os

os.chdir(os.getenv('TUCS','.'))

exec(open('src/load.py').read(), globals()) # don't remove this!
exec(open('src/laser/laserGetOpt.py').read(), globals())

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
#localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser
localArgs=localArgParser.args_from_parser()
#newArg=localArgs.newArg

processors = []

if date != '':
    runs = str(date)
print(runs)


processors.append( Use(runs,run2=enddate,filter=filt_pos,
                       runType='Las',
                       region=region, TWOInput=twoinput) )
#else:
#    processors.append( Use(runs,run2=enddate,filter=filt_pos,runType='Las',
#                           TWOInput=twoinput, amp='15000') )

if os.path.exists('/data/ntuples/las'):
    processors.append( ReadLaser(processingDir='/data/ntuples/las',
                                 diode_num_lg=0, 
                                 diode_num_hg=0, 
                                 doTime=True) )
else:
    processors.append( ReadLaser(diode_num_lg=0, diode_num_hg=0, doTime=True) )

processors.append( CleanLaser() )
#
# Read the reference values from the CondDB
#
# useSqlite=True will read info from 'tileSqlite.db' file (useful for debugging)
# storeADCinfo=False is necessary here otherwise you might have memory problems
#

# processors.append( Print(region='EBA') )

#processors.append( ReadBchFromCool( schema='COOLOFL_TILE/CONDBR2',
#                                    folder='/TILE/OFL02/STATUS/ADC',
#                                    tag='UPD4', Fast=True,
#                                    storeADCinfo=True) )

#processors.append( ReadTimeFromCool( folder='/TILE/OFL02/TIME/CHANNELOFFSET/LAS',
#                                     tag='UPD4'  ) )

processors.append(do_global_time_plot(limit=1.))

doTimePlots=True

if doTimePlots:
    print('We will do the time plots')
    if region == None:
        processors.append(do_time_plot(limit=1.))  # All modules
    else:
        if region.find('LBA')>-1:
            processors.append(do_time_plot(limit=1.,part=LBA))  # LBA modules
        if region.find('LBC')>-1:
            processors.append(do_time_plot(limit=1.,part=LBC))  # LBC modules
        if region.find('EBA')>-1:
            processors.append(do_time_plot(limit=1.,part=EBA))  # EBA modules
        if region.find('EBC')>-1:
            processors.append(do_time_plot(limit=1.,part=EBC))  # EBC modules
#
# Go for it!!!
#
Go(processors,withMBTS=False)
sys.exit(0)



