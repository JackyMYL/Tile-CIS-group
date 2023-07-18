#include <iostream>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>

#include "TROOT.h"
#include "TTree.h"
#include "TStyle.h"
#include "TFile.h"
#include "TMath.h"
#include "TTimeStamp.h"
#include "TDatime.h"
#include "TCanvas.h"
#include "TVirtualPad.h"
#include "TPaveStats.h"
#include "TFrame.h"
#include "TGraph.h"
#include "TGraphErrors.h"
#include "TGraphAsymmErrors.h"
#include "TMultiGraph.h"
#include "TLegend.h"
#include "TLatex.h"
#include "TLine.h"
#include "TPad.h"
#include "TBox.h"
#include "TH1.h"
#include "TH2.h"
#include "TF1.h"
#include "TMap.h"

// LBA 14 is in index 13


void plot(int run, int partition, int module, int channel, int gain){
	std::cout << "Run #" << run <<'\n';
	TString filename;
	filename = filename.Format("tileCalibCIS_%d_CIS.0.root",run);
	filename = TString("/afs/cern.ch/user/t/tilecali/public/w0/ntuples/cis/") + filename;
	TFile *file = TFile::Open(filename,"READ");
	TMap * cisScans = (TMap *)file->FindObjectAny("cisScans");
	if (!cisScans) {
		delete file;
		std::cout << "No CIS scan :(\n";
	} else {
		std::cout << "CIS scan found\n";
		const char* str_part[5] = {"AUX", "LBA", "LBC", "EBA", "EBC"};
		// 1=LBA, 2=LBC, 3=EBA, 4=EBC
		const char* str_gain[2] = {"lowgain", "highgain"};
		TString chan;
		chan=chan.Format("%s%02d_c%02d_%s",str_part[partition],module,channel,str_gain[gain]);
		std::cout << chan << '\n';
		TString name;
		name = name.Format("scan%d_%d_%d_%d",partition, module-1, channel, gain);
		TPair *obj = ((TPair *)(cisScans->FindObject(name)));
		if (!obj) {
			std::cout << "Ch not found :(\n";
		} else {
			std::cout << "Ch found!\n";
			TString title;
			title=title.Format("Run %d: %s",run,(const char *)chan);
			TCanvas * c1 = 0;
			c1 = new TCanvas(name,title);
			TGraphErrors * gr = ((TGraphErrors *)(obj->Value()));
			//gr->Print();
			gr->SetTitle(title);
			gr->SetMarkerStyle(20);
			gr->SetMarkerSize(1);
			double ymax = 1100;
			double xmax = 0;
			gr->SetMinimum(0.);
			gr->SetMaximum(ymax);
			if(gain == 0) xmax = 900; 	// for lowgain channels
			else xmax = 14; 						// for highgain channels
			TVirtualPad *p1=c1->cd(1);
			gr->Draw("A");
			gr->Draw("APL");
			gr->GetXaxis()->SetTitle("Injected Charge (pC)");
			gr->GetXaxis()->CenterTitle();
			gr->GetYaxis()->SetTitle("ADC Counts");
			gr->GetYaxis()->CenterTitle("ADC Counts");
			p1->Update();
			c1->Flush();
			c1->ForceUpdate();
			c1->Update();
			filename = name.Format("%s_%d.png",(const char *)chan,run);
			c1->SaveAs(filename);
		}
		delete cisScans;
	}
	delete file;
}



void plot_all_runs(int partition, int module, int channel, int gain){
	std::cout << "I am begging u\n";
	//int runs[]{416626, 416941, 417164, 417535, 417882, 418169, 418412, 418778, 418994, 419504}; //April 4
	//int runs[]{413287, 413579, 413594, 413976, 414257, 414464, 414513, 414763, 415169, 415434, 415531, 415564, 415914, 416099}; // March 3
	//int runs[]{410258, 410544, 410878, 411022, 411075, 412210, 412416, 412439, 412491, 412637}; //Feb 2
	//int runs[]{410258, 410544, 410878, 411022, 411075, 411839, 411976, 412108, 412210, 412416, 412439, 412491, 412637, 413287, 413579, 413594, 413976, 414257, 414464, 414513, 414763, 415169, 415434, 415531, 415564, 415914, 416099};
	// std::vector<int> runs = {419864, 420384, 420709, 421222, 421606, 422100, 422198, 422233, 422268, 422529, 422767, 423123, 423287}; //May
	std::vector<int> runs = {454529, 454849, 455243, 455563};
	for (unsigned int i=0; i<runs.size(); ++i){
		plot(runs[i], partition, module, channel, gain);
	}
}
