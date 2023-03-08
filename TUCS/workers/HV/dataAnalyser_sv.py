############################################################
#
#dataAnalyser.py   
#
############################################################
#
# Author: romano <sromanos@cern.ch>
#
# May 2013
#
# Goal:
# - Processes the analysis and the plotting
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

#from ROOT import *
import ROOT
import unittest
# insert HV tools

from src.HV.hvtools import *

class dataAnalyser_sv(GenericWorker):
	"HV Analysis"	
	
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
		
		# definition of loops limits
		
		max_partitions, max_modules, max_channels = 4, 64, 48
		
		#for the plots
		
		ini_volt      = 450
		end_volt      = 1000
		binning_volt = (end_volt-ini_volt)*2
		
		ini_low_volt = 0
		end_low_volt = 20
		binning_low_volt = (end_low_volt-ini_low_volt)*2
		
		ini_Dvolt     = -400
		end_Dvolt     = 200		
		binning_Dvolt = 5*abs(end_Dvolt-ini_Dvolt)
		
		ini_ref   = 1180
		end_ref   = 1280
		binning_ref = (end_ref-ini_ref)*4
		
		ini_temp  = 15
		end_temp  = 40
		binning_temp = (end_temp-ini_temp)*4		
		
		period = 1 #number of points per day		
		
		if self.mode=='RegularJob':
			inDir = os.path.join(getResultDirectory(),'HV/files/mergefile/RegularJob')
			outDir = os.path.join(getResultDirectory(),'HV/files/results/RegularJob')
			inFile_name = 'HV_RegularJob_Merged.root'
			
		else:
			inDir = os.path.join(getResultDirectory(),'HV/files/mergefile/' + str(ini_Date))
			outDir = os.path.join(getResultDirectory(),'HV/files/results/'+ str(ini_Date))
			inFile_name = 'HV_' + str(ini_Date) + '_Merged.root'
	
		mergedFile = TFile(inDir + '/' + inFile_name,'READ')
		tree = mergedFile.Get('ZeTree')
		
		tree.Print()
		#print tree.GetMinimun("Date")
		
		n_entries = tree.GetEntries()
		
		# output file tree: branches definitions		
		Measure     = array('f',[ 0 ]) 
		Reference   = array('f',[ 0 ]) 
		Day         = array('f',[ 0 ])
		Date        = array('i',[ 0 ]) 

		MeasureType = array('i',[ 0 ])
		Canal       = array('i',[ 0 ])
		Module      = array('i',[ 0 ])
		Partition   = array('i',[ 0 ]) 
				
		tree.SetBranchAddress('Measure', Measure)
		tree.SetBranchAddress('Reference', Reference)
		tree.SetBranchAddress('Day', Day)
		tree.SetBranchAddress('Date', Date)

		tree.SetBranchAddress('MeasureType', MeasureType)
		tree.SetBranchAddress('Canal', Canal)
		tree.SetBranchAddress('Module', Module)
		tree.SetBranchAddress('Partition', Partition)
		
		# For the evolution plots
		
		ini_day = tree.GetMinimum("Date")
		end_day = tree.GetMaximum("Date")
		binning_day = (end_day-ini_day) / (86400 * period)
		binning_day = int(round(binning_day))
	
		self.HVTool.mkdir(outDir)
		outFile = TFile(outDir + '/A_histograms.root', 'RECREATE')
	
		outFile.mkdir('DHV')
		outFile.mkdir('HV')
		outFile.mkdir('HVset')
		outFile.mkdir('T')
		outFile.mkdir('Ref')
		outFile.mkdir('LV')
		outFile.mkdir('Time')
		outFile.cd()
				
		# Lists of histograms and TProfiles:
			
		h_means, h_sigmas, h_DHV_part, h_final_DHV_part, max_diff_part, h_HV_vs_t_part, h_DHV_vs_t_part, h_T_vs_t_part, h2_map = [], [], [], [], [], [], [], [], []		
		h_HV_vs_t_mod, h_DHV_vs_t_mod, h_T_vs_t_mod = [], [], []			
		h_HV, h_HV_vs_t, h_HVset, h_HVset_vs_t, h_DHV, h_DHV_vs_t, h_T, h_T_vs_t, h_LV, h_LV_vs_t, h_ref, h_ref_vs_t = [], [], [], [], [], [], [], [], [], [], [], []
		
		difference_date, h_intertime, h_intertime_long = [], [], [] # To study the time
		
		# Histrograms declaration
		for ipart in range(4): # loop in all the partitions		
							
			part_name = self.HVTool.get_partition_name(ipart) 
			
			# histos of means
			h_means.append(TH1F("h_means_"+part_name,"All means in partition "+part_name+";#mu_{i}; #events",150,-15,15))
			h_means[ipart].SetDirectory(0)
			
			# histos of sigmas
			h_sigmas.append(TH1F("h_sigmas_"+part_name,"All sigmas in partition "+part_name+";#sigma_{i}; #events",500,0,5))
			h_sigmas[ipart].SetDirectory(0)
			
			# histos of DHV
			h_DHV_part.append(TH1F("h_DHV_"+part_name,"#DeltaHV ("+part_name+");#DeltaHV (V); #events",binning_Dvolt,ini_Dvolt,end_Dvolt))
			h_DHV_part[ipart].SetDirectory(0)
			
			# histos of DHV for good channels
			h_final_DHV_part.append(TH1F("h_final_DHV_"+part_name,"#DeltaHV ("+part_name+") for Good Channels;#DeltaHV (V); #events",binning_Dvolt,ini_Dvolt,end_Dvolt))
			h_final_DHV_part[ipart].SetDirectory(0)
			
			# histos of Max diff
			max_diff_part.append(TH1F("h_max_diff_"+part_name,"Max diff ("+part_name+");Max diff; #events",1000,0,100))
			max_diff_part[ipart].SetDirectory(0)
						
			# TProfiles of HV
			h_HV_vs_t_part.append(TProfile("HV_vs_t_"+part_name,"High Voltage ("+part_name+") vs Time; Day; HV (V)",binning_day ,ini_day,end_day,ini_volt,end_volt))
			h_HV_vs_t_part[ipart].GetXaxis().SetTimeDisplay(1)	
			h_HV_vs_t_part[ipart].SetDirectory(0)
			
			# TProfiles of DHV
			h_DHV_vs_t_part.append(TProfile("DHV_vs_t_"+part_name,"#DeltaHV ("+part_name+") vs Time; Day; #DeltaHV (V)",binning_day,ini_day,end_day,ini_Dvolt,end_Dvolt))
			h_DHV_vs_t_part[ipart].GetXaxis().SetTimeDisplay(1)	
			h_DHV_vs_t_part[ipart].SetDirectory(0)
			
			# TProfiles of Temperatures
			h_T_vs_t_part.append(TProfile("T_vs_t_"+part_name,"T ("+part_name+") vs Time; Day; T (*C)",binning_day,ini_day,end_day,ini_temp,end_temp))
			h_T_vs_t_part[ipart].GetXaxis().SetTimeDisplay(1)	
			h_T_vs_t_part[ipart].SetDirectory(0)
			
			# maps for good and bad channels
			h2_map.append(TH2F("Map_"+part_name,"Mapping of channels for partition "+part_name+";Module;Channel",max_modules+2,0,max_modules+2,max_channels+2,0,max_channels+2))
			h2_map[ipart].SetDirectory(0)
			
			h_HV_vs_t_mod.append([])	
			h_DHV_vs_t_mod.append([])
			h_T_vs_t_mod.append([])
			
			h_HV.append([])	
			h_HVset.append([])			
			h_DHV.append([])					
			h_T.append([])
			h_LV.append([])
			h_ref.append([])
			h_intertime.append([])
			h_intertime_long.append([])
			
			h_HV_vs_t.append([])
			h_HVset_vs_t.append([])
			h_DHV_vs_t.append([])
			h_T_vs_t.append([])
			h_LV_vs_t.append([])			
			h_ref_vs_t.append([])
			
			difference_date.append([])
			for imod in range(64): # loop in all the modules			
			
				mod_name = part_name + str(imod+1).zfill(2)
				
				# TProfiles of HV
				h_HV_vs_t_mod[ipart].append(TProfile("HV_vs_t_"+mod_name,"High Voltage ("+mod_name+") vs Time; Day; HV (V)",binning_day ,ini_day,end_day,ini_volt,end_volt))
				h_HV_vs_t_mod[ipart][imod].GetXaxis().SetTimeDisplay(1)	
				h_HV_vs_t_mod[ipart][imod].SetDirectory(0)
			
				# TProfiles of DHV
				h_DHV_vs_t_mod[ipart].append(TProfile("DHV_vs_t_"+mod_name,"#DeltaHV ("+mod_name+") vs Time; Day; #DeltaHV (V)",binning_day,ini_day,end_day,ini_Dvolt,end_Dvolt))
				h_DHV_vs_t_mod[ipart][imod].GetXaxis().SetTimeDisplay(1)	
				h_DHV_vs_t_mod[ipart][imod].SetDirectory(0)
			
				# TProfiles of Temperatures
				h_T_vs_t_mod[ipart].append(TProfile("T_vs_t_"+mod_name,"T ("+mod_name+") vs Time; Day; T (*C)",binning_day,ini_day,end_day,ini_temp,end_temp))
				h_T_vs_t_mod[ipart][imod].GetXaxis().SetTimeDisplay(1)	
				h_T_vs_t_mod[ipart][imod].SetDirectory(0)
				
				h_HV[ipart].append([])
				h_HVset[ipart].append([])							
				h_DHV[ipart].append([])					
				h_T[ipart].append([])
				h_LV[ipart].append([])
				h_ref[ipart].append([])
				h_intertime[ipart].append([])
				h_intertime_long[ipart].append([])				
				
				h_HV_vs_t[ipart].append([])
				h_HVset_vs_t[ipart].append([])
				h_DHV_vs_t[ipart].append([])
				h_T_vs_t[ipart].append([])
				h_LV_vs_t[ipart].append([])
				h_ref_vs_t[ipart].append([])
				
				difference_date[ipart].append([])
				for ichan in range(48): # loop in all the channels
															
					chan_name = mod_name + '_' + str(ichan+1).zfill(2)
					
					if self.HVTool.IsThisChannelInstrumented(ipart,imod+1,ichan+1):						
												
						# HV
						h_HV[ipart][imod].append(TH1F("h_HV_"+chan_name,"High Voltage ("+chan_name+"); HV (V); #events", binning_volt, ini_volt, end_volt))
						h_HV[ipart][imod][ichan].SetDirectory(0)
						
						h_HV_vs_t[ipart][imod].append(TProfile("HV_vs_t_"+chan_name,"High Voltage ("+chan_name+") vs Time; Day; HV (V)", binning_day, ini_day,end_day, ini_volt,end_volt))
						h_HV_vs_t[ipart][imod][ichan].GetXaxis().SetTimeDisplay(1)	
						h_HV_vs_t[ipart][imod][ichan].SetDirectory(0)
						
						# DHV
						h_DHV[ipart][imod].append(TH1F("h_DHV_"+chan_name,"#DeltaHV ("+chan_name+"); #DeltaHV (V); #events", binning_Dvolt, ini_Dvolt, end_Dvolt))
						#print h_DHV[ipart][imod][ichan]
						h_DHV[ipart][imod][ichan].SetDirectory(0)
						
						h_DHV_vs_t[ipart][imod].append(TProfile("DHV_vs_t_"+chan_name,"#DeltaHV ("+chan_name+") vs Time; Day; #DeltaHV (V)",binning_day,ini_day,end_day,ini_Dvolt,end_Dvolt))
						h_DHV_vs_t[ipart][imod][ichan].GetXaxis().SetTimeDisplay(1)	
						h_DHV_vs_t[ipart][imod][ichan].SetDirectory(0)
						
						# Setting
						h_HVset[ipart][imod].append(TH1F("h_HVset_"+chan_name,"#Requested HV ("+chan_name+"); HVset (V); #events", binning_volt, ini_volt, end_volt))
						h_HVset[ipart][imod][ichan].SetDirectory(0)
						
						h_HVset_vs_t[ipart][imod].append(TProfile("HVset_vs_t_"+chan_name,"Requested HV ("+chan_name+") vs Time; Day; HVset (V)",binning_day,ini_day,end_day,ini_volt,end_volt))
						h_HVset_vs_t[ipart][imod][ichan].GetXaxis().SetTimeDisplay(1)	
						h_HVset_vs_t[ipart][imod][ichan].SetDirectory(0)
		
						
					else:
						# fill with strings the channels that are not intrumented
						h_HV[ipart][imod].append('no instrumented channel')
						h_HV_vs_t[ipart][imod].append('no instrumented channel')
						h_DHV[ipart][imod].append('no instrumented channel')
						h_DHV_vs_t[ipart][imod].append('no instrumented channel')
						h_HVset[ipart][imod].append('no instrumented channel')
						h_HVset_vs_t[ipart][imod].append('no instrumented channel')
						
						
					if ichan<7:
				
						# There are 7 probes for the measurement of the temp						
						h_T[ipart][imod].append(TH1F("h_T_"+chan_name,"T ("+chan_name+"); T (*C); #events", binning_temp, ini_temp, end_temp))
						h_T[ipart][imod][ichan].SetDirectory(0)
						
						h_T_vs_t[ipart][imod].append(TProfile("T_vs_t_"+chan_name,"T ("+chan_name+") vs Time; Day; T (*C)",binning_day,ini_day,end_day,ini_temp,end_temp))
						h_T_vs_t[ipart][imod][ichan].GetXaxis().SetTimeDisplay(1)	
						h_T_vs_t[ipart][imod][ichan].SetDirectory(0)
						
						# There are 7 values of low voltage
						h_LV[ipart][imod].append(TH1F("h_LV_"+chan_name,"Low Voltage ("+chan_name+"); Low Voltage (mV); #events", binning_low_volt, ini_low_volt, end_low_volt))
						h_LV[ipart][imod][ichan].SetDirectory(0)
						
						h_LV_vs_t[ipart][imod].append(TProfile("LV_vs_t_"+chan_name,"Low Voltage ("+chan_name+") vs Time; Day; Low Voltage (mV)",binning_day,ini_day,end_day,ini_low_volt,end_low_volt))
						h_LV_vs_t[ipart][imod][ichan].GetXaxis().SetTimeDisplay(1)	
						h_LV_vs_t[ipart][imod][ichan].SetDirectory(0)
						
					
					if ichan<2:
				
						# There are 2 values for the reference voltage						
						h_ref[ipart][imod].append(TH1F("h_ref_"+chan_name," Reference Voltage ("+chan_name+"); Ref Voltage(mV); #events", binning_ref, ini_ref, end_ref))
						h_ref[ipart][imod][ichan].SetDirectory(0)
						
						h_ref_vs_t[ipart][imod].append(TProfile("Ref_vs_t_"+chan_name,"Reference Voltage ("+chan_name+") vs Time; Day; Ref Voltage (mV)",binning_day,ini_day,end_day,ini_ref,end_ref))
						h_ref_vs_t[ipart][imod][ichan].GetXaxis().SetTimeDisplay(1)	
						h_ref_vs_t[ipart][imod][ichan].SetDirectory(0)
			
					
					difference_date[ipart][imod].append([])
					difference_date[ipart][imod][ichan] = 0
					
					h_intertime[ipart][imod].append(TH1F(chan_name+"_inter_time", "Time difference between two consecutive measurements ("+chan_name+"); #Deltat (s); #events", 600,0,600))
					h_intertime[ipart][imod][ichan].SetDirectory(0)
					h_intertime_long[ipart][imod].append(TH1F(chan_name+"_inter_time_long" , "Time difference between two consecutive measurements ("+chan_name+"); #Deltat (s); Events", 588,0,84640))
					h_intertime_long[ipart][imod][ichan].SetDirectory(0)	
					
			
		#Fill Histograms
		print(n_entries)		
		
		for ievt in range(n_entries):
		#for ievt in range(1,1000):
			
			if ievt%1000000 == 0:
				percent =  1.0*(ievt/n_entries)
				percent *= 100
				print('Event', ievt, 'processing ... ', percent, '% done') 
				
			tree.GetEntry(ievt)			
				
			print("Event", ievt, "Partition = ",Partition[0], "Module = ", Module[0], "Channel = ", Canal[0], 'measureType =', MeasureType[0], 'measure = ', Measure[0], 'refe =', Reference[0])
			
			partition = Partition[0]
			module = Module[0]-1
			channel = Canal[0]-1
			date = Date[0]
			measureType = MeasureType[0]			
			measure = Measure[0]
			
			# Histograms concerning Temperatures			
			if MeasureType[0]==1:
				if channel<7:	
					h_T[partition][module][channel].Fill(measure)					
					h_T_vs_t[partition][module][channel].Fill(date,Measure[0])
					h_T_vs_t_mod[partition][module].Fill(date,Measure[0])				
					h_T_vs_t_part[partition].Fill(date,Measure[0])
					
			
			elif MeasureType[0]==2:
				if self.HVTool.IsThisChannelInstrumented(partition,module+1,channel+1):
					
					h_DHV_part[partition].Fill(Measure[0]-Reference[0])
					h_HV_vs_t_part[partition].Fill(date,Measure[0])
					h_DHV_vs_t_part[partition].Fill(date,Measure[0]-Reference[0])
							
					h_HV_vs_t_mod[partition][module].Fill(date,Measure[0])
					h_DHV_vs_t_mod[partition][module].Fill(date,Measure[0]-Reference[0])
					
					h_HV_vs_t[partition][module][channel].Fill(date,Measure[0])
					h_HVset_vs_t[partition][module][channel].Fill(date,Reference[0])
					h_DHV_vs_t[partition][module][channel].Fill(date,Measure[0]-Reference[0])				
					
					h_HV[partition][module][channel].Fill(Measure[0])
					h_HVset[partition][module][channel].Fill(Reference[0])
					h_DHV[partition][module][channel].Fill(Measure[0]-Reference[0])
			
						
					if difference_date[partition][module][channel]==0:
						difference_date[partition][module][channel] = date	
					else:
						h_intertime[partition][module][channel].Fill(date-difference_date[partition][module][channel])
						h_intertime_long[partition][module][channel].Fill(date-difference_date[partition][module][channel])
						
			elif MeasureType[0]==3:
				if channel<2:
					h_ref[partition][module][channel].Fill(Measure[0])
					h_ref_vs_t[partition][module][channel].Fill(date,Measure[0])
			
			elif MeasureType[0]==4:
				if channel<7:
					h_LV[partition][module][channel].Fill(Measure[0])
					h_LV_vs_t[partition][module][channel].Fill(date,Measure[0])
		
		
		# Write		
		for ipart in range(4): # loop in all the partitions
			outFile.cd()
			
			h_T_vs_t_part[ipart].Write()
			h_DHV_part[ipart].Write()
			h_HV_vs_t_part[ipart].Write()
			h_DHV_vs_t_part[ipart].Write()
			
			for imod in range(64): # loop in all the modules
				
				outFile.cd('HV/')
				h_HV_vs_t_mod[ipart][imod].Write()
				outFile.cd('DHV/')
				h_DHV_vs_t_mod[ipart][imod].Write()
				outFile.cd('T/')
				h_T_vs_t_mod[ipart][imod].Write()
						
				for ichan in range(48): # loop in all the channels
					
					if self.HVTool.IsThisChannelInstrumented(ipart,imod+1,ichan+1):
						outFile.cd("HV/")
						h_HV[ipart][imod][ichan].Write()
						h_HV_vs_t[ipart][imod][ichan].Write()
						
						outFile.cd('DHV/')
						h_DHV[ipart][imod][ichan].Write()
						h_DHV_vs_t[ipart][imod][ichan].Write()
						
						outFile.cd('HVset/')
						h_HVset[ipart][imod][ichan].Write()
						h_HVset_vs_t[ipart][imod][ichan].Write()
					
					if ichan<7:
						outFile.cd("T/")							
						h_T[ipart][imod][ichan].Write()
						h_T_vs_t[ipart][imod][ichan].Write()	
					
					if ichan<2:
						outFile.cd('Ref/')
						h_ref[ipart][imod][ichan].Write()
						h_ref_vs_t[ipart][imod][ichan].Write()
			
					if ichan<7:
						outFile.cd('LV/')
						h_LV[ipart][imod][ichan].Write()
						h_LV_vs_t[ipart][imod][ichan].Write()
					
					outFile.cd('Time/')
					h_intertime[ipart][imod][ichan].Write()
					h_intertime_long[ipart][imod][ichan].Write()
		
		outFile.Write()
		outFile.Close()
					
	def ProcessRegion(self, region):
		if region.GetHash() == 'TILECAL':
			print("You produce the evolutions plots for HV, HVset, DHV, T, LV and refVol. The next step is perfom the HV analysis")	
		
