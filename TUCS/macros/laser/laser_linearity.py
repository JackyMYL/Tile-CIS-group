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
# This scripts contains the different options
# for TileCal PMTs linearity analysis
#
# SV (viret@in2p3.fr) : 26/11/09 (creation) // 30/03/10 (major rev.)
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
# The results could be put on the LASER webpage by LASER expert
#
# http://atlas-tile-laser.web.cern.ch/atlas-tile-laser/Welcome.php?n=Work.Linearity
#
# The wiki scripts to produce those pages are available setting the following to True
#

produce_wiki = True


#
# Following option has to be set to True if you want to use box PMT instead of ratios
#
# At the end of the day, diodes will be used, but for the moment they are affected 
# by light crosstalk effect, so not usable for linearity tests
#

usePM        = True


#
# First give the list of run number you want to use 
#
# A good combination is obtained with the following intensities:
#
# 16000 / 18000 / 20000 / 22000 / 24000 / 28000
#
# Below you may find some examples
#

#run = [140876,140900,140906,140916,140898]
#run = [141050,141051,141057,141062,141064]
#run = [142637,142678,142639,142640,142641,141363]
run = [143124,143126,143130,143134,143141,143148]
#run = [143124]


#
# Create the list of events to be analyzed, and read the LASER information
#
# !!! For the moment linearity calibration ROOTfiles are not directly processed
# !!! you have either to copy them locally, or to create them using the LaserLinearityCalibTool
#

a = Use(run,runType='Las')
b = ReadLaserLin(processingDir='/tmp/sviret',signalMin=0.1)


#
# Read the lookup table (linearity saturation correction), and also the LASER stability constants
#
# useSqlite=True will read info from local 'tileSqlite.db' file (useful for debugging)
# this is the default for the moment, as non-linear constants are not yet on the DB
# 

c = ReadCalibFromCool(schema = 'OFL', folder = 'CALIB/LASER',  runType = 'Las', tag = 'UPD1')

# Or only the classic ATLAS db if you just need ADC info (no lookup table info for the moment)
c2= ReadCalibFromCool(schema = 'OFL', folder = 'CALIB/CES', runType = 'Las_REF', tag = 'UPD1')

#
# The following steps are performing the basic linearity analysis
# 

# 1. Compute the filter attenuations
#

d = getLinCorrections(useBoxPMT=usePM,verbose=False,nEvtCut=2000)

# 2. Compute the slopes,intercepts, and chisquares for all pmts
#

e  = getLinParams(useBoxPMT=usePM,nEvtCut=2000,minpoints=4)

# Launch the analysis 
#

#processors = [a, b, c, d, e] # With saturation correction (local file required)
processors = [a, b, c2, d, e] # Without saturation correction 


#
# The last steps are describing the plot production (default plots are .png, .eps is optional)
# 
# You could produce plots for few parts or for all the TileCal (as for the history plots, PROCEDURE 3)
#
# Below are some examples (uncomment what you want to try)


#
# Example 1: do just some plots
#

# Module EBC59 (large variation limit is set to 1%)
processors.append(do_residual_plot(useBoxPMT=usePM,part=3,drawer=58,limit=1.,doWiki=produce_wiki,doEps=True))

# Module EBC35 (large variation limit is set to 1%)
#processors.append(do_residual_plot(useBoxPMT=usePM,part=3,drawer=34,limit=1.,doWiki=produce_wiki,doEps=True))

# Module LBC09 (large variation limit is set to 1%)
#processors.append(do_residual_plot(useBoxPMT=usePM,part=1,drawer=8,limit=1.,doWiki=produce_wiki,doEps=True))

#
# Example 2: produce all the plots + the wiki update files (takes ~30min)
#

#processors.append(do_residual_plot(useBoxPMT=usePM,limit=1.,doWiki=produce_wiki))


#
# Example 3: produce an individual channel history plot
#

# Module EBC59[8] (large variation limit is set to 1%)
#processors.append(do_chan_plot(part=3,limit=1,mod=58,chan=8,option='Lin',doEps=True))

# Module LBA03[7] (large variation limit is set to 1%)
#processors.append(do_chan_plot(part=0,limit=1,mod=2,chan=7,option='Lin',doEps=True))


#
# Go for it!!!
#

Go(processors)


