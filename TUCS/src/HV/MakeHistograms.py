#------------------------------------------------------------------------ 
#                     HISTOGRAMS BUILDER.CXX
#
# 
#  Tasks :
#     - builds all histograms for all channels, modules and partition
#     - fills all histograms for HV, Temperature, LV and Ref Voltages
#     - writes them in the output file
#
#  Author:
#     sromanos
#        
#  -----------------------------------------------------------------------

import os
import datetime
import time

from ROOT import *
from src.HV.hvtools import *

class MakeHistograms:

	def HistoCreator(self):		
		
		for ipart in range(4): # loop in all the partitions
			
			h_means = TH1D("h_means_"+repr(ipart)+"","All means in partition "+repr(ipart)+";#mu_{i};#events",150,-15,15)
			h_means.SetDirectory(0)
			print(ipart)





