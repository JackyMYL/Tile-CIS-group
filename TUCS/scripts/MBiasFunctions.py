import ROOT
import numpy as np
import json
import scipy.stats as st
import datetime
from xml.dom import minidom
import os

"""
Utilities for MinBias macros

-- Histogram construction utilities --



-- Plotting utilities --

* GetTitle(name)
* GetEtaPhiBin(h,eta,m)
* SetPalettekBird()
* SetPalettekLightTemperature()
* SetPalettekDarkBodyRadiator()
* SetPalettekRainbow()
* SetGlobalMinimumMaximum(histos,log=False)
* SetLocalMinimumMaximum(histo,log=False)


-- Calculating variables --

* GetGaussianAverage(values,truncate=False)
* CalculateVariables(data)


-- Getting correct paths --

* GetShortFilePath(run)
* GetIlumiCalcPath(run)
* GetGRLPath(run)


-- Tile mapping tools --

* GetCellName(ros, module, pmt)
* GetRegionName(cell,specialModule=False)


-- Writing to containters --

* WriteCurrentsToDictionary
* WriteVariablesToDictionary
* WriteOfflineLumiToDictionary



-- Reading from containers --

* LoadRunCurrents(run)
* LoadRunVariables(run)



-- Filtering --

* FilterMBTS(names)


-- Misc --

* IsGoodShortNTuple(file)
* GetRunsFromGRL(interval)



"""

def GetGaussianAverage(values,truncate=False):
    """
    Truncate indicates which amount of standard deviations on each side of the mean is to be included in the range over which the mean will be calculated
    """
    ROOT.gStyle.SetOptFit(111)
    h = ROOT.TH1F("","",50,min(values),max(values))
    for val in values:
    	h.Fill(val)
    f1 = ROOT.TF1("f1","gaus",min(values),max(values));
    f1.SetParameters(h.GetMaximum(), h.GetMean(), h.GetRMS() ); 
    h.Fit("f1")

    # h.Fit("gaus")
    # f1 = h.GetFunction("gaus")
    sigma = f1.GetParameter(2)
    mean = f1.GetParameter(1)
    if truncate:
    	f1.SetRange(mean-truncate*sigma,mean+truncate*sigma)
    	mean = f1.GetParameter(1)
    del h
    print(mean, np.array(values).mean())
    return mean

def GetScipyMean(values,proportiontocut=False):
    values = np.array([v for v in values if v > 0.0])
    mean = values.mean()
    if proportiontocut:
        mean = st.trim_mean(values,proportiontocut)
    return mean

def CalculateVariables(data):
    """
    Takes   List with [PMTCurrent, instantaneous luminosity]
    
    Returns 0: Luminosity coefficient from LogLikelihood fit
            1: Error on luminosity coefficient
            2: Relative error on luminosity coefficient
            3: Offset of fit
            4: Error on offset of fit
            5: Relative error on offset of fit
            6: Chi squared value of goodness of fit test
            7: Total accumulated current
    """
    averagecurrent = GetGaussianAverage([val[0] for val in data])
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
    del h
    return (averagecurrent,lumicoeff,lumicoefferror,lumicoeffrelativeerror,offset,offseterror,offsetrelativeerror,chi2,totalcurrent)


def GetTitle(name):
    if name=='AverageCurrent': return 'Average current [nA]'
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
        print("More than one histogram needed!") 
        return
    minimum,maximum = 99999999,-99999999
    for h in histos:
        if h.GetMinimum() < minimum:
            minimum = h.GetMinimum()
        if h.GetMaximum() > maximum:
            maximum = h.GetMaximum()
    if minimum > maximum:
        print("Warning: minimum > maximum")
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
    Returns filtered list of PMT names without MBTS cells
    """
    MBTS = ['EBA_m%s_c13'%mod for mod in [8,24,43,54]]
    MBTS.extend(['EBC_m%s_c13'%mod for mod in [8,24,43,54]])#29,32,34,37,47,43,54]])
    MBTS.extend(['EBA_m%s_c5'%mod for mod in [39,40,41,42,55,56,57,58]])
    MBTS.extend(['EBC_m%s_c5'%mod for mod in [39,40,41,42,55,56,57,58]])
    return [name for name in names if name not in MBTS]

def GetCellName(ros, module, pmt):

        if ros <2: # Long Barrel
            names = ['D0',  'A1',          'BC1',         'BC1', 'A1',  'A2',
                     'BC2', 'BC2',         'A2',          'A3',  'A3',  'BC3',
                     'BC3', 'D1',          'D1',          'A4',  'BC4', 'BC4',
                     'A4',  'A5',          'A5',          'BC5', 'BC5', 'A6',
                     'A6',  'D2',          'D2',          'A7',  'BC6', 'BC6',
                     'A7',  'Unconnected', 'Unconnected', 'A8',  'BC7', 'BC7',
                     'A8',  'A9',          'A9',          'D3',  'BC8', 'BC8',
                     'D3',  'Unconnected', 'BC8',          'B9',  'A10', 'A10'  ]
                     
        else:
            if (ros==2 and module==15) or (ros==3 and module==18):
                names = ['Unconnected', 'Unconnected', 'Unconnected', 'Unconnected', 'C10', 'C10',
                         'A12',         'A12',         'B11',         'B11',         'A13', 'A13',
                         'E1',          'E2',          'B12',         'B12',         'D45', 'D45',
                         'E3',          'E4',          'A14',         'A14',         'B13', 'B13',
                         'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected', 'A15', 'A15',                       
                         'Unconnected', 'Unconnected', 'B14',         'B14',         'Unconnected', 'Unconnected', 
                         'D6',          'D6',          'Unconnected', 'Unconnected', 'A16', 'A16',
                         'B15',         'B15',         'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected']
            else:
                names = ['E3',          'E4',          'D4',          'D4',          'C10', 'C10',
                         'A12',         'A12',         'B11',         'B11',         'A13', 'A13',
                         'E1',          'E2',          'B12',         'B12',         'D5',  'D5',
                         'Unconnected', 'Unconnected', 'A14',         'A14',         'B13', 'B13',
                         'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected', 'A15', 'A15',                       
                         'Unconnected', 'Unconnected', 'B14',         'B14',         'Unconnected', 'Unconnected', 
                         'D6',          'D6',          'Unconnected', 'Unconnected', 'A16', 'A16',
                         'B15',         'B15',         'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected']
        if (pmt == 1):
            if ( ((ros == 2) and (module in [ 3, 4,12,13,23,24,30,31,35,36,44,45,53,54,60,61])) or
                 ((ros == 3) and (module in [ 4, 5,12,13,19,20,27,28,36,37,44,45,54,55,61,62])) ):
                 return 'MBTS'

        return names[pmt-1]
    
def GetRegionName(cell, specialModule=False): 
# this is only to be used for minbias, since the convention has changed for the input files, take special EBA15 and EBC18 modules into account
# reverse function of getCellName
# gives back partiton and pmt channel(s)
# structure: [[A-side,C-side],[pmt1,pmt2]]
    cellmap ={# long barrel
        'A1':[[1,2],[1,4]], 'A2':[[1,2],[5,8]], 'A3':[[1,2],[9,10]], 'A4':[[1,2],[15,18]], 'A5':[[1,2],[19,20]], 'A6':[[1,2],[23,24]], 'A7':[[1,2],[27,30]], 'A8':[[1,2],[33,36]], 'A9':[[1,2],[37,38]], 'A10':[[1,2],[46,47]], 'BC1':[[1,2],[2,3]], 'BC2':[[1,2],[6,7]], 'BC3':[[1,2],[11,12]], 'BC4':[[1,2],[16,17]], 'BC5':[[1,2],[21,22]], 'BC6':[[1,2],[28,29]], 'BC7':[[1,2],[34,35]], 'BC8':[[1,2],[40,41]], 'B9':[[1,2],[44,45]], 'D0':[[1,2],[0,0]], 'D1':[[1,2],[13,14]], 'D2':[[1,2],[25,26]], 'D3':[[1,2],[39,42]],
      # extended barrel:
            'A12':[[0,3],[6,7]], 'A13':[[0,3],[10,11]], 'A14':[[0,3],[20,21]], 'A15':[[0,3],[28,29]], 'A16':[[0,3],[40,41]], 'B11':[[0,3],[8,9]], 'B12':[[0,3],[14,15]], 'B13':[[0,3],[22,23]],  'B14':[[0,3],[32,33]], 'B15':[[0,3],[42,43]], 'C10':[[0,3],[4,5]], 'D4':[[0,3],[2,3]], 'D5':[[0,3],[16,17]], 'D6':[[0,3],[36,37]], 'E1':[[0,3],[12,12]], 'E2':[[0,3],[13,13]], 'E3':[[0,3],[0,0]], 'E4':[[0,3],[1,1]]  
        }
    if specialModule  and (cell=="E3" or cell=="E4"):
        cellmap = {'E3':[[0,3],[18,18]],'E4':[[0,3],[19,19]] } # EBA15 and EBC18 cabeling
    return cellmap[cell]







#def GetIlumiCalcPath(run):

def GetGRL(run):
    # 2012
    if run >= 200841 and run <= 215643:
         return minidom.parse('/afs/cern.ch/work/t/tavandaa/TileCal/Tucs/data/data12_8TeV.periodAllYear_HEAD_DQDefects-00-01-02_PHYS_StandardGRL_Atlas_Ready.xml')
    # 2015
    elif run >= 266904 and run <= 284484:
         return minidom.parse('/afs/cern.ch/work/t/tavandaa/TileCal/Tucs/data/data15_13TeV.periodAllYear_HEAD_DQDefects-00-02-02_PHYS_StandardGRL_Atlas_Ready_Only.xml')
    # 2016
    elif run >= 296939 and run <= 311481:
         return minidom.parse('/afs/cern.ch/work/t/tavandaa/TileCal/Tucs/data/data16_13TeV.periodAllYear_HEAD_DQDefects-00-02-04_PHYS_StandardGRL_Atlas_Ready_Only.xml')
    # 2017
    elif run >= 324320:
         return minidom.parse('/afs/cern.ch/work/t/tavandaa/TileCal/Tucs/data/data17_13TeV.periodAllYear_HEAD_Unknown_PHYS_StandardGRL_Atlas_Ready_Only.xml')
    else:
        print("Wrong run number given")
        return False


def GetAllRunsFromGRL(xmlGRL,minimumLBs=False):
    LBCollList = xmlGRL.getElementsByTagName("LumiBlockCollection")
    runs = []
    for LBColl in LBCollList:
        RunNumber = LBColl.getElementsByTagName("Run")[0]
        if minimumLBs:
            lbList = LBColl.getElementsByTagName("LBRange")
            LBStart,LBEnd = [],[]
            for lb in lbList:
                lbStart = lb.getAttribute("Start")
                lbEnd   = lb.getAttribute("End")
                LBStart.append(int(lbStart))
                LBEnd.append(int(lbEnd))
            if sum([LBEnd[i]-LBStart[i] for i in range(len(LBStart))]) >= minimumLBs:
                runs.append(int(RunNumber.firstChild.data))
        else:
            runs.append(int(RunNumber.firstChild.data))
    return runs


def GetShortNTuple(run):
    if run >= 266904 and run <= 285746:
        dir = "/afs/cern.ch/work/t/tilmbias/public/2015/"
    elif run >= 289341 and run <= 314258:
        dir = "/afs/cern.ch/work/t/tilmbias/public/2016/"
    elif run > 314258:
        dir = "/afs/cern.ch/work/t/tilmbias/public/2017/"
    else:
        print("Wrong run number given")
        return False
    filenames = [f for f in os.listdir(dir) if os.path.isfile(dir+f)]
    file = False
    for f in filenames:
        if str(run) in f and f.startswith('short'):
            file = ROOT.TFile(dir+f,'READ')
    return file

def IsGoodShortNTuple(file):
    # Check file status
    if not file:
        print("NO file")
        return False
    if file.IsZombie():
        print("ZOMBIE file")
        return False
    elif file.TestBit(ROOT.TFile.kRecovered):
        print("CORRUPTED file")
        return False
    # Check tree status
    t = file.Get('CurrentTree')
    if not t:
        print("TREE MISSING in file")
        return False
    # Check branches status
    brancheswanted = ['PMTCurrent','PMTStatus','IsGood','RunNumber','LumiBlock','IsCollision']#,'PMTGain','PMTCalibPed']
    branchespresent = [b.GetName() for b in t.GetListOfBranches()]
    missingbranches = []
    for b in brancheswanted:
        if b not in branchespresent:
            missingbranches.append(b)
    if missingbranches != []:
        for b in missingbranches:
            print("MISSING BRANCH %s in tree"%b)
        return False
    # Check for collisions
    foundcollision = False
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        if t.IsCollision == 1:
            foundcollision = True
            break
    if not foundcollision:
        print("NO COLLISION EVENTS")
        return False
    return True



def CurrentsToDictionary():
    """
    UNFINISHED
    Loads from ReadMBias
    Stores currents and variables in dictionary to dump as json file
    """
    for event in self.eventsList[:1]:
        if not os.path.isfile("datadicts/CurrentVsInstLumiDataDict_run%s.txt"%event.run.runNumber):
            if 276262 <= event.run.runNumber <= 284484:
                filename = '/afs/cern.ch/user/t/tavandaa/scratch/TileCal/Tucs/data/ilumicalc_histograms_None_276262-284484.root'
            elif 297730 <= event.run.runNumber <= 308084:
                filename = '/afs/cern.ch/user/t/tavandaa/scratch/TileCal/Tucs/data/ilumicalc_histograms_None_297730-308084_OflLumi-13TeV-005.root'
            elif event.run.runNumber > 308084:
                filename = '/cvmfs/atlas.cern.ch/repo/sw/database/GroupData/GoodRunsLists/data16_13TeV/20161101/physics_25ns_20.7.lumicalc.OflLumi-13TeV-005.root'
            else:
                print("No ilumicalc file found!")
                continue
            print("Reading file %s for run %s and filling data dictionary..."%(filename,event.run.runNumber))
            file = TFile(filename,'READ')
            file.cd()
            partitions = ["EBA","LBA","LBC","EBC"]
            PMTCurrent = event.run.data['PMTCurrent']
            PMTStatus = event.run.data['PMTStatus']
            PMTGood = event.run.data['IsGood']
            LumiBlock = event.run.data['LumiBlock']
            if event.run.runNumber == 325713:
                InstLumiList = list(np.loadtxt('Online_lumi_run325713.txt'))
            else:
                histoFile = file.Get('run%s_peaklumiplb' % event.run.runNumber)
                for nLumiBlock in range(len(PMTCurrent)):
                    InstLumiList = histoFile.GetBinContent(nLumiBlock+1)/1000.
            if not histoFile: 
                print("No run file found!")
                continue
            self.CurrentVsInstLumiDataDict["InstLumi"] = [(histoFile.GetBinContent(nLumiBlock+1)/1000.) for nLumiBlock in range(len(PMTCurrent)) if (histoFile.GetBinContent(nLumiBlock+1)/1000.!= 0.0)]
            self.CurrentVsInstLumiDataDict["RunNumber"] = event.run.runNumber
            self.VariablesDataDict["RunNumber"] = event.run.runNumber
            self.CurrentVsInstLumiDataDict["Nlumiblocks"] = len(PMTCurrent)
            self.VariablesDataDict["Nlumiblocks"] = len(PMTCurrent)
            for nPart in range(len(PMTCurrent[0])):
                for nMod in range(len(PMTCurrent[0][nPart])):
                    for nPMT in range(len(PMTCurrent[0][nPart][nMod])):
                        self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)] = {"PMTCurrent": []}
                        self.VariablesDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)] = {}
                        pairs = []
                        for nLumiBlock in range(len(PMTCurrent)):
                            InstLumi = InstLumiList[nLumiBlock]/1000.
                            if InstLumi == 0.0: continue
                            if PMTStatus[nLumiBlock][nPart][nMod][nPMT] < 1: continue
                            if PMTGood[nLumiBlock][nPart][nMod][nPMT] < 1: continue
                            pairs.append([InstLumi,PMTCurrent[nLumiBlock][nPart][nMod][nPMT]])
                            self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["PMTCurrent"].append(PMTCurrent[nLumiBlock][nPart][nMod][nPMT])
                        # Get fit values
                        if pairs == []: continue
                        try:
                            averagecurrent,lumicoeff,lumicoefferror,lumicoeffrelativeerror,offset,offseterror, offsetrelativeerror,chi2,totalcurrent = LumiCoeff(pairs)
                        except ZeroDivisionError:
                            continue
                        # Save fit values to dictionary
                        self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["AverageCurrent"] = averagecurrent
                        self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["LumiCoeff"] = lumicoeff
                        self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["LumiCoeffError"] = lumicoefferror
                        self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["LumiCoeffRelativeError"] = lumicoeffrelativeerror
                        self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["Offset"] = offset
                        self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["OffsetError"] = offseterror
                        self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["OffsetRelativeError"] = offsetrelativeerror
                        self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["Chi2"] = chi2
                        self.CurrentVsInstLumiDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["TotalCurrent"] = totalcurrent
                        self.VariablesDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["AverageCurrent"] = averagecurrent
                        self.VariablesDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["LumiCoeff"] = lumicoeff
                        self.VariablesDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["LumiCoeffError"] = lumicoefferror
                        self.VariablesDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["LumiCoeffRelativeError"] = lumicoeffrelativeerror
                        self.VariablesDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["Offset"] = offset
                        self.VariablesDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["OffsetError"] = offseterror
                        self.VariablesDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["OffsetRelativeError"] = offsetrelativeerror
                        self.VariablesDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["Chi2"] = chi2
                        self.VariablesDataDict["%s_m%s_c%s"%(partitions[nPart],nMod+1,nPMT+1)]["TotalCurrent"] = totalcurrent
            del histoFile
            print("Dumping data to datadicts/CurrentVsInstLumiDataDict_run%s.txt..."%event.run.runNumber)
            with open("datadicts/CurrentVsInstLumiDataDict_run%s.txt"%event.run.runNumber,"w") as outfile:
                json.dump(self.CurrentVsInstLumiDataDict,outfile)
            print("Dumping variables to datadicts/VariablesDataDict_run%s.txt..."%event.run.runNumber)
            with open("datadicts/VariablesDataDict_run%s.txt"%event.run.runNumber,"w") as outfile:
                json.dump(self.VariablesDataDict,outfile)
            data = self.CurrentVsInstLumiDataDict
