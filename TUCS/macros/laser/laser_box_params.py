#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

#
# This script provides the different methods necessary
# for looking at the laser box intrinsic parameters
# It is of primary interest for LASER experts who want to
# check or monitor some basic properties of the system
#
# SV (viret@in2p3.fr) : 21/08/09 
#
# For more info, have a look at the LASER webpage:
# 
# http://atlas-tile-laser.web.cern.ch

#
# There are two sets of reference values for low gain and for high gain
#
# Low  gain runs needs to be filter 6 / intensity 23000
# High gain runs needs to be filter 8 / intensity 23000
#

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
newArg=localArgs.newArg

# First give the period you want to analyze (you can also provide a list)

#runs = '-4 weeks'
runs = '-110 days'
#runs = [142512,142515,142590,142592,142635]

# Then create the set of events to be analyzed, and read the LASER information

a = Use(runs,runType='Las',filter='6')
b = ReadLaser(box_par=True)

processors = [a, b]

# And finally produce the plots which are available on the LASER webpage
#
# You could produce the plots just for one diode 
#
# Uncomment the corresponding line (or all of them)

processors.append(getDiodeHistory(diode=0))
#processors.append(getDiodeHistory(diode=1))
#processors.append(getDiodeHistory(diode=2))
#processors.append(getDiodeHistory(diode=3))

# Then go for it...

Go(processors)


