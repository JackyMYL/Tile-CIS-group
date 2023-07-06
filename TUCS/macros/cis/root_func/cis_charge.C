#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>
#include <iostream>
#include <cstdio>
#include <list>

#include "Riostream.h"
#include "TROOT.h"
#include "TTree.h"
#include "TStyle.h"
#include "TString.h"
#include "TLatex.h"
#include "TFile.h"
#include "TCanvas.h"
#include "TVirtualPad.h"

void labels(int run, const char *type, const char *text){

  TString name;
  name.Form("%s run %d",type,run);

  TLatex l1;
  l1.SetTextColor(2);
  l1.SetTextSize(0.06);
  l1.DrawTextNDC(0.13,0.83,name);
  l1.DrawTextNDC(0.13,0.75,text);
}

// to plot amp/DAC vs event number for low gain default parameters can be used
// cis_charge(RUN_NUMBER)

// to plot ratio just for one module (INDEX from 0 to 63 and _MXX from _M01 to _M64)
// cis_charge(RUN_NUMBER,"eFit_lo[%d][INDEX][]/cispar[6]:Evt","cispar[7]==100 && cispar[6]>15 && eFit_lo[%d][INDEX][]>10","_MXX")

// to plot ratio vs DAC removing outliers:
// cis_charge(RUN_NUMBER,"eFit_lo[%d][][]/cispar[6]:cispar[6]","cispar[7]==100 && cispar[6]>15 && abs(eFit_lo[%d][][]/cispar[6]-1.024)<0.64","_DAC")

// to plot ratio for HG removing under/overflow:
// cis_charge(RUN_NUMBER,"eFit_hi[%d][][]/cispar[6]:Evt","cispar[7]==5 && cispar[6]>1 && Evt<1000 && abs(eFit_hi[%d][][]-480)<470","_hg")


void cis_charge_new(int run, const char *var=NULL, const char *cut=NULL, const char *suff="", const char* style="", int nvars = 1) {

  int logY=0;
  const char * type="CIS";

  const char * part[4] = {"LBA","LBC","EBA","EBC"};
  const char * input="/eos/atlas/atlascerngroupdisk/det-tile/2022";
  const char * output=".";

  if (!var) var = "eFit_lo[%d][][]/cispar[6]:Evt";
  if (!cut) cut = "cispar[7]==100 && cispar[6]>15 && eFit_lo[%d][][]>10";

  TString fname;
  fname.Form("%s/tile_%6.6d_%s.0.aan.root", input,run,type);
  std::cout << "\nRun " << run << std::endl;

  TFile fff(fname,"READ");
  TTree * h2000 = (TTree *)fff.Get("h2000");

  gStyle->SetStatH(0.4);
  gStyle->SetStatW(0.4);
  gStyle->SetOptStat(1100);

  TCanvas * c1 = new TCanvas();
  c1->Divide(2,2);
  TVirtualPad * p;
  TString v,c,t;

  for (int i=0; i<4; ++i) {
    p = c1->cd(i+1);
    p->SetLogy(logY);
    if (nvars == 2){
      v.Form(var, i, i);
    }else{
      v.Form(var,i);
    }
    c.Form(cut,i);
    h2000->Draw(v,c,style);
    t.Form("%s%s",part[i],suff);
    labels(run,type,t);
  }

  if (logY)
    fname.Form("%s/%s_charge_run_%6.6d%s_logy.png", output,type,run,suff);
  else
    fname.Form("%s/%s_charge_run_%6.6d%s.png", output,type,run,suff);

  c1->SaveAs(fname);


}

void cis_plot_frame(int run, const char* str_var, const char* str_cut, const char* str_name, int module=2, int chan=10, const char * xval = 0, const char* style = "", int nvars = 1)
{

  TString var,cut,nam,ind,mod,xxx("Evt");

  if (module>=1 && module <=64) { // module number starts from 1
    if (chan>=0 && chan<=47) {    // channel number starts from 0
      ind.Form("%s[%d][%d]","[%d]",module-1,chan);
      mod.Form("_M%2.2d_ch%2.2d",module,chan);
    } else {
      ind.Form("%s[%d][]","[%d]",module-1);
      mod.Form("_M%2.2d",module);
    }
  } else {
    if (chan>=0 && chan<=47) {    // channel number starts from 0
      ind.Form("%s[][%d]","[%d]",chan);
      mod.Form("_ch%2.2d",chan);
    } else {
      ind.Form("%s[][]","[%d]"); // [%d] here for partition number, will be replaced by 0,1,2,3
      mod.Form("");
    }
  }
  if (xval && xval[0]!=0) {
    xxx.Form("%s",xval);
    mod+=TString("_")+xxx;
    mod.ReplaceAll("[","_");
    mod.ReplaceAll("]","");
  }

  if(nvars == 2){
    var.Form(str_var,(const char *)ind, (const char *)ind);
    cut.Form(str_cut,(const char *)ind);
  }else{
    var.Form(str_var,(const char *)ind);
    cut.Form(str_cut);
  }
  nam.Form(str_name,(const char *)mod);
  cis_charge_new(run,(const char *)var,(const char *)cut,(const char *)nam,(const char *)style, nvars);
}


void cis_timing(int run, int module=2, int chan=2, const char * xval = 0)
{
  const char* var_lo = "tFit_lo%s";
  const char* cut_lo = "cispar[7]==100 && 374 < cispar[6] && cispar[6] < 875";
  const char* name_lo = "%s_LG_timing";
  cis_plot_frame(run, var_lo, cut_lo, name_lo, module, chan, xval);
  const char* var_hi = "tFit_hi%s";
  const char* cut_hi = "cispar[7]==100 && 3 < cispar[6] && cispar[6] < 13";
  const char* name_hi = "%s_HG_timing";
  cis_plot_frame(run, var_hi, cut_hi, name_hi, module, chan, xval);
}

void cis_ampq(int run, int module=2, int chan=2, const char * xval = 0)
{
  const char* var_lo = "eFit_lo%s/cispar[6]:cispar[6]";
  const char* cut_lo = "cispar[7]==100 && 374 < cispar[6] && cispar[6] < 875 && eFit_lo%s > 6";
  // if lowgain amplitude is under 6, it's ignored in CIS calculations.
  const char* name_lo = "%s_LG_AmpQ";
  cis_plot_frame(run, var_lo, cut_lo, name_lo, module, chan, xval, "BOX", 2);
  const char* var_hi = "eFit_hi%s/cispar[6]:cispar[6]";
  const char* cut_hi = "cispar[7]==100 && 3 < cispar[6] && cispar[6] < 13 && eFit_hi%s > 40";
  // if highgain amplitude is under 40, it's ignored in CIS calculations.
  const char* name_hi = "%s_HG_AmpQ";
  cis_plot_frame(run, var_hi, cut_hi, name_hi, module, chan, xval, "BOX", 2);
}


void cis_pulses(int run, int module=2, int chan=10, const char * xval = 0)
{
  const char* var_lo ="sample_lo%s[3]-sample_lo%s[0]:EvtNr";
  const char* cut_lo = "sample_lo%s[3]<100";
  const char* name_lo = "%s_LG_EvtNr";
  cis_plot_frame(run, var_lo, cut_lo, name_lo, module, chan, xval, "COLZ", 2);
}


void check_run(int run){
  cis_timing(run);
  cis_ampq(run);
}

void check_all_runs(){
  //int runs[]{413287, 413579, 413594, 413976, 414257, 414464, 414513, 414763, 415169, 415434, 415531, 415564, 415914, 416099};
  //std::vector<int> runs = {423827, 424146, 424508, 424613, 424692, 424735, 425003, 425008, 425064, 425175, 425480, 425569, 425758, 426076, 426084, 426286, 426330, 426571, 426701};
  //std::vector<int> runs = {423827, 424146, 424508, 424613, 424692, 424735, 425003, 425008, 425064, 425175, 425480, 425569, 425758, 426076, 426084, 426286, 426330, 426571, 426701, 426816};
  std::vector<int> runs = {426084, 426286, 426330, 426571, 426701, 426816, 426939, 426968, 427100, 427157, 427250, 427419, 427775, 427899, 427932, 427941};
  for (unsigned int i=0; i<runs.size(); ++i){
    check_run(runs[i]);
  }
}

void check_all_timing(){
  std::vector<int> runs = {423827, 424146, 424508, 424613, 424692, 424735, 425003, 425008, 425064, 425175, 425480, 425569, 425758, 426076, 426084, 426286, 426330, 426571, 426701};
  for (unsigned int i=0; i<runs.size(); ++i){
    cis_timing(runs[i]);
  }
}

void check_all_ampq(){
  std::vector<int> runs = {423827, 424146, 424508, 424613, 424692, 424735, 425003, 425008, 425064, 425175, 425480, 425569, 425758, 426076, 426084, 426286, 426330, 426571, 426701};
  for (unsigned int i=0; i<runs.size(); ++i){
    cis_ampq(runs[i]);
  }
}

void check_all_pulses(){
  std::vector<int> runs = {423827, 424146, 424508, 424613, 424692, 424735, 425003, 425008, 425064, 425175, 425480, 425569, 425758, 426076, 426084, 426286, 426330, 426571, 426701};
  for (unsigned int i=0; i<runs.size(); ++i){
    cis_pulses(runs[i], 52);
  }
}
