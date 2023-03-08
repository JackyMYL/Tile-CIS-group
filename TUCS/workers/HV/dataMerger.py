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
from src.run import *
from src.oscalls import *
import random
import datetime
import time
import resource

#from ROOT import *
import ROOT
import unittest
# insert HV tools

from src.HV.hvtools import *


class dataMerger(GenericWorker):
	"Merge HV files"
	
	def __init__(self, ini_Date, fin_Date, mode):
				
		self.fin_Date = fin_Date
		self.ini_Date = ini_Date		
		self.HVTool = hvtools()
		self.mode = mode
		
	def ProcessStart(self):
						
		Setfolder = '/afs/cern.ch/user/t/tilehv/public/rootfiles/Or' 
		HVfolder = '/afs/cern.ch/user/t/tilehv/public/rootfiles/HV/RegularJob' 
		
		if self.mode=='RegularJob':
			listFolder = os.path.join(getResultDirectory(),'HV/files/list/RegularJob')
			outDir = os.path.join(getResultDirectory(),'HV/files/mergefile/RegularJob')
			outFile_name = 'HV_RegularJob_Merged.root'
		else:
			listFolder = os.path.join(getResultDirectory(),'HV/files/list/' + str(ini_Date))
			outDir = os.path.join(getResultDirectory(),'HV/files/mergefile/' + str(ini_Date))
			outFile_name = 'HV_' + str(ini_Date) + '_Merged.root'
										
		self.HVTool.mkdir(outDir)
		
		# output file and tree		
		outFile, tree = self.HVTool.createFileTree(outDir + '/' + outFile_name, "ZeTree")
		
		# output file tree: branches definitions		
		Measure     = array('f',[ 0 ]) 
		Reference   = array('f',[ 0 ]) 
		Date        = array('i',[ 0 ]) 

		MeasureType = array('i',[ 0 ])
		Channel       = array('i',[ 0 ])
		Module      = array('i',[ 0 ])
		Partition   = array('i',[ 0 ]) 
				
		tree.Branch('Measure', Measure, 'Measure/F')
		tree.Branch('Reference', Reference,'Reference/F')
		tree.Branch('Date', Date,'Date/I')

		tree.Branch('MeasureType', MeasureType,'MeasureType/I')
		tree.Branch('Channel', Channel,'Channel/I')
		tree.Branch('Module', Module,'Module/I')
		tree.Branch('Partition', Partition,'Partition/I')
				
		for ipart in range(4): # loop in all the partitions		
			#if not ipart==0:
			#	continue
						
			for imod in range(64): # loop in all the modules			
				#if not imod <10:
				#	continue
				
				self.merger(ipart, imod, listFolder, Measure, Reference, Date, MeasureType, Channel, Module, Partition, tree)							
						
		#print 'The merging finish at', datetime.datetime.now()
		outFile.Write()
		outFile.Close()
		
		
	def ProcessRegion(self, region):
		if region.GetHash() == 'TILECAL':
			print("You merge the rootfiles. The next step is perfom the analysis")	
		
		
	def merger(self, ipart, imod, listFolder, Measure, Reference, Date, MeasureType, Channel, Module, Partition, tree):
		while True: #The continues statement just work in a loop. This while is just a trick!
			module = self.HVTool.get_partition_name(ipart) 
			module += str(imod+1).zfill(2)
			print(module)
			a = datetime.datetime.now()	
			# ------------------------------------------------------Or
				
			chain_set = TChain('DCS_tree')								
			if os.path.exists(listFolder+'/Set/'+module+'.list'):				
				with open(listFolder+'/Set/'+module+'.list',"r") as f:
					for line in f:
						chain_set.Add(line[:-1])	
			else:
				print('Error while opening the high voltages list file !')				
				continue
						
			entries_set = chain_set.GetEntries() 
						
			new_timeSet_list = [ [] for x in range(48)] 
			new_HVset_list = [ [] for x in range(48)]							
				
			if not chain_set.GetBranch("EvTime.order"):
				print(' <!> ERROR branch: EvTime.order not found ')
				continue
				
			myTime_set = array('I',[ 0 ])
			chain_set.SetBranchAddress("EvTime.order", myTime_set)					
					
			myHV_set = [ array('f',[ -200. ]) for x in range(48) ]
			for ichan in range(48):						
				branchName_set = "%s.hvOut%d.order" % (module, ichan+1)							
				if not chain_set.GetBranch(branchName_set):
					print(' <!> ERROR branch: '+ branchName_set +' not found ')
					continue
					
				chain_set.SetBranchAddress(branchName_set, myHV_set[ichan])									
			
			for i in range(entries_set):
				chain_set.GetEntry(i)				
								
				for ichan in range(48):						
					my_set = myHV_set[ichan]
					if my_set[0]>1. and my_set[0]<1000.:								
						new_timeSet_list[ichan].append(myTime_set[0])
						new_HVset_list[ichan].append(my_set[0])
						#print module, ichan+1, myTime_set[0], myHV_set[0]
			#for ichan in range(48):
			#	print ichan, len(new_timeSet_list[ichan])		
			# ------------------------------------------------------HV data								
			HV_chain = TChain('DCS_tree')				
			with open(listFolder+'/HV/'+module+'.list',"r") as f:
				for line in f:
					for word in line.split():
						HV_chain.Add(word)								
								
			entries_HV = HV_chain.GetEntries()
			print(entries_HV)					
			#Time branch recovery
				
			my_Time = array('I',[0])
				
			if not HV_chain.GetBranch("EvTime"):
				print(' <!> ERROR branch: EvTime not found ')
				continue
					
			HV_chain.SetBranchAddress("EvTime", my_Time)					
			my_temp = [ array('f',[0]) for x in range(7) ]
			my_HVout = [ array('f',[0]) for x in range(48) ]
			my_Volt = [ array('f',[0]) for x in range(7) ]
			my_HVref = [ array('f',[0]) for x in range(2) ]
					
			# Temperature branches recovery
			for temp_channel in range(7):
				tempBranch_name = "%s.temp%d" % (module, temp_channel+1)
					
				if not HV_chain.GetBranch(tempBranch_name):
					print(' <!> ERROR branch: '+ tempBranch_name +' not found ')
					continue
					
				HV_chain.SetBranchAddress(tempBranch_name, my_temp[temp_channel])
							
			# HVout branches recovery
			for hv_channel in range(48):
				HVoutBranch_name = "%s.hvOut%d" % (module, hv_channel+1)
					
				if not HV_chain.GetBranch(HVoutBranch_name):
					print(' <!> ERROR branch: '+ HVoutBranch_name +' not found ')
					continue
			
				HV_chain.SetBranchAddress(HVoutBranch_name, my_HVout[hv_channel])
		
			# HVref branches recovery
			for hvRef_channel in range(2):
				hvRefBranch_name = "%s.vFix%d" % (module, hvRef_channel+1)
						
				if not HV_chain.GetBranch(hvRefBranch_name):
					print(' <!> ERROR branch: '+ hvRefBranch_name +' not found ')
					continue
							
				HV_chain.SetBranchAddress(hvRefBranch_name, my_HVref[hvRef_channel])
											
			# low voltage branches recovery
			for low_channel in range(7):
				lowBranch_name = "%s.volt%d" % (module, low_channel+1)
				
				if not HV_chain.GetBranch(lowBranch_name):
					print(' <!> ERROR branch: '+ lowBranch_name +' not found ')
					continue
					
				HV_chain.SetBranchAddress(lowBranch_name, my_Volt[low_channel])												
			
			#print '*- ', module, datetime.datetime.now()		
			# defining Module & partition branches					
			for j in range(entries_HV):
				if not HV_chain.GetEvent(j):
					print('Error in module ', module, 'for the entry =', j)
					continue

				HV_chain.GetEvent(j)								
					
				Date[0] = my_Time[0] - 788914800												
				Partition[0] = ipart
				Module[0] = imod + 1
													
				for temp_channel in range(7):					
							
					Channel[0] = temp_channel+1
					MeasureType[0] = 1
					temperature = my_temp[temp_channel]
					Measure[0] = temperature[0]
					Reference[0] = 0.0
					tree.Fill()
								
				for hvRef_channel in range(2):

					Channel[0] = hvRef_channel+1
					MeasureType[0] = 3
					hvRef = my_HVref[hvRef_channel]
					Measure[0] = hvRef[0]
					Reference[0] = 0.0
					tree.Fill()
							
				for low_channel in range(7):

					Channel[0] = low_channel+1
					MeasureType[0] = 4
					volt = my_Volt[low_channel]
					Measure[0] = volt[0]
					Reference[0] = 0.0
					tree.Fill()

				for hvout_channel in range(48):
					
					if not self.HVTool.IsThisChannelInstrumented(ipart,imod+1,hvout_channel+1):
						continue
						
					Channel[0] = hvout_channel+1
					MeasureType[0] = 2
					hvout = my_HVout[hvout_channel]
					Measure[0] = hvout[0]								
					Reference[0] = self.HVTool.getSet(my_Time[0], new_timeSet_list[hvout_channel], new_HVset_list[hvout_channel]) 
					tree.Fill()
				
			print('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
			b = datetime.datetime.now()
			print("Merged in", (b-a))
			return
