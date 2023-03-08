#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# This creates the CIS public plot that shows the channel deviation after
# many months.  
#
# March 04, 2009
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!


"""
Step 1:
You need to set the 'runs' variable to reflect which runs you would like to look at.  There are various examples below: the set of runs used for the Feb. 2009 TileWeek, the set of runs of Feb. 27th 2009, and the last example uses the last month of CIS runs.

You have to specify two sets of runs, and this script compares them.  The sets of runs are called 'runs' and 'runs2'
"""

#runs = 'October 20, 2011', '-28 day' # Use the last month of runs
#runs2 = 'May 1, 2011', '-28 days'


runs2 = '-28 day' # Use the last month of runs
runs = [175167, 175275, 175675, 176330, 176532, 176731, 176853, 176945, 177019, 177138, 177339, 177600] #Feb 14 2011 to March 15 2011




"""
Step 2:
Which regions in the detector do you want to look at?  If you select nothing, the whole detector is used.
"""

selected_region = '' # Look at who detector
#selected_region = 'EBA' # Look at just EBA
#selected_region = 'LBA_m42_c0_lowgain' # Look at LBA module 42 channel 0 lowgain
#selected_region = 'lowgain' # Look at low-gain only
#selected_region = 'EBC_m33_c08_lowgain'
#selected_region = 'LBA_m30_c32_lowgain'
#selected_region = 'EBA'   

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
    u1 = Use(run=runs_past2, run2= runs_past,  runType='CIS', region=selected_region, TWOInput=twoInputs)
else:
    
    u1 = Use(run=runs_past2, run2= '',  runType='CIS', region=selected_region)

############ now for the second set of runs ######################

if type(runs2)== type(int()) or type(runs2)== type(list()): # looks 
    twoInputs_2=False
    runs_past2_2=runs
   # u = Use(run=runs, runType='CIS', region=selected_region)
    print "Use runs input is a int or list"

elif type(runs2)== type(str()):
    print 'runs type string'  
    if not '-' in runs: # if there is NOT '-' in runs (its a date) use date -28days 
        runs_past_2= runs2
        runs_past2_2=runs2+'-28 days'
        twoInputs_2=True
       #u = Use_mod(run=runs_past2, run2=runs_past, runType='CIS', region=selected_region)
    elif runs2[:1]=='-': # checks string to see if it is -x days 
         twoInputs_2=False
         runs_past2_2=runs2
        #u = Use(run=runs, runType='CIS', region=selected_region)
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
        #u = Use_mod(run=runs_past2, run2= runs_past,  runType='CIS', region=selected_region)
    else: # takes the list of two dates and gets the runs inbetween them
        runs_past_2=runs2[0]
        runs_past2_2=runs2[1]
        print 'past_2 ',runs2[0]
        print 'past2_2', runs2[1]
        twoInputs_2=True
       # u = Use_mod(run=runs_past2, run2= runs_past,  runType='CIS', region=selected_region)
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

h = HistoryPlot('CIS')

Go([\
    u1,\
    ReadCIS(),\
    CISFlagProcedure(dbCheck=False),\
    pr,
    h,
    Clear(),
    u2,\
    ReadCIS(),\
    CISFlagProcedure(dbCheck=False),\
    h,\
    pr,\
    s,\
    ])
