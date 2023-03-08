from src.GenericWorker import *
import src.MakeCanvas
import time
import numpy
import src.stats
import math
import json
import string
import os.path
# from MBiasPlotUtils import *

def LumiCoeff(data):
    """
    Takes   List with [PMTCurrent, instantaneous luminosity]
    
    Returns 0: Luminosity coefficient from LogLikelihood fit
            1: Error on luminosity coefficient
            2: Offset of fit
            3: Error on offset of fit
            4: Chi squared value of goodness of fit test
            """
    minx = min([x[0] for x in data])
    maxx = max([x[0] for x in data])
    miny = min([y[1] for y in data])
    maxy = max([y[1] for y in data])
    h = ROOT.TH2F("histo"," ",25,minx,maxx,25,miny,maxy)
    for val in data:
        h.Fill(val[0],val[1])
    prof = h.ProfileX('s')
    prof.Approximate()
    pol1 = ROOT.TF1("pol1","pol1",minx,maxx)
    prof.Fit('pol1',"QR")
    lumicoeff = pol1.GetParameter(1)
    lumicoefferror = pol1.GetParError(1)
    lumicoeffrelativeerror = lumicoefferror/lumicoeff
    offset = pol1.GetParameter(0)
    offseterror = pol1.GetParError(0)
    offsetrelativeerror = offseterror/offset
    chi2 = pol1.GetChisquare() / pol1.GetNDF()
    totalcurrent = h.Integral()
    return (lumicoeff,lumicoefferror,lumicoeffrelativeerror,offset,offseterror,offsetrelativeerror,chi2,totalcurrent)

def GetTitle(name):
    if name=='LumiCoeff': return 'Lumi. Coeff. [#times10^{-33}nA#timescm^{2}s]'
    if name=='LumiCoeffError': return '#sigma(Lumi. Coeff.)'
    if name=='LumiCoeffRelativeError': return '#sigma(Lumi. Coeff.) / Lumi. Coeff.'
    if name=='Offset': return 'Current offset [nA]'
    if name=='OffsetError': return '#sigma(Current offset)'
    if name=='OffsetRelativeError': return '#sigma(Current offset) / Current offset'
    if name=='Chi2': return '#chi^{2} of Lumi. Coeff. fit'
    if name=='TotalCurrent': return 'Accumulated Current [#times10^{33}nA#timescm^{-2}s^{-1}]'
    else: return name


def GetEtaPhiBin(h,eta,m):
    xaxis = h.GetXaxis()
    return (int(xaxis.FindBin(eta)), (m+32) % 64 + 1)

def SetPalettekBird():
    stops = array('d', [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000])
    red   = array('d', [0.2082, 0.0592, 0.0780, 0.0232, 0.1802, 0.5301, 0.8186, 0.9956, 0.9764])
    green = array('d', [0.1664, 0.3599, 0.5041, 0.6419, 0.7178, 0.7492, 0.7328, 0.7862, 0.9832])
    blue  = array('d', [0.5293, 0.8684, 0.8385, 0.7914, 0.6425, 0.4662, 0.3499, 0.1968, 0.0539])
    T = ROOT.TColor()
    TColor.CreateGradientColorTable(9, stops, red, green, blue, 510)

def SetPalettekLightTemperature():
    stops = array('d', [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000])
    red   = array('d', [31./510., 71./510., 123./510., 160./510., 210./510., 222./510., 214./510., 199./510., 183./510.])
    green = array('d', [40./510., 117./510., 171./510., 211./510., 231./510., 220./510., 190./510., 132./510., 65./510.])
    blue  = array('d', [234./510., 214./510., 228./510., 222./510., 210./510., 160./510., 105./510., 60./510., 34./510.])
    T = ROOT.TColor()
    TColor.CreateGradientColorTable(9, stops, red, green, blue, 510)

def SetPalettekDarkBodyRadiator():
    stops = array('d', [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000])
    red   = array('d', [0./510., 45./510., 99./510., 156./510., 212./510., 230./510., 237./510., 234./510., 242./510.])
    green = array('d', [0./510., 0./510., 0./510., 45./510., 101./510., 168./510., 238./510., 238./510., 243./510.])
    blue  = array('d', [0./510., 1./510., 1./510., 3./510., 9./510., 8./510., 11./510., 95./510., 230./510.])
    T = ROOT.TColor()
    TColor.CreateGradientColorTable(9, stops, red, green, blue, 510)

def SetPalettekRainbow():
    stops = array('d', [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000])
    red   = array('d', [0./510., 5./510., 15./510., 35./510, 102./510., 196./510., 208./510., 199./510., 110./510.])
    green = array('d', [0./510., 48./510., 124./510., 192./510., 206./510., 226./510., 97./510., 16./510., 0./510.])
    blue  = array('d', [99./510., 142./510., 198./510., 201./510., 90./510., 22./510., 13./510., 8./510., 2./510.])
    T = ROOT.TColor()
    TColor.CreateGradientColorTable(9, stops, red, green, blue, 510)


def SetGlobalMinimumMaximum(histos,log=False):
    if len(histos) < 2:
        print "More than one histogram needed!" 
        return
    minimum,maximum = 99999999,-99999999
    for h in histos:
        if h.GetMinimum() < minimum:
            minimum = h.GetMinimum()
        if h.GetMaximum() > maximum:
            maximum = h.GetMaximum()
    if minimum > maximum:
        print "Warning: minimum > maximum"
    if log and minimum*maximum < 0.:
        minimum = 0.000001
    for h in histos:
        h.SetMinimum(minimum)
        h.SetMaximum(maximum)

def SetLocalMinimumMaximum(histo,log=False):
        histo.SetMaximum(histo.GetBinContent(histo.GetMaximumBin()))
        histo.SetMinimum(histo.GetBinContent(histo.GetMinimumBin()))

def FilterMBTS(names):
    """
    Takes list of PMT names
    Returns filtered list of PMT names
    """
    MBTS = ['EBA_m%s_c13'%mod for mod in [8,24,43,54]]
    MBTS.extend(['EBC_m%s_c13'%mod for mod in [8,24,43,54]])#29,32,34,37,47,43,54]])
    MBTS.extend(['EBA_m%s_c5'%mod for mod in [39,40,41,42,55,56,57,58]])
    MBTS.extend(['EBC_m%s_c5'%mod for mod in [39,40,41,42,55,56,57,58]])

    # TEMP
    # MBTS.extend(['EBA_m%s_c1'%mod for mod in range(1,49)])
    # MBTS.extend(['EBC_m%s_c1'%mod for mod in range(1,49)])
    # MBTS.extend(['EBA_m%s_c2'%mod for mod in range(1,49)])
    # MBTS.extend(['EBC_m%s_c2'%mod for mod in range(1,49)])

    # MBTS.append('LBC_m28_c34')

    return [name for name in names if name not in MBTS]


def Plot2DEtaVsPhi(data,variable,**kwargs):

    SetPalettekBird()
    print "Making eta vs. phi map of",variable

    etamapLB = {0:0.01,1:0.05,2:0.05,5:0.15,6:0.15,9:0.25,11:0.25,13:0.2,15:0.35,16:0.35,19:0.45,21:0.45,23:0.55,25:0.4,28:0.55,34:0.65,27:0.65,33:0.75,37:0.85,40:0.75,39:0.6,44:0.85,46:0.95}
    etamapEB = {0:1.30,12:1.05,1:1.50,13:1.15,2:0.85,4:0.95,6:1.15942,8:1.05869,10:1.25867,14:1.15803,16:1.00741,20:1.35795,22:1.25738,32:1.35678,28:1.45728,42:1.4562,36:1.20632,40:1.55665}

    EtaBins_Ecells = [-1.6, -1.4, -1.2, -1.1, -1.0, 0.0, 1.0, 1.1, 1.2, 1.4, 1.6]
    EtaBins_Dcells = [-1.39, -1.1, -0.9, -0.7, -0.5, -0.3, -0.1, 0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.39]

    histos2D       = {}
    histos2D['A']  = ROOT.TH2F("A", "", 32, -1.60, 1.60, 64, -3.14159265, 3.14159265)
    histos2D['BC'] = ROOT.TH2F("BC","", 30, -1.50, 1.50, 64, -3.14159265, 3.14159265)
    histos2D['D']  = ROOT.TH2F("D", "", 13, array('d',EtaBins_Dcells), 64, -3.14159265, 3.14159265)
    histos2D['E']  = ROOT.TH2F("E", "", 10, array('d',EtaBins_Ecells), 64, -3.14159265, 3.14159265)

    celltypes = ['A','BC','D','E']
    partitions = ['LBA','LBC','EBA','EBC']

    # Fill the histograms
    for n,part in enumerate(partitions):
        for val in FilterMBTS([key for key in data.keys() if key.startswith(part)]):
            # try:
            val_filtered = val.replace('_m',' ')
            val_filtered = val_filtered.replace('_c',' ')
            module,pmt = [int(s) for s in val_filtered.split() if s.isdigit()]
            cellname = self.PMTool.getCellName(n, module, pmt)
            try:
                cellcoordinates = self.PMTool.getRegionName2015(cellname, False)
            except KeyError:
                # print "KeyError for", val, cellname
                continue

            # Extract the cell type corresponding to the histogram to be filled
            histoKey = cellname.translate(string.maketrans('', ''), '0123456789')
            if histoKey == "B" or histoKey == "C":
                histoKey = "BC"

            PMTch = cellcoordinates[1]

            part = val[:3]
            if part.startswith("L"):
                if part.endswith("A"):
                    eta = etamapLB[PMTch[0]]
                else:
                    eta = -1*etamapLB[PMTch[0]]
            else:
                if part.endswith("A"):
                    eta = etamapEB[PMTch[0]]
                else:
                    eta = -1*etamapEB[PMTch[0]]

            etabin, phibin = GetEtaPhiBin(histos2D[histoKey],eta,module)
            if histos2D[histoKey].GetBinContent(etabin,phibin) == 0.0:
                try:
                    histos2D[histoKey].SetBinContent(etabin,phibin,data[val][variable])
                except KeyError:
                    continue
            else:
                try:
                    binContent = 0.5 * (histos2D[histoKey].GetBinContent(etabin,phibin) + data[val][variable])
                    histos2D[histoKey].SetBinContent(etabin,phibin,binContent)
                except KeyError:
                    continue

    for type in celltypes:
        c = ROOT.TCanvas(type,'%s cells %s'%(type,GetTitle(variable)),900,700)
        c.SetRightMargin(0.15)
        c.SetTopMargin(0.15)
        c.SetLeftMargin(0.15)
        c.SetBottomMargin(0.15)

        c.SetLogz(0)
        SetGlobalMinimumMaximum([histos2D['A'],histos2D['BC'],histos2D['D'],histos2D['E']],log=False)
        histos2D[type].GetXaxis().SetTitle('#eta')
        histos2D[type].GetYaxis().SetTitle('#phi')
        histos2D[type].GetXaxis().SetTitleOffset(0.91)
        histos2D[type].GetYaxis().SetTitleOffset(0.87)
        histos2D[type].GetXaxis().SetTitleSize(0.075)
        histos2D[type].GetYaxis().SetTitleSize(0.075)
        histos2D[type].Draw('COLZ1')

        l = TLatex()
        l.SetNDC()
        l.SetTextFont(42)
        l.DrawLatex(0.25,0.92, "%s cells %s"%(type,GetTitle(variable)))

        c.Print('%s/EtaVsPhi_%scells_%s_%s_globalscale.png'%(self.dir,type,variable,data["RunNumber"]))
        c.Print('%s/EtaVsPhi_%scells_%s_%s_globalscale.pdf'%(self.dir,type,variable,data["RunNumber"]))

        c.Update()
        SetLocalMinimumMaximum(histos2D[type],log=False)                
        c.Print('%s/EtaVsPhi_%scells_%s_%s_localscale.png'%(self.dir,type,variable,data["RunNumber"]))
        c.Print('%s/EtaVsPhi_%scells_%s_%s_localscale.pdf'%(self.dir,type,variable,data["RunNumber"]))

        c.SetLogz(1)
        c.Update()
        SetGlobalMinimumMaximum([histos2D['A'],histos2D['BC'],histos2D['D'],histos2D['E']],log=True)

        c.Print('%s/EtaVsPhi_%scells_%s_%s_globalscale_log.png'%(self.dir,type,variable,data["RunNumber"]))
        c.Print('%s/EtaVsPhi_%scells_%s_%s_globalscale_log.pdf'%(self.dir,type,variable,data["RunNumber"]))

        c.Update()
        SetLocalMinimumMaximum(histos2D[type],log=True)                
        c.Print('%s/EtaVsPhi_%scells_%s_%s_localscale_log.png'%(self.dir,type,variable,data["RunNumber"]))
        c.Print('%s/EtaVsPhi_%scells_%s_%s_localscale_log.pdf'%(self.dir,type,variable,data["RunNumber"]))

    return 0




def PlotAllPMTs(data):
    InstLumi = data['InstLumi']
    maxlumi = max(InstLumi)
    minlumi = min(filter((lambda x: x > 0.0), InstLumi))

    for regionname in [key for key in data.keys() if key not in ["InstLumi","RunNumber"]]:
        if data[regionname]['PMTCurrent'] != []:
            PMTCurrent = data[regionname]['PMTCurrent']
            maximum = max(PMTCurrent)
            minimum = min(PMTCurrent)
        else: continue

        pairs = []
        for i in range(len(PMTCurrent)):
            if InstLumi[i]==0: continue
            pairs.append([InstLumi[i],PMTCurrent[i]]) # fill 2d histo

        c = ROOT.TCanvas('c','',800,600)

        self.CurrentVsInstLumiHistoDict[regionname] = {}
        self.CurrentVsInstLumiHistoDict[regionname]["2D_hist"] = ROOT.TH2F("CurrentVsInstLumi_"+regionname, "", 30, minlumi, maxlumi, 30, minimum - 0.25*(maximum-minimum), maximum + 0.25*(maximum-minimum))
        self.CurrentVsInstLumiHistoDict[regionname]["2D_fit"] = ROOT.TH2F("CurrentVsInstLumi_%s"%regionname, "", 25, minlumi, maxlumi, 25,  minimum - 0.25*(maximum-minimum), maximum + 0.25*(maximum-minimum))

        for j in range(len(pairs)):
            if pairs[j][1]==0.0: continue
            self.CurrentVsInstLumiHistoDict[regionname]["2D_hist"].Fill(pairs[j][0],pairs[j][1])
            if pairs[j][0]>=minlumi:
                self.CurrentVsInstLumiHistoDict[regionname]["2D_fit"].Fill(pairs[j][0],pairs[j][1])

        profilex = self.CurrentVsInstLumiHistoDict[regionname]["2D_hist"].ProfileX('s')
        # do TProffile::Approximate to approximate bin error in bins with zero errors
        profilex.Approximate()

        self.CurrentVsInstLumiHistoDict[regionname]["2D_hist"].Draw("COLZ")
        profilex.Draw("SAME")
        ROOT.gPad.SetRightMargin(0.2)
        self.CurrentVsInstLumiHistoDict[regionname]["2D_hist"].GetXaxis().SetTitle("Inst. Lumi [10^{33}cm^{-2}s^{-1}]")
        self.CurrentVsInstLumiHistoDict[regionname]["2D_hist"].GetYaxis().SetTitle("%s current [nA]"%(self.regionName))
        self.CurrentVsInstLumiHistoDict[regionname]["2D_hist"].GetYaxis().SetTitleOffset(1.7)
        self.CurrentVsInstLumiHistoDict[regionname]["2D_hist"].GetZaxis().SetTitle("Events")

        Leg1 = TLatex()
        Leg1.SetNDC()
        Leg1.SetTextAlign( 11 )
        Leg1.SetTextFont( 42 )
        Leg1.SetTextSize( 0.035 )
        Leg1.SetTextColor( 1 )
        Leg1.DrawLatex(0.19,0.75, "#scale[1.3]{#sqrt{s}=13 TeV}")

        Leg2 = TLatex()
        Leg2.SetNDC()
        Leg2.SetTextAlign( 11 )
        Leg2.SetTextSize( 0.05 )
        Leg2.SetTextColor( 1 )
        Leg2.SetTextFont(42)
        Leg2.DrawLatex(0.32,0.88," Internal")

        Leg2.DrawLatex(0.19,0.82, "Tile Calorimeter")

        atlasLabel = TLatex()
        atlasLabel.SetNDC()
        atlasLabel.SetTextFont( 72 )
        atlasLabel.SetTextColor( 1 )
        atlasLabel.SetTextSize( 0.05 )
        atlasLabel.DrawLatex(0.19,0.88, "ATLAS")

        c.Modified()
        c.Update()

        self.plot_name = "CurrentVsInstLumi_%s"%regionname
        c.Print("%s/%s_2016.png" % (self.dir,self.plot_name))
        self.CurrentVsInstLumiHistoDict[regionname]["2D_hist"].Delete()

        # do plot plus fit plus ratio
        cfit = ROOT.TCanvas('c','',800,600)
        cfit.cd()

        pad1 = ROOT.TPad("pad1","pad1",0,0.420,.99,1)
        pad1.SetBottomMargin(0)
        pad1.Draw()
        pad1.cd()


        profile = self.CurrentVsInstLumiHistoDict[regionname]["2D_fit"].ProfileX('s')
        profile.Approximate()
        profile.Draw()
        profile.GetXaxis().SetRangeUser(minlumi,maxlumi)
        pol1 = ROOT.TF1("pol1","pol1",minlumi, maxlumi)
        profile.Fit('pol1',"QR")
        pol1.Draw("SAME")
        pol1.SetLineColor(kRed)

        legend = ROOT.TLegend(0.21,0.75,0.5,0.92)
        legend.SetFillStyle(0)
        legend.SetFillColor(0)
        legend.SetBorderSize(0)
        legend.AddEntry(profile, "Data 2016, #sqrt{s}=13 TeV", "ep")
        legend.AddEntry(pol1, "Pol1 fit: f(x)= %1.3fx+%1.3f" %(pol1.GetParameter(1), pol1.GetParameter(0)),'l' )
        legend.Draw()

        l1 = TLatex()
        l1.SetNDC()
        l1.SetTextSize(0.06)
        
        try:
            l1.DrawLatex(0.5,0.85, "#chi^{2}/ndf=%1.1f" % (pol1.GetChisquare()/pol1.GetNDF()))
        except ZeroDivisionError:
            continue

        Leg1 = TLatex()
        Leg1.SetNDC()
        Leg1.SetTextAlign( 11 )
        Leg1.SetTextFont( 42 )
        Leg1.SetTextSize( 0.05 )
        Leg1.SetTextColor( 1 )
        #Leg1.DrawLatex(0.2,0.78-0.24, "#scale[1.]{#sqrt{s}=13 TeV}")

        Leg2 =  TLatex()
        Leg2.SetNDC()
        Leg2.SetTextAlign( 11 )
        Leg2.SetTextSize( 0.075 )
        Leg2.SetTextColor( 1 )
        Leg2.SetTextFont(42)
        Leg2.DrawLatex(0.21,0.9-0.22,"              Internal")

        Leg2.DrawLatex(0.21,0.83-0.22, "Tile Calorimeter")

        atlasLabel =  TLatex()
        atlasLabel.SetNDC()
        atlasLabel.SetTextFont( 72 )
        atlasLabel.SetTextColor( 1 )
        atlasLabel.SetTextSize( 0.075 )
        atlasLabel.DrawLatex(0.21,0.9-0.22, "ATLAS")


        profile.GetYaxis().SetTitle("Current %s [nA]"%regionname)
        profile.GetYaxis().SetTitleOffset(1.0)
        profile.GetYaxis().SetTitleSize(0.07)
        profile.GetYaxis().SetLabelSize(0.075)
        profile.GetXaxis().SetLabelColor(0)

        cfit.cd()    

        pad2 = ROOT.TPad('pad2','pad2',0,0.01, .99, 0.395)
        pad2.SetTopMargin(0)
        pad2.SetBottomMargin(0.3)
        #pad2.SetGrid(0,1)
        pad2.SetGridy()
        pad2.Draw()
        pad2.cd()

        #avoid crash
        ROOT.SetOwnership(pad1, false)
        ROOT.SetOwnership(pad2, false)

        fitfunc = ROOT.TH1F("fitfunc","", 1 ,minlumi, maxlumi)
        fitfunc.SetBinContent(1,1)
        fitfunc.SetLineColor(kRed)
        fitfunc.Draw()
        fitfunc.GetXaxis().SetLabelSize(0.1)
        fitfunc.GetYaxis().SetTitleSize(0.12)
        fitfunc.GetXaxis().SetTitleSize(0.12)
        fitfunc.GetYaxis().SetTitleOffset(0.57)
        fitfunc.GetYaxis().CenterTitle()
        fitfunc.GetXaxis().SetTitleOffset(1.1)
        fitfunc.GetYaxis().SetLabelSize(0.1)
        fitfunc.GetYaxis().SetNdivisions(504)
        fitfunc.GetYaxis().SetDecimals()
        fitfunc.SetMinimum(0.982)
        fitfunc.SetMaximum(1.018)

        ratiohist = ROOT.TH1F("ratiohist","",25, minlumi, maxlumi)
        for i in range(ratiohist.GetNbinsX()):
            x = profile.GetBinContent(i+1)
            if x==0.: continue
            y = pol1.Eval(profile.GetBinCenter(i+1))
            quotient = x/y
            x_err = profile.GetBinError(i+1)
            y_err = 0.0 #math.sqrt((pol1.GetParError(1)*x)**2+pol1.GetParError(0)**2)
            quoerr = quotient*math.sqrt((x_err/x)**2+(y_err/y)**2)
            ratiohist.SetBinContent(i+1, quotient)
            ratiohist.SetBinError(i+1, quoerr)

            ratiohist.Draw("SAMEp")
            fitfunc.GetXaxis().SetTitle("Inst. Luminosity [10^{33}cm^{-2}s^{-1}]")
            fitfunc.GetYaxis().SetTitle("Current/f(x)")

        # save plot, several formats...
        cfit.Print("%s/%s_ratioPlot_chi2_2016.png" % (self.dir,self.plot_name))

        self.CurrentVsInstLumiHistoDict[regionname]["2D_fit"].Delete()


def Plot2DModuleVsChannel(data,variable):
    """
    Takes   0: Dictionary of all PMTs
            1: Name of variable to be mapped
    Prints 2D map(s)
    """
    partitions = ['LBA','LBC','EBA','EBC']
    histos2D = [ROOT.TH2F(part,'',64,float(1),float(65),48,float(1),float(49)) for part in partitions]

    # SetPalettekBird()
    SetPalettekDarkBodyRadiator()
    print "Making module vs. channel map of",variable

    # Filling histograms
    for n,part in enumerate(partitions):
        c = ROOT.TCanvas(part,'%s %s'%(part,GetTitle(variable)),900,700)
        c.SetRightMargin(0.15)
        c.SetTopMargin(0.15)
        c.SetLeftMargin(0.15)
        c.SetBottomMargin(0.15)

        for val in FilterMBTS([key for key in data.keys() if key.startswith(part)]):
            val_filtered = val.replace('_m',' ')
            val_filtered = val_filtered.replace('_c',' ')
            xbin,ybin = [int(s) for s in val_filtered.split() if s.isdigit()]
            if data[val].has_key(variable):
                histos2D[n].SetBinContent(xbin,ybin,data[val][variable])

        histos2D[n].GetXaxis().SetTitle('Module #')
        histos2D[n].GetYaxis().SetTitle('Channel #')
        histos2D[n].GetXaxis().SetTitleOffset(0.91)
        histos2D[n].GetYaxis().SetTitleOffset(0.87)
        histos2D[n].GetXaxis().SetTitleSize(0.075)
        histos2D[n].GetYaxis().SetTitleSize(0.075)
        histos2D[n].Draw('COLZ1')

        c.SetLogz(0)
        SetGlobalMinimumMaximum(histos2D,log=False)

        l = TLatex()
        l.SetNDC()
        l.SetTextFont(42)
        l.DrawLatex(0.25,0.92, "%s %s"%(part,GetTitle(variable)))

        c.Print('%s/ModVsChan_%s_%s_%s.png'%(self.dir,part,variable,data["RunNumber"]))
        c.Print('%s/ModVsChan_%s_%s_%s.pdf'%(self.dir,part,variable,data["RunNumber"]))

        c.SetLogz(1)
        c.Modified()
        c.Update()
        SetGlobalMinimumMaximum(histos2D,log=True)

        c.Print('%s/ModVsChan_%s_%s_%s_log.png'%(self.dir,part,variable,data["RunNumber"]))
        c.Print('%s/ModVsChan_%s_%s_%s_log.pdf'%(self.dir,part,variable,data["RunNumber"]))


