#!/usr/bin/env python

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
exec(open('src/laser/laserGetOpt.py').read(), globals()) 

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--low',  action='store',  default=0, arghelp='Low gain run \n')
localArgParser.add_local_arg('--high', action='store',  default=0, arghelp='High gain run \n')
localArgParser.add_local_arg('--iov',  action='store',  default=0, arghelp='IOV \n')
# Get arguments from parser
localArgs=localArgParser.args_from_parser()
lg_REF_run=localArgs.low
lg_REF_run=localArgs.high
iov_run   =localArgs.iov

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
#runs = [150058,149821]


# Create the events to be analyzed, and read the LASER information
# getLast option is used only in case you let us decide which run numbers we should use

#a  = Use(runs,getLast=True,runType='Las',filter='6') # Low gain
#b  = Use(runs,getLast=True,runType='Las',filter='8') # High gain

processors = []

processors.append( Use(lg_REF_run, runType='Las',) )
processors.append( Use(hg_REF_run, runType='Las',) )

processors.append( ReadLaser() )


# Read the reference values from the CondDB
#
# useSqlite=True will read info a local from 'tileSqlite.db' file
# (useful for debugging, but you need to create this file first with laser_stab_references.py)

#d = ReadDB(runType = 'Las_REF', useSqlite=True, tag = 'RUN2-HLT-UPD1-01',version=2) # Use local DB
#d = ReadDB(runType = 'Las_REF', tag = 'RUN2-HLT-UPD1-01',version=2) # Use classic DB
processors.append( ReadCalibFromCool(runType = 'Las_REF', folder='CALIB/CES', tag = 'UPD1') )

# This last step automatically compute the variations,
# with no corrections (stored in event.data['deviation'])
# Corrections are computed further

# Compute the fiber partitions variations, (stored in event.data['fiber_var'])
# Global variations (due to the fiber effect on diode signal) are extracted there

processors.append( getFiberShifts() )

# And finally the globally corrected PMT shifts
processors.append( getPMTShiftsObsolete() )
#g2 = getPMTShiftsObsolete(useDB=True) # Compare them to current DB values

#
# You then have everything, you could do plots, DQ, DB updates,...
#

# CondDB update

processors.append(  WriteDB(runType = 'Las', offline_tag = 'RUN2-HLT-UPD1-00',version=2, runNumber=iov_run) )


# You could also read the info from the CondDB, and make some comparison

#i = ReadDB(runType = 'Las', useSqlite=True, tag = 'RUN2-HLT-UPD1-00', version=2)
#i1 = ReadCalibFromCool(runType = 'Las', schema='OFL', folder='LAS/LIN', tag = 'UPD1')
#i2 = ReadCalibFromCool(runType = 'LasFibre', schema='OFL', folder='CAlIB/LAS/FIBER', tag = 'RUN2-COM-00')

#j = do_summary_plots(gain=0,limit=1.5)
#k = do_summary_plots(gain=1,limit=1.5)
#l = do_summary_plots(gain=2,limit=1.5) # The DQ report (both gain runs are requested here)

#
# Then you could do different sort of operations
#
# !!! FOR WRITING PLEASE MAKE SURE YOU HAVE BOTH TYPES OF RUNS !!!
# !!!           IF YOU WANT TO UPDATE THE DATABASE             !!!
#


# Compute everything, WITH ALL CORRECTIONS and NO DB UPDATE

# Use a predefined list of runs
#processors = [ab,c,d,f,g,j,k,l]
# Use the latest runs
#processors = [a,b,c,d,f,g,j,k,l]

# Compute everything, WITH NO CORRECTIONS and NO DB UPDATE

# Use a predefined list of runs
#processors = [ab,c,d,g,j,k,l]

# Perform a DB update, compute all corrections, use predefined list of runs (RECOMMENDED)
#processors = [ab,c,d,f,g,h]

# Read the local DB copy and compare the variations with the DB values
# useful for checking a recent DB update (you should get 0 deviations)
# processors = [ab,c,d,i1,i2,f,g2,j,k,l]

Go(processors)
