################################################################################
#
# do_average_plot.py
#
################################################################################
#
# Author: Henric
#
# march 2013
#
# Goal:
#     Potential public plots
#
#########1#########2#########3#########4#########5#########6#########7#########8

from src.GenericWorker import *
from src.oscalls import *
import ROOT

class do_average_plot(GenericWorker):
    "Compute history plot for the detector"

    c1 = None

    def __init__(self, f =(lambda event: event.data['deviation']), label="Deviation", cells=['E1', 'E2', 'E3', 'E4', 'D5', 'A13', 'MBTS'], doPdfEps=True):
        #self.cells = ['A-LB', 'A-EB', 'D', 'E1', 'E2', 'E3', 'E4', 'MBTS']
        #self.cells = ['A-LB', 'A-EB', 'D', 'A-E1', 'A-E2', 'C-E1', 'C-E2', 
        #              'E3', 'E4', 'MBTS']
        self.cells = cells

        self.f = f
        self.label = label
        self.doPdfEps = doPdfEps

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)


        self.histo_dict = dict()

        for cell in self.cells:
            self.histo_dict[cell] = dict()

        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag))
        self.HistFile.cd()

        self.dirname = "LaserAverage"
        ROOT.gDirectory.mkdir(self.dirname)
        ROOT.gDirectory.cd(self.dirname)
        self.PMTool   = LaserTools()

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Average Cell response evolution")


    def ProcessStart(self):

        global run_list
        ordered_list = sorted(run_list.getRunsOfType('Las'), key=lambda run: run.runNumber)
        for run in ordered_list:
            for cell in self.cells:
                name = cell+repr(run)
                title = cell+repr(run)
                if cell !='MBTS':
                    self.histo_dict[cell][run] =  ROOT.TH1F(name, title, 80,  -20., 20.)
#                    self.histo_cs_dict[cell][run] =  ROOT.TH1F(name+"_cesium", 
#                                                               title, 150, -50., 25.)
                else:
                    self.histo_dict[cell][run] =  ROOT.TH1F(name, title, 180, -60., 20.)

        n = len(ordered_list)
        self.t_min = int(ordered_list[0].time_in_seconds)
        self.t_max = int(ordered_list[n-1].time_in_seconds)



    def ProcessRegion(self, region):

        numbers = region.GetNumber(1)
        if len(numbers)!=4:
            return region
        # only for ADCs 
        [part, module, pmt, gain] = numbers
        layer =  region.GetLayerName()
        cell  = region.GetCellName()
        
        for event in region.GetEvents():
            if event.run.runType=='Las':

                if 'status' not in event.data:
                    continue

                if event.data['status']&0x4 or event.data['status']&0x10:
                    continue
                
                # if not cell in [ 'E1','E2', 'E3', 'E4', "E4'"]:
                #     if (event.data['HV']<10.) or (event.data['HVSet']<10.): # Emergnecy mode: we don't calculate fiber correction.
                #         continue
                if ('hv_db' in event.data):
                        if (abs(event.data['HV']-event.data['hv_db'])>10.):  # Bad HV, will bias results.
                            continue


                saturation_limits = [800., 12.] # in pC Saturation limits
                if (event.data['signal']>saturation_limits[gain]): 
#                    if self.verbose:
#                        print event.region.GetHash(), event.data['signal'],saturation_limits[gain] 
                    continue

                underflow_limits = [4., 0.06]   # in pC Underflow limits
                if (event.data['signal']<underflow_limits[gain]):  
                    continue
                
                if (cell=='E5' or cell=='E6') and 'MBTS' in self.histo_dict:
                    self.histo_dict['MBTS'][event.run].Fill(self.f(event) )
                elif cell in self.histo_dict:
                    self.histo_dict[cell][event.run].Fill(self.f(event))



                # key = 'f_cesium_db'

                # if event.data.has_key(key):
                #     data = 100.*(event.data[key]-1.)
                #     if layer=='A':
                #         if part<=2:
                #             self.histo_cs_dict['A-LB'][event.run].Fill(data)
                #         else:
                #             self.histo_cs_dict['A-EB'][event.run].Fill(data)

                #     elif layer=='D':
                #         self.histo_cs_dict['D'][event.run].Fill(data)

                #     elif cell=='E1':
                #         print data
                #         self.histo_cs_dict['A-E1'][event.run].Fill(data)

                #     elif cell=='E2':
                #         print data
                #         self.histo_cs_dict['A-E2'][event.run].Fill(data)

                #     elif cell=='E3':
                #         self.histo_cs_dict['E3'][event.run].Fill(data)

                #     elif cell=='E4':
                #         self.histo_cs_dict['E4'][event.run].Fill(data)


    def ProcessStop(self):
        tgraph = {}
        tgraph_cs = {}
        self.HistFile.cd(self.dirname)
        for cell in self.cells:
            tgraph[cell] = ROOT.TGraphErrors()
            npoints = 0
            for run, hist in self.histo_dict[cell].items():
#                print cell, run.runNumber, hist.GetEntries(), hist.GetMean(), hist.GetRMS()
                if hist.GetRMS()!=0.0 and hist.GetMean()!=0.0:
                    fit = ROOT.TF1("fit", "gaus")
                    fit.SetParameter(1,hist.GetMean())
                    fit.SetParameter(2,max(hist.GetRMS(),0.1))
                    if hist.GetEntries()>4:
                        hist.Fit(fit,"LQ0")

                        tgraph[cell].SetPoint(npoints, run.time_in_seconds, 
                                          fit.GetParameter(1))
                        if cell!='MBTS':
                            tgraph[cell].SetPointError(npoints, 600, fit.GetParError(1))
                        else:
                            tgraph[cell].SetPointError(npoints, 600, fit.GetParameter(2))
                        npoints+=1

                hist.Write()
                hist.Delete()
            tgraph[cell].Sort()
            tgraph[cell].SetName(cell)
            tgraph[cell].Write()

            # if cell!='MBTS':
            #     tgraph_cs[cell] = ROOT.TGraphErrors()
            #     npoints = 0
            #     for run, hist in self.histo_cs_dict[cell].iteritems():
            #         if hist.GetEntries()>4:
            #             hist.Fit("gaus", "LQ")
            #             tgraph_cs[cell].SetPoint(npoints, run.time_in_seconds, 
            #                                      gaus.GetParameter(1))
            #             tgraph_cs[cell].SetPointError(npoints, 600, 
            #                                           gaus.GetParError(1))
            #             npoints+=1
            #         hist.Write()
            #         hist.Delete()

            #     tgraph_cs[cell].Sort()
            #     tgraph_cs[cell].SetName("cesium "+cell)
            #     tgraph_cs[cell].Write()
        #
        ## Now do the drawing part
        #
        ## The following formatting should be good for making public plots
        #

        x = 0.19
        y = 0.19
        ROOT.gStyle.SetTimeOffset(0)
        if self.label=='Deviation CF-Pisa':
            # You may have to play with this to make sure the legend 
            # is not covering data
            legend = ROOT.TLegend(x+0.11, y, x+0.33, y+0.2) 
        else:
            legend = ROOT.TLegend(x, y, x+0.22, y+0.2)
        self.c1.cd()
        option="AP"

        self.c1.cd()
        cellLegends = [ '1.0 < |#eta| < 1.1',
                        '1.1 < |#eta| < 1.2', 
                        '1.2 < |#eta| < 1.4',
                        '1.4 < |#eta| < 1.6',
                        'A13' ]  
        #cellLegends = ['D5 cells', '1.1 < |#eta| < 1.2', 
        #              '1.2 < |#eta| < 1.4', '1.4 < |#eta| < 1.6']  
        colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kMagenta, ROOT.kCyan]
        marker = 20
        color = 0


        for cell in sorted(list(set(['E1', 'E2', 'E3', 'E4'])&set(self.cells))) :
            tgraph[cell].SetMaximum(4.0)
            tgraph[cell].SetMinimum(-10.)

            self.draw_cell(tgraph[cell],option,colors[color],marker)
            
            if self.label=='Deviation CF-Pisa':
                legend.AddEntry(tgraph[cell],"%s"%cell+" difference","P")
                tgraph[cell].GetYaxis().SetTitle("Absolute difference: CF"
                                                 " - Pisa [%]");
                tgraph[cell].SetMaximum(3.5)
                tgraph[cell].SetMinimum(-1.5)
            else:
                legend.AddEntry(tgraph[cell],"%s"%cell+" (Laser): " + 
                                cellLegends[color],"P")
                tgraph[cell].GetYaxis().SetTitle("Average response [%]")
            marker +=1
            option="P,same"
            color +=1

        legend.Draw()
        #The following code is to at the "ATLAS" label for public plots
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(72)
        l.SetTextColor(1)
        l.SetTextSize(0.05)
        l.DrawLatex(.3, .86, "ATLAS")        
        
        p = ROOT.TLatex()
        p.SetNDC()
        p.SetTextFont(42)
        p.SetTextColor(1)
        p.SetTextSize(0.05)
        p.DrawLatex(.42, .86, "Internal")
  
        m = ROOT.TLatex()
        m.SetNDC()
        m.SetTextFont(42)
        m.SetTextColor(1)
        m.DrawLatex(.32, .81, "Tile Calorimeter")
        #End Label Code

        self.c1.Modified()
        self.c1.Update()
        
        if self.doPdfEps:
            self.c1.Print(self.dir+"/LaserGapCrack"+self.label.replace(' ','_')+".pdf")
        else:
            self.c1.Print(self.dir+"/LaserGapCrack"+self.label.replace(' ','_')+".png")
        self.c1.Print(self.dir+"/LaserGapCrack"+self.label.replace(' ','_')+".root")
        #self.c1.Print(self.dir+"/LaserGapCrack"+self.label.replace(' ','_')+".C")


        self.c1.Clear()
        legend.Clear()
        cellLegends = ['1.0 < |#eta| < 1.1', 'A13']  
        marker = 20
        color = 0
        option = "AP"
        for cell in list(set(['E1', 'A13'])&set(self.cells)):
            tgraph[cell].SetMaximum(1.0)
            tgraph[cell].SetMinimum(-4.)

            self.draw_cell(tgraph[cell],option,colors[color],marker)
            
            if self.label=='Deviation CF-Pisa':
                legend.AddEntry(tgraph[cell],"%s"%cell+" difference","P")
                tgraph[cell].GetYaxis().SetTitle("Absolute difference: CF"
                                                 " - Pisa [%]");
                tgraph[cell].SetMaximum(3.5)
                tgraph[cell].SetMinimum(-1.5)
            else:
                legend.AddEntry(tgraph[cell],"%s"%cell+" (Laser): " + 
                                cellLegends[color],"P")
                tgraph[cell].GetYaxis().SetTitle("Average response [%]")
            marker +=1
            option="P,same"
            color +=1

        legend.Draw()
        l.DrawLatex(.3, .86, "ATLAS")        
        p.DrawLatex(.42, .86, "Internal")
        m.DrawLatex(.32, .81, "Tile Calorimeter")
        #End Label Code

        self.c1.Modified()
        self.c1.Update()

        if self.doPdfEps:
            self.c1.Print(self.dir+"/LaserE1A13"+self.label.replace(' ','_')+".pdf")
        else:
            self.c1.Print(self.dir+"/LaserE1A13"+self.label.replace(' ','_')+".png")


        if self.label == 'PISA':
            self.c1.Clear()
            legend.Clear()
            marker = 20
            color = 0
            option = "AP"
            for cell in sorted(list(set(['A10', 'A12', 'A13', 'D1', 'D6'])&set(self.cells))):
                tgraph[cell].SetMaximum(3.0)
                tgraph[cell].SetMinimum(-7.)
                
                self.draw_cell(tgraph[cell],option,colors[color],marker)
                legend.AddEntry(tgraph[cell],"%s"%cell+" Pisa","P")
                tgraph[cell].GetYaxis().SetTitle("Absolute variation from Pisa");
                tgraph[cell].GetYaxis().SetTitle("Average response [%]")
                marker +=1
                option="P,same"
                color +=1

            legend.Draw()
            l.DrawLatex(.3, .86, "ATLAS")        
            p.DrawLatex(.42, .86, "Internal")
            m.DrawLatex(.32, .81, "Tile Calorimeter")
        #End Label Code

            self.c1.Modified()
            self.c1.Update()

            if self.doPdfEps:
                self.c1.Print(self.dir+"/LaserPISA.pdf")
            else:
                self.c1.Print(self.dir+"/LaserPISA.png")


            self.c1.Clear()
            legend.Clear()
            marker = 20
            color = 0
            option = "AP"
            for cell in sorted(list(set(['D0', 'D1', 'D2', 'D3', 'D4'])&set(self.cells))):
                tgraph[cell].SetMaximum(3.0)
                tgraph[cell].SetMinimum(-7.)
                
                self.draw_cell(tgraph[cell],option,colors[color],marker)
                legend.AddEntry(tgraph[cell],"%s"%cell+" Pisa","P")
                tgraph[cell].GetYaxis().SetTitle("Absolute variation from Pisa");
                tgraph[cell].GetYaxis().SetTitle("Average response [%]")
                marker +=1
                option="P,same"
                color +=1

            legend.Draw()
            l.DrawLatex(.3, .86, "ATLAS")        
            p.DrawLatex(.42, .86, "Internal")
            m.DrawLatex(.32, .81, "Tile Calorimeter")
        #End Label Code

            self.c1.Modified()
            self.c1.Update()

            if self.doPdfEps:
                self.c1.Print(self.dir+"/LaserPISA-Dcells.pdf")
            else:
                self.c1.Print(self.dir+"/LaserPISA-Dcells.png")
        
        self.c1.Clear()
        legend.Clear()
        cellLegends = ['A13','D5']  
        marker = 20
        color = 0
        option = "AP"
        
        for cell in list(set(['A13','D5'])&set(self.cells)):
            tgraph[cell].SetMaximum(1.0)
            tgraph[cell].SetMinimum(-2.)

            self.draw_cell(tgraph[cell],option,colors[color],marker)
            
            legend.AddEntry(tgraph[cell],"%s"%cell,"P")
            tgraph[cell].GetYaxis().SetTitle("Average response [%]")
            marker +=1
            option="P,same"
            color +=1

        legend.Draw()
        l.DrawLatex(.3, .86, "ATLAS")        
        p.DrawLatex(.42, .86, "Internal")
        m.DrawLatex(.32, .81, "Tile Calorimeter")
        #End Label Code

        self.c1.Modified()
        self.c1.Update()

        if self.doPdfEps:
            self.c1.Print(self.dir+"/LaserA13D5"+self.label.replace(' ','_')+".pdf")
        else:
            self.c1.Print(self.dir+"/LaserA13D5"+self.label.replace(' ','_')+".png")

        self.c1.Clear()
        if 'MBTS' in tgraph:
            self.draw_cell(tgraph['MBTS'],"AP")
            l.DrawLatex(.3, .86, "ATLAS") 
            p.DrawLatex(.42, .86, "Internal") 
            m.DrawLatex(.32, .81, "Tile Calorimeter")
    
            self.c1.Modified()
            self.c1.Update()
            if self.doPdfEps:
                self.c1.Print(self.dir+"/LaserGapCrackMBTS.pdf") 
                self.c1.Print(self.dir+"/LaserGapCrackMBTS.eps") 
            else:
                self.c1.Print(self.dir+"/LaserGapCrackMBTS.png") 
            self.c1.Print(self.dir+"/LaserGapCrackMBTS.C") 



    def draw_cell(self, tgraph, option, color=-1, marker=-1):
        size=1.0
        tgraph.GetXaxis().SetTimeDisplay(1)
        tgraph.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}")
        tgraph.GetXaxis().SetLabelSize(0.03)
        tgraph.GetXaxis().SetLabelOffset(0.02)
        tgraph.GetXaxis().SetTitle("Time [dd/mm and year]")
        tgraph.GetXaxis().SetTitleSize(0.05)
        #tgraph.GetYaxis().SetTitle("Average response [%]")
        tgraph.GetYaxis().SetTitleSize(0.05)
        #tgraph.SetMaximum(2.0)
        #tgraph.SetMinimum(-10.)
        if marker!=-1:
            tgraph.SetMarkerStyle(marker)
        tgraph.SetMarkerSize(size)
        if color!=-1:
            tgraph.SetMarkerColor(color)
            tgraph.SetLineColor(color)
        tgraph.GetXaxis().SetNdivisions(705, 0)           
        d = int(86400)
        tgraph.GetXaxis().SetLimits(d*((self.t_min-d)/d),d*((self.t_max+d)/d))
        tgraph.Sort()
        tgraph.Draw(option)
        
