#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Make the CIS public plot that shows the time stability of a single channel
# and also the detectorwide mean
#
# June 29, 2009
#
# Modified: Dave Hollander <daveh@uchicago.edu>
#
# November 3, 2009

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

runs = ['178956', '179110', '179138', '179347', '179445']

# set of runs for June 2009 public plots update
#runs = [79781,79786,79789,79797,80487,80493,80494,80495,80512,80517,80529,80534,81342,81349,81355,81363,81601,81608,81627,81632,82395,82401,82405,82414,83033,83051,83066,83078,84402,84408,84432,84450,84826,85889,85895,85903,85920,85926,86523,87528,87920,88366,88843,89767,90170,90179,90364,90555,90860,91315,91567,91837,92016,92416,92971,92972]

# The next set of runs are for June 18 - Sept 21
#runs = [135006,134664,134206,133685,133662,133486,133058,132307,131920,131917,131244,130959,130401,129547,129328,128653,127847,127316,126764,126599,126377,126336,125992,125877,125873,125861,125648,125348,124892,124764,124347,124180,124144,124111,123674,123363,123122,122965,122646,122288,122151,122121,122085,122061,122057,122017,121952,121796,121766,121695,121642,121613,121565,121555,121472,121374,121304,121288,121221,121115,121044,120940,120915,120573,120355,120063]

# From June 15th-ish to early August
#runs = [124347,124180,124144,124111,123674,123363,123122,122965,122646,122288,122151,122121,122085,122061,122057,122017,121952,121796,121766,121695,121642,121613,121565,121555,121472,121374,121304,121288,121221,121115,121044,120940,120915,120573,120355,120063,119428,118680,118508]

# Set of runs for November 3, 2009 public plots update
#runs = [131244,130401,129328,127847,126764,126377,125992,125873,125648,124892,124347,124144,123674,123122,122646,122151,122085,122057,121952,121766,121642,121565,121472,121304,121221,121044,120915,120355,79781,79789,80487,80494,80512,80529,81342,81355,81601,81627,82395,82405,83033,83066,84402,84432,84826,85895,85920,86523,87920,88843,90170,90364,90860,91567,92016,92971,92972]

u = Use(run=runs, runType='CIS')
x = ReadCIS()

# Set to True is you want to plot a debugged version which includes the DB values
debug = True


# After you've run the program once, you can comment out this line since the data
# will be stored to /tmp/ and readout in the next Go()
Go([u,x,ReadDB(),CISFlagProcedure(dbCheck=False),SaveTree()])

if debug:
    Go([LoadTree(), 
        #TimeVSMeanCalib_debug(example="LBA_m58_c06", DB="LBA_m58_c06"),\
        TimeVSMeanCalib_debug(example="LBA_m30_c20", DB="LBA_m30_c20"),\
        TimeVSMeanCalib_debug(example="LBA_m25_c34", DB="LBA_m25_c34"),\
        ])
else:
    Go([LoadTree(), 
        #TimeVSMeanCalib(example="LBA_m58_c06"),\
        TimeVSMeanCalib(example="LBA_m30_c20"),\
        TimeVSMeanCalib(example="LBA_m25_c34"),\
        ])
   
