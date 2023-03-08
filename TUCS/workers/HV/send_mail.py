############################################################
#
#plots  
#
############################################################
#
# Author: romano <sromanos@cern.ch>
#
# May 2013
#
# Goal:
# - Produce the evolution plots for: LV, temp, reference voltage, HV, HVset and DeltaHV
#
# Input parameters are:
#
# -> Period for data recovery
#
#
#
#############################################################

from src.ReadGenericCalibration import *
from src.run import *
import datetime
import time

#from ROOT import *
import ROOT

# insert HV tools
from src.HV.hvtools import *

class send_mail(GenericWorker):
	"Make more plots"	
	
	def __init__(self):
				
		self.HVTool = hvtools()
		
	def ProcessStart(self):		
				
		self.HVTool.send_mail()	
		
	def ProcessRegion(self, region):
		if region.GetHash() == 'TILECAL':
			print('The analysis finished at')
			
