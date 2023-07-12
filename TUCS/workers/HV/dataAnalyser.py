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
import sys

#from ROOT import *
import ROOT 

# insert HV tools
from src.HV.hvtools import *

class dataAnalyser(GenericWorker):
	"Evolution plots for all the variables stored in DCS"	
	
	def __init__(self, ini_Date, fin_Date, mode, do_extraPlots):
				
		self.fin_Date = fin_Date
		self.ini_Date = ini_Date		
		self.HVTool = hvtools()
		self.mode = mode
		self.do_extraPlots = do_extraPlots
		
	def ProcessStart(self):		
		
		# definition of loops limits
		print('The analysis start at', datetime.datetime.now())
		
		max_partitions, max_modules, max_channels = 4, 64, 48
		
		#for the plots
		
		ini_volt  = 450 
		end_volt = 1000
		binning_volt = (end_volt-ini_volt)*2
		 
		ini_low_volt = 0
		end_low_volt = 20
		binning_low_volt = (end_low_volt-ini_low_volt)*2
		
		ini_Dvolt     = -400.5
		end_Dvolt     = 200.5
		binning_Dvolt = abs(end_Dvolt-ini_Dvolt)
		binning_Dvolt = 5*int(binning_Dvolt)
		
		ini_ref_volt   = 1180
		end_ref_volt   = 1280
		binning_ref_volt = (end_ref_volt-ini_ref_volt)*4
		
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
		Date        = array('i',[ 0 ]) 

		MeasureType = array('i',[ 0 ])
		Channel     = array('i',[ 0 ])
		Module      = array('i',[ 0 ])
		Partition   = array('i',[ 0 ]) 
				
		tree.SetBranchAddress('Measure', Measure)
		tree.SetBranchAddress('Reference', Reference)
		tree.SetBranchAddress('Date', Date)

		tree.SetBranchAddress('MeasureType', MeasureType)
		tree.SetBranchAddress('Channel', Channel)
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
						h_ref[ipart][imod].append(TH1F("h_ref_"+chan_name," Reference Voltage ("+chan_name+"); Ref Voltage(mV); #events", binning_ref_volt, ini_ref_volt, end_ref_volt))
						h_ref[ipart][imod][ichan].SetDirectory(0)
						
						h_ref_vs_t[ipart][imod].append(TProfile("Ref_vs_t_"+chan_name,"Reference Voltage ("+chan_name+") vs Time; Day; Ref Voltage (mV)",binning_day,ini_day,end_day,ini_ref_volt,end_ref_volt))
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
		
		point = n_entries/100
		increment = n_entries/20
				
		counter = int(0)		
		while counter < n_entries:
		#while counter < 30000000:
					
			# progress bar 
			
			if (counter % (5*point) == 0):
				sys.stdout.write("\r[" + "=" * (counter / increment) +  " " * ((n_entries - counter)/ increment) + "]" +  str(counter / point) + "%")
				sys.stdout.flush()
				print('\n')
						
			tree.GetEntry(counter)				
			#print "Event", counter, "Partition = ",Partition[0], "Module = ", Module[0], "Channel = ", Channel[0], 'measureType =', MeasureType[0], 'measure = ', Measure[0], 'refe =', Reference[0]
			counter += 1
			
			measureType = MeasureType[0]
			partition = Partition[0]
			module = Module[0]-1
			channel = Channel[0]-1
			measure = Measure[0]
			reference = Reference[0]
			date = Date[0] 
			
			deltaHV = Measure[0] - Reference[0]			
						
			# Histograms concerning Temperatures			
			if measureType==1:
				if channel<7:
					h_T[partition][module][channel].Fill(measure)					
					h_T_vs_t[partition][module][channel].Fill(date,measure)					
					
					if self.do_extraPlots:	
						h_T_vs_t_mod[partition][module].Fill(date,measure)			
						h_T_vs_t_part[partition].Fill(date,measure)
						
			elif measureType==2:
				if self.HVTool.IsThisChannelInstrumented(partition,module+1,channel+1):

					h_HV[partition][module][channel].Fill(measure)		
					h_HV_vs_t[partition][module][channel].Fill(date,measure)
					
					h_HVset[partition][module][channel].Fill(reference)
					h_HVset_vs_t[partition][module][channel].Fill(date,reference)
						
					h_DHV[partition][module][channel].Fill(deltaHV)																	
					h_DHV_vs_t[partition][module][channel].Fill(date,deltaHV)			
					
					if self.do_extraPlots:
						h_DHV_part[partition].Fill(deltaHV)
						h_DHV_vs_t_part[partition].Fill(date,deltaHV)
						h_DHV_vs_t_mod[partition][module].Fill(date,deltaHV)
						
						h_HV_vs_t_part[partition].Fill(date,measure)
						h_HV_vs_t_mod[partition][module].Fill(date,measure)						
						
						if difference_date[partition][module][channel]==0:
							difference_date[partition][module][channel] = date	
						else:
							h_intertime[partition][module][channel].Fill(date-difference_date[partition][module][channel])
							h_intertime_long[partition][module][channel].Fill(date-difference_date[partition][module][channel])						
			
			elif measureType==3:
				if channel<2:
					h_ref[partition][module][channel].Fill(measure)
					h_ref_vs_t[partition][module][channel].Fill(date,measure)			
			
			elif measureType==4:
				if channel<7:
					h_LV[partition][module][channel].Fill(measure)
					h_LV_vs_t[partition][module][channel].Fill(date,measure)			
				
		# Analysis	
	
		# Computing other plots
		for ipart in range(4): # loop in all the partitions
		
			threshold_mv_mean   = 1
			threshold_RMS_mean  =  1
			
			threshold_mv_sigmas = 1
			threshold_RMS_sigmas= 1
			
			badChan_threshold_mean  = 5
			badChan_threshold_sigma = 1
							
			for imod in range(64): # loop in all the modules
				
				for ichan in range(48): # loop in all the modules
			
					if self.HVTool.IsThisChannelInstrumented(ipart,imod+1,ichan+1):
						
						if h_DHV[ipart][imod][ichan].Integral() == 0:
							continue
												
						if not self.HVTool.HasThisChannelHVData(ipart, imod, ichan, h_HV_vs_t[ipart][imod][ichan]):
							continue
						
						isGood, imu, _, _= self.HVTool.IsThisChannelGood(h_DHV[ipart][imod][ichan],ini_Dvolt, end_Dvolt, binning_Dvolt, threshold_mv_mean, threshold_RMS_mean, badChan_threshold_mean, badChan_threshold_sigma)
						if isGood:
							h_means[ipart].Fill(imu)					
			
		# Calculation of the thresholds
		
		h_means_mv = []
		h_means_rms = []
		
		h_sigmas_mv = []
		h_sigmas_rms = []

		for ipart in range(4): # loop in all the partitions		
			imean, irms = self.HVTool.MeanAndSigmaThresholds(h_means[ipart])
			#print imean, irms
			h_means_mv.append(imean)
			h_means_rms.append(irms)	
		
		for ipart in range(4): # loop in all the partitions
			for imod in range(64): # loop in all the modules
				for ichan in range(48): # loop in all the modules
						
					if self.HVTool.IsThisChannelInstrumented(ipart,imod+1,ichan+1):
						
						if h_DHV[ipart][imod][ichan].Integral() == 0:
							continue
		
						isigma = self.HVTool.SigmasThresholds(h_DHV[ipart][imod][ichan])
						#print isigma
						h_sigmas[ipart].Fill(isigma)		
			
			fit_sigmas = TF1("f2","gaus",0,10)
			h_sigmas[ipart].Fit("f2","RSQ")
			
			imean = fit_sigmas.GetParameter(1)
			irms = fit_sigmas.GetParameter(2)			
			h_sigmas_mv.append(imean)
			h_sigmas_rms.append(irms)
		
		# Separating good and bad channels
		outputFile = TFile(outDir + '/HV_HVset_plots.root', 'RECREATE')
		self.HVTool.mkdir(outDir + '/Summary')
			
		self.HVTool.FilesHeaderWriter(outDir + '/good_channels.txt',outDir + '/bad_channels.txt',outDir + '/for_latex.txt' , ini_Date, fin_Date)	
		for ipart in range(4): # loop in all the partitions
			part_name = self.HVTool.get_partition_name(ipart)
			print('Partition ', part_name, ' proceeding ...')
			
			threshold_mv_mean    = h_means_mv[ipart]
			threshold_RMS_mean   = h_means_rms[ipart]
			
			threshold_mv_sigmas  = h_sigmas_mv[ipart]
			threshold_RMS_sigmas = h_sigmas_rms[ipart]
			
			self.HVTool.PartitionHeader(part_name, threshold_mv_mean, threshold_RMS_mean, threshold_mv_sigmas, threshold_RMS_sigmas, outDir + '/good_channels.txt', outDir + '/bad_channels.txt')
															
			for imod in range(64): # loop in all the modules
				for ichan in range(48): # loop in all the modules
										
					if self.HVTool.IsThisChannelInstrumented(ipart,imod+1,ichan+1):
											
						status = 0
						
						if h_DHV[ipart][imod][ichan].Integral()==0:
							status = 4
						else:
							if not self.HVTool.HasThisChannelHVData(ipart, imod, ichan, h_HV_vs_t[ipart][imod][ichan]): 
								status = 4
							else:					
								isGood, imu, isigma, causes = self.HVTool.IsThisChannelGood(h_DHV[ipart][imod][ichan],ini_Dvolt, end_Dvolt, binning_Dvolt, threshold_mv_mean, threshold_RMS_mean, badChan_threshold_mean, badChan_threshold_sigma)
								if isGood:						
								
									isUnstable, causes_un, count_error = self.HVTool.IsThisChannelUnStable(h_DHV_vs_t[ipart][imod][ichan], imu)									
									if isUnstable:
										# Unstable channels
										status = 3
										self.HVTool.WriteBadChannel(part_name, imod+1, ichan+1, imu, isigma, outDir + '/bad_channels.txt', causes_un)
										self.HVTool.PerformDiagnosticForBadChannel(outDir + '/bad_channels.txt', h_HV[ipart][imod][ichan], h_HVset[ipart][imod][ichan], h_T[ipart][imod][5], h_ref[ipart][imod][1])
										self.HVTool.threesholdPlots_DHV(ipart, imod+1, ichan+1, imu, outputFile, h_DHV_vs_t[ipart][imod][ichan] , h_HV_vs_t[ipart][imod][ichan], h_HVset_vs_t[ipart][imod][ichan])
										
										#print part_name, imod+1, ichan+1, count_error
									else:
										# Stable and without offset channel
										status = 1
										self.HVTool.WriteGoodChannel(part_name, imod+1, ichan+1, imu, isigma, outDir + '/good_channels.txt')
										self.HVTool.WriteSummary(part_name, imod+1, ichan+1, outDir + '/short_good_channels.txt')
										self.HVTool.threesholdPlots_DHV(ipart, imod+1, ichan+1, imu, outputFile, h_DHV_vs_t[ipart][imod][ichan] , h_HV_vs_t[ipart][imod][ichan], h_HVset_vs_t[ipart][imod][ichan])
																				
										#print part_name, imod+1, ichan+1, count_error
								else:
									#  Channel with offset 
									status = 2
	
									isUnstable, causes_un, count_error = self.HVTool.IsThisChannelUnStable(h_DHV_vs_t[ipart][imod][ichan], imu)								
									if isUnstable:
										status = 3
										causes += causes_un
								
									self.HVTool.WriteBadChannel(part_name, imod+1, ichan+1, imu, isigma, outDir + '/bad_channels.txt', causes)
									self.HVTool.PerformDiagnosticForBadChannel(outDir + '/bad_channels.txt', h_HV[ipart][imod][ichan], h_HVset[ipart][imod][ichan], h_T[ipart][imod][5], h_ref[ipart][imod][1])																
									self.HVTool.offset_forLatex(part_name, imod+1, ichan+1, outDir + '/for_latex.txt' , imu, h_HV[ipart][imod][ichan], h_HVset[ipart][imod][ichan])
									self.HVTool.threesholdPlots_DHV(ipart, imod+1, ichan+1, imu, outputFile, h_DHV_vs_t[ipart][imod][ichan] , h_HV_vs_t[ipart][imod][ichan], h_HVset_vs_t[ipart][imod][ichan])
									
									#print part_name, imod+1, ichan+1, count_error				
						
						# Performing mapping for this channel
						h2_map[ipart].Fill(imod+1, ichan+1, status)						
						
						
						self.HVTool.mkdir(outDir + '/LISTS')
						date_format = time.strftime("%y%m%d", fin_Date.timetuple())
						# writes summary text files	
						if status==2:
							self.HVTool.WriteSummary(part_name, imod+1, ichan+1, outDir + '/LISTS/'+date_format+'_bad_list.txt')	
						if status==3:
							self.HVTool.WriteSummary(part_name, imod+1, ichan+1, outDir + '/LISTS/'+date_format+'_unstable_list.txt')		
						if status==4:
							self.HVTool.WriteSummary(part_name, imod+1, ichan+1, outDir + '/LISTS/'+date_format+'_noHV_list.txt')		
							

		outputFile.Close() 
	
		# Write		
		for ipart in range(4): # loop in all the partitions
			outFile.cd()			
			
			h_means[ipart].Write()
			h_sigmas[ipart].Write()
			h2_map[ipart].Write()
			
			if self.do_extraPlots:
				h_DHV_part[ipart].Write()			
				h_DHV_vs_t_part[ipart].Write()				
				h_HV_vs_t_part[ipart].Write()
				h_T_vs_t_part[ipart].Write()			
			
			for imod in range(64): # loop in all the modules
				
				if self.do_extraPlots:
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
					if self.do_extraPlots:
						h_intertime[ipart][imod][ichan].Write()
						h_intertime_long[ipart][imod][ichan].Write()
		
		outFile.Write()
		outFile.Close()		
						
	def ProcessRegion(self, region):
		if region.GetHash() == 'TILECAL':
			print("You produced the evolutions plots for HV, HVset, DHV, T, LV and refVol. The next step is perfom the HV analysis")	
			print('The analysis finished at', datetime.datetime.now())
			
