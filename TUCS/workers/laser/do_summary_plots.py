############################################################
#
# do_summary_plots.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# August 26, 2009
#
# Goal: 
# Provide the standard DQ analysis for LASER stability runs
#
# Input parameters are:
#
# -> gain: the gain you want to test (0=LOW, 1=HIGH, 2=BOTH)
#         
# -> limit: the maximum tolerable variation (in %). If this variation
#           is excedeed the channels are flagged as BAD
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.laser.toolbox import *
from src.oscalls import *

import src.MakeCanvas
import time
import math

class do_summary_plots(GenericWorker):
    "Produce summary plots"

    def __init__(self, limit=2, gain=0):


        self.limit = limit
        graph_lim  = 5*self.limit
        graph_lim_calib_up = 0
        graph_lim_calib_down = 0
        
        self.gain  = gain

        if self.gain == 0:
            self.gname = 'lg'
            graph_lim_calib_up = 1
            graph_lim_calib_down = -0.05
        if self.gain == 1:
            self.gname = 'hg'
            graph_lim_calib_up = 0.01
            graph_lim_calib_down = -0.002
        if self.gain == 2:
            self.gname = 'global'
            
        self.PMTool = LaserTools()

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        # Create the different canvas
        self.channel = src.MakeCanvas.MakeCanvas()
        self.fiber   = src.MakeCanvas.MakeCanvas()
        self.status  = src.MakeCanvas.MakeCanvas()
            
        self.channel.SetFrameFillColor(0)
        self.channel.SetFillColor(0);
        self.channel.SetBorderMode(0);
        self.channel.SetLogy(1); 
            
        self.fiber.SetFrameFillColor(0)
        self.fiber.SetFillColor(0);
        self.fiber.SetBorderMode(0);
        self.fiber.SetLogy(1); 

        # Then create the different histograms

        self.part_bchan  = [] # partition bad channels
        self.part_wchan  = [] # partition slightly out of range channels
        self.part_nochan = [] # partition channels w/no data
        
        for i in range(4):
            pname = self.PMTool.get_partition_name(i)
            self.part_bchan.append(ROOT.TH2F("%s bad"%(pname),"",500,0.,65.,500,0.,49.))
            self.part_wchan.append(ROOT.TH2F("%s warn"%(pname),"",500,0.,65.,500,0.,49.))
            self.part_nochan.append(ROOT.TH2F("%s nodat"%(pname),"",500,0.,65.,500,0.,49.))

        self.ch  = ROOT.TH1F('channel variation', '', 100, -graph_lim, graph_lim)

        self.calib = ROOT.TH1F('real channel variation', '', 100, graph_lim_calib_down, graph_lim_calib_up)

        # DB : added these histo to split in cell for LB
        self.chA  = ROOT.TH1F('channel variation A', '', 100, -graph_lim/3, graph_lim/3)
        self.chB  = ROOT.TH1F('channel variation B', '', 100, -graph_lim/3, graph_lim/3)
        self.chD  = ROOT.TH1F('channel variation D', '', 100, -graph_lim/3, graph_lim/3)

        # DB : added these histo to split in cell for EB
        self.chEA  = ROOT.TH1F('channel variation EB A', '', 100, -graph_lim/3, graph_lim/3)
        self.chEB  = ROOT.TH1F('channel variation EB B', '', 100, -graph_lim/3, graph_lim/3)
        self.chED  = ROOT.TH1F('channel variation EB D', '', 100, -graph_lim/3, graph_lim/3)

        # DB : added histo specific to A cells : drifting cells with lumi
        self.chA12  = ROOT.TH1F('channel variation A12', '', 50, -graph_lim/3, graph_lim/3)
        self.chA34  = ROOT.TH1F('channel variation A34', '', 50, -graph_lim/3, graph_lim/3)
        self.chA56  = ROOT.TH1F('channel variation A56', '', 50, -graph_lim/3, graph_lim/3)
        self.chA78  = ROOT.TH1F('channel variation A78', '', 50, -graph_lim/3, graph_lim/3)
        self.chA90  = ROOT.TH1F('channel variation A90', '', 50, -graph_lim/3, graph_lim/3)

        
        self.fib = ROOT.TH1F('fiber variation'  , '', 100, -graph_lim, graph_lim)

        # Finally the file containing the bad channel list

        filename = "%s/problem_list_%s.txt" % (self.dir,self.gname)
        self.outfile = open(filename, 'w')        


    # Here we deal with all the necessary cosmetics

    def ProcessStop(self):
        
        self.outfile.close()        

        if self.gain == 2: # In this case we just produce a text file
            return

        # First we create nice exclusion zones

        x_axis_l,x_axis_r = array( 'f' ), array( 'f' )
        y_axis = array( 'f' )

        for i in range(50):
            x_axis_l.append(-self.limit)
            x_axis_r.append(self.limit)
            y_axis.append(i)
        
        self.left= ROOT.TGraph(50,x_axis_l,y_axis)
        self.left.SetLineColor(0)
        self.left.SetFillColor(623)
        self.left.SetLineWidth(30000)
        self.left.SetFillStyle(3001)

        self.right= ROOT.TGraph(50,x_axis_r,y_axis)
        self.right.SetLineColor(0)
        self.right.SetFillColor(623)
        self.right.SetLineWidth(-30000)
        self.right.SetFillStyle(3001)


        self.plot_ch_name   = "channel_var_%d_%s" % (self.runno,self.gname)
        self.plot_calib_name   = "channel_calib_%d_%s" % (self.runno,self.gname)
        self.plot_chA_name   = "channel_var_A_%d_%s" % (self.runno,self.gname)
        self.plot_chEA_name   = "channel_var_EA_%d_%s" % (self.runno,self.gname)

        self.plot_chA12_name   = "channel_var_A12_%d_%s" % (self.runno,self.gname)
        self.plot_chD_name   = "channel_var_D_%d_%s" % (self.runno,self.gname)
        self.plot_chED_name   = "channel_var_ED_%d_%s" % (self.runno,self.gname)
        
        self.plot_fib_name  = "fiber_var_%d_%s" % (self.runno,self.gname)
        self.plot_stat_name = "status_%d_%s" % (self.runno,self.gname)

        # Then the channel status plot
            
        self.channel.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        
        self.ch.GetXaxis().SetLabelOffset(0.015)
        self.ch.GetXaxis().SetLabelSize(0.04)
        self.ch.GetYaxis().SetLabelSize(0.04)
        self.ch.GetXaxis().SetTitle("Channel variation (in %)")
        self.ch.Draw()
        self.left.Draw()
        self.right.Draw()
        self.ch.Draw("same") # This is not very nice but only way to have graph on top of colored zones
        
        # Then we draw the fit result on the plots
        
        self.ch.Fit("gaus","Q0")
        self.ch_fit= ROOT.TVirtualFitter.Fitter(self.ch)
        self.pt_ch = ROOT.TPaveText(0.64,0.54,0.82,0.65,"brNDC")
        self.pt_ch.SetFillColor(5)
        self.pt_ch.SetTextSize(0.05)
        self.pt_ch.SetTextFont(42)                        
        self.pt_ch.AddText("#sigma = %.2f%s\n" % (self.ch_fit.GetParameter(2),'%'))
        self.pt_ch.Draw()

        
        self.date = ROOT.TPaveText(0.75,0.92,0.95,0.97,"brNDC")
        self.date.SetFillColor(18)
        self.date.SetTextSize(0.035)
        self.date.SetTextFont(42)
        self.date.AddText("Date: %s" % (ROOT.TDatime().GetDate()))
        self.date.Draw()
              
        # hack
        self.channel.SetLeftMargin(0.14)
        self.channel.SetRightMargin(0.14)
        self.channel.Modified()

        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
        l.DrawLatex(0.1922,0.867,"ATLAS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.1922,0.811,"Preliminary");

        self.channel.Modified()  

        self.channel.Print("%s/%s.png" % (self.dir,self.plot_ch_name))
        self.channel.Print("%s/%s.eps" % (self.dir,self.plot_ch_name))
        self.channel.Print("%s/%s.root" % (self.dir,self.plot_ch_name))

        # Then the channel status plot without correction
        
        self.calib.GetXaxis().SetLabelOffset(0.015)
        self.calib.GetXaxis().SetLabelSize(0.04)
        self.calib.GetYaxis().SetLabelSize(0.04)
        self.calib.GetXaxis().SetTitle("RAW_PMT/Diode1")
        self.calib.Draw()
        self.left.Draw()
        self.right.Draw()
        self.calib.Draw("same") # This is not very nice but only way to have graph on top of colored zones
        
        # Then we draw the fit result on the plots
        
        self.calib.Fit("gaus","Q0")
        self.calib_fit= ROOT.TVirtualFitter.Fitter(self.calib)
        self.pt_calib = ROOT.TPaveText(0.64,0.54,0.82,0.65,"brNDC")
        self.pt_calib.SetFillColor(5)
        self.pt_calib.SetTextSize(0.05)
        self.pt_calib.SetTextFont(42)                        
        self.pt_calib.AddText("#sigma = %.4f%s\n" % (self.calib_fit.GetParameter(2),'%'))
        #self.pt_calib.AddText("\n")
        #self.pt_calib.AddText("RMS = %.2f%s\n" % (self.calib.GetRMS(),'%'))
        self.pt_calib.Draw()

        
        self.date = ROOT.TPaveText(0.75,0.92,0.95,0.97,"brNDC")
        self.date.SetFillColor(18)
        self.date.SetTextSize(0.035)
        self.date.SetTextFont(42)
        self.date.AddText("Date: %s" % (ROOT.TDatime().GetDate()))
        self.date.Draw()
              
        # hack
        self.channel.SetLeftMargin(0.14)
        self.channel.SetRightMargin(0.14)
        self.channel.Modified()

        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
#        l.DrawLatex(0.1922,0.867,"ATLAS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
#        l2.DrawLatex(0.1922,0.811,"Preliminary");

        self.channel.Modified()  

        self.channel.Print("%s/%s.png" % (self.dir,self.plot_calib_name))
        self.channel.Print("%s/%s.eps" % (self.dir,self.plot_calib_name))
        self.channel.Print("%s/%s.root" % (self.dir,self.plot_calib_name))
        #self.channel.Print("%s/%s.C" % (self.dir,self.plot_calib_name))





        #------------------------------- comparison A, D (Long Barrel)
        
        self.channel.SetLogy(0); 

        self.chA.GetXaxis().SetLabelOffset(0.015)
        self.chA.GetXaxis().SetLabelSize(0.04)
        self.chA.GetYaxis().SetLabelSize(0.04)
        self.chA.GetXaxis().SetTitle("A Cells Gain variation (in %)")
        self.chA.Draw()

        self.chA12.SetLineColor(2)
        self.chA34.SetLineColor(2)
        self.chA56.SetLineColor(4)
        self.chA78.SetLineColor(4)
        self.chA90.SetLineColor(6)

        self.chA12.SetLineStyle(1)
        self.chA34.SetLineStyle(2)
        self.chA56.SetLineStyle(1)
        self.chA78.SetLineStyle(2)
        self.chA90.SetLineStyle(1)
        
        
#        self.left.Draw()
#        self.right.Draw()

        
        # Then we draw the fit result on the plots
        
        self.chA.Fit("gaus","Q0")
        self.chA_fit= ROOT.TVirtualFitter.Fitter(self.chA)
        self.pt_chA = ROOT.TPaveText(0.64,0.54,0.82,0.65,"brNDC")
        self.pt_chA.SetFillColor(5)
        self.pt_chA.SetTextSize(0.05)
        self.pt_chA.SetTextFont(42)                        
        self.pt_chA.AddText("#sigma = %.2f%s\n" % (self.chA_fit.GetParameter(2),'%'))
        #self.pt_ch.AddText("\n")
        #self.pt_ch.AddText("RMS = %.2f%s\n" % (self.chA.GetRMS(),'%'))
        self.pt_chA.Draw()

        
        self.date = ROOT.TPaveText(0.75,0.92,0.95,0.97,"brNDC")
        self.date.SetFillColor(18)
        self.date.SetTextSize(0.035)
        self.date.SetTextFont(42)
        self.date.AddText("Date: %s" % (ROOT.TDatime().GetDate()))
        self.date.Draw()
              
        # hack
        self.channel.SetLeftMargin(0.14)
        self.channel.SetRightMargin(0.14)
        self.channel.Modified()

        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
#        l.DrawLatex(0.1922,0.867,"ATLAS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
#        l2.DrawLatex(0.1922,0.811,"Preliminary");

        self.channel.Modified()  

        self.channel.Print("%s/%s.png" % (self.dir,self.plot_chA_name))
        self.channel.Print("%s/%s.eps" % (self.dir,self.plot_chA_name))
        self.channel.Print("%s/%s.root" % (self.dir,self.plot_chA_name))
        #self.channel.Print("%s/%s.C" % (self.dir,self.plot_chA_name))


        #----  lets split A cells in various contribution

        self.channel.SetLogy(0); 

        self.chA12.GetXaxis().SetLabelOffset(0.015)
        self.chA12.GetXaxis().SetLabelSize(0.04)
        self.chA12.GetYaxis().SetLabelSize(0.04)
        self.chA12.GetXaxis().SetTitle("A Cells Gain variation (in %)")


        self.chA12.SetLineColor(1)
        self.chA34.SetLineColor(2)
        self.chA56.SetLineColor(4)
        self.chA78.SetLineColor(4)
        self.chA90.SetLineColor(6)

        self.chA12.SetLineStyle(1)
        self.chA34.SetLineStyle(2)
        self.chA56.SetLineStyle(2)
        self.chA78.SetLineStyle(2)
        self.chA90.SetLineStyle(1)
        
        self.chA12.Draw()
#        self.chA34.Draw("same")
        self.chA56.Draw("same")
#        self.chA78.Draw("same")
        self.chA90.Draw("same")
        
#        self.left.Draw()
#        self.right.Draw()

        
        # Then we draw the fit result on the plots
        

        
        self.date = ROOT.TPaveText(0.75,0.92,0.95,0.97,"brNDC")
        self.date.SetFillColor(18)
        self.date.SetTextSize(0.035)
        self.date.SetTextFont(42)
        self.date.AddText("Date: %s" % (ROOT.TDatime().GetDate()))
        self.date.Draw()
              
        # hack
        self.channel.SetLeftMargin(0.14)
        self.channel.SetRightMargin(0.14)
        self.channel.Modified()

        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
#        l.DrawLatex(0.1922,0.867,"ATLAS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
#        l2.DrawLatex(0.1922,0.811,"Preliminary");

        self.channel.Modified()  

#        self.channel.Print("%s/%s.png" % (self.dir,self.plot_chA12_name))
        self.channel.Print("%s/%s.eps" % (self.dir,self.plot_chA12_name))
        self.channel.Print("%s/%s.root" % (self.dir,self.plot_chA12_name))
        #self.channel.Print("%s/%s.C" % (self.dir,self.plot_ch12_name))


        #----

        self.chD.GetXaxis().SetLabelOffset(0.015)
        self.chD.GetXaxis().SetLabelSize(0.04)
        self.chD.GetYaxis().SetLabelSize(0.04)
        self.chD.GetXaxis().SetTitle("D Cells variation (in %)")
        self.chD.Draw()

        
#        self.left.Draw()
#        self.right.Draw()

        
        # Then we draw the fit result on the plots
        
        self.chD.Fit("gaus","Q0")
        self.chD_fit= ROOT.TVirtualFitter.Fitter(self.chD)
        self.pt_chD = ROOT.TPaveText(0.64,0.54,0.82,0.65,"brNDC")
        self.pt_chD.SetFillColor(5)
        self.pt_chD.SetTextSize(0.05)
        self.pt_chD.SetTextFont(42)                        
        self.pt_chD.AddText("#sigma = %.2f%s\n" % (self.chD_fit.GetParameter(2),'%'))
        #self.pt_chD.AddText("\n")
        #self.pt_chD.AddText("RMS = %.2f%s\n" % (self.chD.GetRMS(),'%'))
        self.pt_chD.Draw()

        
        self.date = ROOT.TPaveText(0.75,0.92,0.95,0.97,"brNDC")
        self.date.SetFillColor(18)
        self.date.SetTextSize(0.035)
        self.date.SetTextFont(42)
        self.date.AddText("Date: %s" % (ROOT.TDatime().GetDate()))
        self.date.Draw()
              
        # hack
        self.channel.SetLeftMargin(0.14)
        self.channel.SetRightMargin(0.14)
        self.channel.Modified()

        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
#        l.DrawLatex(0.1922,0.867,"ATLAS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
#        l2.DrawLatex(0.1922,0.811,"Preliminary");

        self.channel.Modified()  

        self.channel.Print("%s/%s.png" % (self.dir,self.plot_chD_name))
        self.channel.Print("%s/%s.eps" % (self.dir,self.plot_chD_name))
        self.channel.Print("%s/%s.root" % (self.dir,self.plot_chD_name))
        #self.channel.Print("%s/%s.C" % (self.dir,self.plot_chD_name))


        #------- A extended barrel

        self.chEA.GetXaxis().SetLabelOffset(0.015)
        self.chEA.GetXaxis().SetLabelSize(0.04)
        self.chEA.GetYaxis().SetLabelSize(0.04)
        self.chEA.GetXaxis().SetTitle("A Cells Gain variation (in %)")
        self.chEA.Draw()

        
        
#        self.left.Draw()
#        self.right.Draw()

        
        # Then we draw the fit result on the plots
        
        self.chEA.Fit("gaus","Q0")
        self.chEA_fit= ROOT.TVirtualFitter.Fitter(self.chEA)
        self.pt_chEA = ROOT.TPaveText(0.64,0.54,0.82,0.65,"brNDC")
        self.pt_chEA.SetFillColor(5)
        self.pt_chEA.SetTextSize(0.05)
        self.pt_chEA.SetTextFont(42)                        
        self.pt_chEA.AddText("#sigma = %.2f%s\n" % (self.chEA_fit.GetParameter(2),'%'))
        #self.pt_ch.AddText("\n")
        #self.pt_ch.AddText("RMS = %.2f%s\n" % (self.chEA.GetRMS(),'%'))
        self.pt_chEA.Draw()

        
        self.date = ROOT.TPaveText(0.75,0.92,0.95,0.97,"brNDC")
        self.date.SetFillColor(18)
        self.date.SetTextSize(0.035)
        self.date.SetTextFont(42)
        self.date.AddText("Date: %s" % (ROOT.TDatime().GetDate()))
        self.date.Draw()
              
        # hack
        self.channel.SetLeftMargin(0.14)
        self.channel.SetRightMargin(0.14)
        self.channel.Modified()

        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
#        l.DrawLatex(0.1922,0.867,"ATLAS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
#        l2.DrawLatex(0.1922,0.811,"Preliminary");

        self.channel.Modified()  

        self.channel.Print("%s/%s.png" % (self.dir,self.plot_chEA_name))
        self.channel.Print("%s/%s.eps" % (self.dir,self.plot_chEA_name))
        self.channel.Print("%s/%s.root" % (self.dir,self.plot_chEA_name))
        #self.channel.Print("%s/%s.C" % (self.dir,self.plot_chEA_name))


        #------- D extended barrel

        self.chED.GetXaxis().SetLabelOffset(0.015)
        self.chED.GetXaxis().SetLabelSize(0.04)
        self.chED.GetYaxis().SetLabelSize(0.04)
        self.chED.GetXaxis().SetTitle("D Cells Gain variation (in %)")
        self.chED.Draw()

        
        
#        self.left.Draw()
#        self.right.Draw()

        
        # Then we draw the fit result on the plots
        
        self.chED.Fit("gaus","Q0")
        self.chED_fit= ROOT.TVirtualFitter.Fitter(self.chED)
        self.pt_chED = ROOT.TPaveText(0.64,0.54,0.82,0.65,"brNDC")
        self.pt_chED.SetFillColor(5)
        self.pt_chED.SetTextSize(0.05)
        self.pt_chED.SetTextFont(42)                        
        self.pt_chED.AddText("#sigma = %.2f%s\n" % (self.chED_fit.GetParameter(2),'%'))
        #self.pt_ch.AddText("\n")
        #self.pt_ch.AddText("RMS = %.2f%s\n" % (self.chED.GetRMS(),'%'))
        self.pt_chED.Draw()

        
        self.date = ROOT.TPaveText(0.75,0.92,0.95,0.97,"brNDC")
        self.date.SetFillColor(18)
        self.date.SetTextSize(0.035)
        self.date.SetTextFont(42)
        self.date.AddText("Date: %s" % (ROOT.TDatime().GetDate()))
        self.date.Draw()
              
        # hack
        self.channel.SetLeftMargin(0.14)
        self.channel.SetRightMargin(0.14)
        self.channel.Modified()

        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
#        l.DrawLatex(0.1922,0.867,"ATLAS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
#        l2.DrawLatex(0.1922,0.811,"Preliminary");

        self.channel.Modified()  

        self.channel.Print("%s/%s.png" % (self.dir,self.plot_chED_name))
        print('Fait !!')
        self.channel.Print("%s/%s.eps" % (self.dir,self.plot_chED_name))
        self.channel.Print("%s/%s.root" % (self.dir,self.plot_chED_name))
        #self.channel.Print("%s/%s.C" % (self.dir,self.plot_chED_name))

        #-------------------------------------

        
        # Then the fiber one
                    
        self.fiber.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)

        self.fib.GetXaxis().SetLabelOffset(0.015)
        self.fib.GetXaxis().SetLabelSize(0.04)
        self.fib.GetYaxis().SetLabelSize(0.04)
        self.fib.GetXaxis().SetTitle("Fiber variation (in %)")
        self.fib.Draw()
        self.left.Draw()
        self.right.Draw()
        self.fib.Draw("same")

        # Then we draw the fit result on the plots
        
        self.fib.Fit("gaus","Q0")
        self.fib_fit= ROOT.TVirtualFitter.Fitter(self.fib)
        self.pt_fib = ROOT.TPaveText(0.64,0.54,0.82,0.65,"brNDC")
        self.pt_fib.SetFillColor(5)
        self.pt_fib.SetTextSize(0.05)
        self.pt_fib.SetTextFont(42)                        
        self.pt_fib.AddText("#sigma = %.2f%s\n" % (self.fib_fit.GetParameter(2),'%'))
        self.pt_fib.Draw()
              
        # hack
        self.fiber.SetLeftMargin(0.14)
        self.fiber.SetRightMargin(0.14)
        self.fiber.Modified()

        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
        l.DrawLatex(0.1922,0.867,"ATLAS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.1922,0.811,"Preliminary");

        self.fiber.Modified()  

        self.fiber.Print("%s/%s.png" % (self.dir,self.plot_fib_name))
        self.fiber.Print("%s/%s.eps" % (self.dir,self.plot_fib_name))
        self.fiber.Print("%s/%s.root" % (self.dir,self.plot_fib_name))

        # Then the channel status
            
        self.status.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        self.status.Divide(2,2)
        
        for i in range(4):
            pname = self.PMTool.get_partition_name(i)
            self.status.cd(i+1)
            self.status.cd(i+1).SetGridx(1)
            self.status.cd(i+1).SetGridy(1)
            self.status.cd(i+1).SetTickx(1)
            self.status.cd(i+1).SetTicky(1)
            self.part_nochan[i].GetXaxis().SetTitle("%s Module number"%(pname));
            self.part_nochan[i].GetXaxis().SetNdivisions(515);            
            self.part_nochan[i].GetXaxis().SetTitleOffset(1.2)
            self.part_nochan[i].GetYaxis().SetTitle("Channel number within module");
            self.part_nochan[i].GetYaxis().SetNdivisions(619);
            self.part_nochan[i].Draw()
            self.part_bchan[i].Draw("same")
            self.part_wchan[i].Draw("same")

        self.status.Print("%s/%s.png" % (self.dir,self.plot_stat_name))
        self.status.Print("%s/%s.eps" % (self.dir,self.plot_stat_name))
        self.status.Print("%s/%s.root" % (self.dir,self.plot_stat_name))         

        print("All the information produced were store in the following directory : %s" % (self.dir)) 


    # Here we fill the histograms and the bad channel list

    def ProcessRegion(self, region):
                          
        if 'TILECAL' == region.GetHash():

            partition_list = set()
            fib_list = set()

            first = True

            first_LG = True
            first_HG = True
            
            bad_fib_list    = []
            bad_las_list    = []
            bad_las_event   = []
            no_las_list     = []
            no_las_event    = []
            bad_las_list_K  = []
            bad_las_event_K = []
            no_las_list_K   = []
            no_las_event_K  = []
            
            for event in region.RecursiveGetEvents():

                if 'is_OK' in event.data:

                    #[p, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                    [p, i, j, w] = event.region.GetNumber()

                    if w!=self.gain and self.gain!=2:
                        continue

                    if first and self.gain!=2:
                        self.runno = event.run.runNumber
                        self.outfile.write('##########################################\n') 
                        self.outfile.write('#\n')
                        text = "# This is the LASER stability DQ summary\n"
                        self.outfile.write(text)
                        text = "# Summary for run %d\n" % (event.run.runNumber)
                        self.outfile.write(text)
                        text = "# Date of the run: %s\n" % (event.run.time_in_seconds)
                        self.outfile.write(text)
                        self.outfile.write('#\n')
                        text = "# Maximum relative variation accepted: +/-%.1f%s\n" % (self.limit,'%')
                        self.outfile.write(text)
                        self.outfile.write('#\n')
                        self.outfile.write('#\n')
                        text = "# LASER expert contact number: tilelas@mail.cern.ch\n"
                        self.outfile.write(text)     
                        self.outfile.write('##########################################\n')
                        self.outfile.write('\n') 
                        first=False
                    elif self.gain==2:
                        if first_LG and w==0:
                            first_LG        = False
                            self.ref_LG_evt = event
                        if first_HG and w==1:
                            first_HG        = False
                            self.ref_HG_evt = event 


                    if 'deviation' not in event.data: # No data
                        #[p, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                        [p, i, j, w] = event.region.GetNumber()
                        index        = self.PMTool.get_index(p-1, i-1, j, w)

                        if event.data['status']:
                            no_las_list_K.append(index)
                            no_las_event_K.append(event)
                        else:
                            no_las_list.append(index)
                            no_las_event.append(event)     

                    else:
                        #pmt    = self.PMTool.get_PMT_index(p-1,i-1,j)                          
                        [p, i, pmt, w] = event.region.GetNumber(1)
                        indice = self.PMTool.get_fiber_index(p-1,i-1,pmt)

                        if 'part_var' in event.data and p-1 not in partition_list:
                            print(self.PMTool.get_partition_name(p-1),"global variation =", event.data['part_var'],"%")
                            partition_list.add(p-1)
                            
                        if 'fiber_var' in event.data and indice not in fib_list:
                            fib_list.add(indice)
                            self.fib.Fill(event.data['fiber_var'])

                            if indice not in bad_fib_list and self.limit<math.fabs(event.data['fiber_var']):
                                bad_fib_list.append(indice)
                                                        
                        if not event.data['status']:   # Don't put event on summary plot if already on BC list
                            # Following selection remove the events with low LASER light (fiber problem)
                            self.calib.Fill(event.data['calibration'])
                            if (event.data['calibration']>0.0025 and event.run.data['wheelpos']==8)\
                                   or (event.data['calibration']>0.1 and event.run.data['wheelpos']==6):

                                Celln = self.PMTool.get_stable_cells(p-1,pmt) # Get cell name needs pmt number starting from 1
                                
                                self.ch.Fill(event.data['deviation'])

                                if (Celln == 0 and p<3):
                                    self.chA.Fill(event.data['deviation'])
                                elif (Celln == 1 and p<3):
                                    self.chB.Fill(event.data['deviation'])
                                elif (Celln == 3 and p<3):
                                    self.chD.Fill(event.data['deviation'])

                                if (p<3 and ( (pmt==2) or (pmt==5) or (pmt==6) or (pmt==9) ) ):
                                    self.chA12.Fill(event.data['deviation'])

                                elif (p<3 and ( (pmt==10) or (pmt==11)  or (pmt==16) or (pmt==19) ) ):
                                    self.chA34.Fill(event.data['deviation'])

                                elif (p<3 and ( (pmt==20) or (pmt==21)  or (pmt==24) or (pmt==25) ) ):
                                    self.chA56.Fill(event.data['deviation'])

                                elif (p<3 and ( (pmt==28) or (pmt==31)  or (pmt==34) or (pmt==37) ) ):
                                    self.chA78.Fill(event.data['deviation'])                                
                                    
                                elif (p<3 and ( (pmt==38) or (pmt==39)  or (pmt==47) or (pmt==48) ) ):
                                    self.chA90.Fill(event.data['deviation'])
                                elif (p>2 and ( (pmt==7) or (pmt==8) or (pmt==11) or (pmt==12) or (pmt==21) or (pmt==22) or (pmt==29) or (pmt==30) or (pmt==41) or (pmt==42))): #A extended barrel
                                    self.chEA.Fill(event.data['deviation'])
                                elif (p>2 and ( (pmt==3) or (pmt==4) or (pmt==17) or (pmt==18) or (pmt==37) or (pmt==38))): #D extended barrel
                                    self.chED.Fill(event.data['deviation'])
                                elif (p<3 and Celln == 0): #should not happen
                                    print('Error ... A cell but undefined. Please check consistency of laser/toolbox')
                                    print(p)
                                    print(pmt+1)
                                    print('------')
                                
                        
                        if self.limit<math.fabs(event.data['deviation']):
                            #[p, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                            [p, i, j, w] = event.region.GetNumber()
                            index        = self.PMTool.get_index(p-1, i-1, j, w)
                            
                            if event.data['status']:
                                bad_las_list_K.append(index)
                                bad_las_event_K.append(event)
                            else:
                                bad_las_list.append(index)
                                bad_las_event.append(event)                            

            # Time to write the bad channel lists
            
            # If gain=2 we write a small DQ report
            

            if self.gain==2:
                self.outfile.write('##########################################\n') 
                self.outfile.write('#\n')
                text = "# LASER stability DQ global summary\n"
                self.outfile.write(text)
                text = "# Low  gain run used is %d // Date: %s \n" % (self.ref_LG_evt.run.runNumber,self.ref_LG_evt.run.time_in_seconds)
                self.outfile.write(text)
                text = "# High gain run used is %d // Date: %s \n" % (self.ref_HG_evt.run.runNumber,self.ref_HG_evt.run.time_in_seconds)
                self.outfile.write(text)
                self.outfile.write('#\n')
                text = "# Maximum relative variation accepted: +/-%.1f%s\n" % (self.limit,'%')
                self.outfile.write(text)
                self.outfile.write('#\n')
                self.outfile.write('#\n')
                text = "# LASER expert contact: tilelas@mail.cern.ch\n"
                self.outfile.write(text)     
                self.outfile.write('##########################################\n')
                self.outfile.write('\n') 

                self.outfile.write("1. List of channels with NO LASER (which are not on official BC list):\n")
                self.outfile.write('\n')

                no_las_list.sort()
                bad_las_list.sort()

                for event in no_las_list:

                    [p, i, j, w] = self.PMTool.get_rev_index(event)

                    for event_a in no_las_event:
                        if event.region.GetNumber() == [p+1, i+1, j, w] and 'used' not in event_a.data:

                            event_a.data['used'] = True

                            # Look for the other gain counterpart in the list
                            for event_b in no_las_event:

                                #[p2, i2, j2, w2] = self.PMTool.GetNumber(event_b.data['region'])
                                [p2, i2, j2, w2] = event.region.GetNumber()

                                if p+1==p2 and i+1==i2 and j==j2 and w!=w2:
                            
                                    if i<9:
                                        name = "%s0%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)
                                    else:
                                        name = "%s%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)
                
                                    text = "%s\n" % (name)
                                    self.outfile.write(text)
                                    event_b.data['used'] = True
                                    break
                            

                self.outfile.write('\n')
                self.outfile.write("2. List of channels with BAD LASER (which are not on official BC list):\n")
                self.outfile.write('\n')

                for event in bad_las_list:

                    [p, i, j, w] = self.PMTool.get_rev_index(event)

                    for event_a in bad_las_event:
                        if event.region.GetNumber() == [p+1, i+1, j, w] and 'used' not in event_a.data:

                            event_a.data['used'] = True

                            # Look for the other gain counterpart in the list
                            for event_b in bad_las_event:

                                #[p2, i2, j2, w2] = self.PMTool.GetNumber(event_b.data['region'])
                                [p2, i2, j2, w2] = event.region.GetNumber()

                                if p+1==p2 and i+1==i2 and j==j2 and w!=w2:

                            
                                    if i<9:
                                        name = "%s0%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)
                                    else:
                                        name = "%s%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)

                                    self.low_a = False
                                    self.low_b = False
                                    
                                    if (event_a.data['calibration']<0.0025 and event_a.run.data['wheelpos']==8) \
                                           or (event_a.data['calibration']<0.1 and event_a.run.data['wheelpos']==6):
                                        self.low_a = True

                                    if (event_b.data['calibration']<0.0025 and event_b.run.data['wheelpos']==8) \
                                           or (event_b.data['calibration']<0.1 and event_b.run.data['wheelpos']==6):
                                        self.low_b = True

                                    if self.low_a or self.low_b:                                        
                                        text = "%s : %.2f%s // %.2f%s %s\n" % (name,event_a.data['deviation'],'%',event_b.data['deviation'],'%','==> Low signal channel')
                                    else:
                                        text = "%s : %.2f%s // %.2f%s\n" % (name,event_a.data['deviation'],'%',event_b.data['deviation'],'%')

                                    self.outfile.write(text)

                                    event_b.data['used'] = True
                                    break
            else:

                self.outfile.write("1. List of problematic patch panel fibers:\n")
                self.outfile.write('\n')

                bad_fib_list.sort()
                no_las_list.sort()
                bad_las_list.sort()
                no_las_list_K.sort()
                bad_las_list_K.sort()
            
                for ind in bad_fib_list:                
                    text = "%s / " % (self.PMTool.get_fiber_name(ind))
                    self.outfile.write(text) 

                self.outfile.write('\n')
                self.outfile.write('\n')
                self.outfile.write("2. List of channels with NO LASER (which are not on BC list):\n")
                self.outfile.write('\n')

                for event in no_las_list:

                    [p, i, j, w] = self.PMTool.get_rev_index(event)

                    if p>4:
                        continue

                    if i<9:
                        name = "%s0%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)
                    else:
                        name = "%s%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)
                
                    text = "%s\n" % (name)
                    self.outfile.write(text)
                        
                    self.part_nochan[p].SetMarkerStyle(20)
                    self.part_nochan[p].SetMarkerColor(1)
                    self.part_nochan[p].SetMarkerSize(0.8)
                    self.part_nochan[p].Fill(i+1.5,j+0.5)

                self.outfile.write('\n')
                self.outfile.write("3. List of channels with BAD LASER (which are not on BC list):\n")
                self.outfile.write('\n')

                for event in bad_las_list:

                    [p, i, j, w] = self.PMTool.get_rev_index(event)

                    if p>4:
                        continue
                
                    if i<9:
                        name = "%s0%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)
                    else:
                        name = "%s%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)


                    for event_a in bad_las_event:
                        if event.region.GetNumber() == [p+1, i+1, j, w]:
                            if (event_a.data['calibration']<0.0025 and event_a.run.data['wheelpos']==8)\
                                   or (event_a.data['calibration']<0.1 and event_a.run.data['wheelpos']==6):
                                text = "%s : %.2f%s %s\n" % (name,event_a.data['deviation'],'%','==> Low signal channel')
                            else:
                                text = "%s : %.2f%s\n" % (name,event_a.data['deviation'],'%')
                            self.outfile.write(text)
                            self.var = event_a.data['deviation']                        
                            break

                    if (math.fabs(self.var) > 3*self.limit):
                        self.part_bchan[p].SetMarkerStyle(20)
                        self.part_bchan[p].SetMarkerColor(2)
                        self.part_bchan[p].SetMarkerSize(0.8)
                        self.part_bchan[p].Fill(i+1.5,j+0.5)
                    else:
                        self.part_wchan[p].SetMarkerStyle(20)
                        self.part_wchan[p].SetMarkerColor(800)
                        self.part_wchan[p].SetMarkerSize(0.8)
                        self.part_wchan[p].Fill(i+1.5,j+0.5)  
            
                self.outfile.write('\n')
                self.outfile.write("4. List of KNOWN channels with NO LASER:\n")
                self.outfile.write('\n')

                for event in no_las_list_K:

                    [p, i, j, w] = self.PMTool.get_rev_index(event)

                    if p>4:
                        continue

                    if i<9:
                        name = "%s0%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)
                    else:
                        name = "%s%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)

                    for event_a in no_las_event_K:
                        if event.region.GetNumber() == [p+1, i+1, j, w]:
                            if event_a.data['problems']==set([]):
                                continue
                            probs = event_a.data['problems'].pop()
                            problems = " : KNOWN : %s"%(probs)
                            break
                
                    text = "%s%s\n" % (name,problems)
                    self.outfile.write(text)
                        
                    self.part_nochan[p].SetMarkerStyle(20)
                    self.part_nochan[p].SetMarkerColor(1)
                    self.part_nochan[p].SetMarkerSize(0.8)
                    self.part_nochan[p].Fill(i+1.5,j+0.5)


                self.outfile.write('\n')
                self.outfile.write("5. List of KNOWN channels with BAD LASER:\n")
                self.outfile.write('\n')
                
                for event in bad_las_list_K:

                    [p, i, j, w] = self.PMTool.get_rev_index(event)

                    if p>4:
                        continue
                
                    if i<9:
                        name = "%s0%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)
                    else:
                        name = "%s%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)

                    for event_a in bad_las_event_K:
                        if event.region.GetNumber() == [p+1, i+1, j, w]:
                            #if event_a.data['problems']==set([]):
                             #   continue
                            #probs = event_a.data['problems'].pop()
                            #problems = " : KNOWN : %s"%(probs)
                            #text = "%s : %.2f%s%s\n" % (name,event_a.data['deviation'],'%',problems)
                            text = "%s : %.2f%s\n" % (name,event_a.data['deviation'],'%')
                            self.outfile.write(text)
                            self.var = event_a.data['deviation']                        
                            break
                    
                    if (math.fabs(self.var) > 3*self.limit):
                        self.part_bchan[p].SetMarkerStyle(20)
                        self.part_bchan[p].SetMarkerColor(2)
                        self.part_bchan[p].SetMarkerSize(0.8)
                        self.part_bchan[p].Fill(i+1.5,j+0.5)
                    else:
                        self.part_wchan[p].SetMarkerStyle(20)
                        self.part_wchan[p].SetMarkerColor(800)
                        self.part_wchan[p].SetMarkerSize(0.8)
                        self.part_wchan[p].Fill(i+1.5,j+0.5)  

            
