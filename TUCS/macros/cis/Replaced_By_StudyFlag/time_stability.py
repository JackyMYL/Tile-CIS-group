# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Make time stability plots (calib vs. time) for selected channels and runs.
#
# March 05, 2009
#
# Modified: Andrew Hard <ahard@uchicago.edu>
#
# May 27, 2011


# Step 1:
# What set of runs do you want to run over? The examples below show the
# possible ways of defining sets of runs: by run number, date, or intervals of
# time. The standard for CIS status updates is -28 days.

#runs = '-4 months'
#runs = 'October 5, 2011'
#runs = [188607, 188610, 188621, 188623, 188630, 188631]
runs = '-28 days'
#runs = '-3 months'


# Step 2:
# Select the regions you want to run over (selected_region = '' for the whole detector).
# plotvariations and plottimestab turn off and on the option to print the time stability plots
# for each selected channel. plotvariations plots the relative variations of each channel relative
# to it's initial value in percentage. plottimestab uses actual calibration values.

selected_region = ['LBC_m63_c15']
#selected_region = ['LBA_m20_sD_t01', 'LBA_m09_c28', 'LBA_m09_c29', 'LBA_m09_c32', 'LBA_m29_c41', 'LBA_m45_c22', 'LBC_m40_c04']
#plotvariations = True
plotvariations = False
plottimestab = True
#plottimestab = False

# Step 3:
# Make the plots for calibrations measured in CIS runs or database calibration
# values. Changes in the database calibrations should only appear in the plots
# following re-calibrations.

use_calibration_type = "measured"
#use_calibration_type = "database"

#
# Experts only below
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!



if type(runs)== type(int()) or type(runs)== type(list()): # looks 
    twoInputs=False
    runs_past2=runs
   # u = Use(run=runs, runType='CIS', region=selected_region)
    print "Use runs input is a int or list"

elif type(runs)== type(str()):
    print 'runs type string'  
    if not '-' in runs: # if there is NOT '-' in runs (its a date) use date -28days 
        runs_past= runs
        runs_past2=runs+'-28 days'
        twoInputs=True
       #u = Use_mod(run=runs_past2, run2=runs_past, runType='CIS', region=selected_region)
    elif runs[:1]=='-': # checks string to see if it is -x days 
         twoInputs=False
         runs_past2=runs
        #u = Use(run=runs, runType='CIS', region=selected_region)
    else:
        print 'I dont understand what runs is set to'

elif type(runs)== type(tuple()): # takes tuple of date + -x days and finds runs x amount of days behind given date 
    print 'runs type tuple'
    if '-' in runs[1]:
        runs_past= runs[0]
        runs_past2= ''.join(runs)
        print 'past ',  runs_past
        print 'past2 ',  runs_past2
        twoInputs=True
        #u = Use_mod(run=runs_past2, run2= runs_past,  runType='CIS', region=selected_region)
    else: # takes the list of two dates and gets the runs inbetween them
        runs_past=runs[0]
        runs_past2=runs[1]
        print 'past ',runs[0]
        print 'past2', runs[1]
        twoInputs=True
       # u = Use_mod(run=runs_past2, run2= runs_past,  runType='CIS', region=selected_region)
        print"Dumping plots for %s" % selected_region,
else:
    print 'Runs is not a list string int or tuple and i dont know what to do with it'
    
if twoInputs==True:
    u = Use(run=runs_past2, run2= runs_past,  runType='CIS', region=selected_region, TWOInput=twoInputs)
else:
    
    u = Use(run=runs_past2, run2= '',  runType='CIS', region=selected_region)


Go([u,\
ReadCIS(),\
ReadDB(tag='UPD4'),\
CISRecalibrateProcedure(),\
TimeStability(all=True, plotvariations=plotvariations, plottimestab=plottimestab, cal_type=use_calibration_type)])
