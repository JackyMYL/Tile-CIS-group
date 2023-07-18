# Author: Seb Viret <viret@in2p3.fr>
#
# February 2013
# Silvestre Romano

import datetime
import time
from array import array
import math
import smtplib  
from src.oscalls import *
#from email.MIMEMultipart import MIMEMultipart  
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from email.MIMEText import MIMEText
#from email.MIMEBase import MIMEBase
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.utils import COMMASPACE, formatdate  
from email import encoders  
#from ROOT import *
import ROOT
import resource

class hvtools:
	"This is the hv toolbox"
	
	def Doit(self, com, Debug=-1, Doit=-1):
		if Debug==1: print(com)
		if Doit==1: os.system(com)
		return
		
	def mkdir(self, path):
		if not os.path.exists(path):
			os.system('mkdir -p '+ path)
			print('folder created: ', path)
		return		
	
	def get_partition_name(self,part):
		part_names = ['EBA','EBC','LBA','LBC']
		return part_names[part]		
		
	def createFileTree(self, fileName, treeName):
		f, t = [None, None]
		f = TFile.Open(fileName, "recreate")
		t = TTree(treeName,treeName)
		return [f, t]

	def getSet(self, my_Time, timeSet_list, HVset_list ):		
		reference = 0.
		
		#print timeSet_list[0], my_Time
			
		if (my_Time <= timeSet_list[0]):
			reference = HVset_list[0]
			return reference
		
		#print len(HVset_list)
		for i in range(len(HVset_list)):
			if (my_Time <= timeSet_list[i]):
				reference = HVset_list[i-1]
				return reference
			else:
				reference = HVset_list[i]
		
		return reference	
		
	def IsThisChannelInstrumented(self, part, mod, chan):	
		
		#In EBA and EBC non instrumented channels: 19 20 25 26 27 28 31 32 35 36 39 40 45 46 47 48 Exception for EBA15 and EBC 18	
		if (part==0 or part==1):
			if (part==0 and mod==15):
				if chan in [1,2,3,4,25,26,27,28,31,32,35,36,39,40,45,46,47,48]:
					return False
				else:
					return True
			
			elif (part==1 and mod==18):
				if chan in [1,2,3,4,25,26,27,28,31,32,35,36,39,40,45,46,47,48]:
					return False
				else:
					return True
					
			else:
				if chan in [19,20,25,26,27,28,31,32,35,36,39,40,45,46,47,48]:
					return False
				else:
					return True
							
		#In LBA and LBC non instrumented channels: 32 33 44	
		if (part==2 or part==3):
			if chan in [32,33,44]:
				return False
			else:
				return True		
		
	def Translation_PMT_to_Channel(self, ipmt, ipart):
		channel = -800
		
		if ipmt<=24:
			channel = ipmt-1
		else:
			if ipmt>18:
				if (ipart==2 or ipart==3):
					if ipmt==27:
						channel=24
					elif ipmt==26:
						channel=25
					elif ipmt==25:
						channel=26
					elif ipmt==30:
						channel=27
					elif ipmt==29:
						channel=28
					elif ipmt==28:
						channel=29
					elif ipmt==33:
						channel=30
					elif ipmt==32:
						channel=31
					elif ipmt==31:
						channel=32
					elif ipmt==36:
						channel=33
					elif ipmt==35:
						channel=34
					elif ipmt==34:
						channel=35
					elif ipmt==39:
						channel=36
					elif ipmt==38:
						channel=37
					elif ipmt==37:
						channel=38
					elif ipmt==42:
						channel=39						
					elif ipmt==41:
						channel=40	
					elif ipmt==40:
						channel=41	
					elif ipmt==45:
						channel=42	
					elif ipmt==44:
						channel=43	
					elif ipmt==43:
						channel=44	
					elif ipmt==48:
						channel=45	
					elif ipmt==47:
						channel=46	
					elif ipmt==46:
						channel=47		
				else:
					if (ipart==2 or ipart==3):
						if ipmt==27:
							channel=24
						elif ipmt==26:
							channel=25
						elif ipmt==25:
							channel=26
						elif ipmt==31:
							channel=27
						elif ipmt==32:
							channel=28
						elif ipmt==28:
							channel=29
						elif ipmt==33:
							channel=30
						elif ipmt==29:
							channel=31
						elif ipmt==30:
							channel=32
						elif ipmt==36:
							channel=33
						elif ipmt==35:
							channel=34
						elif ipmt==34:
							channel=35
						elif ipmt==44:
							channel=36
						elif ipmt==38:
							channel=37
						elif ipmt==37:
							channel=38
						elif ipmt==43:
							channel=39						
						elif ipmt==42:
							channel=40	
						elif ipmt==41:
							channel=41	
						elif ipmt==45:
							channel=42	
						elif ipmt==39:
							channel=43	
						elif ipmt==40:
							channel=44	
						elif ipmt==48:
							channel=45	
						elif ipmt==47:
							channel=46	
						elif ipmt==46:
							channel=47			
						
						
		return channel						
						
	def IsThisAKnownGoodChannel(self, part, mod, chan):		
		# this function will help to exclude channels in case of any kind of issue. For the moment it will return True for all the channels!
		
		return True		
		
	def HasThisChannelHVData(self, part, mod, chan, histo):	
		if (histo.GetBinContent(histo.GetNbinsX())==0) and (histo.GetBinContent(histo.GetNbinsX()-1)==0) and (histo.GetBinContent(histo.GetNbinsX()-2)==0):
			return False
		else:
			return True			
	
	def IsThisChannelGood(self, histo, ini_Dvolt, end_Dvolt, binning_Dvolt, threshold_mv_mean, threshold_RMS_mean, bad_channel_threshold_mean, bad_channel_threshold_sigma):
		
		max_value = 0.
		max_bin = 0.
		
		# initial values
		mean_value = -1000
		RMS_value = -1000
		
		for bin in range(1,histo.GetNbinsX()):
			content = histo.GetBinContent(bin)
			if(content>max_value):
				max_value = content
				max_bin   = histo.GetBinCenter(bin)				
				
		# Chekcs for the number of bins (sufficient for the fit)				
		first_entry = True		
		first_non_empty_bin = 0
		non_empty_bins = 0		
		
		for bin in range(1,histo.GetNbinsX()):
			content = histo.GetBinContent(bin)
			if(content>0):
				if(first_entry):
					first_non_empty_bin = bin
					first_entry = False				
				
				non_empty_bins += 1					
				
		consecutive = True
		if(non_empty_bins<=3):		
			# In case the number of non empty bins is lower or equal to 3
			# Checks is thses bins are consecutive	
			
			first_non_empty_bin+non_empty_bins
			for bin in range(first_non_empty_bin,first_non_empty_bin+non_empty_bins):	
				content = histo.GetBinContent(bin)
				if(content<0.001):
					consecutive = False
					break
		
		if(non_empty_bins<=3 and consecutive):
			histo.GetXaxis().SetRangeUser(max_bin-20, max_bin+20)
			mu = histo.GetMean()
			sigma  = histo.GetRMS()
		else:
			fit_fct = TF1("f1","gaus",max_bin-0.5,max_bin+0.5)    
			fit_fct.SetParameter(1,max_bin)
			fit_fct.SetParLimits(0,max_value/1.5,max_value*1.5)
			histo.Fit("f1","RLSQ")
    			#histo.GetFunction('f1').SetLineColor(kRed)						
			
			mu = fit_fct.GetParameter(1)
			sigma  = fit_fct.GetParameter(2)
			
			histo.GetXaxis().SetRangeUser(mu-10*sigma,mu+10*sigma)
			
		causes = ''
		#TOO LARGE DeltaHV
		if(math.fabs(mu-threshold_mv_mean)> bad_channel_threshold_mean*threshold_RMS_mean):
			causes += 'Offset '		
		
		#TOO LARGE RMS of the distribution
		if( sigma > 0.5 ):
			causes += 'Dispersion '
		
		if len(causes)==0:
			return True, mu, sigma, causes
		else:
			return False, mu, sigma, causes		
		
	def IsThisChannelUnStable(self, tprofile, MeanY):
		
		# Threshold definition
		threshold = 0.5
		times = 5 # number of points that can be > thresholds
		
		# Calculates the mean value of the distribution on time
		# Draws two lines corresponding to +- 0.5 V arround the mean value
		
		if( (tprofile.GetMaximum() - tprofile.GetMinimum()) < 3*threshold):
			tprofile.SetMaximum(MeanY+2*threshold)
			tprofile.SetMinimum(MeanY-2*threshold)
		
		
		# Defines criterium to tag unstable a channel
		count_error = 0
		Max = 0
		
		for i in range(tprofile.GetXaxis().GetNbins()-30, tprofile.GetXaxis().GetNbins()):
			content = tprofile.GetBinContent(i)
			temp = math.fabs(content-MeanY)
			if(temp>Max):
				Max = temp
		
			if math.fabs(content-MeanY)>threshold:
				if not content==0:
	     				 count_error += 1
		
		causes = ''		
		if(count_error>times):
    			causes += 'UNSTABLE'
    			return True, causes, count_error
		else:
			return False, causes, count_error	
	
	def MeanAndSigmaThresholds(self, h_means):
		
		#temp_mean corresponds to the all channels addition of histograms
			
		max_value = 0.
		max_bin = 0
		#print h_means[ipart].GetNbinsX()
			
		for bin in range(1,h_means.GetNbinsX()):
			content = h_means.GetBinContent(bin)
			if content>max_value:
				max_value = content
				max_bin = bin					
					
		mean_1 = -1		
		std_dev_1 = -1		
		number_of_standard_deviations = 2		
							
		# first iteration of the fit	
			
		fit_fct_mean = TF1("f1","gaus",h_means.GetBinCenter(max_bin)-3,h_means.GetBinCenter(max_bin)+3)
		h_means.Fit("f1","RSQ")
		mean_1 = fit_fct_mean.GetParameter(1)
		std_dev_1 = fit_fct_mean.GetParameter(2)
			
		# second iteration of the fit
		h_means.Fit("f1","RSQ","",mean_1-number_of_standard_deviations*std_dev_1,mean_1+number_of_standard_deviations*std_dev_1)
		#h_means.GetFunction('f1').SetLineColor(kRed)
		mean = fit_fct_mean.GetParameter(1)
		rms = fit_fct_mean.GetParameter(2)
			
		return mean, rms		
		
	def SigmasThresholds(self, h_DHV):
	
		# Draws the sigmas distribution
		max_value = 0.
		max_bin = 0
		
		for bin in range(1,h_DHV.GetNbinsX()):	
			content = h_DHV.GetBinContent(bin)
			if content>max_value:
				max_value = content
				max_bin = bin					
			
		fit_fct = TF1("f1","gaus",h_DHV.GetBinCenter(max_bin)-3,h_DHV.GetBinCenter(max_bin)+3)
		h_DHV.Fit("f1","RSQ")
		#h_DHV.GetFunction('f1').SetLineColor(kRed)
		sigma = fit_fct.GetParameter(2)
		
		return sigma
		
	def FilesHeaderWriter(self, goodChan_path, badChan_path, forLatex_path, ini_date, fin_date):		
		
		header =  ' ___________________________________________________ '+'\n'
		header += '|                    HV Analysis                    |'+'\n'
		header += '|                                                   |'+'\n'
		#header += '|  Author : Romano sromanos@cern.ch                 |'+'\n'
		header += '|  Initial Date: ' + str(ini_date) + ' to ' + str(fin_date) +'          |'+'\n'
		header += '|                                                   |'+'\n'
		
		good_header = header
		good_header += '|                 GOOD CHANNELS LIST                |'+'\n'
		good_header += '|___________________________________________________|'+'\n'
		good_header += '\n'
		
		good_file = open(goodChan_path,"w")
		good_file.write(good_header)
		good_file.close()
		
		bad_header = header
		bad_header += '|                 BAD CHANNELS LIST                 |'+'\n'
		bad_header += '|___________________________________________________|'+'\n'
		bad_header += '\n'
				
		bad_file = open(badChan_path,"w")
		bad_file.write(bad_header)
		bad_file.close()
		
		latex_header = header
		latex_header += '|                 For latex tables                 |'+'\n'
		latex_header += '|___________________________________________________|'+'\n'
		latex_header += '\n'
				
		latex_file = open(forLatex_path,"w")
		latex_file.write(latex_header)
		latex_file.close()		
		
		return 
		
	def PartitionHeader(self, part_name, threshold_mv_mean, threshold_RMS_mean, threshold_mv_sigmas, threshold_RMS_sigmas, goodChan_path, badChan_path):
	
		good_line =  '------ Partition ' + part_name + ' thresholds ------'+'\n'
		good_line += '      - Mean(Means) = ' + repr(threshold_mv_mean) + '\n'
		good_line += '      - RMS (Means) = ' + repr(threshold_RMS_mean) + '\n'
		good_line += '      - Mean(Sigma) = ' + repr(threshold_mv_sigmas) + '\n'
		good_line += '      - RMS (Sigma) = ' + repr(threshold_RMS_sigmas) + '\n'
		good_line += '------------------------------------------' + '\n'
		good_line += 'Partition \t Module \t Channel \t DeltaHV mean \t \t DeltaHV sigma'  + '\n'
		
		good_file = open(goodChan_path,"a")
		good_file.write(good_line)
		good_file.close()
		
		bad_line =  '------ Partition ' + part_name + ' thresholds ------'+'\n'
		bad_line += '      - Mean(Means) = ' + repr(threshold_mv_mean) + '\n'
		bad_line += '      - RMS (Means) = ' + repr(threshold_RMS_mean) + '\n'
		bad_line += '      - Mean(Sigma) = ' + repr(threshold_mv_sigmas) + '\n'
		bad_line += '      - RMS (Sigma) = ' + repr(threshold_RMS_sigmas) + '\n'
		bad_line += '------------------------------------------' + '\n'
		bad_line += 'Partition \t Module \t Channel  \t DeltaHV mean \t \t DeltaHV sigma \t \t Exclusion cause(s)'+ '\n'
		
		bad_file = open(badChan_path,"a")
		bad_file.write(bad_line)
		bad_file.close()
		
		return
		
	def PerformDiagnosticForBadChannel(self, badChan_path, h_HV, h_HVset, h_T, h_ref):
	
		bad_file = open(badChan_path,"a")		
		line = ' ----- COMPLEMENTARY INFORMATIONS :'  + ' \n'		
		line += '	* HV mean value:     ' + repr(h_HV.GetMean()) + ' \n'
		line += '	* HV RMS:     ' + repr(h_HV.GetRMS()) + ' \n'		
		line += '	* HVset mean value:  ' + repr(h_HVset.GetMean()) + ' \n'
		line += '	* HVset RMS:     ' + repr(h_HVset.GetRMS()) + ' \n'
		line += '	* T pmt22 mean value:  ' + repr(h_T.GetMean()) + ' \n'
		line += '	* T pmt22 RMS:     ' + repr(h_T.GetRMS()) + ' \n'				
		line += '	* Ref mean value:  ' + repr(h_ref.GetMean()) + ' \n'
		line += '	* ref RMS:     ' + repr(h_ref.GetRMS()) + ' \n'	
		line += '------------------------------------------------------' + ' \n'
			
		bad_file.write(line)
		bad_file.close()
		
		return	
		
	def WriteGoodChannel(self, part_name, imod, ichan, Mean, RMS, goodChan_path):
		
		line = part_name + '\t \t   ' + repr(imod) + '\t \t \t' + repr(ichan) + '\t  ' + repr(Mean) + '\t  ' + repr(RMS) + '\n'			 
		File = open(goodChan_path,"a")
		File.write(line)
		File.close()
			
		return		
		
	def WriteBadChannel(self, part_name, imod, ichan, Mean, RMS, badChan_path, causes):
						
		line = part_name + '\t \t   ' + repr(imod) + '\t \t \t' + repr(ichan) + '\t  ' + repr(Mean) + '\t ' + repr(RMS) + '\t ' + repr(causes) +'\n'			 
		File = open(badChan_path,"a")
		File.write(line)
		File.close()		
		
		return
		
	def WriteNoHVChannel(self, part_name, imod, ichan, noHVChan_path):		
				
		line = part_name + '\t \t' + repr(imod) + '\t \t' + repr(ichan) + '\t \t' + 'NO DeltaHV in the window' + '\n'			 
		File = open( noHVChan_path,"a")
		File.write(line)
		File.close()		
		
		return			
		
	def WriteSummary(self, part_name, imod, ichan, path):		
				
		line = part_name + '\t \t' + repr(imod) + '\t \t' + repr(ichan) + '\n'			 
		File = open( path,"a")
		File.write(line)
		File.close()		
		
		return			
	
	def offset_forLatex(self, part_name, imod, ichan, path, imu, h_HV, h_HVset):		
		
		bad_file = open(path,"a")		
		line = part_name + str(imod).zfill(2) + ' & ' + str(ichan).zfill(2) 				
		line += ' & ' + str(h_HV.GetMean())[:6] + ' & ' + str(h_HVset.GetMean())[:6] + ' & ' + str(imu)[:6] + '\\\\ \hline ' + '\n'			
		bad_file.write(line)
		bad_file.close()
		
		return				
		
	def MakeMapping(self,Dir):
		inputFile = TFile(Dir+'/A_histograms.root', 'READ')
		
		self.mkdir(Dir+'/Mapping')
		outputFile = TFile(Dir+'/Mapping/mapping.root', 'RECREATE')		
		
		palette = array('i',[ 0,8,5,2,1 ]) 		
		title = "Mapping_all_partitions"
		c1 = TCanvas(title)
		c1.SetFillColor(0)
		c1.Divide(2,2)
		
		for ipart in range(4):
			title = "Mapping_" + self.get_partition_name(ipart)
			mapChannels = inputFile.Get("Map_"+ self.get_partition_name(ipart))
			gStyle.SetOptStat(0)
			gStyle.SetOptTitle(0)
			
			c2 = TCanvas(title)
			c2.SetFillColor(0)
			mapChannels.SetMaximum(4)
			mapChannels.GetXaxis().SetTitle("Module of "+ self.get_partition_name(ipart)+" partition")
			mapChannels.GetYaxis().SetNdivisions(505,kFALSE)
			gStyle.SetPalette(5,palette) #define colors for the channels (white, green, yellow,red,black)
		
			c2.cd()
			mapChannels.Draw("col")
		
			l = TLatex()
			l.SetNDC()
			l.SetTextFont(72)
			l.SetTextSize(0.05)
			l.SetTextColor(kBlack)
			l.DrawLatex(0.8,0.95, self.get_partition_name(ipart))

			c1.cd(ipart+1)
			mapChannels.Draw("col")
    
			l.DrawLatex(0.8,0.95, self.get_partition_name(ipart))
			mapChannels.GetZaxis().SetTitle("Status")
			outputFile.cd()
			c2.Update()
			c2.Write()
			c2.SaveAs( Dir+'/Mapping/Map_'+ self.get_partition_name(ipart)+'.png',"png")
			
		outputFile.cd()
		c1.Update()
		c1.Write()
		c1.SaveAs( Dir+'/Mapping/Map_Allpartitions.png',"png")
		outputFile.Close()
		
		return
			
	def HVplots(self):	
		
		inputFile = TFile(os.path.join(getResultDirectory(),'HV/files/results/RegularJob/A_histograms.root'), 'READ')
		outputFile = TFile(os.path.join(getResultDirectory(),'HV/files/results/RegularJob/HV_HVset_plots.root'), 'RECREATE')
		leg_names = ['HV','HVset']
		gStyle.SetOptStat(0)
		
		profiles_HV = []
		profiles_HVset = []
		profiles_DHV = []
		canvas = []
		canvas_DHV = []	
		
		for ipart in range(4): # loop in all the partitions
			#if not ipart==0:
			#	continue
	
			profiles_HV.append([])
			profiles_HVset.append([])
			profiles_DHV.append([])
			canvas.append([])
			canvas_DHV.append([])
						
			for imod in range(64): # loop in all the modules
						
				profiles_HV[ipart].append([])
				profiles_HVset[ipart].append([])
				profiles_DHV[ipart].append([])		
				canvas[ipart].append([])
				canvas_DHV[ipart].append([])
				
				for ichan in range(48): # loop in all the modules
					#if not ichan<2:
					#	continue			
					if self.IsThisChannelInstrumented(ipart, imod+1, ichan+1):	
								
						chan_name = self.get_partition_name(ipart)+str(imod+1).zfill(2)+"_"+str(ichan+1).zfill(2)
						print(chan_name)
						 
						name_HV = "HV/HV_vs_t_" + chan_name			
						name_HVset = "HVset/HVset_vs_t_" + chan_name
						name_DHV = "DHV/DHV_vs_t_" + chan_name
								
						inputFile.cd("HV")
						profiles_HV[ipart][imod].append( inputFile.Get(name_HV))
						inputFile.cd("HVset")
						profiles_HVset[ipart][imod].append( inputFile.Get(name_HVset) )
						inputFile.cd("DHV")
						profiles_DHV[ipart][imod].append( inputFile.Get(name_DHV))
												
						imean = profiles_DHV[ipart][imod][ichan].GetMean(2)
						#print imean, imean+0.5, imean-0.5
						xmin = profiles_HV[ipart][imod][ichan].GetXaxis().GetXmax()
						xmax = profiles_HV[ipart][imod][ichan].GetXaxis().GetXmin()
						#print imean, imean+0.5, imean-0.5, xmin, xmax
																	
						DHV_mean_max = TLine(xmin,imean+0.5,xmax,imean+0.5)
						DHV_mean_max.SetLineColor(kBlue)
						DHV_mean_max.SetLineWidth(1)
						DHV_mean_min = TLine(xmin,imean-0.5,xmax,imean-0.5)
						DHV_mean_min.SetLineColor(kBlue)
						DHV_mean_min.SetLineWidth(1)
						
						canvas[ipart][imod].append(TCanvas( chan_name,chan_name ))
						canvas[ipart][imod][ichan].cd()
						gStyle.SetOptStat(kFALSE)
						profiles_HV[ipart][imod][ichan].Draw()
						profiles_HVset[ipart][imod][ichan].Draw('same')
					
						profiles_HV[ipart][imod][ichan].GetYaxis().SetTitle("Voltage (V)")
						profiles_HV[ipart][imod][ichan].SetTitle(chan_name)
			
						profiles_HV[ipart][imod][ichan].SetMarkerStyle(20)
						profiles_HV[ipart][imod][ichan].SetMarkerSize(0.7)
					
						mean = profiles_HV[ipart][imod][ichan].GetMean(2)
						rms = profiles_HV[ipart][imod][ichan].GetRMS()

						mean_set = profiles_HVset[ipart][imod][ichan].GetMean(2)
						
						if mean > mean_set:
							profiles_HV[ipart][imod][ichan].GetYaxis().SetRangeUser(mean_set-4,mean+4)
						else:
							profiles_HV[ipart][imod][ichan].GetYaxis().SetRangeUser(mean-4,mean_set+4)						
						
						profiles_HVset[ipart][imod][ichan].SetMarkerStyle(24)
						profiles_HVset[ipart][imod][ichan].SetMarkerSize(1.1)				
					
						leg = TLegend(0.2,0.7,0.4,0.8)
						leg.SetFillColor(10)
						leg.AddEntry(profiles_HV[ipart][imod][ichan],leg_names[0],"p")			
						leg.AddEntry(profiles_HVset[ipart][imod][ichan],leg_names[1],"p")
						leg.Draw()
						canvas[ipart][imod][ichan].Modified()
						outputFile.cd()
						canvas[ipart][imod][ichan].Write()
						
						canvas_DHV[ipart][imod].append(TCanvas('DHV_'+chan_name,'DHV_'+chan_name ))
						canvas_DHV[ipart][imod][ichan].cd()
						
						profiles_DHV[ipart][imod][ichan].Draw()						
											
						DHV_mean_max.Draw("same")
						DHV_mean_min.Draw("same")
						canvas_DHV[ipart][imod][ichan].Modified()
						canvas_DHV[ipart][imod][ichan].Write()		
					else: 
						profiles_HV[ipart][imod].append( 'no instrumented')
						profiles_HVset[ipart][imod].append( 'no instrumented')
						profiles_DHV[ipart][imod].append( 'no instrumented')
						canvas[ipart][imod].append('no instrumented')
						canvas_DHV[ipart][imod].append('no instrumented')
				
		outputFile.Write()			
		outputFile.Close()			
		
		return		
		
	def send_mail(self):		
		
		self.Doit('cp '+getResultDirectory()+'HV/files/results/RegularJob/Plots/Mapping/Map_Allpartitions.png '+getResultDirectory(), -1, 1)
		self.Doit('cp '+getResultDirectory()+'HV/files/results/RegularJob/bad_channels.txt '+getResultDirectory(), -1, 1)
		self.Doit('cp '+getResultDirectory()+'HV/files/results/RegularJob/Plots/History/Evolution*.png '+getResultDirectory(), -1, 1)
		self.Doit('tar czvf '+getResultDirectory()+'History.tar.gz '+getResultDirectory()+'Evolution*.png', -1, 1)
		
		COMMASPACE = ', '
		
		##----- To
		Tos  =  []
		#Tos  += ["tilecal.hvmonitoring@cern.ch"]
		Tos += ["sromanos@cern.ch"]
		
		##----- CC
		cc=[]
				
		##----- Content
		INDIR = os.path.join(getResultDirectory(),"HV/files/results/RegularJob/")
		'''
		New_bad = self.write_the_changes(INDIR,"good_became_bad.dat","Good ---> Bad channels")
		Old_bad = self.write_the_changes(INDIR,"bad_became_good.dat","Bad ---> Good channels")
		New_unstable = self.write_the_changes(INDIR,"good_became_unstable.dat","Good ---> Unstable channels")
		Old_unstable = self.write_the_changes(INDIR,"unstable_became_good.dat","Unstable ---> Good channels")
		Bad_Becomes_Unstable = self.write_the_changes(INDIR,"bad_became_unstable.dat","Bad ---> Unstable channels")
		Unstable_Becomes_Bad = self.write_the_changes(INDIR,"unstable_became_bad.dat","Unstable ---> Bad channels")
		'''
		changes_uns = self.write_the_changes(INDIR,"diff_unstable_list.dat","Changes in the unstable list")
		changes_bad = self.write_the_changes(INDIR,"diff_bad_list.dat","Changes in the stable with offset list")
		
		text="""
				
		==================
		HV MONITORING
		==================
		
		Hello,

		You can find in attachement the status of the high voltage 
		updated with the last 24 hours data.

		Since the last email, the following channels change of status: \n		
		"""
		
		'''
		text+=New_bad
		text+=Old_bad
		text+=New_unstable
		text+=Old_unstable
		text+=Bad_Becomes_Unstable
		text+=Unstable_Becomes_Bad
		'''
		
		text+=changes_uns
		text+=changes_bad
		
		text+="""
		
		In case of problem, please contact tilecal.hvmonitoring@cern.ch.
		
		Regards,
		  
		HV monitoring
		tilecal.hvmonitoring@cern.ch
		
		PS: Please note that you can access the whole monitoring files following
		the following weblink:
		https://cern.ch/atlas-tile-hv/
 
		"""		
		
		files  =  []		
		files += [getResultDirectory()+"Map_Allpartitions.png"]
		files += [getResultDirectory()+"bad_channels.txt"]
		files += [getResultDirectory()+"History.tar.gz"]
						  
		message = MIMEMultipart()  
		message['From'] = "tilecal.hvmonitoring@cern.ch"
		message['To'] = COMMASPACE.join(Tos)  
		message['Date'] = formatdate(localtime=True)  
		message['Subject'] = "HV monitoring : status"  
		message['Cc'] = COMMASPACE.join(cc)  
    
		message.attach(MIMEText(text))
		
		for f in files:
			#print os.path.basename(f)
			part = MIMEBase('application', 'octet-stream')  
			part.set_payload(open(f, 'rb').read())  
			Encoders.encode_base64(part)  
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))  
			message.attach(part)  
		
		smtp = smtplib.SMTP("localhost")  
		smtp.sendmail("tilecal.hvmonitoring@cern.ch", Tos , message.as_string()) 
		smtp.close()  
		
		self.Doit('rm '+getResultDirectory()+'Map_Allpartitions.png', 1, 1)
		self.Doit('rm '+getResultDirectory()+'bad_channels.txt', 1, 1)		
		self.Doit('rm '+getResultDirectory()+'History.tar.gz',1,1)
		self.Doit('rm '+getResultDirectory()+'Evolution*.png',1,1)
		
		return		

	def write_the_changes(self, INDIR, in_file , Legend):
		Message=""
		#print INDIR+in_file, os.path.exists(INDIR+in_file)
		if(os.path.exists(INDIR+in_file)):
			File=open(INDIR+in_file, 'r')
			
			Message+= "\n"
			Message+= '\t\t' +"""############################################# \n"""
			Message+= '\t\t' + Legend + '\n'
			Message+= '\t\t' + """############################################# \n """

			for txt in File.readlines():
				if txt =='':
					break
				else:
					Message+='\t\t' + txt
			File.close()
		
		return Message	
		
	def IsThisChannelInTheLists(self, ipart, imod, ichan, idate):
		
		date_format = time.strftime("%y%m%d", idate.timetuple())
		INFILE = os.path.join(getResultDirectory(),'HV/files/results/RegularJob/LISTS/')
		INFILE += date_format 
		
		# bad list
		if os.path.exists(INFILE + '_bad_list.txt'):				
			with open(INFILE + '_bad_list.txt',"r") as f:
				for line in f:					
					partition = line[:-1].split()[0]	
					module = line[:-1].split()[1]	
					channel = line[:-1].split()[2]
					#print partition, module, channel
					if not (self.get_partition_name(ipart)==partition):
						continue
					if not (str(imod)==module):
						continue		
					if not (str(ichan)==channel):
						continue					
					return 1
					
					
		# unstable list
		if os.path.exists(INFILE + '_unstable_list.txt'):				
			with open(INFILE + '_unstable_list.txt',"r") as f:
				for line in f:
					partition = line[:-1].split()[0]	
					module = line[:-1].split()[1]	
					channel = line[:-1].split()[2]
					
					if not (self.get_partition_name(ipart)==partition):
						continue
					if not (str(imod)==module):
						continue		
					if not (str(ichan)==channel):
						continue					
					return 2
		
		# no HV list
		if os.path.exists(INFILE + '_noHV_list.txt'):				
			with open(INFILE + '_noHV_list.txt',"r") as f:
				for line in f:
					partition = line[:-1].split()[0]	
					module = line[:-1].split()[1]	
					channel = line[:-1].split()[2]					
					
					if not (self.get_partition_name(ipart)==partition):
						continue
					if not (str(imod)==module):
						continue		
					if not (str(ichan)==channel):
						continue					
					return -1
					
		return 0

	def HasThisChannelBeenUnstableOrBad(self, ipart, imod, ichan, ini_Date_for_history, fin_Date):		
	
		day_interval = (fin_Date - ini_Date_for_history).days  + 1		
		for idate in (ini_Date_for_history + datetime.timedelta(n) for n in range(day_interval)): 
			
			status = self.IsThisChannelInTheLists(ipart,imod, ichan, idate)			
			if status >= 1:
				return True

		return False
	
	def HasThisChannelBeenUnstable(self, ipart, imod, ichan, ini_Date_for_history, fin_Date):		
	
		day_interval = (fin_Date - ini_Date_for_history).days  + 1		
		for idate in (ini_Date_for_history + datetime.timedelta(n) for n in range(day_interval)): 
			
			status = self.IsThisChannelInTheLists(ipart,imod, ichan, idate)
			if status >= 2:
				return True

		return False
		
	def TimeEvolutionOfChannel( self, ipart, imod, ichan, y, h2_evolution, ini_Date_for_history, fin_Date):
	
		x = 1
		status = -4
		nodata = False
		
		day_interval = (fin_Date - ini_Date_for_history).days  + 1		
		for idate in (ini_Date_for_history + datetime.timedelta(n) for n in range(day_interval)):
		
			temp_status = self.IsThisChannelInTheLists( ipart,imod, ichan, idate )
			if( temp_status >= 0 ):
				status = temp_status
				#print status
		
			date_format = time.strftime("%y%m%d", idate.timetuple())
		
			if not nodata:
				h2_evolution.SetBinContent(x,y,status+0.5)
			
			x += 1

		return			
			
	def SetTH2Attributes(self, h2_evolution, ini_Date_for_history, fin_Date, Title, Comments, f_out):
	
		# Set Titles of histo and axes
		h2_evolution.SetTitle("")
		
		# Adaptation of the labels on the X axis
		bin_x = 1
		
		day_interval = (fin_Date - ini_Date_for_history).days + 1		
		for idate in (ini_Date_for_history + datetime.timedelta(n) for n in range(day_interval)): 
		
			i_day_month = time.strftime("%d/%m", idate.timetuple())	
						
			if (idate==ini_Date_for_history or idate==fin_Date):
				h2_evolution.GetXaxis().SetBinLabel(bin_x,i_day_month)
				h2_evolution.GetXaxis().SetLabelSize(0.04)
				h2_evolution.GetXaxis().SetTimeFormat("%d\/%m\/%y")
				#h2_evolution.GetXaxis().SetLabelOffset(0.03)
				
			iday = time.strftime("%d", idate.timetuple())
			if (iday=='01' or iday=='10' or iday=='20' ):
				h2_evolution.GetXaxis().SetBinLabel(bin_x,i_day_month)
				h2_evolution.GetXaxis().SetLabelSize(0.04)
				h2_evolution.GetXaxis().SetTimeFormat("%d\/%m\/%y")
				#h2_evolution.GetXaxis().SetLabelOffset(0.03)
			bin_x += 1
			
		c1 = TCanvas()
		c1.SetCanvasSize(1200,1000)
		c1.SetWindowSize(1200,1000)
		#c1.SetBorderMode(0)
		
		#TStyle options		
		gStyle.SetOptStat(0)
		palette = array('i',[8,5,2]) 
		gStyle.SetPalette(3,palette)  
		gStyle.SetCanvasBorderMode(0)
		gStyle.SetFrameBorderMode(0)
		gStyle.SetOptStat(0)
		gPad.SetLeftMargin(0.2)
		gPad.SetRightMargin(0.02)
		gPad.SetTopMargin(0.1)
		gPad.SetBottomMargin(0.08)
		gPad.SetGridy(1)
		c1.SetFillColor(0)
		
		# Drawing the histo
		h2_evolution.SetMaximum(3)
		h2_evolution.SetMinimum(0)
		h2_evolution.Draw("col")
		c1.Update()
		
		# Adding text information
		title = TLatex()
		title.SetNDC()
		title.SetTextFont(72)
		title.SetTextSize(0.08)
		title.SetTextColor(kBlack)
		title.DrawLatex(0.3,0.92,Title)
  
		comment = TLatex()
		comment.SetNDC()
		comment.SetTextFont(72)
		comment.SetTextSize(0.04)
		comment.SetTextColor(kBlack)
		comment.DrawLatex(0.65,0.92,Comments)

		f_out.cd()
		
		if(Title=="All"):
			c1.SetCanvasSize(1000,1600)

		#c1.Write("test_c1")
		h2_evolution.Write(os.path.join(getResultDirectory(),"HV/files/results/RegularJob/History/Evolution_"+Title)) 
		c1.Print(os.path.join(getResultDirectory(),"HV/files/results/RegularJob/History/Evolution_"+Title+".png"))
		f_out.Write()

		return
	
	def historyPlots(self, fin_Date):	
		
		#------ date and time recovery
		
		#ini_Date_for_history = datetime.date(2014,06,01) #initial date to produce the history plots
		ini_Date_for_history = datetime.date.today() - datetime.timedelta(days=33) 
		
		#fin_Date = datetime.date.today() - datetime.timedelta(days=2)
		 		
		self.mkdir(os.path.join(getResultDirectory(),"HV/files/results/RegularJob/History"))
		f_out = TFile(os.path.join(getResultDirectory(),"HV/files/results/RegularJob/History/history_plots.root"),"RECREATE")		
		
		bin_y = 0
		bin_y_eba = 0
		bin_y_ebc = 0
		bin_y_lba = 0
		bin_y_lbc = 0
		
		for ipart in range(4): # loop in all the partitions
			#if not ipart==0:
			#	continue
			print('Processing partition ' + self.get_partition_name(ipart))												
			
			for imod in range(64): # loop in all the modules
				#if not imod==19:
				#	continue				
				for ichan in range(48): # loop in all the channels					
					
					if not self.IsThisChannelInstrumented(ipart, imod+1, ichan+1):
						continue
					
					if not self.HasThisChannelBeenUnstableOrBad(ipart,imod+1,ichan+1, ini_Date_for_history, fin_Date):
						continue	
														
					if ipart==0:
						bin_y_eba += 1
				
					elif ipart==1:
						bin_y_ebc += 1				
				
					elif ipart==2:
						bin_y_lba += 1				
				
					elif ipart==3:
						bin_y_lbc += 1
					
					if not self.HasThisChannelBeenUnstable(ipart,imod+1,ichan+1, ini_Date_for_history, fin_Date):
						continue
							
					bin_y += 1
					
		#----- computes the number of bins on the X axis
		bin_x = 0		
		day_interval = (fin_Date - ini_Date_for_history).days + 1		
		for idate in (ini_Date_for_history + datetime.timedelta(n) for n in range(day_interval)): 
			bin_x += 1	
			
		h2_evolution = TH2F("h2_evolution","",bin_x,0,bin_x,bin_y,0,bin_y)
		h2_evolution.SetDirectory(0)
		
		h2_evolution_eba = TH2F("h2_evolution_eba","",bin_x,0,bin_x,bin_y_eba,0,bin_y_eba)
		h2_evolution_eba.SetDirectory(0)
		
		h2_evolution_ebc = TH2F("h2_evolution_ebc","",bin_x,0,bin_x,bin_y_ebc,0,bin_y_ebc)
		h2_evolution_ebc.SetDirectory(0)
		
		h2_evolution_lba = TH2F("h2_evolution_lba","",bin_x,0,bin_x,bin_y_lba,0,bin_y_lba)
		h2_evolution_lba.SetDirectory(0)
		
		h2_evolution_lbc = TH2F("h2_evolution_lbc","",bin_x,0,bin_x,bin_y_lbc,0,bin_y_lbc)
		h2_evolution_lbc.SetDirectory(0)	
		
		vec_histos_partitions = [h2_evolution_eba, h2_evolution_ebc, h2_evolution_lba, h2_evolution_lbc]		
				
		bin_y = 1		
				
		for ipart in range(4): # loop in all the partitions
			bin_y_part = 1
			for imod in range(64): # loop in all the modules				
				for ichan in range(48): # loop in all the channels		
					
					if not self.IsThisChannelInstrumented(ipart, imod+1, ichan+1):
						continue
					
					if not self.HasThisChannelBeenUnstableOrBad(ipart,imod+1,ichan+1, ini_Date_for_history, fin_Date):
						continue
				
					#--- bin label
					chan_name = self.get_partition_name(ipart)+str(imod+1).zfill(2)+" pmt"+str(ichan+1).zfill(2)
					
					vec_histos_partitions[ipart].GetYaxis().SetLabelSize(0.04)
					vec_histos_partitions[ipart].GetYaxis().SetBinLabel(bin_y_part, chan_name)					
					
					self.TimeEvolutionOfChannel(ipart, imod+1, ichan+1, bin_y_part, vec_histos_partitions[ipart], ini_Date_for_history, fin_Date)
					bin_y_part += 1
					
					if not self.HasThisChannelBeenUnstable(ipart,imod+1,ichan+1, ini_Date_for_history, fin_Date):
						continue
					
					h2_evolution.GetYaxis().SetLabelSize(0.03)
					h2_evolution.GetYaxis().SetBinLabel(bin_y, chan_name)
					
					self.TimeEvolutionOfChannel(ipart, imod+1, ichan+1, bin_y, h2_evolution, ini_Date_for_history, fin_Date)
					bin_y += 1
					
		
		self.SetTH2Attributes(h2_evolution, ini_Date_for_history, fin_Date, "All","Unstable Only",f_out)	
		
		for ipart in range(4):
			#print 'Processing partition ' + self.get_partition_name(ipart)						
			self.SetTH2Attributes(vec_histos_partitions[ipart], ini_Date_for_history, fin_Date, self.get_partition_name(ipart),"Bad + Unstable",f_out)	
							
		return		
				
	def DrawAllHistograms(self):		
		
		self.SetMyStyle()		
		threshold = 0.5				
		self.mkdir(os.path.join(getResultDirectory(),'HV/files/results/RegularJob/All_Modules/'))
		self.mkdir(os.path.join(getResultDirectory(),'HV/files/results/RegularJob/Summary/'))		
		leg_names = ['HV','HVset']
		gROOT.SetBatch()
						
		for ipart in range(4): # loop in all the partitions
			#if not ipart==1:
			#	continue
			
			print('processing', self.get_partition_name(ipart), '....')
				
			inputFile = TFile(os.path.join(getResultDirectory(),'HV/files/results/RegularJob/A_histograms.root'), 'READ')
			h_map = inputFile.Get("Map_" + self.get_partition_name(ipart))
												
			for imod in range(64): # loop in all the modules
				#if not imod<2:
				#	continue
				
				a = datetime.datetime.now()
				self.for_DrawAllHistograms(ipart, imod,  threshold, inputFile, leg_names, h_map)			
				b = datetime.datetime.now()
				
				module_name = self.get_partition_name(ipart)+"_"+str(imod+1)
				print((b-a))
				print(module_name, 'Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
				
			inputFile.Close()
		return		

	def otherPlots(self,ipart, imod, inputFile):
		
		module_name = self.get_partition_name(ipart)+str(imod+1).zfill(2)
				
		c2 = TCanvas("Summary_other_"+module_name)
		c2.SetCanvasSize(1100,450)
		c2.SetWindowSize(1100,450)
		c2.SetBorderMode(0)
		c2.SetFillColor(0)
		#c2.Divide(3,0,0.001,0.001,0)  			
		c2.Divide(3)
		
		#---- Temperature histo		
		pallete = [1,3,4,6,9,46,2]
		leg = TLegend(0.1,0.72,0.55,0.88)
		leg.SetTextSize(0.032)
		leg.SetFillColor(10)
		leg.SetNColumns(2)
		temp_leg = ["HVmicro", "HVopto int.","HVopto ext.","Drawer int.","Drawer ext.","PMT22","Readout"]
		c2.cd(1)
		gPad.SetGridy()
		options = ["","same","same","same","same","same","same"]
		for itemp in range(7):
			#if not itemp==2:
			#	continue
				
			name_of_histo = "T/T_vs_t_"+self.get_partition_name(ipart)+str(imod+1).zfill(2)+"_"+str(itemp+1).zfill(2)
			h_temp = inputFile.Get(name_of_histo)
			h_temp.SetMarkerStyle(20)
			h_temp.SetMarkerSize(0.5)
			h_temp.SetMarkerColor(pallete[itemp])
			h_temp.GetYaxis().SetTitleSize(0.05)
			h_temp.SetStats(kFALSE)
			self.setRange(h_temp,False,True)
			
			gPad.Update()
			h_temp.Draw(options[itemp])
			h_temp.GetYaxis().SetRangeUser(15,50)
			leg.AddEntry(h_temp,temp_leg[itemp],"p")

		leg.Draw()	
				
		
		'''	
		#---- Temperature histo
		name_of_histo = "T/T_vs_t_"+self.get_partition_name(ipart)+str(imod+1).zfill(2)+"_06"				
		h_temp = inputFile.Get(name_of_histo)						
		h_temp.SetMarkerStyle(20)
		h_temp.SetMarkerSize(1)
		h_temp.GetYaxis().SetTitleSize(0.05)
		#h_temp.GetYaxis().SetTitleOffset(0.33)
		#h_temp.GetYaxis().CenterTitle()
		h_temp.SetStats(kFALSE)
		h_temp.SetTitle("Temp. at PMT22 vs time")
		gStyle.SetOptTitle(0)
		self.setRange(h_temp,False,True)
		'''
		'''								
		#---- Low voltages	
		pallete = [1,3,4,6,9,46,2]
		leg_lv = TLegend(0.1,0.72,0.55,0.88)
		leg_lv.SetTextSize(0.030)
		leg_lv.SetFillColor(10)
		lv_leg = ["HVopto internal","HVopto external","HVmicro","Drawer internal","Drawer external","PMT22","Readout"]
		c2.cd(3)
		gPad.SetGridy()
		options = ["","same","same","same","same","same","same"]
		for ilv in range(7):
			#if not itemp==2:
			#	continue
				
			name_of_histo = "LV/LV_vs_t_"+self.get_partition_name(ipart)+str(imod+1).zfill(2)+"_"+str(ilv+1).zfill(2)
			h_lv = inputFile.Get(name_of_histo)
			h_lv.SetMarkerStyle(20)
			h_lv.SetMarkerSize(0.5)
			h_lv.SetMarkerColor(pallete[ilv])
			h_lv.GetYaxis().SetTitleSize(0.05)
			h_lv.SetStats(kFALSE)
			self.setRange(h_lv,False,True)
			
			gPad.Update()
			h_lv.Draw(options[ilv])
			h_lv.GetYaxis().SetRangeUser(0,30)
			leg.AddEntry(h_lv,lv_leg[ilv],"p")

		leg_lv.Draw()
		'''
		#---- Reference voltages	
		name_of_histo = "Ref/Ref_vs_t_"+self.get_partition_name(ipart)+str(imod+1).zfill(2)+"_01"
		h_ref = inputFile.Get(name_of_histo)
		h_ref.SetMarkerStyle(20)
		h_ref.SetMarkerSize(1)
		h_ref.GetYaxis().SetTitleSize(0.05)
		h_ref.GetYaxis().SetTitle("Ref. (mV)")
		#h_ref.GetYaxis().SetTitleOffset(0.33)
		#h_ref.GetYaxis().CenterTitle()
		h_ref.SetStats(kFALSE)
		h_ref.SetTitle("Ref. Voltage vs time")
		gStyle.SetOptTitle(0)
		self.setRange(h_ref,False,True)
		
		
		#---- Low voltages
		name_of_histo = "LV/LV_vs_t_"+self.get_partition_name(ipart)+str(imod+1).zfill(2)+"_02"
		h_lv = inputFile.Get(name_of_histo)
		h_lv.SetMarkerStyle(20)
		h_lv.SetMarkerSize(1)
		h_lv.GetYaxis().SetTitleSize(0.05)
		h_lv.GetYaxis().SetTitle("LV (mV)")
		#h_lv.GetYaxis().SetTitleOffset(0.33)
		#h_lv.GetYaxis().CenterTitle()
		h_lv.SetStats(kFALSE)
		h_lv.SetTitle("Low Voltage vs time")
		gStyle.SetOptTitle(0)
		h_lv.GetYaxis().SetRangeUser(0,20)
		#self.setRange(h_lv,False,True)
					
		name_of_histo = "LV/LV_vs_t_"+self.get_partition_name(ipart)+str(imod+1).zfill(2)+"_01"
		h_lv_2 = inputFile.Get(name_of_histo)
		h_lv_2.SetMarkerStyle(20)
		h_lv_2.SetMarkerSize(1)
		h_lv_2.SetStats(kFALSE)
		#gStyle.SetOptTitle(0)								
			
		#---- Temperature histo
		'''					
		c2.cd(1)
		gPad.SetGridy()
		gPad.Update()
		h_temp.Draw("e0")		
		'''				
		#---- Reference voltages
							
		c2.cd(2)
		gPad.SetGridy()
		gPad.Update()
		h_ref.Draw("e0")
		
		#---- Low voltages
							
		c2.cd(3)
		gPad.SetGridy()
		h_lv.Draw("e0")	
		c2.cd(3)						
		h_lv_2.Draw("e0same")												
		gPad.Update()
		c2.Update()
		
		c2.Print(os.path.join(getResultDirectory(),'HV/files/results/RegularJob/Summary/Summary_other_'+module_name+'.png'))
		c2.Close()
		return
	
	def for_DrawAllHistograms(self, ipart, imod, threshold, inputFile, leg_names, h_map):
		
		scale = 1.0								
		module_name = self.get_partition_name(ipart)+"_"+str(imod+1).zfill(2)				
		canvas_name =  "All_plots_" + module_name
				
		big_canvas = TCanvas(canvas_name)
		big_canvas.SetCanvasSize(int(1750*scale),int(1250*scale))
		big_canvas.SetWindowSize(int(1750*scale),int(1250*scale))
				
		big_canvas.Divide(6,8)
		position = 0		
			
		self.otherPlots(ipart, imod, inputFile)
		
		for ichan in range(48): # loop in all the channels
			#if not ichan<1:
			#	continue
					
			position += 1				
			if not self.IsThisChannelInstrumented(ipart, imod+1, ichan+1):
				continue
				
			chan_name = self.get_partition_name(ipart)+str(imod+1).zfill(2)+"_"+str(ichan+1).zfill(2)
				
			name_DHV = "DHV/DHV_vs_t_" + chan_name
			#print name_DHV
								
			inputFile.cd("DHV/")
			profiles_DHV = inputFile.Get(name_DHV)				
			imean = profiles_DHV.GetMean(2)					
					
			if(profiles_DHV.GetMaximum() < imean+3*threshold):
				profiles_DHV.SetMaximum(imean+4*threshold)
					
			if(profiles_DHV.GetMinimum() > imean-3*threshold):
				profiles_DHV.SetMinimum(imean-4*threshold)										
								
			# All the plots for a module
			big_canvas.cd(position)				
			profiles_DHV.Draw()
			gStyle.SetOptTitle(0)
			gStyle.SetOptStat(kFALSE)						
			profiles_DHV.SetMarkerSize(0.4)	
									
			content = h_map.GetBinContent(imod+2,ichan+2)					
			if(content==1):
				big_canvas.cd(position).SetFillColor(kGreen)
			if(content==2):
				big_canvas.cd(position).SetFillColor(kYellow)
			if(content==3):
				big_canvas.cd(position).SetFillColor(kRed)
			if(content==4):
				big_canvas.cd(position).SetFillColor(kBlack)
							
			big_canvas.Modified()
			
			l = TLatex()
			l.SetNDC()
			l.SetTextFont(72)
			l.SetTextSize(0.15)
			l.SetTextColor(kBlack)				
			
			text = "PMT "
			text += str(position)
			l.DrawLatex(0.7,0.90,text)					
			#print chan_name, 'Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss				
	
		big_canvas.Print(os.path.join(getResultDirectory(),'HV/files/results/RegularJob/All_Modules/'+canvas_name+'.png',"png"))
		big_canvas.Close()
			
		return	
	
	def setRange(self, histo, X, Y):		
		if(X):
			x_min = 0
			x_max = 0
			
			for i in range(1,histo.GetNbinsX()):
				if(histo.GetBinContent(i)==0):
					x_min = i
				else:
					break
			
			for i in range(histo.GetNbinsX(),1,-1):	
				if(histo.GetBinContent(i)==0):
					x_max = i
				else:
					break
		
		
		if(Y):
			x_min = 12000000
			x_max = -12000000
			
			for i in range(1,histo.GetNbinsX()):
				
				content = histo.GetBinContent(i)
				if content==0:
					continue				
				
				if(content > x_max):
					x_max = content
				
				if(content < x_max):
					x_min = content
				
			majoration = fabs(0.1*x_max)
			minoration = fabs(0.1*x_min)
			
			if(minoration > 40):
				minoration = 40
		
			if(majoration > 40):
				majoration = 40
				
			histo.SetMinimum(x_min-minoration)
			histo.SetMaximum(x_max+majoration)
			
		return
		
		
	def SetMyStyle(self):		
		gStyle.SetFillColor(0)
		gROOT.SetStyle("Plain")   
		gStyle.SetFrameBorderMode(0)
		gStyle.SetCanvasBorderMode(0)
		gStyle.SetPadBorderMode(0)    
		gStyle.SetPadColor(0)
		gStyle.SetCanvasColor(0)    
		gStyle.SetStatColor(0)
		gStyle.SetPalette(1)
		gStyle.SetOptTitle(0)  
		gStyle.SetLabelFont(42, "xyz")
		gStyle.SetTitleFont(42)
		gStyle.SetTitleFont(42, "xyz")
		gStyle.SetStatFont(42)
		gROOT.ForceStyle()        
		gStyle.SetPadTopMargin(0.1)
		gStyle.SetPadLeftMargin(0.09)
		gStyle.SetTitleOffset(1,"Y")				
				
	def GetBetaForAGivenChannel(self, ipar, imod, ipmt):
		
		mod_name = self.get_partition_name(ipart)+str(imod+1).zfill(2)
		pmt_name = str(ipmt+1).zfill(2)
		
		pmt_beta_file=os.path.join(getTucsDirectory(),'data/PMT_beta.dat')
		if os.path.exists(pmt_beta_file):
			with open(pmt_beta_file,"r") as f:
				for line in f:
					module = line.split(";")[1]
					pmt = line.split(";")[2]
					beta = line.split(";")[3]				
				
					if not mod_name==module:
						continue
					if not pmt_name == pmt:
						continue					
					return beta
			
			beta = 6.9
			return beta
				
				
	def PerformMinutesSeparation(self, ipar, imod, ipmt, minutes, minu):
		
		f_in = TFile(os.path.join(getResultDirectory(),"HV/files/mergefile/RegularJob/HV_MERGED_Skimmed.root"), "READ")	
		tree = f_in.Get("ZeTree")
		n_entries = tree.GetEntries()
				
		# output file tree: branches definitions		
		Measure     = array('f',[ 0 ]) 
		Reference   = array('f',[ 0 ]) 
		Day         = array('f',[ 0 ])
		Date        = array('i',[ 0 ]) 

		MeasureType = array('i',[ 0 ])
		Channel     = array('i',[ 0 ])
		Module      = array('i',[ 0 ])
		Partition   = array('i',[ 0 ]) 
				
		tree.SetBranchAddress('Measure', Measure)
		tree.SetBranchAddress('Reference', Reference)
		tree.SetBranchAddress('Day', Day)
		tree.SetBranchAddress('Date', Date)

		tree.SetBranchAddress('MeasureType', MeasureType)
		tree.SetBranchAddress('Channel', Channel)
		tree.SetBranchAddress('Module', Module)
		tree.SetBranchAddress('Partition', Partition)			
				
		considered_date = minu		
		counter = 0		
		Sum = 0	
		
		mean_values = []
		timestamps = []
		
		for ievt in range(n_entries):
			tree.GetEntry(ievt)
			
			if not MeasureType==2:
				continue
			
			if not Partition==ipart:
				continue
			if not Module==imod:
				continue
			if not Channel==ipmt:	
				continue
				
			Sum += Measure	
			counter += 1			
					
			if( fabs(Date-considered_date) >=60*minutes):	
				mean_values.append(Sum*1.0/counter)
				timestamp.append(Date-30*minutes)
				considered_date = Date
				Sum =0
				counter = 0
				
		f_in.Close()		
		return mean_values, timestamps				
				
	def GiveMinimalHVDate(self):
		
		f_in = TFile(os.path.join(getResultDirectory(),"HV/files/mergefile/RegularJob/HV_MERGED_Skimmed.root"), "READ")
		tree = f_in.Get("ZeTree")
		minu = tree.GetMinimum("Date")		
		f_in.Close()		
		return minu		
	
	def threesholdPlots_DHV(self, ipart, imod, ichan, imu, outputFile, profiles_DHV ,profiles_HV, profiles_HVset):			
		
		self.SetMyStyle()
		threshold = 0.5									
		chan_name = self.get_partition_name(ipart)+str(imod).zfill(2)+"_"+str(ichan).zfill(2)
						
		xmin = profiles_HV.GetXaxis().GetXmax()
		xmax = profiles_HV.GetXaxis().GetXmin()
				
		up_line = TLine(xmin,imu+0.5,xmax,imu+0.5)
		up_line.SetLineColor(kBlue)
		up_line.SetLineWidth(1)
		down_line = TLine(xmin,imu-0.5,xmax,imu-0.5)
		down_line.SetLineColor(kBlue)
		down_line.SetLineWidth(1)						
					
		if(profiles_DHV.GetMaximum() < imu+3*threshold):
			profiles_DHV.SetMaximum(imu+4*threshold)
				
		if(profiles_DHV.GetMinimum() > imu-3*threshold):
			profiles_DHV.SetMinimum(imu-4*threshold)						
									
		c1 = TCanvas("Summary_"+chan_name)
		c1.SetCanvasSize(1200,600)
		c1.SetWindowSize(1220,600)
		c1.SetBorderMode(0)
		c1.SetFillColor(0)
		c1.Divide(2)					
			
		#---- DHV histo
						
		c1.cd(1)
		gPad.SetGridy()
		gStyle.SetOptStat(kFALSE)
		gStyle.SetOptTitle(0)
		profiles_DHV.SetStats(kFALSE)
		profiles_DHV.SetTitle("#Delta HV vs time")
		profiles_DHV.GetYaxis().SetTitleSize(0.04)
		profiles_DHV.GetXaxis().SetTitleSize(0.04)
		profiles_DHV.Draw()											
		up_line.Draw("same")
		down_line.Draw("same")											
				
		#---- HV and HVset histo
						
		c1.cd(2)
		gPad.SetGridy()
		gStyle.SetOptStat(kFALSE)
		gStyle.SetOptTitle(0)
		profiles_HV.Draw()
		profiles_HVset.Draw('same')
		profiles_HV.SetStats(kFALSE)
		profiles_HVset.SetStats(kFALSE)					
		profiles_HV.GetYaxis().SetTitle("Volt (V)")
		profiles_HV.GetYaxis().SetTitleOffset(1.2)
		profiles_HV.GetYaxis().SetTitleSize(0.04)
		profiles_HV.GetXaxis().SetTitleSize(0.04)
		profiles_HV.SetTitle("HV and HVset vs time")			
		profiles_HV.SetMarkerStyle(20)
		profiles_HV.SetMarkerSize(0.7)
		
		self.setRange(profiles_HV,False,True)
		
		'''		
		mean = profiles_HV.GetMean(2)
		rms = profiles_HV.GetRMS()
		mean_set = profiles_HVset.GetMean(2)
						
		if mean > mean_set:
			profiles_HV.GetYaxis().SetRangeUser(mean_set-4,mean+4)
		else:
			profiles_HV.GetYaxis().SetRangeUser(mean-4,mean_set+4)						
		'''
			
		profiles_HVset.SetMarkerStyle(24)
		profiles_HVset.SetMarkerSize(1.1)				
		
		leg_names = ['HV','HVset']	
		leg = TLegend(0.2,0.75,0.4,0.85)
		leg.SetFillColor(10)
		leg.AddEntry(profiles_HV,leg_names[0],"p")			
		leg.AddEntry(profiles_HVset,leg_names[1],"p")
		leg.Draw()
										
		c1.Print(os.path.join(getResultDirectory(),'HV/files/results/RegularJob/Summary/Summary_HV_'+chan_name+'.png'))
		outputFile.cd()
		c1.Write("Summary_"+chan_name)
		c1.Close()
			
		#print chan_name, 'Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss		
			
		return	
				
	'''
	def setRootfile(self, ipart, imod):
		
		ini_Date = datetime.date(2014, 1, 1)
		#fin_Date = datetime.date(2012, 9, 30)

		fin_Date = datetime.date.today() - datetime.timedelta(days=1)
		Setfolder = '/afs/cern.ch/user/t/tilehv/public/rootfiles/Or'

		day_interval = (fin_Date - ini_Date).days + 1
		
		mod_name = self.get_partition_name(ipart) + str(imod+1).zfill(2)
		print mod_name		
		HVset_list = []
		time_list = []
		
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
								
					for ichan in range(48):
						branchName_set = mod_name +".hvOut"+str(ichan+1)+".order"
						if treeInput.GetBranch(branchName_set):						
							my_set = myHV_set[ichan]
							if my_set[0]>1. and my_set[0]<1000.:
								print myTime_set[0], my_set[0]
								HVset_list[ichan].append(my_set[0])
								time_list[ichan].append(myTime_set[0])
				rootfile.Close()
			
			#print HVset_list
			print time_list[5]
			
			
			# create the output rootfile
		
			mod_name = part_name[ipar] + str(imod+1).zfill(2)
			output = TFile(os.path.join(getResultDirectory(),'HV/files/rootfiles/Set/Global/'+mod_name+'.root'),"RECRATE")
			tree = TTree("DCS_tree","DCS_tree")

			time   = array('i',[ 0 ])			
			tree.Branch('EvTime.order' , time, 'EvTime.order/I')
	
			branch = [ array('f',[ 0 ]) for x in range(48) ]
			for ichan in range(48):
				
				branchName_set = mod_name +".hvOut"+str(ichan+1)+".order"
				tree.Branch(branchName_set , branch[ichan], branchName_set+'/F')
	
			for ichan in range(48):	
												
				for i in range(len(time_list[ichan])):
					time[0] = time_list[ichan][i]
					branch[ichan][0] = HVset_list[ichan][i]
					tree.Fill()
			
			output.Write()
			output.Close()
	'''
			
			
			
			
						
				
				
				
				
				
				
				
