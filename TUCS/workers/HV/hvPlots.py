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
from src.oscalls import *
from src.run import *
import datetime
import time

#from ROOT import *
import ROOT

# insert HV tools
from src.HV.hvtools import *

class hvPlots(GenericWorker):
	"Make more plots"	
	
	def __init__(self, ini_Date, fin_Date, mode, mapping, allHisto, history):
				
		self.fin_Date = fin_Date
		self.ini_Date = ini_Date		
		self.HVTool = hvtools()
		self.mode = mode
		self.mapping = mapping
		self.allHisto = allHisto
		self.history = history
		
	def ProcessStart(self):		
		
		if self.mode=='RegularJob':
			outDir = os.path.join(getResultDirectory(),'HV/files/results/RegularJob')
		else:
			outDir = os.path.join(getResultDirectory(),'HV/files/results/'+ str(ini_Date))
		
		#print self.mapping, self.allHisto, self.history 
			
		if self.mapping:
			self.HVTool.MakeMapping(outDir)
		if self.allHisto:
			self.HVTool.DrawAllHistograms()
		if self.history:
			self.HVTool.historyPlots(fin_Date)
		
		self.HVTool.HVplots()	
		
	def ProcessRegion(self, region):
		if region.GetHash() == 'TILECAL':
			print('The analysis finished at', datetime.datetime.now())	
			
