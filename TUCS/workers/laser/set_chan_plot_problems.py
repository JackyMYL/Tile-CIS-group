############################################################
#
# set_chan_plot_problems.py
#
###########################################################
#
# Author: Henric
# Oct '12
#
# Input parameters are:
#
# -> limit: the maximum tolerable variation (in %). Represented by two lines
#           
# -> doEps: provide eps plots in addition to default png graphics
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas

class set_chan_plot_problems(GenericWorker):
    
    "Mark problematic channels for do_chan_plot_new"
    
    def __init__(self, problems = ['No CIS calibration']):

        self.problems  = problems


    def ProcessStart(self):
        pass


    def ProcessRegion(self, region):
        # First retrieve all the relevant partition infos

        numbers = region.GetNumber(1)

        if len(numbers)!=3:
            return

        plot = False
        for chan_region in region.GetChildren('readout'):
            for event in chan_region.GetEvents():
                if event.run.runType!='Las':
                    continue
                if 'problems' in event.data:
                    for problem in event.data['problems']:
                        if problem in self.problems:
                            # print "Found one"
                            region.data['doChanPlot'] = True
                            return

    
#    def ProcessStop(self):
#        nop
