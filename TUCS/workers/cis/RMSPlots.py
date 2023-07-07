#################################################### 
#  RMSPlots.py                                     #
#                                                  #
#  Author: Grey Wilburn                            #
#  grey.williams.wilburn@cern.ch                   #
#                                                  #
#  Date: A cloudy afternoon in February 2015       #
####################################################

from src.GenericWorker import *
from src.oscalls import *
from src.region import *
import os.path


import src.MakeCanvas
import src.oscalls
import src.ReadGenericCalibration
from src.region import *

class RMSPlots(GenericWorker):
        "Creates 1D and 2D histograms of CIS Constant RMS/mean"

        def __init__(self,dateLabel):
           
            self.dateLabel = dateLabel

        def ProcessStart(self):
                self.dir = getPlotDirectory()
                self.dir = '%s/cis/Public_Plots/RMSPlotsFinal' % self.dir
                createDir(self.dir)
                self.hlo = ROOT.TH1F('low-gain', '', 20, 0, 1.0)
                self.hhi = ROOT.TH1F('high-gain', '', 20, 0, 1.0)
                self.hdem = ROOT.TH1F('demonstrator', '',8, 0, 0.2)
                self.hdemlo = ROOT.TH1F('demonstratorlo', '',8, 0, 0.2)

                self.hlo.SetLineStyle(1)
                self.hlo.SetLineColor(ROOT.kBlue)

                self.hhi.SetLineStyle(2)
                self.hhi.SetLineColor(ROOT.kRed)

                self.hdem.SetLineStyle(1)
                self.hdem.SetLineColor(ROOT.kBlue)

                self.hdemlo.SetLineStyle(2)
                self.hdemlo.SetLineColor(ROOT.kRed)
                
                self.hlo.StatOverflows(ROOT.kTRUE)
                self.hhi.StatOverflows(ROOT.kTRUE)
                self.hdem.StatOverflows(ROOT.kTRUE)
                self.hdemlo.StatOverflows(ROOT.kTRUE)

                self.c1 = src.MakeCanvas.MakeCanvas()
                ROOT.gPad.SetTickx()
                ROOT.gPad.SetTicky()                  

                #Set up histograms
                self.hval0 = ROOT.TH2D('hval0', '', 64, 1, 65, 48, 0, 48)
                self.hval1 = ROOT.TH2D('hval1', '', 64, 1, 65, 48, 0, 48)
                self.hval2 = ROOT.TH2D('hval2', '', 64, 1, 65, 48, 0, 48)
                self.hval3 = ROOT.TH2D('hval3', '', 64, 1, 65, 48, 0, 48)
                self.hval4 = ROOT.TH2D('hval4', '', 64, 1, 65, 48, 0, 48)
                self.hval5 = ROOT.TH2D('hval5', '', 64, 1, 65, 48, 0, 48)
                self.hval6 = ROOT.TH2D('hval6', '', 64, 1, 65, 48, 0, 48)
                self.hval7 = ROOT.TH2D('hval7', '', 64, 1, 65, 48, 0, 48)

        def ProcessStop(self):
                #Format and print 2D histograms
                ROOT.gStyle.SetOptStat(0)
                #LBA High Gain
                self.c1.Clear()
                self.Draw2DHist(self.hval0, 'LBA', 'high')
                self.c1.Modified()
                self.c1.Print("%s/RMSLBAHigh.png" % self.dir)
                #LBC High Gain
                self.c1.Clear()
                self.Draw2DHist(self.hval1, 'LBC', 'high')
                self.c1.Modified()
                self.c1.Print("%s/RMSLBCHigh.png" % self.dir)
                #EBA High Gain
                self.c1.Clear()
                self.Draw2DHist(self.hval2, 'EBA', 'high')
                self.c1.Modified()
                self.c1.Print("%s/RMSEBAHigh.png" % self.dir)
                #EBC High Gain
                self.c1.Clear()
                self.Draw2DHist(self.hval3, 'EBC', 'high')
                self.c1.Modified()
                self.c1.Print("%s/RMSEBCHigh.png" % self.dir)
                #LBA Low Gain
                self.c1.Clear()
                self.Draw2DHist(self.hval4, 'LBA', 'low')
                self.c1.Modified()
                self.c1.Print("%s/RMSLBALow.png" % self.dir)
                #LBC Low Gain
                self.c1.Clear()
                self.Draw2DHist(self.hval5, 'LBC', 'low')
                self.c1.Modified()
                self.c1.Print("%s/RMSLBCLow.png" % self.dir)
                #EBA Low Gain
                self.c1.Clear()
                self.Draw2DHist(self.hval6, 'EBA', 'low')
                self.c1.Modified()
                self.c1.Print("%s/RMSEBALow.png" % self.dir)
                #EBC Low Gain
                self.c1.Clear()
                self.Draw2DHist(self.hval7, 'EBC', 'low')
                self.c1.Modified()
                self.c1.Print("%s/RMSEBCLow.png" % self.dir)

                #Print histograms to one pdf
                self.c1.Clear()
                self.c1.Divide(2,2)
                self.c1.cd(1)
                self.Draw2DHist(self.hval0, 'LBA', 'high')

                self.c1.cd(2)
                self.Draw2DHist(self.hval4, 'LBA', 'low')

                self.c1.cd(3)
                self.Draw2DHist(self.hval1, 'LBC', 'high')

                self.c1.cd(4)
                self.Draw2DHist(self.hval5, 'LBC', 'low')
                self.c1.Modified()
                self.c1.Print("%s/RMSPlotsAll.pdf(" % self.dir)

                self.c1.cd(1)
                self.Draw2DHist(self.hval2, 'EBA', 'high')

                self.c1.cd(2)
                self.Draw2DHist(self.hval6, 'EBA', 'low')

                self.c1.cd(3)
                self.Draw2DHist(self.hval3, 'EBC', 'high')

                self.c1.cd(4)
                self.Draw2DHist(self.hval7, 'EBC', 'low')
                self.c1.Modified()
                self.c1.Print("%s/RMSPlotsAll.pdf)" % self.dir)

                #Format and print 1D histogram
                self.c1.Clear()
                self.c1.SetLogy(1)
                xtitle = 'CIS Calibration RMS / Mean [%]'
                self.hlo.GetXaxis().SetTitle(xtitle)
                self.hhi.GetXaxis().SetTitle(xtitle)
                ytitle='Number of ADC Channels'
                self.hlo.GetYaxis().SetTitle(ytitle)
                self.hhi.GetYaxis().SetTitle(ytitle)
                self.hhi.GetYaxis().SetRangeUser(0.1,100000)
                self.hlo.GetYaxis().SetRangeUser(0.1,100000)
                print("Entries HG", self.hhi.GetEntries())
                print("Entries LG" ,self.hlo.GetEntries())

                ROOT.gStyle.SetOptStat(0)
                self.c1.Modified()
                self.hlo.Draw('')
                self.hhi.Draw('SAME')
                # self.line.Draw('SAME')
                #self.horline.Draw()
                #Old command for stat boxes, removed 2018 but kept as comment in case they are wanted back
                '''
                ptstatshi = ROOT.TPaveStats(0.7,0.45,0.9,0.65,"brNDC")
                ptstatshi.SetName("statshi")
                ptstatshi.SetBorderSize(0)
                ptstatshi.SetTextAlign(12)
                text = ptstatshi.AddText("high-gain")
                text.SetTextSize(0.046)
                #ptstatshi.AddText("Entries  = %i" % self.hhi.GetEntries())
                ptstatshi.AddText("HG Mean     = %10.4f" % self.hhi.GetMean())
                ptstatshi.AddText("HG RMS      = %10.4f" % self.hhi.GetRMS())
                #ptstatshi.AddText("Overflow = %d" % self.hhi.GetBinContent(self.hhi.GetNbinsX()+1))
                ptstatshi.SetOptStat(1)
                ptstatshi.SetOptFit(0)
                ptstatshi.Draw()

                ptstatslo = ROOT.TPaveStats(0.7,0.7,0.9,0.9,"brNDC")
                ptstatslo.SetName("statslo")
                ptstatslo.SetBorderSize(0)
                ptstatslo.SetTextAlign(12)
                text = ptstatslo.AddText("low-gain")
                text.SetTextSize(0.046)
                #ptstatslo.AddText("Entries  = %i   " % self.hlo.GetEntries())
                ptstatslo.AddText("LG Mean     = %10.4f" % self.hlo.GetMean())
                ptstatslo.AddText("LG RMS      = %10.4f" % self.hlo.GetRMS())
                #ptstatslo.AddText("Overflow = %d" % self.hlo.GetBinContent(self.hlo.GetNbinsX()+1))
                ptstatslo.SetOptStat(1)
                ptstatslo.SetOptFit(0)
                ptstatslo.Draw()
                '''
                meanhi = ROOT.TLatex()
                meanhi.SetNDC()
                meanhi.SetTextSize(.032)
                meanhi.DrawLatex(.60,.88," HG Mean %10.2f%%" % self.hhi.GetMean())

                rmshi = ROOT.TLatex()
                rmshi.SetNDC()
                rmshi.SetTextSize(.032)
                rmshi.DrawLatex(.60,.84," HG RMS  %10.2f%%" % self.hhi.GetRMS())

                meanlo = ROOT.TLatex()
                meanlo.SetNDC()
                meanlo.SetTextSize(.032)
                meanlo.DrawLatex(.60,.80," LG Mean  %10.2f%%" % self.hlo.GetMean())
                
                rmslo = ROOT.TLatex()
                rmslo.SetNDC()
                rmslo.SetTextSize(.032)
                rmslo.DrawLatex(.60,.76," LG RMS   %10.2f%%"   % self.hlo.GetRMS())
                                #legend
                # leg = ROOT.TLegend(0.47,0.4,0.86,0.55, "","brNDC")

                leg = ROOT.TLegend(0.60,0.50,0.70,0.60, "","brNDC")
                leg.SetTextSize(0.032)
                leg.AddEntry(self.hdem," High Gain","l")
                leg.AddEntry(self.hdemlo," Low Gain","l")
                # leg.AddEntry(self.line,"stability boundary","l")
                leg.SetBorderSize(0)
                leg.Draw()

                #For public plots
                # l = ROOT.TLatex()
                # l.SetNDC()
                # l.SetTextFont(72)
                # l.DrawLatex(0.22,0.863,"ATLAS") 

                # l2 = ROOT.TLatex()
                # l2.SetNDC()
                # #l2.SetTextFont(72)
                # l2.DrawLatex(0.31,0.863,"Preliminary")
 
                l3 = ROOT.TLatex()
                l3.SetNDC()
                l3.DrawLatex(0.22, 0.807, "Tile Calorimeter")
                

                l4 = ROOT.TLatex()
                l4.SetNDC()
                l4.DrawLatex(0.22, 0.751, self.dateLabel)
                
                
                self.c1.Print('%s/time_spread_rms.png' % self.dir)
                self.c1.Print('%s/time_spread_rms.eps' % self.dir)
                self.c1.Print('%s/time_spread_rms.pdf' % self.dir)
                self.c1.Print('%s/time_spread_rms.C' % self.dir)


                # RMS plots for demonstrator 
                self.c1.Clear()
                self.c1.SetLogy(1)
                xtitle = 'CIS Calibration RMS / Mean [%]'
                self.hdem.GetXaxis().SetTitle(xtitle)
                self.hdemlo.GetXaxis().SetTitle(xtitle)
                ytitle='Number of ADC Channels'
                self.hdem.GetYaxis().SetTitle(ytitle)
                self.hdemlo.GetYaxis().SetTitle(ytitle)
                self.hdem.GetYaxis().SetRangeUser(0.1,1000)
                self.hdemlo.GetYaxis().SetRangeUser(0.1,1000)

                ROOT.gStyle.SetOptStat(0)
                self.c1.Modified()
                self.hdem.Draw('')
                self.hdemlo.Draw('SAME')

                meandem = ROOT.TLatex()
                meandem.SetNDC()
                meandem.SetTextSize(.032)
                meandem.DrawLatex(.66,.88," HG Mean %10.3f%%" % self.hdem.GetMean())
                
                rmsdem = ROOT.TLatex()
                rmsdem.SetNDC()
                rmsdem.SetTextSize(.032)
                rmsdem.DrawLatex(.66,.84," HG RMS %10.3f%%"   % self.hdem.GetRMS())

                meandemlo = ROOT.TLatex()
                meandemlo.SetNDC()
                meandemlo.SetTextSize(.032)
                meandemlo.DrawLatex(.66,.80," LG Mean %10.3f%%" % self.hdemlo.GetMean())
                
                rmsdemlo = ROOT.TLatex()
                rmsdemlo.SetNDC()
                rmsdemlo.SetTextSize(.032)
                rmsdemlo.DrawLatex(.66,.76," LG RMS  %10.3f%%"   % self.hdemlo.GetRMS())

                #legend
                #leg = ROOT.TLegend(0.47,0.4,0.86,0.55, "","brNDC")

                leg = ROOT.TLegend(0.60,0.50,0.70,0.60, "","brNDC")
                leg.SetTextSize(0.032)
                leg.AddEntry(self.hdem,"Dem. High Gain","l")
                leg.AddEntry(self.hdemlo,"Dem. Low Gain","l")
                # leg.AddEntry(self.line,"stability boundary","l")
                leg.SetBorderSize(0)
                leg.Draw()

                #For public plots
                l = ROOT.TLatex()
                l.SetNDC()
                l.SetTextFont(72)
                l.DrawLatex(0.22,0.863,"ATLAS") 

                l2 = ROOT.TLatex()
                l2.SetNDC()
                #l2.SetTextFont(72)
                l2.DrawLatex(0.35,0.863,"Preliminary")
 
                l3 = ROOT.TLatex()
                l3.SetNDC()
                l3.DrawLatex(0.22, 0.807, "Tile Calorimeter")
                

                l4 = ROOT.TLatex()
                l4.SetNDC()
                l4.DrawLatex(0.22, 0.751, self.dateLabel)

                self.c1.Print('%s/time_spread_rms_dem.png' % self.dir)
                self.c1.Print('%s/time_spread_rms_dem.eps' % self.dir)
                self.c1.Print('%s/time_spread_rms_dem.pdf' % self.dir)
                self.c1.Print('%s/time_spread_rms_dem.C' % self.dir)

        def ProcessRegion(self, region):
                gh = region.GetHash() #region name
                gh_list = gh.split('_')
                #If we don't have an ADC, then we don't care
                if not len(gh_list) == 5:
                        return

                calib_list = [] #contains CIS constants for this ADC
                var_list = []
                for event in region.GetEvents():
                        runnum = event.run.runNumber
                        if int(runnum) in [248375, 248585, 248651, 253312, 248912]:
                                continue
                        if (abs(event.data['calibration'] - 1.28999996185) < 10**(-9) ):
                            print("DEFAULT USED, ommitting run : " + str(runnum) + " ++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                            continue
 
                        calib = event.data['calibration']
                        # print("Run Number: " + str(runnum) + " | " + str(calib))
                        # print("\n")
                        calib_list.append(calib)

                #If there are few runs with data, we don't really care about the RMS
                if len(calib_list) < 3:
                        return

                #Throwout highest and lowest values
                calib_list.pop(calib_list.index(max(calib_list)))
                calib_list.pop(calib_list.index(min(calib_list)))

                #For filling the 2D histograms
                det, part, mod, chan, gain = gh.split('_')
                mod = int(mod[1:])
                chan = int(chan[1:])

                #Calculate mean and rms 
                # What about if there are multiple iovs
                mean_sum = 0
                rms_sum = 0
                for calib in calib_list:
                        mean_sum += calib
                mean = mean_sum / len(calib_list)
                ## Patch
                ## uncomment to produce log files showing which channels gavce high RMS/mean
                if mean == 0:
                        # with open(os.path.join(src.oscalls.getResultDirectory(),'output/cis/RMS/RMSMeanErrors.log'), 'a') as error_logfile:
                        #         error_logfile.write("{}\t{}\n".format(gh,mean))
                        mean = 0.00001
                        # print(f"RMS Error in {gh}")

                        
                for calib in calib_list:
                        rms_sum += (calib - mean)**2
                        rms_now = sqrt(rms_sum /len(calib_list))
                        # Maybe turn this into a logfile if one wants to know all values (for now we just set a threshold and print only those values to the log file)
                        #print("Calib:" + str(calib) + " | " + "Cum. RMS/MEAN " + str(rms_now/mean)) 
                        # print("\n")
                rms = sqrt( rms_sum / len(calib_list))
                print(gh, mean, rms, rms/mean)

                # if rms/mean >0.3:
                #         with open(os.path.join(src.oscalls.getResultDirectory(),'output/cis/RMS/HighRMS.log'), 'a') as rms_logfile:
                #                 rms_logfile.write("{}\t{}\n".format(gh,rms/mean))
                        # print("High RMS/Mean in {}:\t {:.2}%".format(gh, rms/mean))
                #print "Calib:" + str(calib) + " | " + "Cum. RMS " + str(rms_now)  
                #print("\n")
                #Fill the appropriate histograms
                if 'lo' in gh:
                        if "LBA_m14" in gh:
                                self.hdemlo.Fill(100*rms/mean)
                                # print(rms/mean)
                        else:
                                self.hlo.Fill(100*rms/mean)
                                if 'LBA' in gh:
                                        self.hval4.SetBinContent(mod, chan+1, 100*rms/mean)
                                elif 'LBC' in gh:
                                        self.hval5.SetBinContent(mod, chan+1, 100*rms/mean)
                                elif 'EBA' in gh:
                                        self.hval6.SetBinContent(mod, chan+1, 100*rms/mean)
                                elif 'EBC' in gh:
                                        self.hval7.SetBinContent(mod, chan+1, 100*rms/mean)
                else:
                        if "LBA_m14" in gh:
                                self.hdem.Fill(100*rms/mean)
                                # print(rms/mean)
                        else:
                                self.hhi.Fill(100*rms/mean)
                                if 'LBA' in gh:
                                        self.hval0.SetBinContent(mod, chan+1, 100*rms/mean)
                                elif 'LBC' in gh:
                                        self.hval1.SetBinContent(mod, chan+1, 100*rms/mean)
                                elif 'EBA' in gh:
                                        self.hval2.SetBinContent(mod, chan+1, 100*rms/mean)
                                elif 'EBC' in gh:
                                        self.hval3.SetBinContent(mod, chan+1, 100*rms/mean)

        
        def Draw2DHist(self, hist, part, gain):
                #Function that formats the 2D histograms
                if gain == 'low':
                        gainname = 'Low-Gain'
                else:
                        gainname = 'High-Gain'

                #Set min and max for colz
                min = 0.0
                max = 1.0
                
                #Format axes
                hist.GetXaxis().SetTitle("Module Number")
                hist.GetXaxis().CenterTitle(True)
                hist.GetYaxis().SetTitle("Channel Number")
                hist.GetYaxis().CenterTitle(True)
                hist.SetMinimum(min)
                hist.SetMaximum(max)
                hist.Draw("COLZ")

                #Stick legend in upper left corner
                leg = ROOT.TLatex()
                leg.SetNDC()
                leg.SetTextSize(0.03)
                leg.DrawLatex(0.85, 0.980, "RMS/Mean")
                
                title = ROOT.TLatex()
                title.SetNDC()
                title.SetTextFont(62)
                title.SetTextSize(.045)
                title.DrawLatex(0.14, .96, "%s %s RMS/Mean in CIS Constant" % (part, gainname))

