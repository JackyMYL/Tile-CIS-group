# Author:  Andrew Hard           <ahard@uchicago.edu>
# Contrib: John Dougherty        <jdougherty@uchicago.edu>
#
# This macro is intended to map the shape of an injected pulse for a given charge. 
# It will use the 15 different phase values to get 60 samples of the pulse at 104ps intervals. 
# It can then be compared to the pulse shape derived from test beam studies.
#
# December 8, 2010
# Modified April 6, 2011

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

"""
Step 1:
Set the 'runs' variable to reflect which runs you would like to look at.
"""

runs = [190748]
#runs = '-7 days'

#singleDays = False

"""
Step 2:
Specify the region of the detector for which you would like to generate plots.  Works best when an individual channel is selected.
"""

selected_region = 'LBA_m08_c14'

"""
Step 3:
Specify the desired DAC values (for both high and low-gain channels) in the variables below.
"""

dachi = 10
daclo = 512

showAll = True



# EXPERTS ONLY BELOW


u = Use(run=runs, runType='CIS', region=selected_region)

Go([\
    u,\
    ReadCIS(),
    ReadDB(),\
    CISFlagProcedure_modified(),\
    CISRecalibrateProcedure(),\
    PlotPulseShape(all=showAll, region=selected_region),\
    ])
