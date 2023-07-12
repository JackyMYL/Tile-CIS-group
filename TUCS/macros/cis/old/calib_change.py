#!/usr/bin/env python
# Author: Andrew Hard <ahard@uchicago.edu>
#
# This macro creates a map of the % change in CIS
# calibrations for 2 disjoint sets of runs.
#
# June 6, 2011
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!


"""
Step 1:
You have to specify two sets of runs, and this script compares them.  The sets of runs are called 'runs' and 'runs2'. Set 'runs' equal to the newest set of runs, and 'runs2' equal to the oldest set so that the % change is accurate.
"""

# newest run set:
runs = "-28 days"

# oldest run set:
runs2 = 'May 1, 2011', '-28 days'


"""
Step 2:
Which regions in the detector do you want to look at?  If you select nothing, the whole detector is used.
"""

selected_region = '' # Look at who detector

"""
step 3
dump debug information
"""

debug = False

#
#  Experts only below.
#

################## Parse what runs is set to ###########################

if type(runs)== type(int()) or type(runs)== type(list()): # looks 
    twoInputs=False
    runs_past2=runs 
    print "Use runs input is a int or list"

elif type(runs)== type(str()):
    print 'runs type string'  
    if not '-' in runs: # if there is NOT '-' in runs (its a date) use date -28days 
        runs_past= runs
        runs_past2=runs+'-28 days'
        twoInputs=True
    elif runs[:1]=='-': # checks string to see if it is -x days 
         twoInputs=False
         runs_past2=runs
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
    else: # takes the list of two dates and gets the runs inbetween them
        runs_past=runs[0]
        runs_past2=runs[1]
        print 'past ',runs[0]
        print 'past2', runs[1]
        twoInputs=True
        print"Dumping plots for %s" % selected_region,
else:
    print 'Runs is not a list string int or tuple and i dont know what to do with it'
  
if twoInputs==True:
    u1 = Use(run=runs_past2, run2= runs_past,  runType='CIS', region=selected_region, TWOInput=twoInputs)
else:
    
    u1 = Use(run=runs_past2, run2= '',  runType='CIS', region=selected_region)

############ now for the second set of runs ######################

if type(runs2)== type(int()) or type(runs2)== type(list()): # looks 
    twoInputs_2=False
    runs_past2_2=runs
    print "Use runs input is a int or list"

elif type(runs2)== type(str()):
    print 'runs type string'  
    if not '-' in runs: # if there is NOT '-' in runs (its a date) use date -28days 
        runs_past_2= runs2
        runs_past2_2=runs2+'-28 days'
        twoInputs_2=True   
    elif runs2[:1]=='-': # checks string to see if it is -x days 
         twoInputs_2=False
         runs_past2_2=runs2        
    else:
        print 'I dont understand what runs is set to'

elif type(runs2)== type(tuple()): # takes tuple of date + -x days and finds runs x amount of days behind given date 
    print 'runs type tuple'
    if '-' in runs2[1]:
        runs_past_2= runs2[0]
        runs_past2_2= ''.join(runs2)
        print 'past_2 ',  runs_past_2
        print 'past2_2 ',  runs_past2_2
        twoInputs_2=True        
    else: # takes the list of two dates and gets the runs inbetween them
        runs_past_2=runs2[0]
        runs_past2_2=runs2[1]
        print 'past_2 ',runs2[0]
        print 'past2_2', runs2[1]
        twoInputs_2=True       
        print"Dumping plots for %s" % selected_region,
else:
    print 'Runs is not a list string int or tuple and i dont know what to do with it'
    
if twoInputs_2==True:
    u2 = Use(run=runs_past2_2, run2= runs_past_2,  runType='CIS', region=selected_region, TWOInput=twoInputs_2)
else:
    
    u2 = Use(run=runs_past2_2, run2= '',  runType='CIS', region=selected_region)

if not globals().has_key('selected_region'):
    selected_region = ''

if debug:
    pr = Print()
    s = SaveTree()
else:
    pr = None
    s = None

h = MapCalibChange('CIS')

Go([\
    u1,\
    ReadCIS(),\
    CISFlagProcedure_modified(dbCheck=False),\
    pr,
    h,
    Clear(),
    u2,\
    ReadCIS(),\
    CISFlagProcedure_modified(dbCheck=False),\
    h,\
    pr,\
    s,\
    ])
