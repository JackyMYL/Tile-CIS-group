///------------------------------------------------------
///  Arely Cortes Gonzalez
///  CERN. July 18th, 2016
///
///  Do basic checks on laser output list!
///------------------------------------------------------

#include "TTree.h"
#include "TFile.h"
#include "TRandom.h"
#include "TMath.h"
#include <iostream>
#include <iomanip>

#include <string.h>
#include "TROOT.h"
#include "TChain.h"
#include "TH1.h"
#include "TKey.h"
#include "Riostream.h"
#include <vector>


//---------------------------------------
//enums
//---------------------------------------
namespace laser{
   enum laser{
       diffConst_LastLas    = 0,
       diffHV_LastLas       = 1,
       laserConstant        = 2,
       noInstrumented       = 3,
       noUpdate_Cs          = 4,
       Update_HVLas         = 5,
       masked_LG            = 6,
       masked_HG            = 7,
       masked_BothG         = 8

   };
}

namespace Part{
    enum Part{
        partEBA = 0,
        partLBA = 1,
        partLBC = 2,
        partEBC = 3
    };
}

TH2F *EBA[9];
TH2F *LBA[9];
TH2F *LBC[9];
TH2F *EBC[9];

TH1F *LBA_1d[3];
TH1F *LBC_1d[3];
TH1F *EBA_1d[3];
TH1F *EBC_1d[3];
TH1F *TILE_1d[3];


//Reading files
double LastLas_constant[4][64][48];
double LastLas_HV[4][64][48];
double ThisLas_constant[4][64][48];
double ThisLas_HV[4][64][48];

double MaskedCh_LG[4][64][48];
double MaskedCh_HG[4][64][48];

ifstream f_LastLaser;
ifstream f_ThisLaser;
ifstream f_Masked;

double max_Constants = 1.02;
double min_Constants = 0.96;
double max_diffConst_LastLas = 1.0; //7%
double min_diffConst_LastLas = -4.0; //-5%
double max_diffHV_LastLas = 1.5;

//---------------------------------------
// Special channels
// Only in EB!!
//---------------------------------------
bool isSpecialChannel(string &chType, string s_part, int s_mod, int s_ch)
{
    if (s_part == "LBA" || s_part == "LBC"){
        chType = "[Regular]";
        return false;
    }
    
    //uninstrumented (shouldn't even be considered)
    if ((s_part == "EBA") && (s_mod==15) && (s_ch==0 || s_ch==1 || s_ch==2 || s_ch==3)) {
        chType = "[Uninstrumented in EBA]";
        return true;
    }
    //uninstrumented (shouldn't even be considered)
    if ((s_part == "EBC") && (s_mod==18) && (s_ch==0 || s_ch==1 || s_ch==2 || s_ch==3)) {
        chType = "[Uninstrumented in EBC]";
        return true;
    }
    //C10 or special merged
    if ( (s_ch==5) && ( (s_mod>=39&&s_mod<=42) || (s_mod>=55&&s_mod<=58) ) ) {
        chType = "[C10 or merged]";
        return true;
    }
    //MBTS inner
    if ( (s_ch==4) && ( (s_mod>=39&&s_mod<=42) || (s_mod>=55&&s_mod<=58) ) ) {
        chType = "[MBTS inner]";
        return true;
    }
    //MBTS outer
    if ( (s_ch==12) && (s_mod==3 || s_mod==8 || s_mod==24 || s_mod==43 || s_mod==63 || s_mod==54 || s_mod==59 ) ) {
        chType = "[MBTS outer]";
        return true;
    }
    //MBTS outer
    if ( (s_ch==12) && (s_mod==20) && (s_part == "EBA") ) {
        chType = "[MBTS outer]";
        return true;
    }
    //MBTS outer
    if ( (s_ch==12) && (s_mod==19) && (s_part == "EBC") ) {
        chType = "[MBTS outer]";
        return true;
    }
    //E4'
    if ( (s_ch==12) && (s_mod==29 || s_mod==32 || s_mod==34 || s_mod==37 ) ) {
        chType = "[E4']";
        return true;
    }
    //E1
    if (s_ch==12) {
        chType = "[E1]";
        return true;
    }
    //E2
    if (s_ch==13) {
        chType = "[E2]";
        return true;
    }
    //E3
    if (s_ch==0) {
        chType = "[E3]";
        return true;
    }
    //E4
    if (s_ch==1) {
        chType = "[E4]";
        return true;
    }
    chType = "[Regular]";
    return false;
}
bool isSpecialChannel(string &chType, int s_mod, int s_ch)//can be used only for EB!!!
{
    //C10 or special merged
    if ( (s_ch==5) && ( (s_mod>=39&&s_mod<=42) || (s_mod>=55&&s_mod<=58) ) ) {
        chType = "[C10 or merged]";
        return true;
    }
    //MBTS inner
    if ( (s_ch==4) && ( (s_mod>=39&&s_mod<=42) || (s_mod>=55&&s_mod<=58) ) ) {
        chType = "[MBTS inner]";
        return true;
    }
    //MBTS outer
    if ( (s_ch==12) && (s_mod==3 || s_mod==8 || s_mod==24 || s_mod==43 || s_mod==63 || s_mod==54 || s_mod==59 ) ) {
        chType = "[MBTS outer]";
        return true;
    }
    //E4'
    if ( (s_ch==12) && (s_mod==29 || s_mod==32 || s_mod==34 || s_mod==37 ) ) {
        chType = "[E4']";
        return true;
    }
    //E1
    if (s_ch==12) {
        chType = "[E1]";
        return true;
    }
    //E2
    if (s_ch==13) {
        chType = "[E2]";
        return true;
    }
    //E3
    if (s_ch==0) {
        chType = "[E3]";
        return true;
    }
    //E4
    if (s_ch==1) {
        chType = "[E4]";
        return true;
    }
    
    chType = "[Regular]";
    return false;
}
string isSpecialChannel(int s_mod, int s_ch)//can be used only for EB!!!
{
    //C10 or special merged
    if ( (s_ch==5) && ( (s_mod>=39&&s_mod<=42) || (s_mod>=55&&s_mod<=58) ) ) {
        return "[C10 or merged]";
    }
    //MBTS inner
    if ( (s_ch==4) && ( (s_mod>=39&&s_mod<=42) || (s_mod>=55&&s_mod<=58) ) ) {
        return "[MBTS inner]";
    }
    //MBTS outer
    if ( (s_ch==12) && (s_mod==3 || s_mod==8 || s_mod==24 || s_mod==43 || s_mod==63 || s_mod==54 || s_mod==59 ) ) {
        return "[MBTS outer]";
    }
    //E4'
    if ( (s_ch==12) && (s_mod==29 || s_mod==32 || s_mod==34 || s_mod==37 ) ) {
        return "[E4']";
    }
    //E1
    if (s_ch==12) {
        return "[E1]";
    }
    //E2
    if (s_ch==13) {
        return "[E2]";
    }
    //E3
    if (s_ch==0) {
        return "[E3]";
    }
    //E4
    if (s_ch==1) {
        return "[E4]";
    }
    
    return "[Regular]";
}


void printOutliers(TH2F *h2D, TH2F *h2D_diff, float _max_, float _min_, string s_part)
{
    h2D_diff->Reset();
    h2D_diff->SetMarkerSize(0.75);
    h2D_diff->SetMarkerColor(kBlue+1);
    //Scan the histogram
    for (int mm = 1; mm<64+1; ++mm)
    {
        for (int cc = 1; cc<48+1; ++cc)
        {
            if (h2D->GetBinContent(mm, cc) == -1000.) continue;
            
            if (h2D->GetBinContent(mm, cc) > _max_) {
                h2D_diff->SetBinContent(mm, cc, h2D->GetBinContent(mm, cc));
                cout << ((string)h2D->GetName()).substr (0,3) << "\tmod: " << mm << "\tch: " << cc-1 << "\tvalue: " << h2D->GetBinContent(mm, cc)
                << "\t";
                if (s_part == "LBA" || s_part == "LBC")cout << "[Regular]";
                else cout << isSpecialChannel(mm, cc-1);
                if (s_part=="EBA" && EBA[laser::masked_BothG]->GetBinContent(mm,cc)>0) cout << " Masked!";
                if (s_part=="EBC" && EBC[laser::masked_BothG]->GetBinContent(mm,cc)>0) cout << " Masked!";
                if (s_part=="LBA" && LBA[laser::masked_BothG]->GetBinContent(mm,cc)>0) cout << " Masked!";
                if (s_part=="LBC" && LBC[laser::masked_BothG]->GetBinContent(mm,cc)>0) cout << " Masked!";
                cout << endl;
            }
            if (h2D->GetBinContent(mm, cc) < _min_) {
                h2D_diff->SetBinContent(mm, cc, h2D->GetBinContent(mm, cc));
                cout << ((string)h2D->GetName()).substr (0,3) << " \tmod: " << mm << "\tch: " << cc-1 << "\tvalue: " << h2D->GetBinContent(mm, cc)
                << "\t";
                if (s_part == "LBA" || s_part == "LBC")cout << "[Regular]";
                else cout << isSpecialChannel(mm, cc-1);
                if (s_part=="EBA" && EBA[laser::masked_BothG]->GetBinContent(mm,cc)>0) cout << " Masked!";
                if (s_part=="EBC" && EBC[laser::masked_BothG]->GetBinContent(mm,cc)>0) cout << " Masked!";
                if (s_part=="LBA" && LBA[laser::masked_BothG]->GetBinContent(mm,cc)>0) cout << " Masked!";
                if (s_part=="LBC" && LBC[laser::masked_BothG]->GetBinContent(mm,cc)>0) cout << " Masked!";
                cout << endl;
            }
        }
    }
    
    
}

void separatePartMod(string &tmp_part, int &tmp_module)
{
  
    //cout << "INFO::separatePartMod tmp_part " << tmp_part << endl;
    stringstream tmp_part_stream(tmp_part.substr(3,2));
    tmp_part_stream >> tmp_module;
    tmp_part = tmp_part.substr(0,3);
}

void doChecksDiff(bool doPrintOutliers=true)
{
    //assuming files are named: new_db.txt and Laser_DB.txt
    bool debugging = false;
    if (!debugging) gErrorIgnoreLevel = kWarning;
    
    //-------- create the histograms
    EBA[laser::masked_LG]        = new TH2F("EBA_maskedLG",          "EBA [LG masked];Module;Channel",                      64, 0.5, 64.5, 48, -0.5, 47.5);
    EBA[laser::masked_HG]        = new TH2F("EBA_maskedHG",          "EBA [HG masked];Module;Channel",                      64, 0.5, 64.5, 48, -0.5, 47.5);
    EBA[laser::masked_BothG]     = new TH2F("EBA_maskedBothG",       "EBA [Both gains masked];Module;Channel",              64, 0.5, 64.5, 48, -0.5, 47.5);
    EBA[laser::noInstrumented]   = new TH2F("EBA_notInstrumented",   "EBA [not instrumented];Module;Channel",               64, 0.5, 64.5, 48, -0.5, 47.5);
    EBA[laser::noUpdate_Cs]      = new TH2F("EBA_noUpdate_Cs",       "EBA [no update since Cs can];Module;Channel",         64, 0.5, 64.5, 48, -0.5, 47.5);
    EBA[laser::Update_HVLas]     = new TH2F("EBA_Update_HVLas",      "EBA [new update since last Laser];Module;Channel",    64, 0.5, 64.5, 48, -0.5, 47.5);
    EBA[laser::diffConst_LastLas]= new TH2F("EBA_diffConst_LastLas", "EBA [Change of constant wrt last update];Module;Channel",64, 0.5, 64.5, 48, -0.5, 47.5);
    EBA[laser::diffHV_LastLas]   = new TH2F("EBA_diffHV_LastLas",    "EBA [Change of HV wrt last update];Module;Channel",   64, 0.5, 64.5, 48, -0.5, 47.5);
    EBA[laser::laserConstant]    = new TH2F("EBA_laserConstant",     "EBA [Laser constants];Module;Channel",                64, 0.5, 64.5, 48, -0.5, 47.5);

    EBA_1d[laser::diffConst_LastLas]= new TH1F("EBA_diffConst_LastLas", "EBA [Change of constant wrt last update];(C_{laser}^{new}-C_{laser}^{old})/C_{laser}^{old} [%]; ",  100,-20.,20.);
    EBA_1d[laser::diffHV_LastLas]   = new TH1F("EBA_diffHV_LastLas",    "EBA [Change of HV wrt last update];(HV^{new}-HV^{old})/HV^{old} [%]; ", 100,-5.,5.);
    EBA_1d[laser::laserConstant]    = new TH1F("EBA_laserConstant",     "EBA [Laser constants];Laser constant;",             100,0.5,1.5);
    
    LBA[laser::masked_LG]        = new TH2F("LBA_maskedLG",          "LBA [LG masked];Module;Channel",                      64, 0.5, 64.5, 48, -0.5, 47.5);
    LBA[laser::masked_HG]        = new TH2F("LBA_maskedHG",          "LBA [HG masked];Module;Channel",                      64, 0.5, 64.5, 48, -0.5, 47.5);
    LBA[laser::masked_BothG]     = new TH2F("LBA_maskedBothG",       "LBA [Both gains masked];Module;Channel",              64, 0.5, 64.5, 48, -0.5, 47.5);
    LBA[laser::noInstrumented]   = new TH2F("LBA_notInstrumented",   "LBA [not instrumented];Module;Channel",               64, 0.5, 64.5, 48, -0.5, 47.5);
    LBA[laser::noUpdate_Cs]      = new TH2F("LBA_noUpdate_Cs",       "LBA [no update since Cs can];Module;Channel",         64, 0.5, 64.5, 48, -0.5, 47.5);
    LBA[laser::Update_HVLas]     = new TH2F("LBA_Update_HVLas",      "LBA [new update since last Laser];Module;Channel",    64, 0.5, 64.5, 48, -0.5, 47.5);
    LBA[laser::diffConst_LastLas]= new TH2F("LBA_diffConst_LastLas", "LBA [Change of constant wrt last update];Module;Channel",64, 0.5, 64.5, 48, -0.5, 47.5);
    LBA[laser::diffHV_LastLas]   = new TH2F("LBA_diffHV_LastLas",    "LBA [Change of HV wrt last update];Module;Channel",   64, 0.5, 64.5, 48, -0.5, 47.5);
    LBA[laser::laserConstant]    = new TH2F("LBA_laserConstant",     "LBA [Laser constants];Module;Channel",                64, 0.5, 64.5, 48, -0.5, 47.5);
   
    LBA_1d[laser::diffConst_LastLas]= new TH1F("LBA_diffConst_LastLas", "LBA [Change of constant wrt last update];(C_{laser}^{new}-C_{laser}^{old})/C_{laser}^{old} [%]; ",  100,-20.,20.);
    LBA_1d[laser::diffHV_LastLas]   = new TH1F("LBA_diffHV_LastLas",    "LBA [Change of HV wrt last update];(HV^{new}-HV^{old})/HV^{old} [%]; ", 100,-5.,5.);
    LBA_1d[laser::laserConstant]    = new TH1F("LBA_laserConstant",     "LBA [Laser constant];Laser constant;",             100,0.5,1.5);

    EBC[laser::masked_LG]        = new TH2F("EBC_maskedLG",          "EBC [LG masked];Module;Channel",                      64, 0.5, 64.5, 48, -0.5, 47.5);
    EBC[laser::masked_HG]        = new TH2F("EBC_maskedHG",          "EBC [HG masked];Module;Channel",                      64, 0.5, 64.5, 48, -0.5, 47.5);
    EBC[laser::masked_BothG]     = new TH2F("EBC_maskedBothG",       "EBC [Both gains masked];Module;Channel",              64, 0.5, 64.5, 48, -0.5, 47.5);
    EBC[laser::noInstrumented]   = new TH2F("EBC_notInstrumented",   "EBC [not instrumented];Module;Channel",               64, 0.5, 64.5, 48, -0.5, 47.5);
    EBC[laser::noUpdate_Cs]      = new TH2F("EBC_noUpdate_Cs",       "EBC [no update since Cs can];Module;Channel",         64, 0.5, 64.5, 48, -0.5, 47.5);
    EBC[laser::Update_HVLas]     = new TH2F("EBC_Update_HVLas",      "EBC [new update since last Laser];Module;Channel",    64, 0.5, 64.5, 48, -0.5, 47.5);
    EBC[laser::diffConst_LastLas]= new TH2F("EBC_diffConst_LastLas", "EBC [Change of constant wrt last update];Module;Channel",64, 0.5, 64.5, 48, -0.5, 47.5);
    EBC[laser::diffHV_LastLas]   = new TH2F("EBC_diffHV_LastLas",    "EBC [Change of HV wrt last update];Module;Channel",   64, 0.5, 64.5, 48, -0.5, 47.5);
    EBC[laser::laserConstant]    = new TH2F("EBC_laserConstant",     "EBC [Laser constants];Module;Channes",                64, 0.5, 64.5, 48, -0.5, 47.5);
    
    EBC_1d[laser::diffConst_LastLas]= new TH1F("EBC_diffConst_LastLas", "EBC [Change of constant wrt last update];(C_{laser}^{new}-C_{laser}^{old})/C_{laser}^{old} [%]; ",  100,-20.,20.);
    EBC_1d[laser::diffHV_LastLas]   = new TH1F("EBC_diffHV_LastLas",    "EBC [Change of HV wrt last update];(HV^{new}-HV^{old})/HV^{old} [%]; ", 100,-5.,5.);
    EBC_1d[laser::laserConstant]    = new TH1F("EBC_laserConstant",     "EBC [Laser constants];Module;Channel",             100,0.5,1.5);

    LBC[laser::masked_LG]        = new TH2F("LBC_maskedLG",          "LBC [LG masked];Module;Channel",                      64, 0.5, 64.5, 48, -0.5, 47.5);
    LBC[laser::masked_HG]        = new TH2F("LBC_maskedHG",          "LBC [HG masked];Module;Channel",                      64, 0.5, 64.5, 48, -0.5, 47.5);
    LBC[laser::masked_BothG]     = new TH2F("LBC_maskedBothG",       "LBC [Both gains masked];Module;Channel",              64, 0.5, 64.5, 48, -0.5, 47.5);
    LBC[laser::noInstrumented]   = new TH2F("LBC_notInstrumented",   "LBC [not instrumented];Module;Channel",               64, 0.5, 64.5, 48, -0.5, 47.5);
    LBC[laser::noUpdate_Cs]      = new TH2F("LBC_noUpdate_Cs",       "LBC [no update since Cs can];Module;Channel",         64, 0.5, 64.5, 48, -0.5, 47.5);
    LBC[laser::Update_HVLas]     = new TH2F("LBC_Update_HVLas",      "LBC [new update since last Laser];Module;Channel",    64, 0.5, 64.5, 48, -0.5, 47.5);
    LBC[laser::diffConst_LastLas]= new TH2F("LBC_diffConst_LastLas", "LBC [Change of constant wrt last update];Module;Channel",64, 0.5, 64.5, 48, -0.5, 47.5);
    LBC[laser::diffHV_LastLas]   = new TH2F("LBC_diffHV_LastLas",    "LBC [Change of HV wrt last update];Module;Channel",   64, 0.5, 64.5, 48, -0.5, 47.5);
    LBC[laser::laserConstant]    = new TH2F("LBC_laserConstant",     "LBC [Laser constants];Module;Channel",                64, 0.5, 64.5, 48, -0.5, 47.5);
    
    LBC_1d[laser::diffConst_LastLas]= new TH1F("LBC_diffConst_LastLas", "LBC [Change of constant wrt last update];(C_{laser}^{new}-C_{laser}^{old})/C_{laser}^{old} [%]; ",  100,-20.,20.);
    LBC_1d[laser::diffHV_LastLas]   = new TH1F("LBC_diffHV_LastLas",    "LBC [Change of HV wrt last update];(HV^{new}-HV^{old})/HV^{old} [%]; ", 100,-5.,5.);
    LBC_1d[laser::laserConstant]    = new TH1F("LBC_laserConstant",     "LBC [Laser constants];Laser constant;",             100,0.5,1.5);

    TILE_1d[laser::diffConst_LastLas]= new TH1F("TILE_diffConst_LastLas", "[Change of constant wrt last update];(C_{laser}^{new}-C_{laser}^{old})/C_{laser}^{old} [%]; ",  100,-20.,20.);
    TILE_1d[laser::diffHV_LastLas]   = new TH1F("TILE_diffHV_LastLas",    "[Change of HV wrt last update];(HV^{new}-HV^{old})/HV^{old} [%]; ", 100,-5.,5.);
    TILE_1d[laser::laserConstant]    = new TH1F("TILE_laserConstant",     "[Laser constants];Laser constant;",             100,0.5,1.5);

    for (int mm = 1; mm<65; ++mm)
    {
        for (int cc = 1; cc < 49; ++cc)
        {
            //EBA[laser::noInstrumented]   ->SetBinContent(mm, cc, -1000.0);
            //EBA[laser::noUpdate_Cs]      ->SetBinContent(mm, cc, -1000.0);
            //EBA[laser::Update_HVLas]     ->SetBinContent(mm, cc, -1000.0);
            EBA[laser::diffConst_LastLas]->SetBinContent(mm, cc, -1000.0);
            EBA[laser::diffHV_LastLas]   ->SetBinContent(mm, cc, -1000.0);
            EBA[laser::laserConstant]    ->SetBinContent(mm, cc, -1000.0);
            
            //LBA[laser::noInstrumented]   ->SetBinContent(mm, cc, -1000.0);
            //LBA[laser::noUpdate_Cs]      ->SetBinContent(mm, cc, -1000.0);
            //LBA[laser::Update_HVLas]     ->SetBinContent(mm, cc, -1000.0);
            LBA[laser::diffConst_LastLas]->SetBinContent(mm, cc, -1000.0);
            LBA[laser::diffHV_LastLas]   ->SetBinContent(mm, cc, -1000.0);
            LBA[laser::laserConstant]    ->SetBinContent(mm, cc, -1000.0);
            
            //EBC[laser::noInstrumented]   ->SetBinContent(mm, cc, -1000.0);
            //EBC[laser::noUpdate_Cs]      ->SetBinContent(mm, cc, -1000.0);
            //EBC[laser::Update_HVLas]     ->SetBinContent(mm, cc, -1000.0);
            EBC[laser::diffConst_LastLas]->SetBinContent(mm, cc, -1000.0);
            EBC[laser::diffHV_LastLas]   ->SetBinContent(mm, cc, -1000.0);
            EBC[laser::laserConstant]    ->SetBinContent(mm, cc, -1000.0);
            
            //LBC[laser::noInstrumented]   ->SetBinContent(mm, cc, -1000.0);
            //LBC[laser::noUpdate_Cs]      ->SetBinContent(mm, cc, -1000.0);
            //LBC[laser::Update_HVLas]     ->SetBinContent(mm, cc, -1000.0);
            LBC[laser::diffConst_LastLas]->SetBinContent(mm, cc, -1000.0);
            LBC[laser::diffHV_LastLas]   ->SetBinContent(mm, cc, -1000.0);
            LBC[laser::laserConstant]    ->SetBinContent(mm, cc, -1000.0);

        }
    }
    
    //-------- read the data
    //EBC64 38 0    1.000000  -1.000000
    string tmp_part;
    int    tmp_module;
    int    tmp_channel;
    int    tmp_zero;
    float  tmp_constant;
    float  tmp_HV;
    int    tmp_gain;

    //--------- masked channels
    f_Masked.open("masked.txt");
    
    if (!f_Masked) {
        std::cout<<"ERROR :: File masked.txt not found.\n"<<endl;
        return;
    } else {
        std::cout << "INFO ::  Reading file: masked.txt\n" << endl;
        while(!f_Masked.eof())
        {
	    f_Masked >> tmp_part;
	    // Filter lines that do not start with module names
	    if (!tmp_part.rfind("LB",0) and !tmp_part.rfind("EB",0)) continue;
            separatePartMod(tmp_part, tmp_module);
            f_Masked >> tmp_channel;
            f_Masked >> tmp_gain;
            
            int myPart_ctr = -1;
            if (tmp_part == "EBA") myPart_ctr = Part::partEBA;
            if (tmp_part == "LBA") myPart_ctr = Part::partLBA;
            if (tmp_part == "LBC") myPart_ctr = Part::partLBC;
            if (tmp_part == "EBC") myPart_ctr = Part::partEBC;
            
            if ( (myPart_ctr <0) || (myPart_ctr>3) )   { cout << "ERROR::Partition Number not correct: " << myPart_ctr << endl; return;}
            if ( (tmp_module <1) || (tmp_module>64) )  { cout << "ERROR::Module Number not correct: " << tmp_module << endl;    return;}
            if ( (tmp_channel <0) || (tmp_channel>47) ){ cout << "ERROR::Channel Number not correct: " << tmp_channel << endl;  return;}
            
	    if (debugging) cout << " Reading " << tmp_part << tmp_module << " " << tmp_channel << endl;

            if (tmp_gain == 0){//LG
                if (myPart_ctr == Part::partEBA) { EBA[laser::masked_LG]->SetBinContent(tmp_module, tmp_channel+1, 1.0); }
                if (myPart_ctr == Part::partEBC) { EBC[laser::masked_LG]->SetBinContent(tmp_module, tmp_channel+1, 1.0); }
                if (myPart_ctr == Part::partLBA) { LBA[laser::masked_LG]->SetBinContent(tmp_module, tmp_channel+1, 1.0); }
                if (myPart_ctr == Part::partLBC) { LBC[laser::masked_LG]->SetBinContent(tmp_module, tmp_channel+1, 1.0); }
            } else if (tmp_gain == 1){//HG
                if (myPart_ctr == Part::partEBA) { EBA[laser::masked_HG]->SetBinContent(tmp_module, tmp_channel+1, 1.0); }
                if (myPart_ctr == Part::partEBC) { EBC[laser::masked_HG]->SetBinContent(tmp_module, tmp_channel+1, 1.0); }
                if (myPart_ctr == Part::partLBA) { LBA[laser::masked_HG]->SetBinContent(tmp_module, tmp_channel+1, 1.0); }
                if (myPart_ctr == Part::partLBC) { LBC[laser::masked_HG]->SetBinContent(tmp_module, tmp_channel+1, 1.0); }
            }
        }
    }
    f_Masked.close();
    //checking what channels have both gains masked
    for (int mm = 1; mm < 65; ++mm)
    {
        for (int cc = 1; cc < 49; ++cc)
        {
            if (EBA[laser::masked_LG]->GetBinContent(mm,cc)>0. && EBA[laser::masked_HG]->GetBinContent(mm,cc)>0.){
                EBA[laser::masked_BothG]->SetBinContent(mm,cc, 1.0);
            }
            if (EBC[laser::masked_LG]->GetBinContent(mm,cc)>0. && EBC[laser::masked_HG]->GetBinContent(mm,cc)>0.){
                EBC[laser::masked_BothG]->SetBinContent(mm,cc, 1.0);
            }
            if (LBA[laser::masked_LG]->GetBinContent(mm,cc)>0. && LBA[laser::masked_HG]->GetBinContent(mm,cc)>0.){
                LBA[laser::masked_BothG]->SetBinContent(mm,cc, 1.0);
            }
            if (LBC[laser::masked_LG]->GetBinContent(mm,cc)>0. && LBC[laser::masked_HG]->GetBinContent(mm,cc)>0.){
                LBC[laser::masked_BothG]->SetBinContent(mm,cc, 1.0);
            }
        }
    }
    
    //--------- last update
    f_LastLaser.open("Laser_DB.txt");
    
    if (!f_LastLaser) {
      std::cout<<"ERROR :: File Laser_DB.txt not found.\n"<<endl;
      return;
    } else {
       std::cout << "INFO ::  Reading file: Laser_DB.txt\n" << endl;
       while(!f_LastLaser.eof())
      {
          f_LastLaser >> tmp_part;
	  // Filter lines that do not start with module names
	  if (!tmp_part.rfind("LB",0) and !tmp_part.rfind("EB",0)) continue;
          separatePartMod(tmp_part, tmp_module);
          f_LastLaser >> tmp_channel;
          f_LastLaser >> tmp_zero;
          f_LastLaser >> tmp_constant;
          f_LastLaser >> tmp_HV;

	  if (debugging) cout << tmp_part << "\t" << tmp_module << "\t" <<  tmp_channel << "\t" << tmp_zero << "\t" << tmp_constant << "\t" << tmp_HV <<endl;
	  
	  //fix partition
          int myPart_ctr = -1;
          if (tmp_part == "EBA") myPart_ctr = Part::partEBA;
          if (tmp_part == "LBA") myPart_ctr = Part::partLBA;
          if (tmp_part == "LBC") myPart_ctr = Part::partLBC;
          if (tmp_part == "EBC") myPart_ctr = Part::partEBC;
          
          if ( (myPart_ctr <0) || (myPart_ctr>3) )   { cout << "ERROR::Partition Number not correct: " << myPart_ctr << endl; return;}
          if ( (tmp_module <1) || (tmp_module>64) )  { cout << "ERROR::Module Number not correct: " << tmp_module << endl;    return;}
          if ( (tmp_channel <0) || (tmp_channel>47) ){ cout << "ERROR::Channel Number not correct: " << tmp_channel << endl;  return;}

          LastLas_constant[myPart_ctr][tmp_module-1][tmp_channel] = tmp_constant;
          LastLas_HV[myPart_ctr][tmp_module-1][tmp_channel] = tmp_HV;
       }
    }
    f_LastLaser.close();

    //--------- new update
    f_ThisLaser.open("new_db.txt");
    
    if (!f_ThisLaser) {
        std::cout<<"ERROR :: File new_db.txt not found.\n"<<endl;
        return;
    } else {
        std::cout << "INFO ::  Reading file: new_db.txt\n" << endl;
        while(!f_ThisLaser.eof())
        {
            f_ThisLaser >> tmp_part;
	    // Filter lines that do not start with module names
	    if (!tmp_part.rfind("LB",0) and !tmp_part.rfind("EB",0)) continue;
            separatePartMod(tmp_part, tmp_module);
            f_ThisLaser >> tmp_channel;
            f_ThisLaser >> tmp_zero;
            f_ThisLaser >> tmp_constant;
            f_ThisLaser >> tmp_HV;
            
            if (debugging) cout << tmp_part << "\t" << tmp_module << "\t" <<  tmp_channel << "\t" << tmp_zero << "\t" << tmp_constant << "\t" << tmp_HV <<endl;
            //fix partition
            int myPart_ctr = -1;
            if (tmp_part == "EBA") myPart_ctr = Part::partEBA;
            if (tmp_part == "LBA") myPart_ctr = Part::partLBA;
            if (tmp_part == "LBC") myPart_ctr = Part::partLBC;
            if (tmp_part == "EBC") myPart_ctr = Part::partEBC;
            
            if ( (myPart_ctr <0) || (myPart_ctr>3) )   { cout << "ERROR::Partition Number not correct: " << myPart_ctr << endl; return;}
            if ( (tmp_module <1) || (tmp_module>64) )  { cout << "ERROR::Module Number not correct: " << tmp_module << endl;    return;}
            if ( (tmp_channel <0) || (tmp_channel>47) ){ cout << "ERROR::Channel Number not correct: " << tmp_channel << endl;  return;}
            
            ThisLas_constant[myPart_ctr][tmp_module-1][tmp_channel] = tmp_constant;
            ThisLas_HV[myPart_ctr][tmp_module-1][tmp_channel] = tmp_HV;
        }
    }
    f_ThisLaser.close();
    
    ///--------- Now we save some plots :)
    
    // Fill histograms
    cout << "\n\n\n*** ** * ** *** ** * ** *** ** * ** *** ** * ** *** Checking input\n"<<endl;

    string channelType = "[Regular]";
    bool isSpecialCh = false;
    
    for (int mm = 1; mm < 65; ++mm)
    {
        for (int cc = 0; cc < 48; ++cc)
        {
            isSpecialCh = isSpecialChannel(channelType, mm, cc); // only relevant for EB
            
            if (LastLas_HV[Part::partEBA][mm-1][cc] == -2.0) EBA[laser::noInstrumented] ->SetBinContent(mm, cc+1, 1.0);
            else if (ThisLas_constant[Part::partEBA][mm-1][cc] == 1.0) EBA[laser::noUpdate_Cs] ->SetBinContent(mm, cc+1, 1.0);

            if (LastLas_HV[Part::partLBA][mm-1][cc] == -2.0) LBA[laser::noInstrumented] ->SetBinContent(mm, cc+1, 1.0);
            else if (ThisLas_constant[Part::partLBA][mm-1][cc] == 1.0) LBA[laser::noUpdate_Cs] ->SetBinContent(mm, cc+1, 1.0);
            
            if (LastLas_HV[Part::partLBC][mm-1][cc] == -2.0) LBC[laser::noInstrumented] ->SetBinContent(mm, cc+1, 1.0);
            else if (ThisLas_constant[Part::partLBC][mm-1][cc] == 1.0) LBC[laser::noUpdate_Cs] ->SetBinContent(mm, cc+1, 1.0);
            
            if (LastLas_HV[Part::partEBC][mm-1][cc] == -2.0) EBC[laser::noInstrumented] ->SetBinContent(mm, cc+1, 1.0);
            else if (ThisLas_constant[Part::partEBC][mm-1][cc] == 1.0) EBC[laser::noUpdate_Cs] ->SetBinContent(mm, cc+1, 1.0);
            
            //constants and HV difference (new - old)
            double correctedConst = 0.0;
            //------EBA
            if (LastLas_HV[Part::partEBA][mm-1][cc] != -2.0) {
	        bool masked=(EBA[laser::masked_LG]->GetBinContent(mm-1,cc)>0. || EBA[laser::masked_HG]->GetBinContent(mm-1,cc)>0.);

                EBA[laser::laserConstant] ->SetBinContent(mm, cc+1, ThisLas_constant[Part::partEBA][mm-1][cc]);
		if (!masked) EBA_1d[laser::laserConstant] ->Fill(ThisLas_constant[Part::partEBA][mm-1][cc]);

                correctedConst = 100.0*(ThisLas_constant[Part::partEBA][mm-1][cc]-LastLas_constant[Part::partEBA][mm-1][cc])/LastLas_constant[Part::partEBA][mm-1][cc];
                if (correctedConst != 0.0)  EBA[laser::diffConst_LastLas] ->SetBinContent(mm, cc+1, correctedConst);
		if (!masked) EBA_1d[laser::diffConst_LastLas] ->Fill(correctedConst);
                
                if ((LastLas_HV[Part::partEBA][mm-1][cc] == -1.0) && (ThisLas_HV[Part::partEBA][mm-1][cc] != -1.0) )
                    EBA[laser::Update_HVLas]->SetBinContent(mm, cc+1, 1);
                else if ((LastLas_HV[Part::partEBA][mm-1][cc] != -1.0) && (ThisLas_HV[Part::partEBA][mm-1][cc] == -1.0) )
                    cout << "WARNING :: EBA Mod:" << mm << " Chan:"<< cc << " went back to HV=-1 (HV_before="<< LastLas_HV[Part::partEBA][mm-1][cc]<<
                    ", HV_now=" << ThisLas_HV[Part::partEBA][mm-1][cc] << ") " << channelType << endl;
                else EBA[laser::diffHV_LastLas] ->SetBinContent(mm, cc+1, LastLas_HV[Part::partEBA][mm-1][cc]-ThisLas_HV[Part::partEBA][mm-1][cc]);
            }
            //------LBA
            if (LastLas_HV[Part::partLBA][mm-1][cc] != -2.0){
	        bool masked=(LBA[laser::masked_LG]->GetBinContent(mm-1,cc)>0. || LBA[laser::masked_HG]->GetBinContent(mm-1,cc)>0.);

                LBA[laser::laserConstant] ->SetBinContent(mm, cc+1, ThisLas_constant[Part::partLBA][mm-1][cc]);
		if (!masked) LBA_1d[laser::laserConstant] ->Fill(ThisLas_constant[Part::partLBA][mm-1][cc]);                

                correctedConst = 100.0*(ThisLas_constant[Part::partLBA][mm-1][cc]-LastLas_constant[Part::partLBA][mm-1][cc])/LastLas_constant[Part::partLBA][mm-1][cc];
                if (correctedConst != 0.0) LBA[laser::diffConst_LastLas] ->SetBinContent(mm, cc+1, correctedConst);
		if (!masked) LBA_1d[laser::diffConst_LastLas] ->Fill(correctedConst);                

                if ((LastLas_HV[Part::partLBA][mm-1][cc] == -1.0) && (ThisLas_HV[Part::partLBA][mm-1][cc] != -1.0) )
                    LBA[laser::Update_HVLas]->SetBinContent(mm, cc+1, 1);
                else if ((LastLas_HV[Part::partLBA][mm-1][cc] != -1.0) && (ThisLas_HV[Part::partLBA][mm-1][cc] == -1.0) )
                    cout << "WARNING :: LBA Mod:" << mm << " Chan:"<< cc << " went back to HV=-1 (HV_before="<< LastLas_HV[Part::partLBA][mm-1][cc]<<
                    ", HV_now=" << ThisLas_HV[Part::partLBA][mm-1][cc] << ") " << channelType << endl;
                else LBA[laser::diffHV_LastLas] ->SetBinContent(mm, cc+1, LastLas_HV[Part::partLBA][mm-1][cc]-ThisLas_HV[Part::partLBA][mm-1][cc]);
            }
            //------LBC
            if (LastLas_HV[Part::partLBC][mm-1][cc] != -2.0){
	        bool masked=(LBC[laser::masked_LG]->GetBinContent(mm-1,cc)>0. || LBC[laser::masked_HG]->GetBinContent(mm-1,cc)>0.);

                LBC[laser::laserConstant] ->SetBinContent(mm, cc+1, ThisLas_constant[Part::partLBC][mm-1][cc]);
		if (!masked) LBC_1d[laser::laserConstant] ->Fill(ThisLas_constant[Part::partLBC][mm-1][cc]);                
                
                correctedConst = 100.0*(ThisLas_constant[Part::partLBC][mm-1][cc]-LastLas_constant[Part::partLBC][mm-1][cc])/LastLas_constant[Part::partLBC][mm-1][cc];
                if (correctedConst != 0.0) LBC[laser::diffConst_LastLas] ->SetBinContent(mm, cc+1, correctedConst);
		if (!masked) LBC_1d[laser::diffConst_LastLas] ->Fill(correctedConst);

                if ((LastLas_HV[Part::partLBC][mm-1][cc] == -1.0) && (ThisLas_HV[Part::partLBC][mm-1][cc] != -1.0) )
                    LBC[laser::Update_HVLas]->SetBinContent(mm, cc+1, 1);
                else if ((LastLas_HV[Part::partLBC][mm-1][cc] != -1.0) && (ThisLas_HV[Part::partLBC][mm-1][cc] == -1.0) )
                    cout << "WARNING :: LBC Mod:" << mm << " Chan:"<< cc << " went back to HV=-1 (HV_before="<< LastLas_HV[Part::partLBC][mm-1][cc]<<
                    ", HV_now=" << ThisLas_HV[Part::partLBC][mm-1][cc] << ") " << channelType << endl;
                else LBC[laser::diffHV_LastLas] ->SetBinContent(mm, cc+1, LastLas_HV[Part::partLBC][mm-1][cc]-ThisLas_HV[Part::partLBC][mm-1][cc]);
            }
            //------EBC
            if (LastLas_HV[Part::partEBC][mm-1][cc] != -2.0){
       	        bool masked=(EBC[laser::masked_LG]->GetBinContent(mm-1,cc)>0. || EBC[laser::masked_HG]->GetBinContent(mm-1,cc)>0.);
	        
                EBC[laser::laserConstant] ->SetBinContent(mm, cc+1, ThisLas_constant[Part::partEBC][mm-1][cc]);
		if (!masked) EBC_1d[laser::laserConstant] ->Fill(ThisLas_constant[Part::partEBC][mm-1][cc]);                
                
                correctedConst = 100.0*(ThisLas_constant[Part::partEBC][mm-1][cc]-LastLas_constant[Part::partEBC][mm-1][cc])/LastLas_constant[Part::partEBC][mm-1][cc];
                if (correctedConst != 0.0) EBC[laser::diffConst_LastLas] ->SetBinContent(mm, cc+1, correctedConst);
		if (!masked) EBC_1d[laser::diffConst_LastLas] ->Fill(correctedConst);
                
                if ((LastLas_HV[Part::partEBC][mm-1][cc] == -1.0) && (ThisLas_HV[Part::partEBC][mm-1][cc] != -1.0) )
                    EBC[laser::Update_HVLas]->SetBinContent(mm, cc+1, 1);
                else if ((LastLas_HV[Part::partEBC][mm-1][cc] != -1.0) && (ThisLas_HV[Part::partEBC][mm-1][cc] == -1.0) )
                    cout << "WARNING :: EBC Mod:" << mm << " Chan:"<< cc << " went back to HV=-1 (HV_before="<< LastLas_HV[Part::partEBC][mm-1][cc]<<
                    ", HV_now=" << ThisLas_HV[Part::partEBC][mm-1][cc] << ") " << channelType << endl;
                else EBC[laser::diffHV_LastLas] ->SetBinContent(mm, cc+1, LastLas_HV[Part::partEBC][mm-1][cc]-ThisLas_HV[Part::partEBC][mm-1][cc]);
                
            }//instrumented
        }//loop over channels
    }//loop over modules
    
    TCanvas *myCanvas;
    myCanvas = new TCanvas("myCanvas", "my little cute Canvas",484,86,800,750);
    gStyle->SetOptStat(0);
    gStyle->SetPalette(1);
    myCanvas->SetFillColor(0);
    myCanvas->SetBorderMode(0);
    myCanvas->SetBorderSize(2);
    myCanvas->SetTickx(1);
    myCanvas->SetTicky(1);
    myCanvas->SetFrameBorderMode(0);
    myCanvas->SetFrameBorderMode(0);
    myCanvas->SetLogy(0);
    myCanvas->SetRightMargin(0.15);
    myCanvas->cd();
    
    gStyle->SetPaintTextFormat("1.3f");
    
    TLatex printInfo;
    printInfo.SetNDC();
    printInfo.SetTextFont(42);
    
    myCanvas->cd();
    
    TH2F *PrintDiff = new TH2F("PrintDiff", "", 64, 0.5, 64.5, 48, -0.5, 47.5);
    
    TLegend *legendTopLeft = new TLegend(0.09,0.9,0.95,0.95, "");
    legendTopLeft-> SetNColumns(2);
    legendTopLeft->SetFillStyle(0);
    legendTopLeft->SetFillColor(0);
    legendTopLeft->SetBorderSize(0);
    
    //---------------Not instrumented
    gStyle->SetHatchesLineWidth(2/*nominal=1*/);
    gStyle->SetHatchesSpacing(0.6/*nominal=1*/);
    
    EBA[laser::noInstrumented]->SetLineColor(kGray);
    EBA[laser::noInstrumented]->SetFillColor(kGray);
    EBA[laser::noInstrumented]->SetFillStyle(3354);
    EBA[laser::noInstrumented]->Draw("BOX");
    //myCanvas->SaveAs("diff_plots/EBA_noInstrumented.pdf");
    LBA[laser::noInstrumented]->SetLineColor(kGray);
    LBA[laser::noInstrumented]->SetFillColor(kGray);
    LBA[laser::noInstrumented]->SetFillStyle(3354);
    LBA[laser::noInstrumented]->Draw("BOX");
    //myCanvas->SaveAs("diff_plots/LBA_noInstrumented.pdf");
    EBC[laser::noInstrumented]->SetLineColor(kGray);
    EBC[laser::noInstrumented]->SetFillColor(kGray);
    EBC[laser::noInstrumented]->SetFillStyle(3354);
    EBC[laser::noInstrumented]->Draw("BOX");
    //myCanvas->SaveAs("diff_plots/EBC_noInstrumented.pdf");
    LBC[laser::noInstrumented]->SetLineColor(kGray);
    LBC[laser::noInstrumented]->SetFillColor(kGray);
    LBC[laser::noInstrumented]->SetFillStyle(3354);
    LBC[laser::noInstrumented]->Draw("BOX");
    //myCanvas->SaveAs("diff_plots/LBC_noInstrumented.pdf");
    
    //---------------Masked LG
    legendTopLeft->Clear();
    legendTopLeft->AddEntry(LBA[laser::noInstrumented], "Not instrumented", "f");
    legendTopLeft->AddEntry(EBA[laser::masked_LG], "Masked LG", "f");
    
    EBA[laser::masked_LG]->SetLineColor(kBlack);
    EBA[laser::masked_LG]->SetFillColor(kBlack);
    EBA[laser::masked_LG]->SetFillStyle(3144);
    EBA[laser::noInstrumented]->SetTitle("EBA");
    EBA[laser::noInstrumented]->Draw("BOX");
    EBA[laser::masked_LG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/EBA_masked_LG.pdf");
    
    LBA[laser::masked_LG]->SetLineColor(kBlack);
    LBA[laser::masked_LG]->SetFillColor(kBlack);
    LBA[laser::masked_LG]->SetFillStyle(3144);
    LBA[laser::noInstrumented]->SetTitle("LBA");
    LBA[laser::noInstrumented]->Draw("BOX");
    LBA[laser::masked_LG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/LBA_masked_LG.pdf");

    EBC[laser::masked_LG]->SetLineColor(kBlack);
    EBC[laser::masked_LG]->SetFillColor(kBlack);
    EBC[laser::masked_LG]->SetFillStyle(3144);
    EBC[laser::noInstrumented]->SetTitle("EBC");
    EBC[laser::noInstrumented]->Draw("BOX");
    EBC[laser::masked_LG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/EBC_masked_LG.pdf");

    LBC[laser::masked_LG]->SetLineColor(kBlack);
    LBC[laser::masked_LG]->SetFillColor(kBlack);
    LBC[laser::masked_LG]->SetFillStyle(3144);
    LBC[laser::noInstrumented]->SetTitle("LBC");
    LBC[laser::noInstrumented]->Draw("BOX");
    LBC[laser::masked_LG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/LBC_masked_LG.pdf");
    
    //---------------Masked HG
    legendTopLeft->Clear();
    legendTopLeft->AddEntry(LBA[laser::noInstrumented], "Not instrumented", "f");
    legendTopLeft->AddEntry(EBA[laser::masked_HG], "Masked HG", "f");
    
    EBA[laser::masked_HG]->SetLineColor(kBlack);
    EBA[laser::masked_HG]->SetFillColor(kBlack);
    EBA[laser::masked_HG]->SetFillStyle(3144);
    EBA[laser::noInstrumented]->SetTitle("EBA");
    EBA[laser::noInstrumented]->Draw("BOX");
    EBA[laser::masked_HG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/EBA_masked_HG.pdf");

    LBA[laser::masked_HG]->SetLineColor(kBlack);
    LBA[laser::masked_HG]->SetFillColor(kBlack);
    LBA[laser::masked_HG]->SetFillStyle(3144);
    LBA[laser::noInstrumented]->SetTitle("LBA");
    LBA[laser::noInstrumented]->Draw("BOX");
    LBA[laser::masked_HG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/LBA_masked_HG.pdf");

    EBC[laser::masked_HG]->SetLineColor(kBlack);
    EBC[laser::masked_HG]->SetFillColor(kBlack);
    EBC[laser::masked_HG]->SetFillStyle(3144);
    EBC[laser::noInstrumented]->SetTitle("EBC");
    EBC[laser::noInstrumented]->Draw("BOX");
    EBC[laser::masked_HG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/EBC_masked_HG.pdf");

    LBC[laser::masked_HG]->SetLineColor(kBlack);
    LBC[laser::masked_HG]->SetFillColor(kBlack);
    LBC[laser::masked_HG]->SetFillStyle(3144);
    LBC[laser::noInstrumented]->SetTitle("LBC");
    LBC[laser::noInstrumented]->Draw("BOX");
    LBC[laser::masked_HG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/LBC_masked_HG.pdf");
    
    //---------------Masked BOTHG
    legendTopLeft->Clear();
    legendTopLeft->AddEntry(LBA[laser::noInstrumented], "Not instrumented", "f");
    legendTopLeft->AddEntry(EBA[laser::masked_BothG], "Masked LG & HG", "f");
    
    EBA[laser::masked_BothG]->SetLineColor(kBlack);
    EBA[laser::masked_BothG]->SetFillColor(kBlack);
    EBA[laser::masked_BothG]->SetFillStyle(3144);
    EBA[laser::noInstrumented]->SetTitle("EBA");
    EBA[laser::noInstrumented]->Draw("BOX");
    EBA[laser::masked_BothG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/EBA_masked_BothG.pdf");

    LBA[laser::masked_BothG]->SetLineColor(kBlack);
    LBA[laser::masked_BothG]->SetFillColor(kBlack);
    LBA[laser::masked_BothG]->SetFillStyle(3144);
    LBA[laser::noInstrumented]->SetTitle("LBA");
    LBA[laser::noInstrumented]->Draw("BOX");
    LBA[laser::masked_BothG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/LBA_masked_BothG.pdf");

    EBC[laser::masked_BothG]->SetLineColor(kBlack);
    EBC[laser::masked_BothG]->SetFillColor(kBlack);
    EBC[laser::masked_BothG]->SetFillStyle(3144);
    EBC[laser::noInstrumented]->SetTitle("EBC");
    EBC[laser::noInstrumented]->Draw("BOX");
    EBC[laser::masked_BothG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/EBC_masked_BothG.pdf");

    LBC[laser::masked_BothG]->SetLineColor(kBlack);
    LBC[laser::masked_BothG]->SetFillColor(kBlack);
    LBC[laser::masked_BothG]->SetFillStyle(3144);
    LBC[laser::noInstrumented]->SetTitle("LBC");
    LBC[laser::noInstrumented]->Draw("BOX");
    LBC[laser::masked_BothG]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->SaveAs("diff_plots/LBC_masked_BothG.pdf");
    
    //------------ laser constant
    cout << "\n\n\n*** ** * ** *** ** * ** *** ** * ** *** ** * ** *** Checking Laser constants\n"<<endl;
    legendTopLeft->Clear();
    legendTopLeft->AddEntry(LBA[laser::noInstrumented], "Not instrumented", "f");

    EBA[laser::laserConstant]->SetMinimum(min_Constants);
    EBA[laser::laserConstant]->SetMaximum(max_Constants);
    EBA[laser::noInstrumented]->SetTitle("EBA [Laser Constants]");
    EBA[laser::noInstrumented]->Draw("BOX");
    EBA[laser::laserConstant]->Draw("COLZsame");
    if (doPrintOutliers){
       printOutliers(EBA[laser::laserConstant], PrintDiff, max_Constants, min_Constants, "EBA");
       PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBA_LaserConstant.pdf");
    
    LBA[laser::laserConstant]->SetMinimum(min_Constants);
    LBA[laser::laserConstant]->SetMaximum(max_Constants);
    LBA[laser::noInstrumented]->SetTitle("LBA [Laser Constants]");
    LBA[laser::noInstrumented]->Draw("BOX");
    LBA[laser::laserConstant]->Draw("COLZsame");
    if (doPrintOutliers){
       printOutliers(LBA[laser::laserConstant], PrintDiff, max_Constants, min_Constants, "LBA");
       PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBA_LaserConstant.pdf");
    
    EBC[laser::laserConstant]->SetMinimum(min_Constants);
    EBC[laser::laserConstant]->SetMaximum(max_Constants);
    EBC[laser::noInstrumented]->SetTitle("EBC [Laser Constants]");
    EBC[laser::noInstrumented]->Draw("BOX");
    EBC[laser::laserConstant]->Draw("COLZsame");
    if (doPrintOutliers){
       printOutliers(EBC[laser::laserConstant], PrintDiff, max_Constants, min_Constants, "EBC");
       PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBC_LaserConstant.pdf");
    
    LBC[laser::laserConstant]->SetMinimum(min_Constants);
    LBC[laser::laserConstant]->SetMaximum(max_Constants);
    LBC[laser::noInstrumented]->SetTitle("LBC [Laser Constants]");
    LBC[laser::noInstrumented]->Draw("BOX");
    LBC[laser::laserConstant]->Draw("COLZsame");
    if (doPrintOutliers){
       printOutliers(LBC[laser::laserConstant], PrintDiff, max_Constants, min_Constants, "LBC");
       PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBC_LaserConstant.pdf");

    //------------ now remove masked
    //checking what channels have both gains masked
    for (int mm = 1; mm < 65; ++mm)
    {
        for (int cc = 1; cc < 49; ++cc)
        {
            if (EBA[laser::masked_BothG]->GetBinContent(mm,cc)>0.){
                EBA[laser::laserConstant]->SetBinContent(mm,cc,-1000.0);
            }
            if (EBC[laser::masked_BothG]->GetBinContent(mm,cc)>0.){
                EBC[laser::laserConstant]->SetBinContent(mm,cc,-1000.0);
            }
            if (LBA[laser::masked_BothG]->GetBinContent(mm,cc)>0.){
                LBA[laser::laserConstant]->SetBinContent(mm,cc,-1000.0);
            }
            if (LBC[laser::masked_BothG]->GetBinContent(mm,cc)>0.){
                LBC[laser::laserConstant]->SetBinContent(mm,cc,-1000.0);
            }
        }
    }
    legendTopLeft->Clear();
    legendTopLeft->AddEntry(EBA[laser::noInstrumented], "Not instrumented", "f");
    legendTopLeft->AddEntry(EBA[laser::masked_BothG], "Masked (LG&HG)", "f");
    
    EBA[laser::laserConstant]->SetMinimum(min_Constants);
    EBA[laser::laserConstant]->SetMaximum(max_Constants);
    EBA[laser::noInstrumented]->SetTitle("EBA [Laser Constants]");
    EBA[laser::noInstrumented]->Draw("BOX");
    EBA[laser::masked_BothG]->Draw("BOXsame");
    EBA[laser::laserConstant]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(EBA[laser::laserConstant], PrintDiff, max_Constants, min_Constants, "EBA");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBA_LaserConstant_NoMasked.pdf");
    
    EBC[laser::laserConstant]->SetMinimum(min_Constants);
    EBC[laser::laserConstant]->SetMaximum(max_Constants);
    EBC[laser::noInstrumented]->SetTitle("EBC [Laser Constants]");
    EBC[laser::noInstrumented]->Draw("BOX");
    EBC[laser::masked_BothG]->Draw("BOXsame");
    EBC[laser::laserConstant]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(EBC[laser::laserConstant], PrintDiff, max_Constants, min_Constants, "EBC");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBC_LaserConstant_NoMasked.pdf");
    
    LBA[laser::laserConstant]->SetMinimum(min_Constants);
    LBA[laser::laserConstant]->SetMaximum(max_Constants);
    LBA[laser::noInstrumented]->SetTitle("LBA [Laser Constants]");
    LBA[laser::noInstrumented]->Draw("BOX");
    LBA[laser::masked_BothG]->Draw("BOXsame");
    LBA[laser::laserConstant]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(LBA[laser::laserConstant], PrintDiff, max_Constants, min_Constants, "LBA");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBA_LaserConstant_NoMasked.pdf");
    
    LBC[laser::laserConstant]->SetMinimum(min_Constants);
    LBC[laser::laserConstant]->SetMaximum(max_Constants);
    LBC[laser::noInstrumented]->SetTitle("LBC [Laser Constants]");
    LBC[laser::noInstrumented]->Draw("BOX");
    LBC[laser::masked_BothG]->Draw("BOXsame");
    LBC[laser::laserConstant]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(LBC[laser::laserConstant], PrintDiff, max_Constants, min_Constants, "LBC");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBC_LaserConstant_NoMasked.pdf");
    
    //------------ constant difference wrt last update
    cout << "\n\n\n*** ** * ** *** ** * ** *** ** * ** *** ** * ** *** Checking Laser constants differences\n"<<endl;
    legendTopLeft->Clear();
    legendTopLeft->AddEntry(LBA[laser::noInstrumented], "Not instrumented", "f");
    LBA[laser::noUpdate_Cs]->SetFillColor(kWhite); LBA[laser::noUpdate_Cs]->SetLineColor(kBlack);
    legendTopLeft->AddEntry(LBA[laser::noUpdate_Cs], "No difference wrt last update", "f");
    
    EBA[laser::diffConst_LastLas]->SetMinimum(min_diffConst_LastLas);
    EBA[laser::diffConst_LastLas]->SetMaximum(max_diffConst_LastLas);
    EBA[laser::noInstrumented]->SetTitle("EBA [Change of constant wrt last update]");
    EBA[laser::diffConst_LastLas]->GetZaxis()->SetTitle("(C_{laser}^{new} - C_{laser}^{old})/C_{laser}^{old} [%]");
    EBA[laser::diffConst_LastLas]->GetZaxis()->CenterTitle();
    EBA[laser::noInstrumented]->Draw("BOX");
    EBA[laser::diffConst_LastLas]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(EBA[laser::diffConst_LastLas], PrintDiff, max_diffConst_LastLas, min_diffConst_LastLas, "EBA");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBA_diffConst_LastLas.pdf");
    
    LBA[laser::diffConst_LastLas]->SetMinimum(min_diffConst_LastLas);
    LBA[laser::diffConst_LastLas]->SetMaximum(max_diffConst_LastLas);
    LBA[laser::noInstrumented]->SetTitle("LBA [Change of constant wrt last update]");
    LBA[laser::diffConst_LastLas]->GetZaxis()->SetTitle("(C_{laser}^{new} - C_{laser}^{old})/C_{laser}^{old} [%]");
    LBA[laser::diffConst_LastLas]->GetZaxis()->CenterTitle();
    LBA[laser::noInstrumented]->Draw("BOX");
    LBA[laser::diffConst_LastLas]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(LBA[laser::diffConst_LastLas], PrintDiff, max_diffConst_LastLas, min_diffConst_LastLas, "LBA");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBA_diffConst_LastLas.pdf");
    
    EBC[laser::diffConst_LastLas]->SetMinimum(min_diffConst_LastLas);
    EBC[laser::diffConst_LastLas]->SetMaximum(max_diffConst_LastLas);
    EBC[laser::noInstrumented]->SetTitle("EBC [Change of constant wrt last update]");
    EBC[laser::diffConst_LastLas]->GetZaxis()->SetTitle("(C_{laser}^{new} - C_{laser}^{old})/C_{laser}^{old} [%]");
    EBC[laser::diffConst_LastLas]->GetZaxis()->CenterTitle();
    EBC[laser::noInstrumented]->Draw("BOX");
    EBC[laser::diffConst_LastLas]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(EBC[laser::diffConst_LastLas], PrintDiff, max_diffConst_LastLas, min_diffConst_LastLas, "EBC");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBC_diffConst_LastLas.pdf");
    
    LBC[laser::diffConst_LastLas]->SetMinimum(min_diffConst_LastLas);
    LBC[laser::diffConst_LastLas]->SetMaximum(max_diffConst_LastLas);
    LBC[laser::noInstrumented]->SetTitle("LBC [Change of constant wrt last update]");
    LBC[laser::diffConst_LastLas]->GetZaxis()->SetTitle("(C_{laser}^{new} - C_{laser}^{old})/C_{laser}^{old} [%]");
    LBC[laser::diffConst_LastLas]->GetZaxis()->CenterTitle();
    LBC[laser::noInstrumented]->Draw("BOX");
    LBC[laser::diffConst_LastLas]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(LBC[laser::diffConst_LastLas], PrintDiff, max_diffConst_LastLas, min_diffConst_LastLas, "LBC");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBC_diffConst_LastLas.pdf");
    
    //------------ now remove masked
    //checking what channels have both gains masked
    for (int mm = 1; mm < 65; ++mm)
    {
        for (int cc = 1; cc < 49; ++cc)
        {
            if (EBA[laser::masked_BothG]->GetBinContent(mm,cc)>0.){
                EBA[laser::diffConst_LastLas]->SetBinContent(mm,cc,-1000.0);
            }
            if (EBC[laser::masked_BothG]->GetBinContent(mm,cc)>0.){
                EBC[laser::diffConst_LastLas]->SetBinContent(mm,cc,-1000.0);
            }
            if (LBA[laser::masked_BothG]->GetBinContent(mm,cc)>0.){
                LBA[laser::diffConst_LastLas]->SetBinContent(mm,cc,-1000.0);
            }
            if (LBC[laser::masked_BothG]->GetBinContent(mm,cc)>0.){
                LBC[laser::diffConst_LastLas]->SetBinContent(mm,cc,-1000.0);
            }
        }
    }
    legendTopLeft->Clear();
    legendTopLeft->AddEntry(EBA[laser::noInstrumented], "Not instrumented", "f");
    legendTopLeft->AddEntry(EBA[laser::masked_BothG], "Masked (LG&HG)", "f");
    
    EBA[laser::diffConst_LastLas]->SetMinimum(min_diffConst_LastLas);
    EBA[laser::diffConst_LastLas]->SetMaximum(max_diffConst_LastLas);
    EBA[laser::noInstrumented]->SetTitle("EBA [Change of constant wrt last update]");
    EBA[laser::diffConst_LastLas]->GetZaxis()->SetTitle("(C_{laser}^{new} - C_{laser}^{old})/C_{laser}^{old} [%]");
    EBA[laser::diffConst_LastLas]->GetZaxis()->CenterTitle();
    EBA[laser::noInstrumented]->Draw("BOX");
    EBA[laser::masked_BothG]->Draw("BOXsame");
    EBA[laser::diffConst_LastLas]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(EBA[laser::diffConst_LastLas], PrintDiff, max_diffConst_LastLas, min_diffConst_LastLas, "EBA");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBA_diffConst_LastLas_NoMasked.pdf");
    
    EBC[laser::diffConst_LastLas]->SetMinimum(min_diffConst_LastLas);
    EBC[laser::diffConst_LastLas]->SetMaximum(max_diffConst_LastLas);
    EBC[laser::noInstrumented]->SetTitle("EBC [Change of constant wrt last update]");
    EBC[laser::diffConst_LastLas]->GetZaxis()->SetTitle("(C_{laser}^{new} - C_{laser}^{old})/C_{laser}^{old} [%]");
    EBC[laser::diffConst_LastLas]->GetZaxis()->CenterTitle();
    EBC[laser::noInstrumented]->Draw("BOX");
    EBC[laser::masked_BothG]->Draw("BOXsame");
    EBC[laser::diffConst_LastLas]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(EBC[laser::diffConst_LastLas], PrintDiff, max_diffConst_LastLas, min_diffConst_LastLas, "EBC");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBC_diffConst_LastLas_NoMasked.pdf");
    
    LBA[laser::diffConst_LastLas]->SetMinimum(min_diffConst_LastLas);
    LBA[laser::diffConst_LastLas]->SetMaximum(max_diffConst_LastLas);
    LBA[laser::noInstrumented]->SetTitle("LBA [Change of constant wrt last update]");
    LBA[laser::diffConst_LastLas]->GetZaxis()->SetTitle("(C_{laser}^{new} - C_{laser}^{old})/C_{laser}^{old} [%]");
    LBA[laser::diffConst_LastLas]->GetZaxis()->CenterTitle();
    LBA[laser::noInstrumented]->Draw("BOX");
    LBA[laser::masked_BothG]->Draw("BOXsame");
    LBA[laser::diffConst_LastLas]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(LBA[laser::diffConst_LastLas], PrintDiff, max_diffConst_LastLas, min_diffConst_LastLas, "LBA");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBA_diffConst_LastLas_NoMasked.pdf");
    
    LBC[laser::diffConst_LastLas]->SetMinimum(min_diffConst_LastLas);
    LBC[laser::diffConst_LastLas]->SetMaximum(max_diffConst_LastLas);
    LBC[laser::noInstrumented]->SetTitle("LBC [Change of constant wrt last update]");
    LBC[laser::diffConst_LastLas]->GetZaxis()->SetTitle("(C_{laser}^{new} - C_{laser}^{old})/C_{laser}^{old} [%]");
    LBC[laser::diffConst_LastLas]->GetZaxis()->CenterTitle();
    LBC[laser::noInstrumented]->Draw("BOX");
    LBC[laser::masked_BothG]->Draw("BOXsame");
    LBC[laser::diffConst_LastLas]->Draw("COLZsame");
    if (doPrintOutliers){
        printOutliers(LBC[laser::diffConst_LastLas], PrintDiff, max_diffConst_LastLas, min_diffConst_LastLas, "LBC");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBC_diffConst_LastLas_NoMasked.pdf");
    
    
    //------------ HV difference wrt last update
    
    EBC[laser::Update_HVLas]->SetLineColor(kBlack);
    LBA[laser::Update_HVLas]->SetFillColor(kBlack);
    LBA[laser::Update_HVLas]->SetLineColor(kBlack);
    LBA[laser::Update_HVLas]->SetFillColor(kBlack);
    EBC[laser::Update_HVLas]->SetLineColor(kBlack);
    EBC[laser::Update_HVLas]->SetFillColor(kBlack);
    LBC[laser::Update_HVLas]->SetLineColor(kBlack);
    LBC[laser::Update_HVLas]->SetFillColor(kBlack);
    
    cout << "\n\n\n*** ** * ** *** ** * ** *** ** * ** *** ** * ** *** Checking HV differences\n"<<endl;
    legendTopLeft->Clear();
    legendTopLeft->AddEntry(LBA[laser::noInstrumented], "Not instrumented", "f");
    legendTopLeft->AddEntry(LBC[laser::Update_HVLas], "New HV value to DB (laser constants are now #neq1)", "f");
    
    EBA[laser::diffHV_LastLas]->SetMinimum(-1.0 * max_diffHV_LastLas);
    EBA[laser::diffHV_LastLas]->SetMaximum(max_diffHV_LastLas);
    EBA[laser::noInstrumented]->SetTitle("EBA [Change of HV wrt last update]");
    EBA[laser::diffHV_LastLas]->GetZaxis()->SetTitle("HV_{old} - HV_{new} [V]");
    EBA[laser::diffHV_LastLas]->GetZaxis()->CenterTitle();
    EBA[laser::noInstrumented]->Draw("BOX");
    EBA[laser::diffHV_LastLas]->Draw("COLZsame");
    EBA[laser::Update_HVLas]->Draw("BOXsame");
    if (doPrintOutliers){
        printOutliers(EBA[laser::diffHV_LastLas], PrintDiff, max_diffHV_LastLas, -1.0*max_diffHV_LastLas, "EBA");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBA_diffHV_LastLas.pdf");
    
    LBA[laser::diffHV_LastLas]->SetMinimum(-1.0 * max_diffHV_LastLas);
    LBA[laser::diffHV_LastLas]->SetMaximum(max_diffHV_LastLas);
    LBA[laser::noInstrumented]->SetTitle("LBA [Change of HV wrt last update]");
    LBA[laser::diffHV_LastLas]->GetZaxis()->SetTitle("HV_{old} - HV_{new} [V]");
    LBA[laser::diffHV_LastLas]->GetZaxis()->CenterTitle();
    LBA[laser::noInstrumented]->Draw("BOX");
    LBA[laser::diffHV_LastLas]->Draw("COLZsame");
    LBA[laser::Update_HVLas]->Draw("BOXsame");
    if (doPrintOutliers){
        printOutliers(LBA[laser::diffHV_LastLas], PrintDiff, max_diffHV_LastLas, -1.0*max_diffHV_LastLas, "LBA");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBA_diffHV_LastLas.pdf");
    
    EBC[laser::diffHV_LastLas]->SetMinimum(-1.0 * max_diffHV_LastLas);
    EBC[laser::diffHV_LastLas]->SetMaximum(max_diffHV_LastLas);
    EBC[laser::noInstrumented]->SetTitle("EBC [Change of HV wrt last update]");
    EBC[laser::diffHV_LastLas]->GetZaxis()->SetTitle("HV_{old} - HV_{new} [V]");
    EBC[laser::diffHV_LastLas]->GetZaxis()->CenterTitle();
    EBC[laser::noInstrumented]->Draw("BOX");
    EBC[laser::diffHV_LastLas]->Draw("COLZsame");
    EBC[laser::Update_HVLas]->Draw("BOXsame");
    if (doPrintOutliers){
        printOutliers(EBC[laser::diffHV_LastLas], PrintDiff, max_diffHV_LastLas, -1.0*max_diffHV_LastLas, "EBC");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBC_diffHV_LastLas.pdf");
    
    LBC[laser::diffHV_LastLas]->SetMinimum(-1.0 * max_diffHV_LastLas);
    LBC[laser::diffHV_LastLas]->SetMaximum(max_diffHV_LastLas);
    LBC[laser::noInstrumented]->SetTitle("LBC [Change of HV wrt last update]");
    LBC[laser::diffHV_LastLas]->GetZaxis()->SetTitle("HV_{old} - HV_{new} [V]");
    LBC[laser::diffHV_LastLas]->GetZaxis()->CenterTitle();
    LBC[laser::noInstrumented]->Draw("BOX");
    LBC[laser::diffHV_LastLas]->Draw("COLZsame");
    LBC[laser::Update_HVLas]->Draw("BOXsame");
    if (doPrintOutliers){
        printOutliers(LBC[laser::diffHV_LastLas], PrintDiff, max_diffHV_LastLas, -1.0*max_diffHV_LastLas, "LBC");
        PrintDiff->Draw("sametext");
    }
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBC_diffHV_LastLas.pdf");
    
    //---------- no update wrt last Cesium update
    Int_t colors[] = {0, 1}; // #colors >= #levels - 1
    gStyle->SetPalette((sizeof(colors)/sizeof(Int_t)), colors);
    
    legendTopLeft->Clear();
    legendTopLeft->AddEntry(LBA[laser::noInstrumented], "Not instrumented", "f");
    LBA[laser::noUpdate_Cs]->SetFillColor(kBlack); LBA[laser::noUpdate_Cs]->SetLineColor(kBlack);
    legendTopLeft->AddEntry(LBA[laser::noUpdate_Cs], "Laser constant = 1 (no correction wrt Cs)", "f");
    
    EBA[laser::noUpdate_Cs]->Draw("COL");
    EBA[laser::noInstrumented]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBA_noUpdate_Cs.pdf");
    
    LBA[laser::noUpdate_Cs]->Draw("COL");
    LBA[laser::noInstrumented]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBA_noUpdate_Cs.pdf");
    
    EBC[laser::noUpdate_Cs]->Draw("COL");
    EBC[laser::noInstrumented]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBC_noUpdate_Cs.pdf");
    
    LBC[laser::noUpdate_Cs]->Draw("COL");
    LBC[laser::noInstrumented]->Draw("BOXsame");
    legendTopLeft->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBC_noUpdate_Cs.pdf");

    // Save histograms
    TFile *outfile = new TFile("diff_plots/doChecksDiff.root","RECREATE");

    EBA_1d[laser::diffConst_LastLas]->Write();
    EBA_1d[laser::diffConst_LastLas]->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBA_1D_diffConst_LastLas_NoMasked.pdf");
    LBA_1d[laser::diffConst_LastLas]->Write();
    LBA_1d[laser::diffConst_LastLas]->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LDA_1D_diffConst_LastLas_NoMasked.pdf");
    LBC_1d[laser::diffConst_LastLas]->Write();
    LBC_1d[laser::diffConst_LastLas]->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBC_1D_diffConst_LastLas_NoMasked.pdf");
    EBC_1d[laser::diffConst_LastLas]->Write();
    EBC_1d[laser::diffConst_LastLas]->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBC_1D_diffConst_LastLas_NoMasked.pdf");

    TILE_1d[laser::diffConst_LastLas]->Add(EBA_1d[laser::diffConst_LastLas]);
    TILE_1d[laser::diffConst_LastLas]->Add(LBA_1d[laser::diffConst_LastLas]);
    TILE_1d[laser::diffConst_LastLas]->Add(LBC_1d[laser::diffConst_LastLas]);
    TILE_1d[laser::diffConst_LastLas]->Add(EBC_1d[laser::diffConst_LastLas]);
    TILE_1d[laser::diffConst_LastLas]->Write();
    TILE_1d[laser::diffConst_LastLas]->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/TILE_1D_diffConst_LastLas_NoMasked.pdf");

    EBA_1d[laser::laserConstant]->Write();
    EBA_1d[laser::laserConstant]->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBA_1D_LaserConstant_NoMasked.pdf");
    LBA_1d[laser::laserConstant]->Write();
    LBA_1d[laser::laserConstant]->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBA_1D_LaserConstant_NoMasked.pdf");
    LBC_1d[laser::laserConstant]->Write();
    LBC_1d[laser::laserConstant]->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/LBC_1D_LaserConstant_NoMasked.pdf");
    EBC_1d[laser::laserConstant]->Write();
    EBC_1d[laser::laserConstant]->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/EBC_1D_LaserConstant_NoMasked.pdf");

    TILE_1d[laser::laserConstant]->Add(EBA_1d[laser::laserConstant]);
    TILE_1d[laser::laserConstant]->Add(LBA_1d[laser::laserConstant]);
    TILE_1d[laser::laserConstant]->Add(LBC_1d[laser::laserConstant]);
    TILE_1d[laser::laserConstant]->Add(EBC_1d[laser::laserConstant]);
    TILE_1d[laser::laserConstant]->Write();
    TILE_1d[laser::laserConstant]->Draw();
    myCanvas->RedrawAxis(); myCanvas->SaveAs("diff_plots/TILE_1D_LaserConstant_NoMasked.pdf");

    outfile->Close();

    exit(0);  
} 
