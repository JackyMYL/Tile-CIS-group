#!/usr/bin/env python

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

if 'region' in dir():
    a = Use(runs,run2=enddate,runType='Las', filter=filt_pos, region=region, TWOInput=twoinput)
else:
    a = Use(runs,run2=enddate,runType='Las', filter=filt_pos, TWOInput=twoinput, amp='15000')

if os.path.exists('/data/ntuples/las'):
    b = ReadLaser(processingDir='/data/ntuples/las',diode_num_lg=0, diode_num_hg=0)
else:
    b = ReadLaser(diode_num_lg=0, diode_num_hg=0)



c = CleanLaser()

d = ReadBchFromCool(schema='COOLOFL_TILE/CONDBR2',folder='/TILE/OFL02/STATUS/ADC',tag='UPD4', Fast=True)

e = ReadCalFromCool( schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                     folder='/TILE/OFL02/CALIB/CES',
                     runType = 'Las_REF',
                     tag = 'RUN2-HLT-UPD1-01',
                     verbose=True)

processors = [a, b, c, d, e]

#processors.append(ReadDCSHV())

#processors.append(Print())

#
## The following steps are intended to compute the gain variations,
#

# Compute the fiber partitions variations, (stored in event.data['fiber_var'])
# Global variations (due to the fiber effect on diode signal) are extracted there
#OnlyGlobalShifts = False
#if OnlyGlobalShifts:
processors.append(getGlobalShiftsDirect(siglim=3.,n_iter=2,verbose=True))
#else:
processors.append(getFiberShiftsDirect(siglim=2.,verbose=True))

# And finally the globally corrected PMT shifts, (stored in event.data['deviation'])

processors.append(getPMTShiftsDirect())

# The last steps are describing the plot production (default plots are .png)
#
# At each level, you could produce plots for few parts
# or for all the TileCal
#
# Below are some examples (uncomment what you want to try)

#processors.append(do_henrics_plot())

if not 'region' in dir():
    processors.append(do_pmts_plot_henric(limit=1.,filter=filt_pos))  # All modules
else:
    if 'LBA' in region:
        processors.append(do_pmts_plot_henric(limit=1.,part=0 ,filter=filt_pos))  # LBA modules
    if 'LBC' in region:
        processors.append(do_pmts_plot_henric(limit=1.,part=1 ,filter=filt_pos))  # LBC modules
    if 'EBA' in region:
        processors.append(do_pmts_plot_henric(limit=1.,part=2 ,filter=filt_pos))  # EBA modules
    if 'EBC' in region:
        processors.append(do_pmts_plot_henric(limit=1.,part=3 ,filter=filt_pos))  # EBC modules




#
# Go for it!!!
#


Go(processors)
#Go ([a])




