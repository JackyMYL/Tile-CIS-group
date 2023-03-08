# Author: Grey Wilburn <gwwilburn@gmail.com>
# Edited by: Andrew Mattillion <amattillion@gmail.com>

# This is the code used to make the TileCal Cell Energy Deposition
# public plot with 2015 collision data and MC presented in February
# 2016.

from src.ReadGenericCalibration import *
from src.oscalls import *
from src.region import *
from src.MakeCanvas import *
from ROOT import TFile
from subprocess import call
import os

class CellEnergy(ReadGenericCalibration):
    """Extract Cell Energies for Cell Energy Deposition Public Plots and store histograms in local root files"""

    def __init__(self,
                  processingDir=('root://castoratlas//castor/cern.ch/atlas/'
                                 'atlascerngroupdisk/det-tile/{Tyear}/'), 
                  all=False):
                  
        self.processingDir = processingDir
        self.ftDict = {}
       
        #For output plot stylings
        ROOT.gStyle.SetOptStat(0)
        ROOT.gErrorIgnoreLevel = 1001

    def ProcessStart(self):
        #Global dictionary to map cell names to D3PD indices
        self.cell_hash_dict = {}

        #Run ReadCellNoiseFromCool.py simply because it has the cell indices
        #used in the D3PD's
        cellnoise = False
        for file in os.listdir("."):
            if file == 'cellnoise.out':
                cellnoise = True
        if not cellnoise:
            call(['ReadCellNoiseFromCool.py'], stdout = open( './cellnoise.out', 'w'), shell=True)

        #Extract cell indices using ReadCellNoise output by parsing text
        file = open("cellnoise.out", "r")
        for line in file:
            linelist2 = []
            linelist = line.split(' ')
            for element in linelist:
                if element != '':
                    linelist2.append(element)

            partlist = list(linelist[0])
            partname = partlist[0] + partlist [1] + partlist[2] + '_m' + partlist[3] + partlist[4]
            cell_list = list(linelist2[1])
            cell_name = partname + '_'
            #print cell_name

            #ReadCellNoiseFromCool does not account for new E cells in EBA15 and EBC18
            #Therefore, we need to shift the indices by 1 after each cell appears in the output
            correction = 0
            ebac = False
            ebcc = False

            for element in cell_list:
                if element not in ['s', 'p', '+', '-', '*']:
                    cell_name += element
                if cell_name == 'EBA_m15_D4' and not ebac:
                    correction += 1
                    ebac = True
                if cell_name == 'EBC_m18_D4' and not ebac:
                    correction += 1
                    ebcc = True
             
            #Here we cut out problematic cells
            #All gap/crack cells ('E' cells) and 3 noticed problematic cells are excluded
            if not cell_name in self.cell_hash_dict:
                if not ('E1' in cell_name or 'E2' in cell_name or 'E3' in cell_name or 'E4' in cell_name 
                        or 'LBC_m58_A7' in cell_name or 'EBC_m18_D40' in cell_name or "LBA_m62_A6" in cell_name):
                    self.cell_hash_dict[cell_name] = int(linelist2[3]) - correction

        #Now we prepare to extract the cell energies from the root files

        #We need to keep track of a few things to look for issues
        #Maps cell energy to eta and phi values, used in creating eta vs. phi 2d hist to find hot/cold cells
        eta_phi_dict = {}
        #Maps avg energy to each cell, associated pmt's, used to diagnose problems  
        energy_dict = {}
        #counts the number of events w/ severely negative energy for each cell
        neg_en_dict = {}
        #list of cells w/ issues
        bad_list = []

        #We will loop over files with these run numbers
        self.run_list = [15, 24, 61, 63, 69, 122, 149, 168, 249, 258]
        #self.run_list = [222500]
                       

        histo = ROOT.TH1D('cell_energy', '', 100, -1.0, 5.0)
        eta_phi_histo = ROOT.TH2D("eta_phi", "", 34, -1.7, 1.7, 64, -3.14, 3.14)
        eta_energy_histo = ROOT.TH2D("eta_energy", "", 34, -1.6, 1.6, 1000, 0, 10)
        eta_energy_profile = ROOT.TProfile("eta_energy_profile", "", 34, -1.6, 1.6)
        sumpt_histo = ROOT.TH1D('sumpt', "", 150, 0, 150)
        ntracks_histo = ROOT.TH1D('ntracks', "", 150, 0, 150)     
        total_event_count = 0
        
        for run in self.run_list:
             event_id = 0
             f,t = self.Get_h2000(run)
             print(f.GetName())
             #Turn off all tBranches except the ones we will use
             t.SetBranchStatus("*", 0)
             #t.SetBranchStatus("HLT_noalg_mb_L1RD0_FILLED", 1) #This is used for the random trigger distribution
             t.SetBranchStatus("L1_MBTS_1", 1)
             t.SetBranchStatus("vxp_n", 1)
             t.SetBranchStatus("vxp_type", 1)
             t.SetBranchStatus("vxp_nTracks", 1)
             t.SetBranchStatus("vxp_E", 1)
             t.SetBranchStatus("vxp_sumPt", 1)
             t.SetBranchStatus("tile_Gain1", 1)
             t.SetBranchStatus("tile_Gain2", 1)
             t.SetBranchStatus("tile_E", 1)
             t.SetBranchStatus("tile_Ediff", 1)
             t.SetBranchStatus("tile_Status1", 1)
             t.SetBranchStatus("tile_Status2", 1)
             t.SetBranchStatus("tile_eta", 1)
             t.SetBranchStatus("tile_phi", 1)
             
             
             #The 'set branch address' method should speed up reading the root files
             vxp_type_vec = ROOT.vector('short')()
             vxp_nTracks_vec = ROOT.vector('int')()
             vxp_E_vec = ROOT.vector('float')()
             vxp_sumPt_vec = ROOT.vector('float')()
             tile_Gain1_vec = ROOT.vector('short')()
             tile_Gain2_vec = ROOT.vector('short')()
             tile_Status1_vec = ROOT.vector('unsigned short')()           
             tile_Status2_vec = ROOT.vector('unsigned short')()           
             tile_E_vec = ROOT.vector('float')()           
             tile_Ediff_vec = ROOT.vector('float')()           
             tile_eta_vec = ROOT.vector('float')()           
             tile_phi_vec = ROOT.vector('float')()  
             t.SetBranchAddress("vxp_type", vxp_type_vec)
             t.SetBranchAddress("vxp_nTracks", vxp_nTracks_vec)
             t.SetBranchAddress("vxp_E", vxp_E_vec)
             t.SetBranchAddress("vxp_sumPt", vxp_sumPt_vec)
             t.SetBranchAddress("tile_Gain1", tile_Gain1_vec)
             t.SetBranchAddress("tile_Gain2", tile_Gain2_vec)  
             t.SetBranchAddress( "tile_E", tile_E_vec )
             t.SetBranchAddress( "tile_Status1", tile_Status1_vec)
             t.SetBranchAddress( "tile_Status2", tile_Status2_vec)
             t.SetBranchAddress( "tile_eta", tile_eta_vec)
             t.SetBranchAddress( "tile_phi", tile_phi_vec)
             t.SetBranchAddress( "tile_Ediff", tile_Ediff_vec)
        
             nevt = float(t.GetEntries())

             #Loop over events in file
             i = 0
             while t.GetEntry(i):
                 i += 1
                 
                 #if t.HLT_noalg_mb_L1RD0_FILLED == 0:
                     #continue
                 if t.L1_MBTS_1 == 0:
                     continue 

                 hasPileUpVertex = False
                 hasPrimaryVertex = False
                 pvlocation = -1
                 for ivtx in range(t.vxp_n):
                        if vxp_type_vec.at(ivtx) == 3 and vxp_nTracks_vec.at(ivtx) >= 4:
#                        if vxp_type_vec.at(ivtx) == 3:
                                hasPileUpVertex = True
                        if vxp_type_vec.at(ivtx) == 1:
                                hasPrimaryVertex = True
                                pvlocation = ivtx
                #Cut 1: Using cuts that are used in MinBias Analysis
                 if hasPileUpVertex or not hasPrimaryVertex:
                        continue
                # The following cuts were used when trying to investigate the discrepancy
                # between data and MC.

                #Cut 2: low energy in interaction or no interaction -> less physics tail
#                 if hasPrimaryVertex:
#                        continue

#                #Cut 3: ask for events with more physics  -> tail should increase
#                 if not ( hasPileUpVertex and hasPrimaryVertex ):
#                       continue

                # Cut 4: on sumPt
#                 if vxp_sumPt_vec.at(pvlocation) > 40000:
#                        continue 
                
                #Cut 5: on sumPt and number of tracks
#                 if vxp_sumPt_vec.at(pvlocation) > 40000 and vxp_nTracks_vec.at(pvlocation) >= 60:
#                        continue
                
                #Cut 6: a variation of the cut on sumPt
#                 if vxp_sumPt_vec.at(pvlocation) > 40000 or vxp_sumPt_vec.at(pvlocation) < 5000:
#                        continue 

                #Cut 7: another variation of the sumPt cut
#                 if vxp_sumPt_vec.at(pvlocation) < 5000:
#                        continue        
        
                #The following 3 lines are used when plotting the distribution of sumpt and ntracks
#                 if pvlocation >= 0:
#                         sumpt_histo.Fill(vxp_sumPt_vec.at(pvlocation)*.001)
#                        ntracks_histo.Fill(vxp_nTracks_vec.at(pvlocation))
                 

                                 
                 EnergyHistograms = True
                 if EnergyHistograms:
                         #Loop over cells that passed cut
                         for cell in self.cell_hash_dict:
                             hash = self.cell_hash_dict[cell]

                             #set up dictionaries
                             if not cell in eta_phi_dict:
                                 neg_en_dict[cell] = 0
                                 energy_dict[cell] = {}
                                 energy_dict[cell]['total'] = 0
                                 energy_dict[cell]['pmt1'] = 0
                                 energy_dict[cell]['pmt2'] = 0
                                 eta_phi_dict[cell] = {}
                                 eta_phi_dict[cell]['eta'] = tile_eta_vec.at(hash)
                                 eta_phi_dict[cell]['phi'] = tile_phi_vec.at(hash)

                             #If at least one PMT is problem-free, we will read its energy 
                             if (tile_Status1_vec.at(hash) < 3) or (tile_Status2_vec.at(hash) < 3):
                                 energy = tile_E_vec.at(hash)
                                 ediff = tile_Ediff_vec.at(hash)
                                 #Extract energies of individial pmt's
                                 e1 = 0.5*(energy + ediff)
                                 e2 = 0.5*(energy - ediff)
                                 #Modifiy dictionaries
                                 energy_dict[cell]['total'] += 0.001 * energy
                                 energy_dict[cell]['pmt1'] += 0.001 * e1
                                 energy_dict[cell]['pmt2'] += 0.001 * e2

                            #Fill 1D histogram, 2D eta phi histogram, 2D eta energy histogram
                             histo.Fill(0.001 * energy)
                             eta_phi_histo.Fill(tile_eta_vec.at(hash), tile_phi_vec.at(hash), 0.001 * energy)
                             eta_energy_histo.Fill(tile_eta_vec.at(hash), .001 * energy)
                             
                             if energy > 500:
                                 eta_energy_profile.Fill(tile_eta_vec.at(hash), energy)

                             #If energy is suuuper low, we want to know about it
                             if energy < -400:
                                 print(cell, energy)
                                 neg_en_dict[cell] += 1
                                 bad_list.append(cell) 
                 event_id += 1
                 total_event_count += 1
                 if event_id % 1000 == 0:
                     print("\n\nevent #:", event_id, run)
                     print("total event #:", total_event_count)
                     print("Percent of events complete %s %d %%" % (run, int(100 * (float(event_id) / nevt))))

        #Important for normalizing
        print("\nFinal total event count = %i" % total_event_count)
        scale_factor = float(1) / float(total_event_count)
        print("Scale Factor for this data set = %f\n" % scale_factor)

        PlotEnergyHistograms = True
        if PlotEnergyHistograms:         
                #Print information about problematic cells
                for cell in bad_list:
                   mean_en = scale_factor * energy_dict[cell]['total']
                   mean_e1 = scale_factor * energy_dict[cell]['pmt1']
                   mean_e2 = scale_factor * energy_dict[cell]['pmt2']
         
                   print("\n Bad Cell: ", cell, mean_en)
                   print("pmt1: ", mean_e1)
                   print("pmt2: ", mean_e2, "\n") 

                #Now we plot
                c1 = src.MakeCanvas.MakeCanvas()
                c1.SetLogy()
                c1.cd()
         
                #Format stats box
                ptstats = TPaveText(0.60,0.45,0.85,0.70,"brNDC")
                ptstats.SetName("stats")
                ptstats.SetBorderSize(2)
                ptstats.SetFillColor(0)
                ptstats.SetTextAlign(12)
                text = ptstats.AddText(0.03, 0.90, "Entries")
                text.SetTextSize(.035)
                text = ptstats.AddText(0.97,0.90, str(int(histo.GetEntries())))
                text.SetTextAlign(32)
                text.SetTextSize(.035)
                text = ptstats.AddText(0.03, 0.70, "Mean")
                text.SetTextSize(.035)
                text = ptstats.AddText(0.97, 0.70, "%.03g" % (histo.GetMean(1)))
                text.SetTextAlign(32)
                text.SetTextSize(.035)
                text = ptstats.AddText(0.03, 0.50, "RMS")
                text.SetTextSize(.035)
                text = ptstats.AddText(0.97, 0.50, "%.03g" % (histo.GetRMS(1))) 
                text.SetTextAlign(32)
                text.SetTextSize(.035)
                text = ptstats.AddText(0.03, 0.30, "Underflow")
                text.SetTextSize(.035)
                text = ptstats.AddText(0.97, 0.30, str(int(histo.GetBinContent(0))))
                text.SetTextAlign(32)
                text.SetTextSize(.035)
                text = ptstats.AddText(0.03, 0.10, "Overflow")
                text.SetTextSize(.035)
                text = ptstats.AddText(0.97, 0.10, str(int(histo.GetBinContent(histo.GetNbinsX()+1))))
                text.SetTextAlign(32)
                text.SetTextSize(.035)

                #Format histogram
                histo.GetXaxis().SetTitle("Tile Cell Energy [GeV]")
                histo.GetYaxis().SetTitle("# of Cells / 0.06 GeV / Event")
                histo.GetYaxis().SetTitleOffset(1.2)
                histo.GetYaxis().SetLimits(0.00001, 10000) 
                histo.SetMarkerStyle(26)
                # Set error bars. It is very important to do this BEFORE scaling 
                for i in range(0,102):
                    histo.SetBinError(i, sqrt(histo.GetBinContent(i)))

                #Draw unnormalized version of histogram
                histo.Draw('E1')
                ptstats.Draw()

                #Format legend
                leg = ROOT.TLegend(0.60, 0.86, 0.85, 0.90)
                leg.SetBorderSize(1)
                leg.AddEntry(histo, "MCvercut1and7", "pe")
                leg.Draw()
                c1.Print('cell_energy_histo_MCvercut1and7_unscaled.png')

                #Save unnormalized version of histogram
                hist_file = ROOT.TFile("cell_energy_histo_MCvercut1and7_unscaled.root", "new")
                histo.Write()
                hist_file.Close()     

                #Same process for the normalized histogram 
                c1.Clear()
                histo.Scale(scale_factor)
                histo.SetMinimum(0.00001)
                histo.SetMaximum(100000)
                histo.Draw('E1')
                ptstats.Draw()
                leg.Draw()
                c1.Print('cell_energy_histo_MCvercut1and7_scaled.png')

                hist_file = ROOT.TFile("cell_energy_histo_MCvercut1and7_scaled.root", "new")
                histo.Write()
                hist_file.Close()  
                
        moreplots = False
        if moreplots:   
 
                #Now we make the eta phi 2d histogram
                c2 = src.MakeCanvas.MakeCanvas()
                c2.cd()
                eta_phi_histo.Scale(scale_factor)
                eta_phi_histo.GetXaxis().SetTitle("Eta")
                eta_phi_histo.GetYaxis().SetTitle("Phi")
                eta_phi_histo.GetYaxis().SetTitleOffset(0.6)
                eta_phi_histo.SetMinimum(-0.01)
                eta_phi_histo.SetMaximum(0.02)
                                           
                eta_phi_histo.Draw("COLZ")
                c2.SetLeftMargin(0.08)
                c2.SetRightMargin(0.15)
                c2.Print('eta_phi_histo_13TeVcut1andL1MBTS.png')
                
                #Now make the eta energy 2D histogram
                c3 = src.MakeCanvas.MakeCanvas()
                c3.cd()
                eta_energy_histo.GetXaxis().SetTitle("Eta")
                eta_energy_histo.GetYaxis().SetTitle("Energy")
                eta_energy_histo.GetYaxis().SetTitleOffset(0.7)
                
                eta_energy_histo.Draw("COLZ")
                c3.SetLeftMargin(0.08)
                c3.SetRightMargin(0.15)
                c3.Print('eta_energy_histo_13TeVcut1andL1MBTS.png')
                
                #Now make the eta energy profile histogram of the previous 2D histogram
                c4 = src.MakeCanvas.MakeCanvas()
                c4.cd()
                eta_energy_profile.GetXaxis().SetTitle("Eta")
                eta_energy_profile.GetYaxis().SetTitle("Energy")
                eta_energy_profile.GetYaxis().SetTitleOffset(0.8)
                eta_energy_profile.SetMinimum(400)
                eta_energy_profile.SetMaximum(1500)
       
                eta_energy_profile.Draw('E1')
                c4.Print('eta_energy_profile_13TeVcut1andL1MBTS.png')

                #Save the eta energy profile in a ROOT file
                hist_file = ROOT.TFile("eta_energy_profile_13TeVcut1andL1MBTS.root", "new")
                eta_energy_profile.Write()
                hist_file.Close()

        vertexplots = False
        if vertexplots:

                #Now we make the sumpt vertex histogram
                c5 = src.MakeCanvas.MakeCanvas()
                c5.cd()
                sumpt_histo.GetXaxis().SetTitle("Sumpt [GeV]")

                sumpt_histo.Draw('E1')
                c5.Print('sumpt13TeVL1MBTS.png')
 
                hist_file = ROOT.TFile("sumpt13TeVL1MBTS.root", "new")
                sumpt_histo.Write()
                hist_file.Close()     

                #Now we make the ntracks vertex histogram
                c6 = src.MakeCanvas.MakeCanvas()
                c6.cd()
                ntracks_histo.GetXaxis().SetTitle("Number of Tracks ")

                ntracks_histo.Draw('E1')
                c6.Print('ntracks13TeVL1MBTS.png')

                hist_file = ROOT.TFile("ntracks13TeVL1MBTS.root", "new")
                ntracks_histo.Write()
                hist_file.Close()     

    def ProcessStop(self):
        pass
        
    def ProcessRegion(self, region):
        pass

    def Get_h2000(self, run):
        # The folllowing two lines will change based on the name of the files and where they are stored.
        #Use the directory root://eosatlas//eos/atlas/user/a/amattill/CellEnergyPublicPlot/RandomTrigger/ROOT if making RT distribution     
        self.processingDir ='root://eosatlas//eos/atlas/user/a/amattill/CellEnergyPublicPlot/13TeVData/ROOT'
        f = TFile.Open('%s/user.btuan.7238488.D3PD._%d.root' % (self.processingDir,run), "read")
        if f == None:
            t = None
            print('Failed to open a file!')
        else:
            t = f.Get('caloD3PD')
            self.ftDict[run] = [f, t]
            if (not t):
                print('could not find h2000 tree')
                return
       
            return f,t
