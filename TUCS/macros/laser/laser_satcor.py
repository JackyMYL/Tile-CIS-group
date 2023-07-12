#!/usr/bin/env python

import os
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

#
# This scripts creates the saturation correction table
#
# SV (viret@in2p3.fr) : 15/01/10 (creation)
#
# For more info, have a look at the LASER webpage:
# 
# http://atlas-tile-laser.web.cern.ch

#
# The run used for linearity has the following properties
#
# Filter wheel moving / intensity fixed
#
# A list of those runs could be obtained via the following link:
#
# http://tileinfo.web.cern.ch/tileinfo/commselect.php?select=select+run,date,lasfilter,lasreqamp,events+from+comminfo+where+lasfilter+like+%27%%28%%27+and+lasreqamp+not+like+%27%%28%%27+and+events%3E%279000%27+order+by+run+desc&rows=200


#
# These first steps corresponds to PROCEDURE 7 of the LASER webpage
# it creates a dummy DB with the LASER constants (not yet available on DB)
# The saturation correction will be added to this file, and then crosscheck could be done
# locally using the local DB file
#

runs = [150434,150444]
a = Use(runs,runType='Las')
b = ReadLaser()
#c = ReadDB(runType = 'Las_REF', tag = 'RUN2-HLT-UPD1-01',version=2) # Use classic DB
c = ReadCalibFromCool(schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2', runType = 'Las_REF', folder='/TILE/OFL02/CALIB/CES', tag='RUN2-HLT-UPD1-01')
#c = ReadCalibFromCool(schema = 'OFL', runType = 'Las_REF', folder='CALIB/CES', tag='UPD1')
d = getFiberShifts()
e = getPMTShiftsObsolete()
f = WriteDB(runType = 'Las', offline_tag = 'RUN2-HLT-UPD1-00',version=2,runNumber=130000)

processors = [a,b,c,d,e,f]

# If you want to produce this local sqlite file, just uncomment the following line
#Go(processors)



#
# Following option has to be set to True if you want to use box PMT instead of diodes
# At the end of the day, diodes will be used, but for the moment (Jan 2010) they are affected 
# by light crosstalk effect, so not usable for linearity tests
#

usePM        = True


#
# First give the list of run number you want to use 
#
# A good combination could be reached with the following intensities:
#
# 16000 / 18000 / 20000 / 22000 / 24000 / 28000
#
# Below you may find some examples
#

#run = [141362,141364,141368,141051,141062]
#run = [142637,142678,142639,142640,142641]
run = [143124,143126,143130,143134,143141,143148]


#
# Create the list of events to be analyzed, and read the LASER information
#
#

g = Use(run,runType='Las')
h = ReadLaserLin(processingDir='/tmp/sviret',signalMin=0.1)


#
# The following steps are intended to perform the linearity analysis
# 


#
# Read the lookup table (linearity saturation correction), and also the LASER stability constants
#
# useSqlite=True will read info from local 'tileSqlite.db' file (useful for debugging)

# Here you access the file you have just created
#i = ReadDB(runType = 'Las', useSqlite=True, tag = 'RUN2-HLT-UPD1-00', version=2)
i = ReadCalibFromCool(schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2', runType = 'Las', folder='/TILE/OFL02/CALIB/LAS/LIN', tag='RUN2-HLT-UPD1-01')
#i = ReadCalibFromCool(schema = 'OFL', runType = 'Las', folder='CALIB/LAS', tag='UPD1')

# Or only the classic ATLAS db if you just need ADC info
#i2= ReadDB(runType = 'Las_REF', tag = 'RUN2-HLT-UPD1-01', version=2)
i2 = ReadCalibFromCool(schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2', runType = 'Las_REF', folder='/TILE/OFL02/CALIB/CES', tag='RUN2-HLT-UPD1-01')
#i2 = ReadCalibFromCool(schema = 'OFL', runType = 'Las_REF', folder='CALIB/CES', tag='UPD1')

# Compute the linearity info (see laser_linearity.py for more details)

j = getLinCorrections(useBoxPMT=usePM,verbose=False,nEvtCut=2000)
k = getLinParams(useBoxPMT=usePM,nEvtCut=2000,minpoints=4)

# Compute the saturation correction and a lookup table giving the 
# relation between measured and real signal (in pC)

l = getSatCorrections(useBoxPMT=usePM)


# Write the lookup table in the CondDB
# Folder /TILE/OFL**/CALIB/LAS/NLN

m = WriteDB(runType = 'Las_NLN', offline_tag = 'RUN2-HLT-UPD1-00',version=2,runNumber=131000) 


# Launch the analysis without DB update (just produce some plot)

processors = [g, h, i2, j, k, l]

# Launch the full thing, with DB creation

#processors = [g, h, i2, j, k, l, m]

# Launch the analysis using the correction implemented  (good crosscheck)
# You need to have the non-linear correction already in the local file

#processors = [g, h, i, j, k, l]

#
# Go for it!!!
#

Go(processors)


