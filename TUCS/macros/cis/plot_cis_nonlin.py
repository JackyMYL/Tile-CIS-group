#!/usr/bin/env python
# Author: Dave Hollander <daveh@uchicago.edu>
#
# April 27, 2010
# 
# Major revision by John Dougherty (jdougherty@uchicago.edu)
#
# December 8, 2010
#


##################################################
# 
# This macro produces the following linearity studies (in Tucs/plots/latest/cis)
#
#   linearity/Corr_TILECAL_<region>.ps
#       Per-gain residual distribution with non-linear correction applied
#
#   linearity/unCorr_TILECAL_<region>.ps
#       Per-gain residual distribution without correction
#
#   mean_low_linearity.eps
#       Mean residual distribution for the low gains of the entire selected 
#       region, both corrected and uncorrected
#
#   mean_low_linearity_corr.eps
#       Mean residual distribution for the low gains of the entire selected 
#       region, corrections applied
#       
#   mean_low_linearity_uncorr.eps
#       Mean residual distribution for the low gains of the entire selected 
#       region, corrections not applied
#
#   non_lin_fit.eps
#       Comparison of the database non-linear correction factors with the
#       experimental ratios.
#
##################################################


##################################################
# Select some range of runs.  Selecting more than one run will make the
# region-wide average plots comparison plots of the earliest and latest runs.
# The gain-specific plots are produced using the most recent run in the
# interval.  non_lin_fit.eps will use all specified runs.  Runs can be specified
# individually by a list, by a range of days before today, or by two dates, as 
# explained below.
##################################################

##  List
#runs = [188434, 189319]

## The first run from '-x days' ago compared to today
runs = '-28 days'
                
## The first run after runs compared to the last run on runs2
#runs = "July 20, 2010"
#runs2 = "November 4, 2010"

##################################################
#  Select some region to analyze.  Note that for the mean_low_linearity* plots
#  to be of interest, you should run over at least a module.  Runtime over an
#  entire module, producing all plots, is about 1 minute.
##################################################

selected_region = 'LBC_m18'             #format: LBC_m01_c36

##################################################
#  To produce the gain-specific linearity studies in ./linearity/, set
#  SingleGain to True
##################################################

SingleGain = True

##################################################
#  To use correction data from an SQLite file, set sqlite to True
##################################################

sqlite = False

##################################################
#  The first time it is run, PlotNonLinear.py generates the file nonLinCorr.txt,
#  which is the database table of non-linear corrections.  This behaviour saves
#  a call to the database on subsequent runs.  If you would prefer not to
#  generate nonLinCorr.txt, set NLCWrite to False.
##################################################

NLCWrite = True



################################################################################
#  Experts only below                                                          #
################################################################################

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals())

try: runs2
except NameError:
    u = Use(run=runs, runType='CIS', region=selected_region)
else:
    u = Use(run=runs, run2=runs2, runType='CIS',region=selected_region, 
            TWOInput=True)

try: selected_region
except NameError:
    selected_region='LBC_m01'
    
readbchfromcool = ReadBadChFromCool(schema='OFL',  tag='UPD4', Fast=True)
readcalfromcool = ReadCalibFromCool(schema='OFL', runType='CIS', folder='CALIB/CIS', tag='UPD4')


Go([
    u,\
    ReadCIS(),\
    CleanCIS(),\
    #ReadDB(),\
    readbchfromcool,\
    readcalfromcool,\
    GetScans(all=True),\
    ShowCISScans(all=True),\
    PlotNonLinear(nlcwrite=NLCWrite),\
    CISLinear(useSqlite=sqlite, SingleGain=SingleGain),\
    ])
