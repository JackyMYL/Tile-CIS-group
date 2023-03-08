#!/usr/bin/env python

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
exec(open('src/laser/laserGetOpt.py').read(), globals()) 

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
newArg=localArgs.newArg

# This scripts provides the different methods necessary
# for computing relative variations w.r.t reference values
# and store them to the CondDB (need both low and high gain there)
#
# SV (viret@in2p3.fr) : 16/07/09 
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
#
# Here you have the choice, you could give the run number yourself
# or let us do the job, and take the two last corresponding runs


# You decided to give the run numbers
#runs = [666666,888888]

# You let us decide...
runs = '-1 month'

# Create the events to be analyzed, and read the LASER information
# getLast option is used only in case you let us decide which run numbers we should use

a  = Use(runs,getLast=True,runType='Las',filter='6') # Low gain
b  = Use(runs,getLast=True,runType='Las',filter='8') # High gain

ab = Use(runs,runType='Las') # If you gave the run number yourself

c = ReadLaser()


# Read the reference values from the CondDB
#
# useSqlite=True will read info from 'tileSqlite.db' file
# (useful for debugging)

#d = ReadDB(runType = 'Las_REF', useSqlite=True, tag = 'RUN2-HLT-UPD1-01',version=2) # Use local DB
d = ReadCalibFromCool(schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2', runType = 'Las_REF', folder='/TILE/OFL02/CALIB/CES', tag = 'RUN2-HLT-UPD1-01')
#d = ReadCalibFromCool(schema = 'OFL', runType = 'Las_REF', folder='CALIB/CES', tag = 'UPD1')


# This last step automatically compute the variations,
# with no corrections (stored in event.data['deviation'])
# Corrections are computed further

# Compute the global partitions variations, (stored in event.data['part_var'])

e = getGlobalShifts(verbose=True)

# Compute the fiber partitions variations, (stored in event.data['fiber_var'])

f = getFiberShifts()

# And finally the globally corrected PMT shifts 

g = getPMTShiftsObsolete()

#
# You then have everything, you could do plots, DQ, DB updates,...
#

# CondDB update

h = WriteDB(runType = 'Las', offline_tag = 'RUN2-HLT-UPD1-00')


# You could also read the info from the CondDB, and make some comparison

#i = ReadDB(runType = 'Las', useSqlite=True, tag = 'RUN2-HLT-UPD1-00')
i1 = ReadCalibFromCool(schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2', runType = 'Las', folder='/TILE/OFL02/CALIB/LAS/LIN', tag = 'RUN2-HLT-UPD1-00')
#i1 = ReadCalibFromCool(schema = 'OFL', runType = 'Las', folder='CALIB/LAS', tag = 'UPD1')
i2 = ReadCalibFromCool(schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2', runType = 'Las', folder='/TILE/OFL02/CALIB/LAS/FIBER', tag = 'RUN2-COM-00')
#i2 = ReadCalibFromCool(schema = 'OFL', runType = 'Las', folder='CALIB/LAS/FIBER', tag = 'RUN2-COM-00')

j = do_summary_plots(gain=0,limit=1.5)
k = do_summary_plots(gain=1,limit=1.5)
l = do_summary_plots(gain=2,limit=1.5) # New feature, provides the global DQ list

#
# Then you could do different sort of operations
#
# !!! FOR WRITING PLEASE MAKE SURE YOU HAVE BOTH TYPES OF RUNS !!! 
# !!!           IF YOU WANT TO UPDATE THE DATABASE             !!!
#


# Compute everything, WITH ALL CORRECTIONS and NO DB UPDATE

# Use a predefined list of runs
processors = [ab,c,d,f,g,j,k,l]
# Use the latest runs 
#processors = [a,b,c,d,e,f,g,j,k]

# Compute everything, WITH NO CORRECTIONS and NO DB UPDATE

# Use a predefined list of runs
#processors = [ab,c,d,g,j,k]

# Perform a DB update, compute all corrections, use predefined list of runs
#processors = [ab,c,d,e,f,g,h]

# Read the local DB copy 
#processors = [ab,c,d,e,f,g,i1,i2]

Go(processors)


