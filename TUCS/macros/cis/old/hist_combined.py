#!/usr/bin/env python
# Author: Joshua Montgomery <Joshua.Montgomery@gmail.com>
#
# This is a macro which can create all of the current CIS Public
# Plots as well as a number of other useful plots with a relatively broad
# scope. These provide overviews of detector status from various perspectives
# but are not generally useful in investigating specific problems
#
# October 31, 2011
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!


"""
Step 1:
You need to set the 'runs' variable to reflect which runs you would like to look at.  There are 
various examples below: the set of runs used for the Feb. 2009 TileWeek, the set of runs of 
Feb. 27th 2009, and the last example uses the last month of CIS runs.

You have to specify two sets of runs, and this script compares them.  The sets of runs are called
'runs' and 'runs2.  NOTE:  Earlier runs should be 'runs', while more recent runs should be 'runs2'.
This will allow the plot to show the proper decrease in CIS constants over time, rather than showing
an increase.'

If you are plotting something which looks at only a single interval, Runs will be used (not Runs2)

NOTE: There are occasionally strange CIS runs taken during maintenance periods -- generally TUCS 
is capable of figuring this out and ignoring them, but GetScans.py isn't quite as bright, so if you get
a memory allocation issue when running GetScans, this is probably because one of your selected runs is
behaving poorly. Only the Tune Quality Flag Distributions plots make use of the GetScans module.
"""
	
#runs = [100489,100699,100814,101152,101441,102009] # Runs as of Feb. 2009 TileWeek
runs2 = [175167, 175275, 175675, 176330, 176532, 176731, 176853, 176945, 177019, 177138, 177339, 177600] #Feb 14 2011 to March 15 2011
#runs = '-28 day'
runs = 'June 04, 2011', '-28 day' # Use the last month of runs
"""
Step 2:
Which regions in the detector do you want to look at?  If you select nothing, the whole detector is used.
"""

selected_region = '' # Look at whole detector

"""
Step 3:
Select which plots you want output:
"""
"""
Plots 1: 
History Plots:
Hist_Percent_Public shows the public plot of the percentage change of individual channel's CIS constants
Hist_Percent_Regions makes 2D temperature plots, one for gain of each side of each barrel (8 in total),
showing the percent change in CIS constant by individual channel, organized by channel VS module numbers.
"""

Hist_Percent_Public = True

Hist_Percent_Regions = True


"""
Plots 2: 
Calibration constant mapping:
Calib_Const_Regions prints 8 2D histograms showing the average CIS Calibration Constant for the
interval of supplied runs
"""

Calib_Const_Regions = True

"""
Plots 3:
Performance Plots:
This uses the PerformancePlots.py worker module to generate time-stamped
performance plots of the detector with both full CIS Data, as well as a
summary with three points: 'No CIS Calibration', 'Bad CIS', and 'Total Bad'
The plots need only a start and end date. The formats to be used can either be
a string with the form DD/MM/YY or an integer in epoch seconds.
If no end date is specified it is understood to be up to the latest data available.
This uses the Wiki_Status_Log.txt stored in the CIS Archives at:
/afs/cern.ch/users/t/tilecali/w0/ntuples/cis/flaglogs
"""
Print_Performance_Plot = True

from_date = '05/05/11'
to_date = '' # if left empty this defaults to the latest date with data

"""
Plots 4:
Calibration Constant Distributions:
This macro makes the CIS public plot that shows the distribution of
calibration constants over the time interval or run interval specified by 'runs'.
There are two 1D histograms (one per gain) and
each entry is a channel's calibration constant.
"""

Calibration_Distributions = True

"""
Plots 5:
Tune Quality Flag Distributions:
RMS and Ch2: Tune the fixed-charge RMS and chi2 quality flags --
       Produces important distributions/histograms with RMS cutoffs
       to check Gaussian distributions. These plots can be found in the CIS note #2

Max Point and Likely Calibration: Tune the maximum value in fit range quality flag
       and also the likely calib flag (like above). Plots histograms of the maximum
       response in fit range in ADC counts (can clearly see half and 60% response channels)
       as well as a fit to a histogram of the calibration factor in number of channels.
"""
Tune_RMS_Chi2 = True

Tune_MaxPoint_LikelyCalib = True

"""
step 4
dump debug information
"""
debug = False

#
#  Experts only below.
#


macros_2run_interval = [Hist_Percent_Public] ## This list is for easy addition of other two-run macros
macros_DB_check = [Calibration_Distributions, Tune_RMS_Chi2, Tune_MaxPoint_LikelyCalib, 
Calibration_Distributions]

use_two_run_interval = False
database_check = False

for macro in macros_2run_interval:
    if macro:
        use_two_run_interval = True

for macro in macros_DB_check:
    if macro:
        database_check = True

getscans = None # initialize for multiple macro uses

if not globals().has_key('selected_region'):
    selected_region = ''

    
###### Logic #########

if debug:
    pr = Print()
    s = SaveTree()
else:
    pr = None
    s = None

if Hist_Percent_Public:
    hist_percent_public = HistoryPlot('CIS')
else:
    hist_percent_public = None

if Hist_Percent_Regions:
    hist_percent_regions = HistPlotRegions('CIS')
else:
    hist_percent_regions = None

if Calib_Const_Regions:
    calib_const_regions = CISConstantRegions()
else:
    calib_const_regions = None

if Print_Performance_Plot:
    performance_plots = PerformancePlots(mindate=from_date, maxdate=to_date)
else:
    performance_plots = None

if Calibration_Distributions:
   calibration_distributions = CalibDist()
else:
   calibration_distributions = None

if Tune_RMS_Chi2:
   tune_rms_chi2 = TuneCuts(probbad=True) ## Don't change this from True ...keeping it as a switch for now.
else:
   tune_rms_chi2 = None

if Tune_MaxPoint_LikelyCalib:
   tune_maxpoint_likelycalib = TuneCutsMaxPointLikelyCalib()
else:
   tune_maxpoint_likelycalib = None

if Tune_MaxPoint_LikelyCalib or Tune_RMS_Chi2:
    getscans = GetScans(all=True)


################## Parse what runs is set to ###########################
u1 = Use(run=runs, runType='CIS', region=selected_region)
if globals().has_key('runs2'):
    u2 = Use(run=runs2, runType='CIS', region=selected_region)
#########################################################################



### building The Go lists ##
if use_two_run_interval:
    Go([\
        u1,\
        ReadCIS(),\
        ReadDB(),\
        CISFlagProcedure_modified(dbCheck=database_check),\
        getscans,\
        CISRecalibrateProcedure(all=True),\
        pr,\
        hist_percent_public,\
        hist_percent_regions,\
        calib_const_regions,\
        performance_plots,\
        calibration_distributions,\
        tune_rms_chi2,\
        tune_maxpoint_likelycalib,\
        Clear(),\
        u2,\
        ReadCIS(),\
        ReadDB(),\
        CISFlagProcedure_modified(dbCheck=database_check),\
        hist_percent_public,\
        hist_percent_regions,\
        pr,\
        s,\
        ])
else:
    Go([\
        u1,\
        ReadCIS(),\
        ReadDB(),\
        CISFlagProcedure_modified(dbCheck=database_check),\
        getscans,\
        CISRecalibrateProcedure(all=True),\
        hist_percent_public,\
        hist_percent_regions,\
        calib_const_regions,\
        performance_plots,\
        calibration_distributions,\
        tune_rms_chi2,\
        tune_maxpoint_likelycalib,\
        pr,\
        s,\
        ])
