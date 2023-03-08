############################################################
#
#dataMerger.py   
#
############################################################
#
# Author: romano <sromanos@cern.ch>
#
# Febreary 2013
#
# Goal:
# - Hadd the settings
# - Create the list of files to be merged
# - Merge the rootfiels for HV data and settings
# 
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
from dateutil import rrule

#from ROOT import *
import ROOT
import unittest
# insert HV tools

from src.HV.hvtools import *


class dataMerger2(GenericWorker):
	"Merge HV files"
	
	def __init__(self, ini_Date, fin_Date, regularJob):
				
		self.fin_Date = fin_Date
		self.ini_Date = ini_Date		
		self.HVTool = hvtools()
		self.regularJob = regularJob
		
	def ProcessStart(self):
			
		########### DEBUG #########
		Debug = 1
		Doit =  1
		###########################	
				
		# Create the folders for hadd the Set and the list of HV-Set to be merge
		
		if self.regularJob:
			typeJob = 'RegularJob'
		else:
			typeJob = 'HV_analysis'
				
		listFolder = os.path.join(getResultDirectory(),'HV/files/list/' + typeJob)
		HVFolder = os.path.join(getResultDirectory(),'HV/files/rootfiles/' + typeJob + '/HV')
		setFolder = os.path.join(getResultDirectory(),'HV/files/rootfiles/' + typeJob + '/Set')

		#self.HVTool.Doit('rm -rf ' + setFolder + '/Global', Debug, Doit)
		self.HVTool.mkdir(setFolder + '/Global')
		
		#self.HVTool.Doit('rm -rf '+listFolder, Debug, Doit)
		self.HVTool.mkdir(listFolder + '/HV')
		self.HVTool.mkdir(listFolder + '/Set')		
		
		# loop in all the partitions
		for ipart in range(4):
			# loop in all the modules
			for imod in range(64):
					
				if(imod != -1):
					continue
																
				if (imod<9):							
					strMod = '0' + str(imod+1)
				else:
					strMod = str(imod+1)
					
				module = self.HVTool.get_partition_name(ipart) 
				module += strMod
				
				# hadd the setting and create the list of rootfiles to be merged
				self.HVTool.hadd_list(typeJob, ini_Date, fin_Date, module, Debug, Doit)

		# Merger
		print('MERGE PROCESS')
		# output directory
		outputFolder = os.path.join(getResultDirectory(),'HV/files/mergefile/' + typeJob)
		self.HVTool.mkdir(outputFolder)
		
		# output file and tree
		mergeFile_name = 'HV_' + typeJob + '_Merged.root'
		outFile, tree = self.HVTool.createFileTree(outputFolder + '/' + mergeFile_name, "ZeTree")
		
		# output file tree: branches definitions		
		Measure     = array('d',[ 0 ]) 
		Reference   = array('d',[ 0 ]) 
		Day         = array('d',[ 0 ])
		
		MeasureType = array('i',[ 0 ])
		Date        = array('i',[ 0 ]) 
		Canal       = array('i',[ 0 ])
		Module      = array('i',[ 0 ])
		Partition   = array('i',[ 0 ]) 
				
		tree.Branch('Measure', Measure, 'Measure/D')
		tree.Branch('Reference', Reference,'Reference/D')
		tree.Branch('Day', Day,'Day/D')

		tree.Branch('MeasureType', MeasureType,'MeasureType/I')
		tree.Branch('Date', Date,'Date/I')
		tree.Branch('Canal', Canal,'Canal/I')
		tree.Branch('Module', Module,'Module/I')
		tree.Branch('Partition', Partition,'Partition/I')
		
		
		# loop in all the partitions
		for ipart in range(4):
			# loop in all the modules
			for imod in range(64):
			
				if (imod<9):							
					strMod = '0' + str(imod+1)
				else:
					strMod = str(imod+1)
					
				module = self.HVTool.get_partition_name(ipart) 
				module += strMod
			
				if(imod != 1):
					continue
			
				# ------------------------------------------------------Settings
				set_chain = TChain('DCS_tree')
								
				with open(listFolder+'/Set/'+module+'.list',"r") as f:
					for line in f:
						set_chain.Add(line[:-1])	
				
				# number of entries
				entries_set = set_chain.GetEntries()
				#print entries_set
				
				# TimeOrder record 
				Time_set = [ 0 for x in range(entries_set) ]
				#print Time_set
								
				# Time Setting branch recovery
				setTime = array('i',[ 0 ])
								
				if not set_chain.GetBranch("EvTime.order"):
					print(' <!> ERROR branch: EvTime.order not found ')
				else:
					set_chain.SetBranchStatus("EvTime.order", 1)
					set_chain.SetBranchAddress("EvTime.order", setTime)
					
					# Setting branches recovery 
					my_setting = [ array('f',[-200.0]) for x in range(1,49) ]								
					
					for i in range(entries_set):
						set_chain.GetEntry(i)					
						
						# Setting record						
						for set_channel in range(1,49):
							setBranch_name = "%s.hvOut%d.order" % (module, set_channel)
							#print my_setting[set_channel-1]
							
							if not set_chain.GetBranch(setBranch_name):
								print(' <!> ERROR branch: '+ setBranch_name +' not found ')
								continue
							
							set_chain.SetBranchStatus(setBranch_name, 1) 
							set_chain.SetBranchAddress(setBranch_name, my_setting[set_channel-1])
														
							#if (my_setting[i-1]>0):
								#bigSet = [ [0 for i in range(set_channel-1)] for j in range(i) ]
								#print bigSet
		
				# ------------------------------------------------------HV data			
							
				HV_chain = TChain('DCS_tree')
				
				with open(listFolder+'/HV/'+module+'.list',"r") as f1:
					for line in f1:
						for word in line.split():
							#print word
							HV_chain.Add(word)				
								
								
				# number of entries
				entries_HV = HV_chain.GetEntries()
				print(entries_HV)
								
				# time record:
				Timestamp = [ 0.0 for x in range(entries_HV) ]
				#print Timestamp
				
				Time_values = [ 0.0 for x in range(entries_HV) ]
				#print Timestamp
				
				Time_errors = [ 0.0 for x in range(entries_HV) ]
				#print Timestamp
						
				#Time branch recovery
				
				Time_ref = 788914800 # 
				day_sec = 86400
				my_Time = array('i',[0])
				
				if not HV_chain.GetBranch("EvTime"):
					print(' <!> ERROR branch: EvTime not found ')
					continue
					
				else:
					HV_chain.SetBranchStatus("EvTime", 1)
					HV_chain.SetBranchAddress("EvTime", my_Time)
					
					# Setting branches recovery 
					my_temp = [ array('f',[0.0]) for x in range(1,8) ]
					my_HVout = [ array('f',[0.0]) for x in range(1,49) ]
					my_Volt = [ array('f',[0.0]) for x in range(1,8) ]
					my_HVref = [ array('f',[0.0]) for x in range(1,3) ]
					
					# Temperature branches recovery
					for temp_channel in range(1,8):
						tempBranch_name = "%s.temp%d" % (module, temp_channel)
						#print tempBranch_name
						
						if not HV_chain.GetBranch(tempBranch_name):
							print(' <!> ERROR branch: '+ tempBranch_name +' not found ')
							continue
					
						HV_chain.SetBranchStatus(tempBranch_name, 1) 
						HV_chain.SetBranchAddress(tempBranch_name, my_temp[temp_channel-1])
									
					# HVout branches recovery
					for hv_channel in range(1,49):
						HVoutBranch_name = "%s.hvOut%d" % (module, hv_channel)
						#print HVoutBranch_name
							
						if not HV_chain.GetBranch(HVoutBranch_name):
							print(' <!> ERROR branch: '+ HVoutBranch_name +' not found ')
							continue
					
						HV_chain.SetBranchStatus(HVoutBranch_name, 1) 
						HV_chain.SetBranchAddress(HVoutBranch_name, my_HVout[hv_channel-1])
		
					# HVref branches recovery
					for hvRef_channel in range(1,3):
						hvRefBranch_name = "%s.vFix%d" % (module, hvRef_channel)
						#print hvRefBranch_name
						
						if not HV_chain.GetBranch(hvRefBranch_name):
							print(' <!> ERROR branch: '+ hvRefBranch_name +' not found ')
							continue
							
						HV_chain.SetBranchStatus(hvRefBranch_name, 1) 
						HV_chain.SetBranchAddress(hvRefBranch_name, my_HVref[hvRef_channel-1])
											
					# low voltage branches recovery
					for low_channel in range(1,3):
						lowBranch_name = "%s.volt%d" % (module, low_channel)
						#print lowBranch_name
						
						if not HV_chain.GetBranch(lowBranch_name):
							print(' <!> ERROR branch: '+ lowBranch_name +' not found ')
							continue
					
						HV_chain.SetBranchStatus(lowBranch_name, 1) 
						HV_chain.SetBranchAddress(lowBranch_name, my_Volt[low_channel-1])
												
					
					# defining Module & partition branches					
					for j in range(entries_HV):
						if not HV_chain.GetEvent(j):
							print('Error in module ', module, 'for the entry j =', j)
							continue
						else:		
							HV_chain.GetEvent(j)	
							print(HV_chain.GetEvent(j))
							
							# Time branches
							Timestamp[j] = my_Time[0]
							Date = my_Time[0] - Time_ref
							
							my_Time[0] -= Time_ref
							my_Time[0] /= day_sec
							Time_values[j] = my_Time[0]
							Time_errors[j] = 0
							
							Day = my_Time[0]
							
							Partition = ipart
							Module = imod
							
							for temp_channel in range(1,8):						
								
								# Zetree								
								Canal = temp_channel
								MeasureType = 1
								Measure = my_temp[temp_channel-1]
								Reference = 0
								tree.Fill()
								
							for hvRef_channel in range(1,3):

								# Zetree								
								Canal = hvRef_channel
								MeasureType = 3
								Measure = my_HVref[hvRef_channel-1]
								Reference = 0
								tree.Fill()
							
							for low_channel in range(1,3):
								#print "low_channel",low_channel
								# Zetree								
								Canal = low_channel
								MeasureType = 4
								Measure = my_Volt[low_channel-1]
								Reference = 0
								tree.Fill()

						
						
							
				
		outFile.Write()
		outFile.Close()
		
		
		
	def ProcessRegion(self, region):
		if region.GetHash() == 'TILECAL':
			print("You merge the rootfiles. The next step is perfom the analysis")	
		
		
		
		
