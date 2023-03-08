void LowgainDetAvg()
{
//=========Macro generated from canvas: c1_n1/c1
//=========  (Mon Mar  6 14:06:07 2023) by ROOT version 6.24/00
   TCanvas *c1_n1 = new TCanvas("c1_n1", "c1",0,0,800,602);
   gStyle->SetOptStat(0);
   c1_n1->SetHighLightColor(2);
   c1_n1->Range(1.674702e+09,1.237018,1.677854e+09,1.335104);
   c1_n1->SetFillColor(0);
   c1_n1->SetBorderMode(0);
   c1_n1->SetBorderSize(0);
   c1_n1->SetTickx(1);
   c1_n1->SetTicky(1);
   c1_n1->SetLeftMargin(0.16);
   c1_n1->SetTopMargin(0.05);
   c1_n1->SetBottomMargin(0.16);
   c1_n1->SetFrameBorderMode(0);
   c1_n1->SetFrameBorderMode(0);
   
   TH2D *throwsPawaysPhisto__9 = new TH2D("throwsPawaysPhisto__9","",1,1.675206e+09,1.677539e+09,1,1.252712,1.330199);
   throwsPawaysPhisto__9->SetStats(0);
   throwsPawaysPhisto__9->SetLineWidth(2);
   throwsPawaysPhisto__9->SetMarkerStyle(20);
   throwsPawaysPhisto__9->SetMarkerSize(1.2);
   throwsPawaysPhisto__9->GetXaxis()->SetTimeDisplay(1);
   throwsPawaysPhisto__9->GetXaxis()->SetTimeFormat("#splitline{%b %d}{%Y} %F1970-01-01 00:00:00");
   throwsPawaysPhisto__9->GetXaxis()->SetRange(1,1);
   throwsPawaysPhisto__9->GetXaxis()->SetNdivisions(100503);
   throwsPawaysPhisto__9->GetXaxis()->SetLabelFont(42);
   throwsPawaysPhisto__9->GetXaxis()->SetLabelOffset(0.025);
   throwsPawaysPhisto__9->GetXaxis()->SetLabelSize(0.025);
   throwsPawaysPhisto__9->GetXaxis()->SetTickLength(0.04);
   throwsPawaysPhisto__9->GetXaxis()->SetTitleOffset(1);
   throwsPawaysPhisto__9->GetXaxis()->SetTitleFont(42);
   throwsPawaysPhisto__9->GetYaxis()->SetTitle("CIS Calibration [ADC count/pC]");
   throwsPawaysPhisto__9->GetYaxis()->SetRange(1,1);
   throwsPawaysPhisto__9->GetYaxis()->CenterTitle(true);
   throwsPawaysPhisto__9->GetYaxis()->SetLabelFont(42);
   throwsPawaysPhisto__9->GetYaxis()->SetTitleOffset(1.2);
   throwsPawaysPhisto__9->GetYaxis()->SetTitleFont(42);
   throwsPawaysPhisto__9->GetZaxis()->SetLabelFont(42);
   throwsPawaysPhisto__9->GetZaxis()->SetTitleOffset(1);
   throwsPawaysPhisto__9->GetZaxis()->SetTitleFont(42);
   throwsPawaysPhisto__9->Draw("");
   
   Double_t Graph0_fx1001[7] = {
   1.675363e+09,
   1.67551e+09,
   1.675708e+09,
   1.676062e+09,
   1.67675e+09,
   1.676979e+09,
   1.677522e+09};
   Double_t Graph0_fy1001[7] = {
   1.283831,
   1.283585,
   1.283971,
   1.283548,
   1.283693,
   1.283741,
   1.283612};
   Double_t Graph0_fex1001[7] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph0_fey1001[7] = {
   0.00898682,
   0.008985098,
   0.008987798,
   0.00898484,
   0.008985852,
   0.008986184,
   0.008985286};
   TGraphErrors *gre = new TGraphErrors(7,Graph0_fx1001,Graph0_fy1001,Graph0_fex1001,Graph0_fey1001);
   gre->SetName("Graph0");
   gre->SetTitle("Graph");

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#ffff00");
   gre->SetFillColor(ci);
   gre->SetFillStyle(1000);

   ci = TColor::GetColor("#ffff00");
   gre->SetLineColor(ci);

   ci = TColor::GetColor("#0000ff");
   gre->SetMarkerColor(ci);
   gre->SetMarkerStyle(23);
   gre->SetMarkerSize(1.3);
   
   TH1F *Graph_Graph01001 = new TH1F("Graph_Graph01001","Graph",100,1.675147e+09,1.677738e+09);
   Graph_Graph01001->SetMinimum(1.272724);
   Graph_Graph01001->SetMaximum(1.294799);
   Graph_Graph01001->SetDirectory(0);
   Graph_Graph01001->SetStats(0);
   Graph_Graph01001->SetLineWidth(2);
   Graph_Graph01001->SetMarkerStyle(20);
   Graph_Graph01001->SetMarkerSize(1.2);
   Graph_Graph01001->GetXaxis()->SetNdivisions(509);
   Graph_Graph01001->GetXaxis()->SetLabelFont(42);
   Graph_Graph01001->GetXaxis()->SetTitleOffset(1);
   Graph_Graph01001->GetXaxis()->SetTitleFont(42);
   Graph_Graph01001->GetYaxis()->SetNdivisions(305);
   Graph_Graph01001->GetYaxis()->SetLabelFont(42);
   Graph_Graph01001->GetYaxis()->SetTitleOffset(1);
   Graph_Graph01001->GetYaxis()->SetTitleFont(42);
   Graph_Graph01001->GetZaxis()->SetLabelFont(42);
   Graph_Graph01001->GetZaxis()->SetTitleOffset(1);
   Graph_Graph01001->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_Graph01001);
   
   gre->Draw("e3");
   
   Double_t Graph0_fx1002[7] = {
   1.675363e+09,
   1.67551e+09,
   1.675708e+09,
   1.676062e+09,
   1.67675e+09,
   1.676979e+09,
   1.677522e+09};
   Double_t Graph0_fy1002[7] = {
   1.283831,
   1.283585,
   1.283971,
   1.283548,
   1.283693,
   1.283741,
   1.283612};
   Double_t Graph0_fex1002[7] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph0_fey1002[7] = {
   0.00898682,
   0.008985098,
   0.008987798,
   0.00898484,
   0.008985852,
   0.008986184,
   0.008985286};
   gre = new TGraphErrors(7,Graph0_fx1002,Graph0_fy1002,Graph0_fex1002,Graph0_fey1002);
   gre->SetName("Graph0");
   gre->SetTitle("Graph");

   ci = TColor::GetColor("#ffff00");
   gre->SetFillColor(ci);
   gre->SetFillStyle(1000);

   ci = TColor::GetColor("#ffff00");
   gre->SetLineColor(ci);

   ci = TColor::GetColor("#0000ff");
   gre->SetMarkerColor(ci);
   gre->SetMarkerStyle(23);
   gre->SetMarkerSize(1.3);
   
   TH1F *Graph_Graph_Graph010011002 = new TH1F("Graph_Graph_Graph010011002","Graph",100,1.675147e+09,1.677738e+09);
   Graph_Graph_Graph010011002->SetMinimum(1.272724);
   Graph_Graph_Graph010011002->SetMaximum(1.294799);
   Graph_Graph_Graph010011002->SetDirectory(0);
   Graph_Graph_Graph010011002->SetStats(0);
   Graph_Graph_Graph010011002->SetLineWidth(2);
   Graph_Graph_Graph010011002->SetMarkerStyle(20);
   Graph_Graph_Graph010011002->SetMarkerSize(1.2);
   Graph_Graph_Graph010011002->GetXaxis()->SetNdivisions(509);
   Graph_Graph_Graph010011002->GetXaxis()->SetLabelFont(42);
   Graph_Graph_Graph010011002->GetXaxis()->SetTitleOffset(1);
   Graph_Graph_Graph010011002->GetXaxis()->SetTitleFont(42);
   Graph_Graph_Graph010011002->GetYaxis()->SetNdivisions(305);
   Graph_Graph_Graph010011002->GetYaxis()->SetLabelFont(42);
   Graph_Graph_Graph010011002->GetYaxis()->SetTitleOffset(1);
   Graph_Graph_Graph010011002->GetYaxis()->SetTitleFont(42);
   Graph_Graph_Graph010011002->GetZaxis()->SetLabelFont(42);
   Graph_Graph_Graph010011002->GetZaxis()->SetTitleOffset(1);
   Graph_Graph_Graph010011002->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_Graph_Graph010011002);
   
   gre->Draw("p");
   
   Double_t Graph1_fx1003[7] = {
   1.675363e+09,
   1.67551e+09,
   1.675708e+09,
   1.676062e+09,
   1.67675e+09,
   1.676979e+09,
   1.677522e+09};
   Double_t Graph1_fy1003[7] = {
   1.291493,
   1.291491,
   1.291422,
   1.291592,
   1.291438,
   1.291398,
   1.291355};
   Double_t Graph1_fex1003[7] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph1_fey1003[7] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   gre = new TGraphErrors(7,Graph1_fx1003,Graph1_fy1003,Graph1_fex1003,Graph1_fey1003);
   gre->SetName("Graph1");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetMarkerStyle(20);
   gre->SetMarkerSize(1.3);
   
   TH1F *Graph_Graph11003 = new TH1F("Graph_Graph11003","Graph",100,1.675147e+09,1.677738e+09);
   Graph_Graph11003->SetMinimum(1.291331);
   Graph_Graph11003->SetMaximum(1.291615);
   Graph_Graph11003->SetDirectory(0);
   Graph_Graph11003->SetStats(0);
   Graph_Graph11003->SetLineWidth(2);
   Graph_Graph11003->SetMarkerStyle(20);
   Graph_Graph11003->SetMarkerSize(1.2);
   Graph_Graph11003->GetXaxis()->SetNdivisions(509);
   Graph_Graph11003->GetXaxis()->SetLabelFont(42);
   Graph_Graph11003->GetXaxis()->SetTitleOffset(1);
   Graph_Graph11003->GetXaxis()->SetTitleFont(42);
   Graph_Graph11003->GetYaxis()->SetNdivisions(305);
   Graph_Graph11003->GetYaxis()->SetLabelFont(42);
   Graph_Graph11003->GetYaxis()->SetTitleOffset(1);
   Graph_Graph11003->GetYaxis()->SetTitleFont(42);
   Graph_Graph11003->GetZaxis()->SetLabelFont(42);
   Graph_Graph11003->GetZaxis()->SetTitleOffset(1);
   Graph_Graph11003->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_Graph11003);
   
   gre->Draw("p");
   
   TH2D *throwsPawaysPhisto_copy__10 = new TH2D("throwsPawaysPhisto_copy__10","",1,1.675206e+09,1.677539e+09,1,1.252712,1.330199);
   throwsPawaysPhisto_copy__10->SetDirectory(0);
   throwsPawaysPhisto_copy__10->SetStats(0);
   throwsPawaysPhisto_copy__10->SetLineWidth(2);
   throwsPawaysPhisto_copy__10->SetMarkerStyle(20);
   throwsPawaysPhisto_copy__10->SetMarkerSize(1.2);
   throwsPawaysPhisto_copy__10->GetXaxis()->SetTimeDisplay(1);
   throwsPawaysPhisto_copy__10->GetXaxis()->SetTimeFormat("#splitline{%b %d}{%Y} %F1970-01-01 00:00:00");
   throwsPawaysPhisto_copy__10->GetXaxis()->SetRange(1,1);
   throwsPawaysPhisto_copy__10->GetXaxis()->SetNdivisions(100503);
   throwsPawaysPhisto_copy__10->GetXaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__10->GetXaxis()->SetLabelOffset(0.025);
   throwsPawaysPhisto_copy__10->GetXaxis()->SetLabelSize(0.025);
   throwsPawaysPhisto_copy__10->GetXaxis()->SetTickLength(0.04);
   throwsPawaysPhisto_copy__10->GetXaxis()->SetTitleOffset(1);
   throwsPawaysPhisto_copy__10->GetXaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__10->GetYaxis()->SetTitle("CIS Calibration [ADC count/pC]");
   throwsPawaysPhisto_copy__10->GetYaxis()->SetRange(1,1);
   throwsPawaysPhisto_copy__10->GetYaxis()->CenterTitle(true);
   throwsPawaysPhisto_copy__10->GetYaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__10->GetYaxis()->SetTitleOffset(1.2);
   throwsPawaysPhisto_copy__10->GetYaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__10->GetZaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__10->GetZaxis()->SetTitleOffset(1);
   throwsPawaysPhisto_copy__10->GetZaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__10->Draw("sameaxis");
   
   TLegend *leg = new TLegend(0.2,0.23,0.6,0.28,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextFont(62);
   leg->SetTextSize(0.032);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   TLegendEntry *entry=leg->AddEntry("Graph0","Absolute Systematic Uncertainty #pm0.7%","F");

   ci = TColor::GetColor("#ffff00");
   entry->SetFillColor(ci);
   entry->SetFillStyle(1000);

   ci = TColor::GetColor("#ffff00");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   leg->Draw();
   
   leg = new TLegend(0.2,0.2793,0.65,0.3793,NULL,"brNDC");
   leg->SetBorderSize(0);
   leg->SetTextFont(62);
   leg->SetTextSize(0.032);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   entry=leg->AddEntry("Graph1","9708 Channel Average (RMS=0.03%)","p");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1.3);
   entry->SetTextFont(62);
   entry=leg->AddEntry("Graph0","Single Channel (Long Barrel, C-Side) (RMS=0.02%)","ep");

   ci = TColor::GetColor("#ffff00");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);

   ci = TColor::GetColor("#0000ff");
   entry->SetMarkerColor(ci);
   entry->SetMarkerStyle(23);
   entry->SetMarkerSize(1.3);
   entry->SetTextFont(62);
   leg->Draw();
   TLatex *   tex = new TLatex(0.2,0.832,"Tile Calorimeter");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.2,0.774,"Low-Gain ADCs");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.2,0.716,"February 2022");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
   c1_n1->Modified();
   c1_n1->cd();
   c1_n1->SetSelected(c1_n1);
}
