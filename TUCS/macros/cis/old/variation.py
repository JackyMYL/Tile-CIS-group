#!/usr/bin/env python
# Author: Andrew Hard <ahard@uchicago.edu>
# Updated: Joshua Montgomery <joshuam@uchicago.edu> 
# Make time variation plots (% change in calib vs. time) for selected channels and runs.
#
# July 7, 2011
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

#Step 1:
# What set of runs do you want to run over? The examples below show the
# possible ways of defining sets of runs: by run number, date, or intervals of
# time. The standard for CIS status updates is -28 days.

#runs = '-5 month'
#runs = '-28 days'

# all good runs between 3/01/2011 and 6/23/2011
#runs = [176731, 176853, 176945, 177019, 177138, 177339, 177600, 177774, 178242,
#        178036, 178039, 178115, 178449, 178594, 178781, 178956, 179110, 179138,
#        179347, 179445, 179463, 179744, 179946, 180091, 180092, 180128, 180130,
#        180278, 180408, 180622, 180769, 181232, 181507, 181982, 182029, 182118,
#        182254, 182494, 182621, 182624, 182865, 182891, 182931, 183009, 183166,
#        183367, 183558, 183591, 183719, 183767, 183785, 183855, 183860, 183945,
#        184313, 184315]

#same interval as above, except with only 50% of the runs (to save time)
runs = [176853, 177019, 177339, 177774, 178036, 178115, 178594, 178956, 179138,
        179445, 179744, 180091, 180128, 180278, 180622, 181232, 181982, 182118,
        182494, 182624, 182891, 183009, 183367, 183591, 183767, 183855, 183945,
        184315]

# Step 2:
# 
# Select the cells/modules/barrels/channels which you would like to make plots
# of.
#
#  Ex: EBC_m45_c03
#
#  Ex: EBC_m45_cD6

selected_region = ['EBC_m05_c%02d' % chan for chan in xrange(3, 8)]
selected_region += ['LBC_m26_c%02d' % chan for chan in xrange(24, 26)]
selected_region += ['LBC_m26_c%02d' % chan for chan in xrange(29, 31)]
selected_region += ['LBC_m26_c40']
selected_region += ['LBA_m23_c%02d' % chan for chan in xrange(38, 40)]



# Step 3:
# Make the plots for calibrations measured in CIS runs or database calibration
# values. Changes in the database calibrations should only appear in the plots
# following re-calibrations.

parameter = "calibration"
#parameter = "calibration_db"

#
# Experts only below
#

u1 = Use(run=runs, useDateProg=True, runType='CIS')
x1 = ReadCIS()

Go([u1, x1, ReadDB(),  CISRecalibrateProcedure(),
    Variation(region=selected_region, all=True, parameter=parameter)])
