# Author: Dave Hollander <daveh@uchicago.edu>
#
# April 19, 2010
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

# Note: Tiletb ntuples have moved to 2010 folder, now called tile_runNumber_CIS.0.aan.root
# Need to change timing script to use the new setup.

# Special note: Since the validation ntuples have migrated and are now structured differently from the old h1000
# style ntuples, there are two separate timing scripts. If the runs you are using are on or before May 31, 2010,
# then use the worker 'timingCIS()', otherwise use the 'NewTimingCIS()' worker.



#selected_region = ''                     # Look at who detector
selected_region = 'EBA_m08_c10'              # Look at just EBA


###############list of inputs############

runs = [181982, 183367] # this is just a lits of runs 
#runs = 'March 29, 2010' # picks runs 28 days before date typed 
#runs = '-28 days' # looks at the last 28 days of runs 
#runs = 'March 18, 2010','March 8, 2010' #looks at runs taken between these  days 
#runs = 'May 19, 2010','-19 days' # picks runs taken between date and number of days in the past

#########################################




u = Use(run=runs, runType='CIS', region=selected_region)


if not globals().has_key('selected_region'):
    selected_region = ''


Go([\
    u,\
    ReadCIS(),
    ReadDB(),\
    CISFlagProcedure(),\
    CISRecalibrateProcedure(),\
    #timingCIS(all=True),\
    NewTimingCIS(all=True,Phase=0,dachi=10,daclo=512),\
    ])
