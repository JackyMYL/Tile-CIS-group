############################################################
#
#
#
############################################################
#
# Author: Cora Fischer
# Date: October 2014
# Aim: Produce response variation plot in cell A13 in 2012 data for cesium and mbias
#
#
###########################################################

from src.GenericWorker import *
import src.MakeCanvas
import src.oscalls
import os.path
import time
import math


#this worker is called by macros/CompareCsMbias.py
class PlotCsMbias(GenericWorker):
    "Compute history plot Cs"
    c1 = None
    
    def __init__(self, doEps = False, verbose=False, channels= [[2,3],[10,11]]):
        self.verbose = verbose
        self.doEps    = doEps
        self.origin   = ROOT.TDatime()

        self.tgraph_cesium = ROOT.TGraphErrors()

        self.time_max = 0
        self.time_min = 10000000000000000
	
        self.dir = src.oscalls.getPlotDirectory() #where to save the plots

        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),'Comparison')
        src.oscalls.createDir(self.dir)
	    
        self.meanMBias = []
        self.errorMBias = []
        self.dateMBias = []
	
        self.data_cesium = dict()
        self.data_cesium_ref = dict()

        self.channels = channels


    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('cesium'):            
            if run.time == None: continue
            
            if run.time_in_seconds < self.time_min:
                self.time_min = run.time_in_seconds
                self.origin = ROOT.TDatime(str(run.time))
                
            if run.time_in_seconds > self.time_max:
                self.time_max = run.time_in_seconds

    
            if run.runType=='cesium':
                self.data_cesium[run.runNumber] = stats()
                self.data_cesium_ref[run.runNumber] = stats()

        print((self.time_min))

    def ProcessRegion(self, region):
        numbers = region.GetNumber()

        if len(numbers)==4:
            [part, module, ch, gain] = numbers
        elif len(numbers)==3:
            [part, module, ch] = numbers
        else:
            return 

	

        for event in region.GetEvents():
	    #print region
            numbers = region.GetNumber()

            if len(numbers)==4:
                [part, module, channel, gain] = numbers
            elif len(numbers)==3:
                [part, module, channel] = numbers

            if event.run.runType=='cesium' and 'calibration' in event.data:
                if isinstance(event.data['calibration'], float):
                    #self.data_cesium[event.run.runNumber].fill(100.*(event.data['calibration']/event.data['f_integrator_db']-1.))
                    if ch in self.channels[1]:
                        self.data_cesium[event.run.runNumber].fill(event.data['calibration'])
                    if ch==17 or ch==18:
                        self.data_cesium_ref[event.run.runNumber].fill(event.data['calibration'])
            if event.run.runType=='Las' or event.run.runType=='Phys':
                if 'meanA13oD5' in event.data:
                    print((event.data['meanA13oD5'], event.data['errorA13oD5']))
                    self.meanMBias.append(event.data['meanA13oD5'])
                    self.errorMBias.append(event.data['errorA13oD5'])
                    self.dateMBias.append(event.data['date'])
			  
    def ProcessStop(self):
	    
       date_ces = []
       val_ces = [] #A13
       err_ces = [] #A13 	 
       norm_ces = [] #D5
       nerr_ces = [] #D5   

       for run in run_list.getRunsOfType('cesium'):
           print((run.time_in_seconds))
           time = run.time_in_seconds-self.time_min
           print(time)
           timeR = datetime.datetime.strptime(run.time,'%Y-%m-%d %H:%M:%S')# get runtime
           date = ROOT.TDatime(timeR.year, timeR.month, timeR.day, timeR.hour, timeR.minute, timeR.second)
           time = date.Convert()
	   #time = run.time
           print((run.runNumber, time))

           print(('cesium ', self.data_cesium[run.runNumber].entries, self.data_cesium[run.runNumber].mean(), self.data_cesium[run.runNumber].error()))
           if self.data_cesium[run.runNumber].entries!=0:
               date_ces.append(time)
               val_ces.append(self.data_cesium[run.runNumber].mean())
               err_ces.append(self.data_cesium[run.runNumber].error())
               norm_ces.append(self.data_cesium_ref[run.runNumber].mean())
               nerr_ces.append(self.data_cesium_ref[run.runNumber].error())
               #npoints = self.tgraph_cesium.GetN()
	       #error=self.data_cesium[run.runNumber].mean()/self.data_cesium_ref[run.runNumber].mean()*math.sqrt((self.data_cesium[run.runNumber].error()/self.data_cesium[run.runNumber].mean())**2+(self.data_cesium_ref[run.runNumber].error()/self.data_cesium_ref[run.runNumber].mean())**2)
               #self.tgraph_cesium.SetPoint( npoints,
                                            #time, 
                                            #self.data_cesium[run.runNumber].mean()/self.data_cesium_ref[run.runNumber].mean())
               #self.tgraph_cesium.SetPointError(npoints, 
                                                #0., 
                                                #error)
       # graph for minbias data
       Date = [] 						
       for i in range(len(self.dateMBias)):
           Date.append(self.dateMBias[i].Convert())

       # now: find closest cesium run to mbias runs to normalize with D5 response ######################################	
       for r in range(len(Date)):
           diffmin = [100000000., 0]
           diffmin2 = [100000000., 0]	
           for ces in range(len(date_ces)):
               if abs(date_ces[ces]-Date[r])<diffmin[0]:
                   diffmin[0]=abs(date_ces[ces]-Date[r]) #store time difference in sec
                   diffmin[1]=ces                        #store respective index
	   #second iteration to find second closest run...there are probably better ways to do this
           for ces in range(len(date_ces)):
               if ces==diffmin[1]: continue
               if abs(date_ces[ces]-Date[r])<diffmin2[0]:
                   diffmin2[0]=abs(date_ces[ces]-Date[r])                          #store time difference in sec
                   diffmin2[1]=ces                                                 #store respective index
           if diffmin[0]<0.2*diffmin2[0]:                                          #if a lot closer to first run than second:
               helpmean=norm_ces[diffmin[1]]*self.meanMBias[r]                     # normalize with the repective D5 value
               self.errorMBias[r]=helpmean*math.sqrt((self.errorMBias[r]/self.meanMBias[r])**2+(nerr_ces[diffmin[1]]/norm_ces[diffmin[1]])**2)
               self.meanMBias[r]=helpmean
           else:         	                                                    #otherwise: take average value
               helperror1 = 1./nerr_ces[diffmin[1]]**2
               helperror2 = 1./nerr_ces[diffmin2[1]]**2
               average = (helperror1*norm_ces[diffmin[1]]+helperror2*norm_ces[diffmin2[1]])/(helperror1+helperror2) #weighted average
               werror = 1./(helperror1+helperror2)
               helpmean= average*self.meanMBias[r]
               self.errorMBias[r]=helpmean*math.sqrt((self.errorMBias[r]/self.meanMBias[r])**2+werror/average**2)
               self.meanMBias[r]=helpmean
       #####################################################################################################################
				
       #for mbias: first normalize to first mbias run
       ref_ind = 0
       for i in range(len(Date)):
           if Date[i]==min(Date):
               ref_ind=i

       Time = array('f', Date)
       Mean = array('f', self.meanMBias)
       MeanError = array('f', self.errorMBias)
       dummy = []
       for i in range(len(Date)):
           dummy.append(0.0)
       Dummy = array('f', dummy)

       relat = array('f',[])
       error = array('f',[])
        
       print((len(Date)))
       for i in range(len(Date)):
           relat.append(Mean[i]/Mean[ref_ind]-1.) #build relative variation wrt first run	
           error.append(math.sqrt(MeanError[i]**2/Mean[ref_ind]**2+MeanError[ref_ind]**2*Mean[i]**2/Mean[ref_ind]**4))
           print((relat[i], error[i]))
	   
       c1 = ROOT.TCanvas('c1','',1000,500)
       c1.SetRightMargin(0.1)
       c1.SetGridy()
       
       #graph for cesium data
       ref_ind_ces = 0
       
       for i in range(len(date_ces)):
           if date_ces[i]==min(date_ces):
               ref_ind_ces=i
	   
       Time_ces = array('f', date_ces)
       dummy_ces = []
       for i in range(len(Time_ces)):
           dummy_ces.append(0.0)
       Dummy_ces = array('f', dummy_ces)

       relat_ces = array('f',[])
       error_ces = array('f',[])
       Val_ces = array('f', val_ces)
       Err_ces = array('f', err_ces)
       
       maxpoint = 0.
       scnd_point = 0
       
       for i in range(len(Time_ces)):
           relat_ces.append(val_ces[i]/val_ces[ref_ind_ces]-1.) #build relative variation wrt first run	
           error_ces.append(math.sqrt(err_ces[i]**2/val_ces[ref_ind_ces]**2+err_ces[ref_ind_ces]**2*val_ces[i]**2/val_ces[ref_ind_ces]**4))
           if val_ces[i]>maxpoint and i!=ref_ind_ces:
               maxpoint=val_ces[i]
               scnd_point=i
           print((relat_ces[i], error_ces[i]))
       
       ## now: do trick to 'normalize' mbias data to first cesium run: interpolate between first 2 cesium points and normalize first mbias run to lie on this interpolation
       incline = (relat_ces[scnd_point]-relat_ces[ref_ind_ces])/(date_ces[scnd_point]-date_ces[ref_ind_ces])
       normdiff = incline*(Date[ref_ind]-date_ces[ref_ind_ces])
       
       print(("par: ", incline, normdiff))
       
       for i in range(len(Date)):
           relat[i]=relat[i]+normdiff
       ######################################################################################################################################################################
       
       print((len(Time_ces), len(relat_ces), len(Dummy_ces), len(error_ces)))
       self.tgraph_cesium = ROOT.TGraphErrors(len(Time_ces), Time_ces, relat_ces , Dummy_ces, error_ces)
       
       
       #self.tgraph_cesium.Draw("AP")
       self.RelativeRatio = ROOT.TGraphErrors(len(Time), Time, relat, Dummy, error)
       #self.RelativeRatio.Draw("APsame")
       

       self.RelativeRatio.SetMarkerStyle(20)
       self.RelativeRatio.SetLineColor(kBlue)
       self.RelativeRatio.SetMarkerColor(kBlue)
       
       mg = ROOT.TMultiGraph()
       mg.Add(self.tgraph_cesium)
       mg.Add(self.RelativeRatio)
       mg.Draw("ap")
       
       mg.GetXaxis().SetTimeDisplay(1)
       mg.GetXaxis().SetNdivisions(-505)
       mg.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}")
       mg.GetXaxis().SetTimeOffset(0,"gmt")
       mg.GetXaxis().SetTitle("Time")
       mg.GetXaxis().SetTitleOffset(1.6)
       mg.GetXaxis().SetLabelOffset(0.033)
       #self.HistFile.cd()       
       #self.tgraph_cesium.SetName("cesium")
       #self.tgraph_cesium.Write()
       #c1.Write()
       
       legend = ROOT.TLegend(0.6,0.7,0.9,0.9)
       legend.SetFillStyle(0)
       legend.SetFillColor(0)
       legend.SetBorderSize(0)
       legend.AddEntry(self.RelativeRatio, 'Minimum Bias Data', "ep")
       legend.AddEntry(self.tgraph_cesium, 'Cesium Data', "ep")
       legend.Draw()
       
       mg.GetYaxis().SetTitle("Relative variation of A13 cell response")

       c1.Modified()
       c1.Update()
	
       self.plot_name1 = "CompA13_Cs_Mbias"
        # save plot, several formats...
       c1.Print("%s/%s.root" % (self.dir, self.plot_name1))
       c1.Print("%s/%s.eps" % (self.dir, self.plot_name1))
       c1.Print("%s/%s.png" % (self.dir,self.plot_name1))
       
       #del c1, self.RelativeRatio, self.tgraph_cesium


class stats:
    def __init__(self):
        self.entries = 0
        self.sum     = float(0.)
        self.sum2    = float(0.)

    def fill(self, value):
        self.entries += 1 
        self.sum     += value
        self.sum2    += value*value

    def mean(self):
        if self.entries>0:
            return self.sum/self.entries
    
    def rms(self):
        if self.entries>0:
            return sqrt(self.sum2/self.entries)

    def stddev(self):
        if self.entries>0:
            return sqrt(self.sum2/self.entries-self.mean()*self.mean())

    def error(self):
        if self.entries>0:
            return sqrt((self.sum2/self.entries-self.mean()*self.mean())/self.entries)

    
#    def entries(self):
#        return int(self.entries)
    
