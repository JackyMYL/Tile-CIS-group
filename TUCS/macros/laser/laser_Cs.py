#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

#
# This script provides a method to
# compare LASER data with Cs
#
# SV (viret@in2p3.fr) : 20/04/10 (creation)
#
# For more info, have a look at the LASER webpage:
# 
# http://atlas-tile-laser.web.cern.ch

# 
# The macro utilization is explained in PROCEDURE 9 of the LASER shifter's manual:
#
# http://atlas-tile-laser.web.cern.ch/atlas-tile-laser/Welcome.php?n=Work.HowTo
#

exec(open('src/laser/laserGetOpt.py').read(), globals()) 

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
newArg=localArgs.newArg

#
# First give the run you want to use for your comparison
#

# First you need a run containing the old Cs constants and the Laser values right
# after the last Cs scan

run_1 = 146962

# The second run is just needed for getting the new Cs constants 

run_2 = 153250



runs = [run_1,run_2] 


#
# Then give the type of gain. Thie is set via the filter position 
#
# High gain is '8', low gain is '6'

filt_pos='6' # Here we choose high gain

#
# Create the list events to be analyzed, and read the LASER information
#
#

a = Use(runs,runType='Las',filter=filt_pos)
b = ReadLaser()


#
# Read the reference values from the official CondDB
#

d = ReadCalibFromCool(schema = 'OFL', folder = 'CALIB/CES', runType = 'Las_REF', tag = 'UPD1') # ATLAS CondDB


#
# The following steps are intended to compute the gain variations,
# 

# Compute the fiber partitions variations, (stored in event.data['fiber_var'])
# Global variations (due to the fiber effect on diode signal) are extracted there

f  = getFiberShifts()

# And finally the globally corrected PMT shifts, (stored in event.data['deviation']) 

g = compareCs_with_Las(run_bef=run_1,run_aft=run_2)

# Launch the analysis

processors = [a, b, d, f, g]

#
# Go for it!!!
#

Go(processors)


