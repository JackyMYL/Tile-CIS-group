############################################################
#
#dataTaker.py  
#
############################################################
#
# Author: romano <sromanos@cern.ch>
#
# Febreary 2013
#
# Goal:
#
# - Download data and settings for a given period
# 
# - Read the tuples from tileHV account
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
import random
import datetime
import time

# insert HV tools

from src.HV.hvtools import *
from src.HV.grabHV.TileDCSDataPlotter import *
from src.HV.grabSet.TileDCSDataPlotter import *


class dataTaker(GenericWorker):
	"Recover HV files from oracle database"
	
	def __init__(self, ini_Date, fin_Date, mode):
						
		self.fin_Date = fin_Date
		self.ini_Date = ini_Date		
		self.HVTool = hvtools()
		self.mode = mode
		
	def ProcessStart(self):
	
		########### DEBUG #########
		Debug = 1
		Doit =  1
		###########################
	
		# create the repertory for the HV and HVset
		
		HVfolder = os.path.join(getResultDirectory(),'HV/files/rootfiles/')
						
		#loop in dates between ini_Date and fin_Date		
		day_interval = (fin_Date - ini_Date).days + 1
		for idate in (ini_Date + timedelta(n) for n in range(day_interval)): 
			
			for ipart in range(4): # loop in all the partitions
				
				for imod in range(64): # loop in all the modules
					
					for Type in ['HV','Or']:
						
						if (imod!=1):
							continue
					
						module = self.HVTool.get_partition_name(ipart) 
						module += str(imod+1).zfill(2)								
															
						iyear = time.strftime("%y", idate.timetuple())
						imonth = time.strftime("%m", idate.timetuple())
						iday = time.strftime("%d", idate.timetuple())
						
						path = Type 						
						if Type=='HV':
							if mode=='RegularJob':
								path += '/' + mode
							else: 
								path += '/' + str(ini_Date) 						
						
						path += '/20' + iyear + '/' + imonth + '/'
						rootfile = module + '.' + iyear + imonth + iday 
						
						self.HVTool.mkdir( HVfolder + path )
						
						if not os.path.exists( HVfolder + path + rootfile + '.root' ):
														
							recoveryCommand = 'python ./src/HV/grab' + Type + '/TileDCSDataPlotter.py tree ' + module + ' "ALL_HV,ALL_LVPS_STATES" '
							recoveryCommand += '"20' + iyear + '-' + imonth + '-' + iday + ' 00:00:00" "20' + iyear + '-' + imonth + '-' + iday + ' 23:59:59" "" ' 
							recoveryCommand +=  HVfolder + path + rootfile							
							self.HVTool.Doit(recoveryCommand, Debug, Doit)	
						else:
							print('file', os.path.basename(path + '.root'), 'it was already recovered ')
							
									
											
		
	def ProcessRegion(self, region):
		if region.GetHash() == 'TILECAL':
			print("You copy the rootfiles. The next step is the merging")	
		
		
		
		
		
		
		
		
		
		
			
