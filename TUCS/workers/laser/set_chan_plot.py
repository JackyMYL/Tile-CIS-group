############################################################
#
# set_chan_plot.py
#
############################################################
#
# Author: Henric
#
#
# Input parameters are:
#
# -> part: the partition number (1=LBA, 2=LBC, 3=EBA, 4=EBC) you want to plot.
#
# -> mod: the module number.
#
# -> chan: the channel number.
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

class set_chan_plot(GenericWorker):
    
    "Mark channel for do_chan_plot_new"

    c1 = None
    
    def __init__(self,  limit=1, part=1, mod=1, chan=0, doEps = False):
        self.doEps    = doEps
        self.part     = part
        self.mod      = mod
        self.chan     = chan


    def ProcessStart(self):
        pass

    
    def ProcessRegion(self, region):
        # First retrieve all the relevant partition infos

        numbers = region.GetNumber()

        if len(numbers)!=3:
            return

        [part, module, chan] = numbers        

        if part != self.part:
            return

        if module != self.mod:
            return

        if chan != self.chan:
            return

        region.data['doChanPlot'] = True
