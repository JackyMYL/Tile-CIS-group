// Author: Dawit Belayneh
// code to obtain phi modulation corrections
// Given muon events obtain phi modulated energy
//
// To compile: g++ phi_mod.cxx $(root-config --cflags --libs) -o <executable name>
//
//
#include <vector>
#include <cmath>
#include <map>
#include <iostream>
#include <string>
#include <utility>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "TMath.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1.h"
#include "TCanvas.h"
#include "TProfile.h"
#include "TLorentzVector.h"

// contains all the FCS structs needed
#include "FastCaloSimAnalyzer/FCS_Cell.h"
// contains getDDE method to access cell structs from eta, phi and layer info
#include "FastCaloSimAnalyzer/CaloGeometryFromFile.h"

// input: FCS_matchedcellvector - layer information
// output: total hit energy deposit
float getTotalHitEnergy(FCS_matchedcellvector *layer)
{
	float tot_energy = 0.0;
	// get num of cells in layer
	int ncells = layer->size();
	//std::cout << "ncells is " + std::to_string(ncells) + "\n";
	for (int ci = 0; ci < ncells; ci++)
	{
		// loop through cell hits and sum energy
		//std::cout << "accessing cell #" + std::to_string(ci) + "\n";
		FCS_matchedcell cell = layer->m_vector.at(ci);
		std::vector<FCS_hit> hits = cell.hit;
		int nhits = hits.size();
		for (int hi = 0; hi < nhits; hi++)
		{
			tot_energy += hits[hi].hit_energy;	
		}	
	}
	//std::cout << "tot_energy: " + std::to_string(tot_energy) + "\n";
	return tot_energy;	
}

// input: muon phi, eta, layer, *m_cell_coordinates, *m_cell_identifiers
// output: phi correction 
//
float findImpactCellID(float eta, float phi, std::vector<std::pair<float,float>> *layer_coordinates ,std::vector<float> *layer_identifiers)
{

  	std::vector<float> distance;
  	int index = 0;

  	for (auto xy : *(layer_coordinates)) 
	{
		float deta = xy.first - eta;
    		float dphi = xy.second - phi;
    		float d = deta * deta + dphi * dphi;
    		distance.push_back(d);
    		//std::cout<<"index: "<<index<<" cell_id: "<<m_cell_identifiers[layer][index]<<"find impact, d: "<<d<<std::endl;
        	index++;
	}
    
	int minElementIndex = std::min_element(distance.begin(), distance.end()) - distance.begin();
    
        Long64_t impactcell_id = layer_identifiers->at(minElementIndex);
	return impactcell_id;	
}

// given muon smaple  
// produce E vs phiMod plot for each layer
//
// Make optional:
// 	input file name
// 	energy cut 
// 	output dir name
//
int main(int argc, char** argv)
{

	time_t start_time;
	time_t end_time;
	start_time = time(NULL);

	if (argc == 0)
	{
		std::cout << "Arguments not passed\n";
		return 1;
	}

	// phi_mod92(input_file, energy_cut)
	char* input_file = argv[1];
	char* output_name = argv[2];
	char* en_cut = argv[3];
	int e_cut = atoi(en_cut); // cast to char* to int


	// Open Geo TTree and get co-ordinates
	std::cout << "Reading Geometry File\n";
	TFile* geoFile = TFile::Open("/eos/atlas/atlascerngroupdisk/proj-simul/CaloGeometry/ATLAS-R2-2016-01-00-01.root");
  	TTree* geoTree = (TTree*)geoFile->Get("ATLAS-R2-2016-01-00-01");
  	int centries = geoTree->GetEntries();

	// co-ordinate maps keyed by m_cell_identifiers 
	// used by findImpactCell and getPhiCorrection
	//
	
	std::map<Long64_t,float> m_cells_eta_raw; 
	std::map<Long64_t,float> m_cells_phi_raw;
	std::map<Long64_t,float> m_cells_phi;
	std::map<Long64_t,float> m_cells_r_raw;

	std::map<Int_t, std::vector< std::pair<float, float> >> m_cell_coordinates;
	std::map<Int_t, std::vector<float>> m_cell_identifiers; 

  	// declare the brach address variables
  	Int_t m_cell_layer;
	Long64_t m_cell_identifier; 
	float m_cell_eta_raw, m_cell_phi_raw, m_cell_phi, m_cell_r_raw;

	// fill in layer-2 cell phi and eta values to hist
	//TH1F *cell_phi = new TH1F("cell center phi raw", "cell_center_phi_raw", 300, -4, 4);
	//TH1F *cell_eta = new TH1F("cell center eta raw", "cell_center_eta_raw", 400, -2, 2);

  	geoTree->SetBranchAddress("calosample", &m_cell_layer);
  	geoTree->SetBranchAddress("identifier", &m_cell_identifier);
  	geoTree->SetBranchAddress("eta_raw",    &m_cell_eta_raw);
  	geoTree->SetBranchAddress("phi_raw",    &m_cell_phi_raw);
  	geoTree->SetBranchAddress("phi",        &m_cell_phi);
  	geoTree->SetBranchAddress("r_raw",      &m_cell_r_raw);

	std::cout << "Getting coordinates\n";
  	for (int icell = 0; icell < centries; icell++)
    	{
    		geoTree->GetEntry(icell);

		//if (m_cell_layer == 2 and std::fabs(m_cell_eta_raw) < 0.5)
		//{
		//	cell_phi->Fill(m_cell_phi_raw);
		//	cell_eta->Fill(m_cell_eta_raw);	
		//}

    		m_cells_eta_raw[m_cell_identifier] = m_cell_eta_raw;
    		m_cells_phi_raw[m_cell_identifier] = m_cell_phi_raw;
    		m_cells_phi[m_cell_identifier] = m_cell_phi;
    		m_cells_r_raw[m_cell_identifier] = m_cell_r_raw;

    		m_cell_coordinates[m_cell_layer].push_back(std::make_pair(m_cell_eta_raw, m_cell_phi_raw));
    		m_cell_identifiers[m_cell_layer].push_back(m_cell_identifier);
    	}

	std::cout << "Number of cells in layer 2 is: " << m_cell_coordinates[2].size() << "\n";

	std::cout << "Coordinates loaded\n";
	geoFile->Close();
	// Close Geo tree
	// /////////////////////////////////
	// Setup getDDE method to obtain impact cell ID
	// // Load geo file
	CaloGeometryFromFile* geo = new CaloGeometryFromFile();
	geo->LoadGeometryFromFile("/eos/atlas/atlascerngroupdisk/proj-simul/CaloGeometry/ATLAS-R2-2016-01-00-01.root","ATLAS-R2-2016-01-00-01");	
	////////////////////////////////////
        // Open muon TTree

	TFile *muFile = new TFile(input_file);

	// TFile *muFile = new TFile("/eos/atlas/atlascerngroupdisk/proj-simul/InputSamplesRun3_test/pid13_E100000_disj_eta_m25_m20_20_25_rel62/calohits.root");
	TTree *muTree = (TTree*)muFile->Get("FCS_ParametrizationInput");
	std::cout << "Opening Muon evetns file and Tree\n";
	// why is this needed?
	gInterpreter->GenerateDictionary("vector<vector<float> >", "vector");
	// define variable types
	// TruthE    : vector<float>
	std::vector<float> *truth_e = nullptr;
	//std::vector<int> *truth_pdg = nullptr;
	std::vector<std::vector<float>> *m_TTC_mid_eta = nullptr;	
	std::vector<std::vector<float>> *m_TTC_mid_phi = nullptr;
	FCS_matchedcellvector *m_Sampling_0 = 0;
	FCS_matchedcellvector *m_Sampling_1 = 0;
	FCS_matchedcellvector *m_Sampling_2 = 0;
	FCS_matchedcellvector *m_Sampling_3 = 0;
	FCS_matchedcellvector *m_Sampling_4 = 0;
	FCS_matchedcellvector *m_Sampling_5 = 0;
	FCS_matchedcellvector *m_Sampling_6 = 0;
	FCS_matchedcellvector *m_Sampling_7 = 0;
	// Set branch addresses
	std::cout << "Assigning BrachAddresses for Muon Tree. \n";
	muTree->SetBranchAddress("TruthE", &truth_e);
	//muTree->SetBranchAddress("TruthPDG", &truth_pdg); 
	muTree->SetBranchAddress("newTTC_mid_eta", &m_TTC_mid_eta);					
	muTree->SetBranchAddress("newTTC_mid_phi", &m_TTC_mid_phi);
	muTree->SetBranchAddress("Sampling_0", &m_Sampling_0);	
	muTree->SetBranchAddress("Sampling_1", &m_Sampling_1);		
	muTree->SetBranchAddress("Sampling_2", &m_Sampling_2);		
	muTree->SetBranchAddress("Sampling_3", &m_Sampling_3);		
	muTree->SetBranchAddress("Sampling_4", &m_Sampling_4);		
	muTree->SetBranchAddress("Sampling_5", &m_Sampling_5);		
	muTree->SetBranchAddress("Sampling_6", &m_Sampling_6);		
	muTree->SetBranchAddress("Sampling_7", &m_Sampling_7);		

	// vector of ptrs to FCS... ptrs
	std::vector<FCS_matchedcellvector*> layerlist; // list of layer ptrs we care about
	layerlist.push_back(m_Sampling_0); // populate layerlist		
	layerlist.push_back(m_Sampling_1);			
	layerlist.push_back(m_Sampling_2);			
	layerlist.push_back(m_Sampling_3);			
	layerlist.push_back(m_Sampling_4);			
	layerlist.push_back(m_Sampling_5);			
	layerlist.push_back(m_Sampling_6);			
	layerlist.push_back(m_Sampling_7);		

	std::cout << "Creating Output root file \n";
	std::cout << output_name << "\n";	
	TFile *outFile = new TFile(output_name, "RECREATE");
	// create a folder in output root file for each layer
	int nlayers = layerlist.size();
	for (int layer = 0; layer < nlayers; layer++)
	{
		std::string lyr = "Layer_";
		std::string dir_title = lyr.append(std::to_string(layer));
		outFile->mkdir(dir_title.c_str(), dir_title.c_str());
	}

	// list of TProfile objects in eta bins for layers
	std::vector<TProfile*> bins;	
	int nbins = 64; // bins: bins[0] = 0.0 - 0.05, bins[1] = 0.05 - 0.1, ...
	float etastp = 3.2 / nbins;
	for (int b = 0; b < nbins; b++)
	{
	
		// prof obj for layer
		std::string plot_title = std::to_string(b*etastp);
		plot_title.append("-");
		plot_title.append(std::to_string((b+1)*etastp));
		TProfile *m_profile = new TProfile(plot_title.c_str(), plot_title.c_str(),30,0,0.03);	

		// set TProfile plot style here
		m_profile->GetXaxis()->SetTitle("phi_mod");
		m_profile->GetYaxis()->SetTitle("E [Mev]");
		m_profile->SetMarkerStyle(7);
		bins.push_back(m_profile);
	}

	// get number of muon entries in TTree
	int nentries = muTree->GetEntries();
	for (int layer = 2; layer < 3; layer++)
	{ 	
		// Phi granularity of detector depends on Layer # and eta values
		
		float gran; 
		if (layer == 0 or layer == 4)
		{
			gran = 256.;
		}
		else if (layer >= 1 and layer <= 3)
		{	
			gran = 512.;
		} 
		else // layers 5,6,7
		{
			gran = 128.;
		}

		// Adjust x axis of bins profiles depending on granularity
		for (int b = 0; b < nbins; b++)
		{
			// special case if layers 5,6,7 and eta < 2.5 then gran * 3
			// note: eta < 2.5 ==> b < 50	
			if (b < 50 and layer >= 5 and layer <= 7)
			{
				bins[b]->SetBins(30, 0, TMath::Pi()/(3*gran));
			}
			else
			{
				bins[b]->SetBins(30, 0, TMath::Pi()/gran);
			}	
		}
	
		for (int nmu = 0; nmu < nentries; nmu++)
		{		

			muTree->GetEntry(nmu);

			/*
			if (nmu % 1000 == 0)
			{
				std::cout << "Processing muon entry # " + std::to_string(nmu) + "\n";	
				//std::cout << "... number of particles: " + std::to_string(truth_pdg->size()) + "\n";
			}
			*/
			if (truth_e->back() < e_cut)
			{
				continue;
			}

			// get layer energy, eta, phi
			float layer_energy = getTotalHitEnergy(layerlist[layer]);
			float eta = (*m_TTC_mid_eta)[0][layer]; // access 0 for some reason
			float phi = (*m_TTC_mid_phi)[0][layer];
			// get phi_correction	
			// get impact cell by using getDDE method
			const CaloDetDescrElement* impactCell;
			// (layer, eta, phi, float* dist)
			// if particle inside cell dist < 0 and if particle outside dist > 0
			float* dist;
			int* stps;
			float zero = 0;
			int one = 1;
			dist = &(zero);
			stps = &(one);
			impactCell = geo->getDDE(layer, eta, phi, dist, stps);
			// veto events with dist > 0 as they are outside closest cell => outside layer
			if ( (dist != nullptr) and (*dist > 0) )
			{
				 continue;
			}

			float impactCellPhi = impactCell->phi();

			float m_phi_mod = std::fmod(std::fabs(phi - impactCellPhi),TMath::Pi()/gran);
			//std::cout << "...|...Filling point to plot\n";
			// std::cout << "eta: " << eta << "\n";
			// std::cout << "index: " << static_cast<int>(eta / 0.05) << "\n";
			
			// Optimize the range of x axis to correspond to the gran in use
			// i.e phi_mode in 0.0 to TMath::Pi()/gran
			// And keep number of bins fixed to 30
			bins[std::fabs(static_cast<int>(eta / etastp))]->Fill(m_phi_mod, layer_energy);
		}

		// Write eta bin hists for this layer	
		std::cout << "Writing plots for layer " + std::to_string(layer) + "\n";
		std::string lyr = "Layer_";
		std::string dir_title = lyr.append(std::to_string(layer));
		outFile->cd(dir_title.c_str());
		for (int b = 0; b < nbins; b++)
		{
			bins[b]->Write();
			bins[b]->Reset(); // after writing out for layer, reset for next layer
		}	

	}

	std::cout << "Closing root files.\n";
	outFile->Close();
	muFile->Close();	

	end_time = time(NULL);

	std::cout << "Total Run time for " << nentries << "muon events: " << (end_time - start_time) << "sec.\n";

	return 0;
}
