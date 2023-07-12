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


# First give the period you want to analyze

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
newArg=localArgs.newArg

runs = [RUNLIST] # Runlist example

#runs = '-3 weeks'
#runs = '-12 days'


# Then create the set of events to be analyzed, and read the LASER information

a = Use(runs,runType='Las')
b = ReadLaser(box_par=True)

# And finally produce the plots

c = getDiodeHistory(diode=DIODE)

# Then go for it...

processors = [a, b, c]

Go(processors)


