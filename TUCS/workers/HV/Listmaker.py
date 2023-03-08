############################################################
#
#Listmaker.py   
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
# 
# Input parameters are:
#
# -> Period for data recovery
# 
# -> Option to read the rotfiles from tileHV or from the local folder
#
#
#############################################################

from src.ReadGenericCalibration import *
from src.run import *
from src.oscalls import *
import random
import datetime
import time
from dateutil import rrule

#from ROOT import *
import unittest
# insert HV tools

from src.HV.hvtools import *


class Listmaker(GenericWorker):
	"Merge HV files"
	
	def __init__(self, ini_Date, fin_Date, mode):
				
		self.fin_Date = fin_Date
		self.ini_Date = ini_Date		
		self.HVTool = hvtools()
		self.mode = mode
		
	def ProcessStart(self):
			
		########### DEBUG #########
		Debug = -1
		Doit =  1
		###########################	
		
		# Create the folders for hadd the Set and the list of HV-Set to be merge				
		
		Setfolder = '/afs/cern.ch/user/t/tilehv/public/rootfiles/Or' 
		HVfolder = '/afs/cern.ch/user/t/tilehv/public/rootfiles/HV/RegularJob' 
		
		if self.mode=='RegularJob':
			listFolder = os.path.join(getResultDirectory(),'HV/files/list/RegularJob')
		else:
			listFolder = os.path.join(getResultDirectory(),'HV/files/list/' + str(ini_Date))
		
		globFolder = os.path.join(getResultDirectory(),'HV/files/rootfiles/Set/Global')
		self.HVTool.mkdir(globFolder)
		self.HVTool.mkdir(listFolder + '/HV')
		self.HVTool.mkdir(listFolder + '/Set')	
		
		self.HVTool.Doit('rm -f ' + listFolder + '/HV/*', Debug, Doit)
		self.HVTool.Doit('rm -f ' + listFolder + '/Set/*', Debug, Doit)
		self.HVTool.Doit('rm -f ' + globFolder + '/*', Debug, Doit)	
		
		ini_Date_set = datetime.date(2014, 1, 1)
		day_interval = (fin_Date - ini_Date).days + 1
		
		for ipart in range(4): # loop in all the partitions
			#if not ipart==0:
			#	continue		
			for imod in range(64): # loop in all the modules					
				#if not imod<10:
				#	continue				
				
				a = datetime.datetime.now()
				#create the setting rootfiles to be merged
				self.new_settings(ipart, imod, ini_Date_set, self.fin_Date, Setfolder)
				
				mod_name = self.HVTool.get_partition_name(ipart) + str(imod+1).zfill(2)					
				txt_file = open(listFolder+'/HV/'+mod_name+'.list',"w")				
				for idate in (ini_Date + timedelta(n) for n in range(day_interval)): 
		
					iday = time.strftime("%d", idate.timetuple())
					imonth = time.strftime("%m", idate.timetuple())
					iyear = time.strftime("%y", idate.timetuple())

					# list of HV data to be merged
					if os.path.exists(HVfolder+'/20'+iyear+'/'+imonth+'/'+mod_name+'.'+iyear+imonth+iday+'.root'):
						fileInput = TFile(HVfolder+'/20'+iyear+'/'+imonth+'/'+mod_name+'.'+iyear+imonth+iday+'.root',"READ")
						treeInput = fileInput.Get("DCS_tree")
						if treeInput.GetEntries()>10:										
							txt_file.write(HVfolder+'/20'+iyear+'/'+imonth+'/'+mod_name+'.'+iyear+imonth+iday+'.root'+'\n')
					
				txt_file.close()

				# list of Setting
				self.HVTool.Doit('ls ' + globFolder + '/' + mod_name + '.root > ' + listFolder + '/Set/' + mod_name + '.list', Debug, Doit)
				b = datetime.datetime.now()
				print("produce list ", (b-a))
				
	def ProcessRegion(self, region):
		if region.GetHash() == 'TILECAL':
			print("You create the list of the HV and HVset files to be merged in a single rootfile"	)
	
	
	def new_settings(self, ipar, imod, ini_Date, fin_Date, Setfolder):

		while True: #The continues statement just work in a loop. This while is just a trick!
		
			#Setfolder = '/afs/cern.ch/user/t/tilehv/public/rootfiles/Or'
			day_interval = (fin_Date - ini_Date).days + 1
			part_name = ["EBA","EBC","LBA","LBC"]
	
			mod_name = part_name[ipar] + str(imod+1).zfill(2)
			print(mod_name)		
			HVset_list = []
			time_list = []
			time_all_list = []
		
			for idate in (ini_Date + datetime.timedelta(n) for n in range(day_interval)):
			
				temp = idate.timetuple()
				iday = time.strftime("%d", temp)
				imonth = time.strftime("%m", temp)
				iyear = time.strftime("%y", temp)
				date = time.strftime("%y-%m-%d", temp)				
		
				if os.path.exists(Setfolder+'/20'+iyear+'/'+imonth+'/'+mod_name+'.'+iyear+imonth+iday+'.root'):
				
					rootfile = TFile(Setfolder+'/20'+iyear+'/'+imonth+"/"+mod_name+'.'+iyear+imonth+iday+'.root',"READ")
					treeInput = rootfile.Get("DCS_tree")								
				
					if treeInput.GetEntries()<=1:
						#print ' <!> ERROR GetEntrie= ',treeInput.GetEntries()
						rootfile.Close()
						continue
													
					if not treeInput.GetBranch("EvTime.order"):
						#print ' <!> ERROR branch: EvTime.order not found '
						rootfile.Close()
						continue
				
					myTime_set = array('l',[ 0 ])
					treeInput.SetBranchAddress("EvTime.order", myTime_set)
			
					myHV_set = [ array('f',[ -200. ]) for x in range(48) ]

					for ichan in range(48):	
													
						HVset_list.append([])
						time_list.append([])	
								
						branchName_set = mod_name +".hvOut"+str(ichan+1)+".order"						
						if not treeInput.GetBranch(branchName_set):
							#print ' <!> ERROR branch: '+ branchName_set +' not found '
							continue
						treeInput.SetBranchAddress(branchName_set, myHV_set[ichan])
					
					for i in range(treeInput.GetEntries()):
						treeInput.GetEntry(i)				
						time_all_list.append(myTime_set[0])
						#print myTime_set[0]				
						for ichan in range(48):
															
							branchName_set = mod_name +".hvOut"+str(ichan+1)+".order"
							if treeInput.GetBranch(branchName_set):						
								my_set = myHV_set[ichan]
								if my_set[0]>10. and my_set[0]<1000.:
									#print myTime_set[0], my_set[0]
									HVset_list[ichan].append(my_set[0])
									#time_list[ichan].append(myTime_set[0])	
								else:
									HVset_list[ichan].append(0)
							else:
								HVset_list[ichan].append(0)
					
						
					rootfile.Close()
				
			print(len(HVset_list[4]))
			print(len(HVset_list[3]))
			print(len(time_all_list))
		
			# create the output rootfile
			
			globFolder = os.path.join(getResultDirectory(),'HV/files/rootfiles/Set/Global')
			mod_name = part_name[ipar] + str(imod+1).zfill(2)
			output = TFile(globFolder+'/'+mod_name+'.root',"RECREATE")
			tree = TTree("DCS_tree","DCS_tree")
		
			time_stamp   = array('i',[ 0 ])			
			tree.Branch('EvTime.order' , time_stamp, 'EvTime.order/I')
			
			branch = [ array('f',[ 0 ]) for x in range(48) ]
			for ichan in range(48):
					
				branchName_set = mod_name +".hvOut"+str(ichan+1)+".order"
				tree.Branch(branchName_set , branch[ichan], branchName_set+'/F')
	
													
			for i in range(len(time_all_list)):
				time_stamp[0] = time_all_list[i]
				#print time_stamp[0]
				for ichan in range(48):
					
					#print branch[ichan], HVset_list[ichan][i]
					branch[ichan][0] = HVset_list[ichan][i]
				tree.Fill()
			
			output.Write()
			output.Close()
	
			print('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
			return	
	
	
