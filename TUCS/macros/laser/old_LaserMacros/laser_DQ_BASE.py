#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
#
# This scripts provides the some examples
# concerning DQ plots
#
# SV (viret@in2p3.fr) : 20/08/09 (creation) // 24/09/09 (major rev.)
#
# For more info, have a look at the LASER webpage:
# 
# http://atlas-tile-laser.web.cern.ch

#
# There are two sets of stability runs for low gain and for high gain
#
# Low  gain runs needs to be filter 6 / intensity 23000
# High gain runs needs to be filter 8 / intensity 23000
#

#
# The results could be put on the LASER webpage by LASER expert
#
# Low  gain: http://atlas-tile-laser.web.cern.ch/atlas-tile-laser/Welcome.php?n=Work.LowGainStability
# High gain: http://atlas-tile-laser.web.cern.ch/atlas-tile-laser/Welcome.php?n=Work.HighGainStability
#
# The wiki scripts to produce those pages are available setting the following to True
#

exec(open('src/laser/laserGetOpt.py').read(), globals()) 

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
newArg=localArgs.newArg

produce_wiki = True

# 
# Webpage update procedure is detailed in PROCEDURE 2 of the LASER shifter's manual:
#
# http://atlas-tile-laser.web.cern.ch/atlas-tile-laser/Welcome.php?n=Work.HowTo
#


#
# First give the period you want to analyze (this is starting from today)
# 
# Note: if you give a runlist the runs have to have same filter and amplitude settings (you don't have to care if you give a period)
#

runs = [248370] # Runlist example


#
# Then give the type of gain. Thie is set via the filter position 
#
# High gain is '8', low gain is '6'

filt_pos='FILT' # Here we choose high gain

#
# Create the list events to be analyzed, and read the LASER information
#
#

a = Use(runs,runType='Las',filter=filt_pos)
b = ReadLaser()
#
# Read the reference values from the CondDB
#
# useSqlite=True will read info from 'tileSqlite.db' file (useful for debugging)

#d = ReadDB(runType = 'Las_REF', useSqlite=True, tag = 'RUN2-HLT-UPD1-01', version=2, storeADCinfo=False) # Local DB
d =ReadCalibFromCool(schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2', runType = 'Las_REF', folder='/TILE/OFL02/CALIB/CES',  tag = 'RUN2-HLT-UPD1-01')
#d =ReadCalibFromCool(schema = 'OFL', runType = 'Las_REF', folder='CALIB/CES',  tag = 'UPD1')


#d = ReadDB(runType = 'Las_REF', tag = 'RUN2-HLT-UPD1-01', version=2, storeADCinfo=False) # ATLAS CondDB


#
# The following steps are intended to compute the gain variations,
# 

# Compute the global partitions variations, (stored in event.data['part_var'])

#e = getGlobalShifts()
#e = getGlobalShifts()

# Compute the fiber partitions variations, (stored in event.data['fiber_var'])
# Partition variations are computed afterwards, from there

f = getFiberShifts()

# And finally the globally corrected PMT shifts, (stored in event.data['deviation']) 

g = getPMTShiftsObsolete()

# Launch the analysis

processors = [a, b, d, f, g]


#
# The last steps are describing the plot production (default plots are .png)
# 
# At each level, you could produce plots for few parts
# or for all the TileCal
#
# Below are some examples (uncomment what you want to try)

#
# Example 1: do just some plots
#

# Partition LBA (large variation limit is set to 2%)
#processors.append(do_part_plot(part=0,limit=2.,filter=filt_pos))

# Fiber LB1A (large variation limit is set to 1%, eps plot is also produced)
#processors.append(do_fiber_plot(fib=0,limit=1.,doEps=True,filter=filt_pos))

# Module LBA22 (large variation limit is set to 1%)
#processors.append(do_pmts_plot(part=0,drawer=21,limit=1.,filter=filt_pos))


#
# Example 2: produce all the plots
#

#processors.append(do_part_plot(limit=1.,filter=filt_pos))  # All partitions 
#processors.append(do_fiber_plot(limit=1.,filter=filt_pos)) # All fibers
#processors.append(do_pmts_plot(limit=1.,filter=filt_pos))  # All modules


#
# Example 3: produce all the plots + the wiki update files
#

processors.append(do_part_plot(limit=1.5,doWiki=produce_wiki,filter=filt_pos,nDays=10))
processors.append(do_fiber_plot(limit=1.5,doWiki=produce_wiki,filter=filt_pos,nDays=10))
processors.append(do_pmts_plot(limit=1.5,doWiki=produce_wiki,filter=filt_pos,nDays=10))

# Evolution of the systematic error due to light distribution instability 
processors.append(syst_errors_evolution(gain=0))

# Evolution of the systematic error due to light distribution instability 
processors.append(syst_errors_evolution(gain=1))

#
# Go for it!!!
#

Go(processors)


