# Author: Henric <henric.wilkens@cern.ch>
# Sept, 2012
# Modifications: 
#		Feb, 2014 Silvestre M. Romano <sromanos@cern.ch>

from src.GenericWorker import *
import math
from src.laser.toolbox import *
from src.oscalls import *
import array

class LasOverCs_phyRuns(GenericWorker):
	"A class for making laser/Cs ratio splitting the data in layers"

	def __init__(self,verbose=False,type='readout',n_sig = 2, name = '' ):
		self.verbose = verbose
		self.type = type
		self.PMTool = LaserTools()	
	
		# histograms for all the data
		self.scatter = ROOT.TH2F('scatter','scatter plot all channels', 75, -2.5, 2.5, 75, -2.5, 2.5)
		self.dev_las = ROOT.TH1F('dev_las','Las deviation all channels', 100, -2.5, 2.5)
		self.dev_cs = ROOT.TH1F('dev_cs','CS deviation all channels', 100, -2.5, 2.5)
	
		self.scatter.GetXaxis().SetTitle('Dev Cs (%)')
		self.scatter.GetYaxis().SetTitle('Dev las (%)')
		self.scatter.SetMarkerStyle(7)
		self.dev_las.GetXaxis().SetTitle('Dev las (%)')
		self.dev_cs.GetXaxis().SetTitle('Dev Cs (%)') 
	
		# histogram for data split in layers
		self.hname = [['LB','LB_layerA','LB_layerBC','LB_layerD'],['EB','EB_layerA','EB_layerB','EB_layerD']]
		self.ratios_layer = []
		self.scatter_layer = []
		self.dev_cs_layer = []
		self.dev_las_layer = []	
	
		for j in range(0,2):
		
			self.ratios_layer.append([])
			self.scatter_layer.append([])
			self.dev_las_layer.append([])
			self.dev_cs_layer.append([])

			for k in range(0,4):
				
				hratio_name = 'ratio_%s' % (self.hname[j][k])
				hscatter_name = 'scatter_%s' % (self.hname[j][k])
				hlas_name = 'lasDev_%s' % (self.hname[j][k])
				hcs_name = 'csDev_%s' % (self.hname[j][k])
			
				self.scatter_layer[j].append( ROOT.TH2F(hscatter_name,hscatter_name,100, -2.5, 2.5, 100, -2.5, 2.5) ) 
				self.scatter_layer[j][k].GetXaxis().SetTitle('CS Deviation (%)')
				self.scatter_layer[j][k].GetYaxis().SetTitle('Laser Deviation (%)')
				self.scatter_layer[j][k].SetMarkerStyle(7)
			
				self.ratios_layer[j].append( ROOT.TH1F(hratio_name,hratio_name,75, 0.98, 1.02) ) 
				self.ratios_layer[j][k].GetXaxis().SetTitle('f_{las}/f_{Cs}')
			
				self.dev_las_layer[j].append( ROOT.TH1F(hlas_name,hlas_name,100, -2.5, 2.5) ) 
				self.dev_las_layer[j][k].GetXaxis().SetTitle('Dev_{las} (%)')
			
				self.dev_cs_layer[j].append( ROOT.TH1F(hcs_name,hcs_name,100, -2.5, 2.5) ) 
				self.dev_cs_layer[j][k].GetXaxis().SetTitle('Dev_{Cs} (%)')			
			
		# Spliting the data in layer A_EB in A12-14 and A15,16
		self.hname_EB_A = ['A12_13_14','A15_16']
		self.ratios_EB_A = []
		self.scatter_EB_A = []
		self.dev_EB_A_cs = []
		self.dev_EB_A_las = []
	
		for j in range(0,2):
		
			hratio_name = 'ratio_EB_%s' % (self.hname_EB_A[j])
			hscatter_name = 'scatter_EB_%s' % (self.hname[j])
			hlas_name = 'lasDev_EB_%s' % (self.hname[j])
			hcs_name = 'csDev_EB_%s' % (self.hname[j])
		
			self.scatter_EB_A.append( ROOT.TH2F(hscatter_name,hscatter_name,100, -2.5, 2.5, 100, -2.5, 2.5) ) 
			self.scatter_EB_A[j].GetXaxis().SetTitle('CS Deviation (%)')
			self.scatter_EB_A[j].GetYaxis().SetTitle('Laser Deviation (%)')
			self.scatter_EB_A[j].SetMarkerStyle(7)
		
			self.ratios_EB_A.append( ROOT.TH1F(hratio_name,hratio_name,75, 0.98, 1.02) ) 
			self.ratios_EB_A[j].GetXaxis().SetTitle('f_{las}/f_{Cs}')
		
			self.dev_EB_A_las.append( ROOT.TH1F(hlas_name,hlas_name,100, -2.5, 2.5) ) 
			self.dev_EB_A_las[j].GetXaxis().SetTitle('Dev_{las} (%)')
		
			self.dev_EB_A_cs.append( ROOT.TH1F(hcs_name,hcs_name,100, -2.5, 2.5) ) 
			self.dev_EB_A_cs[j].GetXaxis().SetTitle('Dev_{Cs} (%)')			
			
		self.n_sig = n_sig 
		self.name = name
		self.n_entries = []
	
		try:
			self.HistFile.cd()
		except:
			self.initHistFile(getResultDirectory()+"csLas_" +self.name+".root")
		self.HistFile.cd()
		gDirectory.mkdir("all")
		for j in range(2):
			for k in range(4):			
				gDirectory.mkdir(self.hname[j][k])
    	
		self.outfile = open(os.path.join(getResultDirectory(),"noCompatible_"+self.name+'.txt'),"w")

	def ProcessRegion(self, region):        
	
		numbers = region.GetNumber()  
		if len(numbers)!=3: # This is were the cesium is 
			return
			
		[part_num, module, pmt] = region.GetNumber(1)
		part_num -= 1
		module -= 1
	
		cellname = self.PMTool.getCellName(part_num, module, pmt) 
		layername = self.PMTool.get_pmt_layer(part_num, module, pmt) 		 
	
		las = []
		ces = []
		ces_run = []
	        		
		for event in sorted(region.GetEvents(), key=lambda event: event.run.time):
			if event.run.runType == 'cesium':
				if 'calibration' in event.data and not event.data['calibration']==None:
					#print 'cesium',event.data['calibration'],event.run.time
					ces_run.append( event.run.runNumber )
					ces.append( event.data['calibration'] )
			
		for childregion in region.GetChildren('readout'): # The laser is below
			for event in sorted(childregion.GetEvents(), key=lambda event: event.run.time):
				if event.run.runType == 'Las' and 'deviation' in event.data:
					#print 'Las',event.data['deviation'],event.run.time	
					las.append( event.data['deviation'] )
					self.n_entries.append(event.data['number_entries'] )	       
       
		if len(las) == 2 and len(ces) == 4:
			if not ces_run[0]==ces_run[3]:
				var_las = las[1]
				var_cs = (ces[3]-ces[0])/ces[0]
				var_cs *= 100

			else:
				var_las = 1
				var_cs = -300 # This values will exclude the channel
				if self.verbose:
                                    print(('Exclude channel', region.GetHash(), ces_run))
		
		elif len(las) == 2 and len(ces) == 3:
			if not ces_run[0]==ces_run[2]:	    
				var_las = las[1]
				var_cs = (ces[2]-ces[0])/ces[0]
				var_cs *= 100

			else:
				var_las = 1
				var_cs = -300 # This values will exclude the channel
				if self.verbose:
					print(('Exclude channel', region.GetHash(), ces_run))
	
		elif len(las) == 2 and len(ces) == 2:
			if not ces_run[0]==ces_run[1]:
				var_las = las[1]
				var_cs = (ces[1]-ces[0])/ces[0]
				var_cs *= 100
			else:
				var_las = 1
				var_cs = -300 # This values will exclude the channel
				if self.verbose:
					print(('Exclude channel', region.GetHash(), ces_run))
				
		else:
			var_las = 1
			var_cs = -300 # This values will exclude the channel
			if self.verbose:
				print(('Exclude channel', region.GetHash(),'len(Las)', len(las), 'len(Cs)', len(ces)))
	
		ratio = 1.+ (var_cs/100)
		ratio /= 1. + (var_las/100)
	
		if ratio>0.0:				
			if (layername in ('A','B','BC','D')) and not (cellname=='D4' or cellname=='C10'):
		
				self.scatter.Fill( var_cs, var_las )
				self.dev_las.Fill( var_las )
				self.dev_cs.Fill( var_cs ) 
				if (part_num==0 or part_num==1):
					self.ratios_layer[0][0].Fill(ratio)
					self.scatter_layer[0][0].Fill( var_cs, var_las )
					self.dev_las_layer[0][0].Fill( var_las )
					self.dev_cs_layer[0][0].Fill( var_cs )
					#print self.hname[0][0]
				if (part_num==2 or part_num==3):
					self.ratios_layer[1][0].Fill(ratio)
					self.scatter_layer[1][0].Fill( var_cs, var_las )
					self.dev_las_layer[1][0].Fill( var_las )
					self.dev_cs_layer[1][0].Fill( var_cs )
					#print self.hname[1][0]
				
		
			if (part_num==0 or part_num==1):
				if layername=='A':
					self.ratios_layer[0][1].Fill(ratio)
					self.scatter_layer[0][1].Fill( var_cs, var_las )
					self.dev_las_layer[0][1].Fill( var_las )
					self.dev_cs_layer[0][1].Fill( var_cs )
					#print self.hname[0][1]
				elif layername=='BC':
					self.ratios_layer[0][2].Fill(ratio)
					self.scatter_layer[0][2].Fill( var_cs, var_las )
					self.dev_las_layer[0][2].Fill( var_las )
					self.dev_cs_layer[0][2].Fill( var_cs )
					#print self.hname[0][2]
				else:
					self.ratios_layer[0][3].Fill(ratio)
					self.scatter_layer[0][3].Fill( var_cs, var_las )
					self.dev_las_layer[0][3].Fill( var_las )
					self.dev_cs_layer[0][3].Fill( var_cs )
					#print self.hname[0][3]
			
		
			if (part_num==2 or part_num==3):
				if layername=='A':
					self.ratios_layer[1][1].Fill(ratio)
					self.scatter_layer[1][1].Fill( var_cs, var_las )
					self.dev_las_layer[1][1].Fill( var_las )
					self.dev_cs_layer[1][1].Fill( var_cs )
					#print self.hname[1][1]	
				
					if cellname=='A15' or cellname=='A16':
						self.ratios_EB_A[0].Fill(ratio)
						self.scatter_EB_A[0].Fill( var_cs, var_las )
						self.dev_EB_A_las[0].Fill( var_las )
						self.dev_EB_A_cs[0].Fill( var_cs )
					if cellname=='A12' or cellname=='A13' or cellname=='A14': 			
						self.ratios_EB_A[1].Fill(ratio)
						self.scatter_EB_A[1].Fill( var_cs, var_las )
						self.dev_EB_A_las[1].Fill( var_las )
						self.dev_EB_A_cs[1].Fill( var_cs )
					
				elif layername=='B':
					if not cellname=='C10':			
						self.ratios_layer[1][2].Fill(ratio)
						self.scatter_layer[1][2].Fill( var_cs, var_las )
						self.dev_las_layer[1][2].Fill( var_las )
						self.dev_cs_layer[1][2].Fill( var_cs )
						#print self.hname[1][2]
					
				else:
					if not cellname=='D4':			
						self.ratios_layer[1][3].Fill(ratio)
						self.scatter_layer[1][3].Fill( var_cs, var_las )
						self.dev_las_layer[1][3].Fill( var_las )
						self.dev_cs_layer[1][3].Fill( var_cs )
						#print self.hname[1][3]	
			
			
			if (var_cs > 2.0 and var_las < -2.0) and (var_cs < -2.0 and var_las > 2.0):
				self.outfile.write(region.GetHash() + 'laser dev: ' + str(var_las) + ' - ces dev:  '+ str(var_cs) + ' - ratio: '+ str(ratio)+'\n')
				if self.verbose:
					print(('No compatible channel', region.GetHash(), 'Cs dev', var_cs, 'Las dev ', var_las, 'ratio', ratio))
		
			if abs(var_cs) < 2.0 and abs(var_las) > 2.0:
				self.outfile.write(region.GetHash() + 'laser dev: ' + str(var_las) + ' - ces dev:  '+ str(var_cs) + ' - ratio: '+ str(ratio)+'\n')	
				if self.verbose:	
					print(('No compatible channel', region.GetHash(), 'Cs dev', var_cs, 'Las dev ', var_las, 'ratio', ratio))

  
	def ProcessStop(self):
    	
		self.outfile.close()	
		self.HistFile.cd("../")	
		gDirectory.cd("all/")
		self.scatter.Write()
		self.dev_las.Write()
		self.dev_cs.Write()
		
		c1 = TCanvas('LB_comp','LB layer components')
		c1.cd()
		leg = TLegend(0.2,0.5,0.4,0.8)
		leg.SetFillColor(10)
	
		self.ratios_layer[0][0].SetLineWidth(4)
		self.ratios_layer[1][0].SetLineWidth(4)
	
		for j in range(2):
			for k in range(0,4):
				if not k==0:
					self.ratios_layer[j][k].SetLineStyle(k)			
				
		
		option = ["","same","same","same"]	
		for k in range(0,4):
			leg.AddEntry(self.ratios_layer[0][k],self.hname[0][k],"l")
			self.ratios_layer[0][k].Draw(option[k])
	
		leg.Draw()
		self.HistFile.cd("../")	
		self.HistFile.cd("LB/")			
		c1.Write()
	
		c2 = TCanvas('EB_comp','EB layer components')
		c2.cd()
		leg2 = TLegend(0.2,0.5,0.4,0.8)
		leg2.SetFillColor(10)
		
		for k in range(0,4):
			leg.AddEntry(self.ratios_layer[1][k],self.hname[0][k],"l")
			self.ratios_layer[1][k].Draw(option[k])
	
		leg2.Draw()
		self.HistFile.cd("../")
		self.HistFile.cd("EB/")			
		c2.Write()	
		
		for j in range(2):		
			for k in range(4):
									
				self.ratios_layer[j][k].SetLineWidth(2)
				self.ratios_layer[j][k].SetLineStyle(1)
	
				# Thresholds		
				mean = self.ratios_layer[j][k].GetMean()
				rms = self.ratios_layer[j][k].GetRMS()
				range_fit = [mean-(self.n_sig*rms),mean+(self.n_sig*rms)]
	
				fun = TF1('fun','gaus',range_fit[0],range_fit[1] )
				self.ratios_layer[j][k].Fit(fun,'','',range_fit[0],range_fit[1])
				self.ratios_layer[j][k].GetFunction('fun').SetLineColor(ROOT.kRed)

				par = fun.GetParameters()
				par_error = fun.GetParErrors()			
			
				self.HistFile.cd("../")
				ROOT.gDirectory.cd(self.hname[j][k]+'/')
				self.scatter_layer[j][k].Write()
				self.ratios_layer[j][k].Write()
				self.dev_las_layer[j][k].Write()
				self.dev_cs_layer[j][k].Write()
	
				# Output files
				fitParam_name = "%s/fitParam_%s_%s" % (getResultDirectory(),self.hname[j][k],self.name)
				fitParam = str(par[0])+'+/-'+str(par_error[0])+'\n'+str(par[1])+'+/-'+str(par_error[1])+'\n'+str(par[2])+'+/-'+str(par_error[2])
				n = str(self.n_entries[0]) + '-' + str(self.n_entries[1])			
			
				with open(fitParam_name,"w") as f:
					f.write(fitParam)
					f.write('\n'+n+'\n')
	
	
		for j in range(2):		
			
			self.ratios_EB_A[j].SetLineWidth(2)
			self.ratios_EB_A[j].SetLineStyle(1)

			# Thresholds		
			mean = self.ratios_EB_A[j].GetMean()
			rms = self.ratios_EB_A[j].GetRMS()
			range_fit = [mean-(self.n_sig*rms),mean+(self.n_sig*rms)]
		
			fun = TF1('fun','gaus',range_fit[0],range_fit[1] )
			self.ratios_EB_A[j].Rebin(3)
			self.ratios_EB_A[j].Fit(fun,'','',range_fit[0],range_fit[1])
		
			self.ratios_EB_A[j].GetFunction('fun').SetLineColor(ROOT.kRed)
			par = fun.GetParameters()
			par_error = fun.GetParErrors()
		
			self.HistFile.cd("../")
			gDirectory.cd(self.hname[1][1]+'/')		
			self.ratios_EB_A[j].Write()

			# Output files
			fitParam_name = "%s/fitParam_%s_%s" % (getResultDirectory(),self.hname_EB_A[j],self.name)
			fitParam = str(par[0])+'+/-'+str(par_error[0])+'\n'+str(par[1])+'+/-'+str(par_error[1])+'\n'+str(par[2])+'+/-'+str(par_error[2])
			n = str(self.n_entries[0]) + '-' + str(self.n_entries[1])			

			with open(fitParam_name,"w") as f:
				f.write(fitParam)
				f.write('\n'+n+'\n')
	
	
	
