############################################################
#
# do_module_channel_plot.py
#
############################################################
#
# Author: Henric
#
# May 2019
#
# Goal: 
#    make channe vs module plots
#
# Input parameters are:
#
#
############################################################

from src.GenericWorker import *
import src.MakeCanvas

class do_module_channel_plot(GenericWorker):
    "X-axis is module number, Y-axis is channel number, Z quantity to display"

    c1 = None

    def __init__(self, key):
        self.key = key

        self.dir    = getPlotDirectory(subdir=outputTag)

        if self.c1 == None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Tile Map")
            
        self.hist = []

        self.hist.append(ROOT.TH2F("LBA", "LBA [Laser Constant];Module;Channel", 64, 0.5, 64.5, 48, -0.5, 47.5))
        self.hist.append(ROOT.TH2F("LBC", "LBC [Laser Constant];Module;Channel", 64, 0.5, 64.5, 48, -0.5, 47.5))
        self.hist.append(ROOT.TH2F("EBA", "EBA [Laser Constant];Module;Channel", 64, 0.5, 64.5, 48, -0.5, 47.5))
        self.hist.append(ROOT.TH2F("EBC", "EBC [Laser Constant];Module;Channel", 64, 0.5, 64.5, 48, -0.5, 47.5))

        self.masked = []
        
        self.masked.append(ROOT.TH2F("LBA_masked", "LBA;Module;Channel", 64, 0.5, 64.5, 48, -0.5, 47.5))
        self.masked.append(ROOT.TH2F("LBC_masked", "LBC", 64, 0.5, 64.5, 48, -0.5, 47.5))
        self.masked.append(ROOT.TH2F("EBA_masked", "EBA", 64, 0.5, 64.5, 48, -0.5, 47.5))
        self.masked.append(ROOT.TH2F("EBC_masked", "EBC", 64, 0.5, 64.5, 48, -0.5, 47.5))

        self.notInst = []
        
        self.notInst.append(ROOT.TH2F("LBA_notInstrumented", "LBA;Module;Channel", 64, 0.5, 64.5, 48, -0.5, 47.5))
        self.notInst.append(ROOT.TH2F("LBC_notInstrumented", "LBC;Module;Channel", 64, 0.5, 64.5, 48, -0.5, 47.5))
        self.notInst.append(ROOT.TH2F("EBA_notInstrumented", "EBA;Module;Channel", 64, 0.5, 64.5, 48, -0.5, 47.5))
        self.notInst.append(ROOT.TH2F("EBC_notInstrumented", "EBC;Module;Channel", 64, 0.5, 64.5, 48, -0.5, 47.5))

        for module in range(1,65):
            for channel in [30,31,43]:
                self.notInst[0].SetBinContent(module, channel+1, 1.)   # Why, oh why channel+1 
                self.notInst[1].SetBinContent(module, channel+1, 1.)

            for channel in [18,19,24,25,26,27,28,29,33,34,42,43,44,45,46,47]:
                if module !=15:
                    self.notInst[2].SetBinContent(module, channel+1, 1.)
                if module !=18:            
                    self.notInst[3].SetBinContent(module, channel+1, 1.)

        for channel in [0,1,2,3,24,25,26,27,28,29,33,34,42,43,44,45,46,47]:
            self.notInst[2].SetBinContent(15, channel+1, 1.)
            self.notInst[3].SetBinContent(18, channel+1, 1.)

        return

    
    def ProcessStart(self):
        
        return
    

    def ProcessRegion(self, region):
        numbers = region.GetNumber(0)
        if len(numbers)!=4:
            return

        [part,module, channel, gain] = numbers
        if self.key in region.data:
            print(channel )
            self.hist[part-1].SetBinContent(module,channel+1,1./region.data[self.key])
            
            if 'problems' in region.data:
                if len( region.data['problems'].intersection({'ADC masked (unspecified)', 'ADC dead',
                                                              'No data', 'Very large HF noise', 
                                                              'Severe stuck bit', 'Severe data corruption',
                                                              'Channel masked (unspecified)','No PMT connected',
                                                              'Wrong HV'}) )!=0:
                    self.masked[part-1].SetBinContent(module,channel+1,1.)
        return
    

    def ProcessStop(self):
        #  First set gStyle 
        ROOT.gStyle.SetPaintTextFormat("1.3f");
        ROOT.gStyle.SetPalette(57);
        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleBorderSize(0)
        ROOT.gStyle.SetTitleX(0.5)
        ROOT.gStyle.SetTitleY(1.0)
        print((ROOT.gStyle.GetPadLeftMargin()))
        ROOT.gStyle.SetTitleAlign(23)         # Horizontaly center(2), verticaly top(3)
        ROOT.gStyle.SetPadTopMargin(0.12)
        ROOT.gStyle.SetPadBottomMargin(0.1)
        ROOT.gStyle.SetPadRightMargin(.15)
        ROOT.gStyle.SetPadLeftMargin(.10)
        # No effect ROOT.gStyle.SetHistTopMargin(0.4)
        ROOT.gStyle.SetHatchesLineWidth(2)
        ROOT.gStyle.SetHatchesSpacing(0.6)

        # Then divide, so the TPads get created with the updated style
        self.c1.Divide(2,2,0.01,0.01)
        
        legendTopLeft = TLegend(0.09,0.9,0.95,0.95, "")
        legendTopLeft.SetNColumns(2)
        legendTopLeft.SetFillStyle(0);
        legendTopLeft.SetFillColor(0);
        legendTopLeft.SetBorderSize(0);

        for part in range(4):    
            tpad = self.c1.cd(part+1)
            tpad.SetTickx(1)
            tpad.SetTicky(1)
            tpad.SetFrameBorderMode(0)

            self.notInst[part].SetLineColor(kGray)
            self.notInst[part].SetFillColor(kGray)
            self.notInst[part].SetFillStyle(3354)
            self.notInst[part].Draw("BOX")
            
            self.hist[part].SetMinimum(0.9)
            self.hist[part].SetMaximum(1.02)
            self.hist[part].GetZaxis().SetTitle('Laser constant')
            self.hist[part].GetZaxis().CenterTitle()
            self.hist[part].Draw("COLZsame")
            
            self.masked[part].SetLineColor(ROOT.kBlack)
            self.masked[part].SetFillColor(ROOT.kBlack)
            self.masked[part].SetFillStyle(3144)
            self.masked[part].Draw("BOXsame")

            legendTopLeft.Clear();
            legendTopLeft.AddEntry(self.notInst[part], "Not Instrumented","f")
            legendTopLeft.AddEntry(self.masked[part], "Masked","f")
            legendTopLeft.Draw();

            tpad.RedrawAxis()
            

        self.c1.Modified()
        self.c1.Update()

        ROOT.gStyle.SetPaperSize(26,20)
        self.c1.Print("%s/%s.eps" % (self.dir, "module_channel"))
        self.c1.Print("%s/%s.root" % (self.dir, "module_channel"))
        return 
    
