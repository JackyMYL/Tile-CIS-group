#!/usr/bin/env python

import os
import sys
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
run_lg=localArgs.low
run_hg=localArgs.high
iov   =localArgs.iov

LB_threshold = 1.5
EB_threshold = 0.5

if ((run_lg != 0) and (run_hg != 0)):
    runs = [run_lg,run_hg]
elif (run_lg != 0):
    runs = [run_lg]
elif (run_hg != 0):
    runs = [run_hg]
else:
    assert False, "No run specified"
#    sys.exit(3);
    

# 
# Based on laser_stab_variations.py
#
# This scripts provides the different methods necessary
# for computing relative variations w.r.t reference values
# and store them to the CondDB (need both low and high gain there)
#



# Create the events to be analyzed, and read the LASER information
# getLast option is used only in case you let us decide which run numbers we should use

processors = []

processors.append( Use(runs,runType='Las') ) # specify one run or two runs (HG/LG)

processors.append( ReadLaser(diode_num_lg=0, diode_num_hg=0) )

processors.append( CleanLaser() )

# Read the reference values from the CondDB
#
# useSqlite=True will read info a local from 'tileSqlite.db' file
# (useful for debugging, but you need to create this file first with laser_stab_references.py)

processors.append( ReadBadChFromCool( schema='OFL',
                                    tag='UPD4',
                                    Fast=True,
                                    storeADCinfo=True ) )

d = ReadCalibFromCool( schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                     folder='/TILE/OFL02/CALIB/CES',
                     runType = 'Las_REF',
                     tag = 'RUN2-HLT-UPD1-01',
                     verbose=False)

d0 = ReadCalibFromCool(schema='OFL',
                    runType = 'Las_REF',
                    folder='CALIB/CES',
                    tag = 'UPD4')

processors.append(d)



# This last step automatically compute the variations,
# with no corrections (stored in event.data['deviation'])
# Corrections are computed further

# Compute the fiber partitions variations, (stored in event.data['fiber_var'])
# Global variations (due to the fiber effect on diode signal) are extracted there

processors.append( getFiberShifts(UseStableCells=True,SkipEmergency=False,verbose=True) )

# And finally the globally corrected PMT shifts  

processors.append( getPMTShiftsObsolete(Threshold_LB=1.5,Threshold_EB=2.0) ) # 1.5 percent for LB, 2 percent for EB
#
#g2 = getPMTShiftsObsolete(useDB=True,Threshold_LB=1.5,Threshold_EB=2) # Compare them to current DB values

#
# You then have everything, you could do plots, DQ, DB updates,...
#

# CondDB update
e = equalizeHGLG()
processors.append( e )
processors.append( e )

processors.append( WriteDB(runType = 'Las', offline_tag = 'RUN2-HLT-UPD1-00',version=2,runNumber=iov) ) #default is 'RUN2-HLT-UPD1-00', 'RUN2-UPD4-02'


# You could also read the info from the CondDB, and make some comparison


# i = ReadCalibFromCool( schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
#                     folder='/TILE/OFL02/CALIB/LAS/LIN',
#                     runType = 'Las',
#                     tag = 'RUN2-HLT-UPD1-01',
#                     verbose=True) 


#j = do_summary_plots(gain=0,limit=1.5) #low gain
#k = do_summary_plots(gain=1,limit=1.5) #high gain
#l = do_summary_plots(gain=2,limit=1.5) # The DQ report (both gain runs are requested here)

#
# Then you could do different sort of operations
#
# !!! FOR WRITING PLEASE MAKE SURE YOU HAVE BOTH TYPES OF RUNS !!! 
# !!!           IF YOU WANT TO UPDATE THE DATABASE             !!!
#


# Compute everything, WITH ALL CORRECTIONS and NO DB UPDATE

# Use a predefined list of runs
#processors = [ab,c,d,f,g2,j]
#processors = [ab,c,d,f,g]
# Use the latest runs 
#processors = [a,b,c,d,f,g,j,k,l]

# Compute everything, WITH NO CORRECTIONS and NO DB UPDATE

# Use a predefined list of runs
#processors = [ab,c,d,g,j,k,l]

# Perform a DB update, compute all corrections, use predefined list of runs (RECOMMENDED)
# processors = [ab,c,d,f,g,gc,gc,h]

# Test to perform a DB, with 2 IOV :
#processors = [ab1,c,d,f,g,h1,ab2,c,f,g,h2]

# Read the local DB copy and compare the variations with the DB values
# useful for checking a recent DB update (you should get 0 deviations)
#processors = [ab,c,d,i,f,g2,j]

Go(processors)


