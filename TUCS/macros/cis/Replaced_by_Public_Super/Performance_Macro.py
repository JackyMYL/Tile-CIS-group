# Author: Joshua Montgomery <joshua.montgomery@cern.ch>
# Oct. 13, 2011
# This Macro uses the PerformancePlots.py worker module
# To generate time-stamped performance plots of the detector
# with both full CIS Data, as well as a summary with three points:
# 'No CIS Calibration', 'Bad CIS', and 'Total Bad'


import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals())

from workers.cis.PerformancePlots import *

# First Choose a date range
# Accepted inputs must be in epoch seconds or a
# string with the format %d/%m/%y (like '05/08/10')
# The from_date is mandatory
# The to_date will default to the latest date with data if left empty or False

from_date = '05/05/10'
to_date = '' # if left empty this defaults to the latest date with data





##### Experts Only Below #####

Performance_inst = PerformancePlots(mindate=from_date, maxdate=to_date)
Channel_Lists = Performance_inst.Read_Wiki_Log()
Standard_graphs, CIS_graphs = Performance_inst.Fill_Perform_Plots(Channel_Lists)
Performance_inst.Draw_Perform_Plot(Standard_graphs)
Performance_inst.Draw_Perform_CIS_Plot(CIS_graphs)

