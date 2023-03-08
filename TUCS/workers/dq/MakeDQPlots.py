from src.GenericWorker import *
from ROOT import TGraph,TH2F,gStyle
import time,datetime

class MakeDQPlots(GenericWorker):
    "Make plot of data quality status"

    def __init__(self,type,runForDetail,runType="DQStatus"):
        self.type = type
        self.runType = runType
        self.runForDetail = runForDetail
        self.noiseDict = {}
        self.maskedDict= {}
        self.badCellDict= {}
        self.maskedCellDict= {}
        self.initHistFile()
        gStyle.SetTimeOffset(0)

    def ProcessStart(self):
        self.h_timeline_masked = TGraph()
        self.h_timeline_masked.SetNameTitle('h_timeline_masked','Evolution of Masked Channels')
        self.h_timeline_noise = TGraph()
        self.h_timeline_noise.SetNameTitle('h_timeline_noise','Evolution of Noisy Channels')
        self.h_timeline_maskedCell = TGraph()
        self.h_timeline_maskedCell.SetNameTitle('h_timeline_maskedCell','Evolution of Masked Cells')
        self.h_timeline_badCell = TGraph()
        self.h_timeline_badCell.SetNameTitle('h_timeline_badCell','Evolution of Masked Cell Components')

        if self.runForDetail==-1:
            global run_list
            self.runForDetail = run_list[-1].runNumber

        print('Using run: ',self.runForDetail,' for 2D masking plots.')
        self.h_etaphi_maskedCell = TH2F('h_etaphi_maskedCell','Map of Masked Cells',34,-1.7,1.7,64,-3.2,3.2)
        self.h_etaphiA_maskedCell = TH2F('h_etaphiA_maskedCell','Map of Masked A Cells',34,-1.7,1.7,64,-3.2,3.2)
        self.h_etaphiBC_maskedCell = TH2F('h_etaphiBC_maskedCell','Map of Masked BC Cells',34,-1.7,1.7,64,-3.2,3.2)
        self.h_etaphiD_maskedCell = TH2F('h_etaphiD_maskedCell','Map of Masked D Cells',17,-1.7,1.7,64,-3.2,3.2)
        self.h_etaphi_badCell = TH2F('h_etaphi_badCell','Amount of Tile Masked Cells',34,-1.7,1.7,64,-3.2,3.2)
        self.h_etaphiA_badCell = TH2F('h_etaphiA_badCell','Amount of Tile Masked A Cells',34,-1.7,1.7,64,-3.2,3.2)
        self.h_etaphiBC_badCell = TH2F('h_etaphiBC_badCell','Amount of Tile Masked BC Cells',34,-1.7,1.7,64,-3.2,3.2)
        self.h_etaphiD_badCell = TH2F('h_etaphiD_badCell','Amount of Tile Masked D Cells',17,-1.7,1.7,64,-3.2,3.2)
    
    def ProcessStop(self):
        i=0
        for t in list(self.maskedDict.keys()):
            self.h_timeline_masked.SetPoint(i,t,self.maskedDict[t]/19640.0*100.)
            self.h_timeline_noise.SetPoint(i,t,self.noiseDict[t]/19640.0*100.)
            i += 1
        self.h_timeline_masked.GetXaxis().SetNdivisions(8,False)
        self.h_timeline_masked.GetXaxis().SetTimeDisplay(1)
        self.h_timeline_masked.GetXaxis().SetTimeFormat("%b-%y")
        self.h_timeline_noise.GetXaxis().SetNdivisions(8,False)
        self.h_timeline_noise.GetXaxis().SetTimeDisplay(1)
        self.h_timeline_noise.GetXaxis().SetTimeFormat("%b-%y")
        self.h_timeline_masked.GetYaxis().SetTitle("% of TileCalorimeter")
        self.h_timeline_noise.GetYaxis().SetTitle("% of TileCalorimeter")
        self.h_timeline_masked.Write()
        self.h_timeline_noise.Write()

        i=0
        for t in list(self.maskedCellDict.keys()):
            self.h_timeline_maskedCell.SetPoint(i,t,self.maskedCellDict[t]/5150.0*100.)
            self.h_timeline_badCell.SetPoint(i,t,self.badCellDict[t]/5150.0*100.)
            i += 1
        self.h_timeline_maskedCell.GetXaxis().SetNdivisions(8,False)
        self.h_timeline_maskedCell.GetXaxis().SetTimeDisplay(1)
        self.h_timeline_maskedCell.GetXaxis().SetTimeFormat("%b-%y")
        self.h_timeline_badCell.GetXaxis().SetNdivisions(8,False)
        self.h_timeline_badCell.GetXaxis().SetTimeDisplay(1)
        self.h_timeline_badCell.GetXaxis().SetTimeFormat("%b-%y")
        self.h_timeline_maskedCell.GetYaxis().SetTitle("% of TileCalorimeter")
        self.h_timeline_badCell.GetYaxis().SetTitle("% of TileCalorimeter")
        self.h_timeline_maskedCell.Write()
        self.h_timeline_badCell.Write()
       
        self.h_etaphi_maskedCell.SetXTitle('#eta')
        self.h_etaphi_maskedCell.SetYTitle('#phi')
        self.h_etaphi_maskedCell.Write()
        self.h_etaphiA_maskedCell.SetXTitle('#eta')
        self.h_etaphiA_maskedCell.SetYTitle('#phi')
        self.h_etaphiA_maskedCell.Write()
        self.h_etaphiBC_maskedCell.SetXTitle('#eta')
        self.h_etaphiBC_maskedCell.SetYTitle('#phi')
        self.h_etaphiBC_maskedCell.Write()
        self.h_etaphiD_maskedCell.SetXTitle('#eta')
        self.h_etaphiD_maskedCell.SetYTitle('#phi')
        self.h_etaphiD_maskedCell.Write()
        self.h_etaphi_badCell.SetXTitle('#eta')
        self.h_etaphi_badCell.SetYTitle('#phi')
        self.h_etaphi_badCell.Write()
        self.h_etaphiA_badCell.SetXTitle('#eta')
        self.h_etaphiA_badCell.SetYTitle('#phi')
        self.h_etaphiA_badCell.Write()
        self.h_etaphiBC_badCell.SetXTitle('#eta')
        self.h_etaphiBC_badCell.SetYTitle('#phi')
        self.h_etaphiBC_badCell.Write()
        self.h_etaphiD_badCell.SetXTitle('#eta')
        self.h_etaphiD_badCell.SetYTitle('#phi')
        self.h_etaphiD_badCell.Write()
       

    def ProcessRegion(self,region):
        if 'gain' in region.GetHash():
            for event in region.GetEvents():
#                if event.run.runType != self.runType:
#                    continue
                theTime = self.GetTime(event)
            
                # Set all the counters to zero for each run
                if theTime not in list(self.maskedDict.keys()):
                    self.maskedDict[theTime] = 0
                    self.noiseDict[theTime]  = 0
                
                # Increment ADC counters
                if event.data['isBad']:   self.maskedDict[theTime] += 1
                if event.data['isNoisy']: self.noiseDict[theTime]  += 1

        elif '_t' in region.GetHash():

            for event in region.GetEvents():
#                if event.run.runType != self.runType:
#                    continue
                theTime = self.GetTime(event)
                # Set all the counters to zero for each run
                if theTime not in list(self.maskedCellDict.keys()):
                    self.badCellDict[theTime]    = 0
                    self.maskedCellDict[theTime] = 0
                
                # Increment Cell counters
                self.badCellDict[theTime] += event.data['isBad']
                if event.data['isMasked']: self.maskedCellDict[theTime] += 1
                
                if event.run.runNumber == self.runForDetail:
                    eta,phi = region.GetEtaPhi()
                    
                    # Fill twice for D-cell to account for 2-tower coverage
                    if '_sD' in region.GetHash() and '_t08' not in region.GetHash():
                        self.h_etaphi_badCell.Fill(eta+0.05,phi,event.data['isBad'])
                        self.h_etaphi_badCell.Fill(eta-0.05,phi,event.data['isBad'])
                    else:
                        self.h_etaphi_badCell.Fill(eta,phi,event.data['isBad'])
                    if event.data['isMasked']:                        
                        if '_sD' in region.GetHash() and '_t08' not in region.GetHash():
                            # Fill twice for D-cell to account for 2-tower coverage
                            self.h_etaphi_maskedCell.Fill(eta+0.05,phi,1.0)
                            self.h_etaphi_maskedCell.Fill(eta-0.05,phi,1.0)
                        else:
                            self.h_etaphi_maskedCell.Fill(eta,phi,1.0)
                    if '_sA' in region.GetHash():
                        self.h_etaphiA_badCell.Fill(eta,phi,event.data['isBad'])
                        if event.data['isMasked']: self.h_etaphiA_maskedCell.Fill(eta,phi,1.0)
                    elif '_sBC' in region.GetHash():
                        self.h_etaphiBC_badCell.Fill(eta,phi,event.data['isBad'])
                        if event.data['isMasked']: self.h_etaphiBC_maskedCell.Fill(eta,phi,1.0)
                    elif '_sD' in region.GetHash():
                        self.h_etaphiD_badCell.Fill(eta,phi,event.data['isBad'])
                        if event.data['isMasked']: self.h_etaphiD_maskedCell.Fill(eta,phi,1.0)
                    
            

    def GetTime(self,event):
        theDate = datetime.datetime(int(event.run.time[0:4]),int(event.run.time[5:7]),int(event.run.time[8:10]),int(event.run.time[11:13]),int(event.run.time[14:16]),int(event.run.time[17:19]) )
        return int(theDate.strftime('%s'))

