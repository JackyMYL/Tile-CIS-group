############################################################
#
# set_chan_plot_itc.py
#
############################################################
#
# Author: Henric
# Early november '12
#
# Input parameters are:
#  None
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas

class set_chan_plot_itc(GenericWorker):

    "Mark ITCs for do_chan_plot_new"
        
    def __init__(self):
        pass


    def ProcessStart(self):
        pass
    
        
    def ProcessRegion(self, region):
        # First retrieve all the relevant partition infos

        numbers = region.GetNumber()

        if len(numbers)!=3:
            return

        layername = region.GetLayerName()

        if  layername.find('MBTS')!=-1:
            region.data['doChanPlot'] = True
        
        if  layername.find('E')!=-1:
            region.data['doChanPlot'] = True

            
    def ProcessStop(self):
        return
