void LowgainDetAvg()
{
//=========Macro generated from canvas: c1_n1/c1
//=========  (Fri Mar  3 00:47:07 2023) by ROOT version 6.24/00
   TCanvas *c1_n1 = new TCanvas("c1_n1", "c1",0,0,800,602);
   gStyle->SetOptStat(0);
   c1_n1->SetHighLightColor(2);
   c1_n1->Range(1.653767e+09,1.236845,1.671636e+09,1.334917);
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
   
   TH2D *throwsPawaysPhisto__5 = new TH2D("throwsPawaysPhisto__5","",1,1.656626e+09,1.669849e+09,1,1.252537,1.330013);
   throwsPawaysPhisto__5->SetStats(0);
   throwsPawaysPhisto__5->SetLineWidth(2);
   throwsPawaysPhisto__5->SetMarkerStyle(20);
   throwsPawaysPhisto__5->SetMarkerSize(1.2);
   throwsPawaysPhisto__5->GetXaxis()->SetTimeDisplay(1);
   throwsPawaysPhisto__5->GetXaxis()->SetTimeFormat("#splitline{%b}{%Y} %F1970-01-01 00:00:00");
   throwsPawaysPhisto__5->GetXaxis()->SetRange(1,1);
   throwsPawaysPhisto__5->GetXaxis()->SetNdivisions(100505);
   throwsPawaysPhisto__5->GetXaxis()->SetLabelFont(42);
   throwsPawaysPhisto__5->GetXaxis()->SetLabelOffset(0.025);
   throwsPawaysPhisto__5->GetXaxis()->SetLabelSize(0.025);
   throwsPawaysPhisto__5->GetXaxis()->SetTickLength(0.04);
   throwsPawaysPhisto__5->GetXaxis()->SetTitleOffset(1);
   throwsPawaysPhisto__5->GetXaxis()->SetTitleFont(42);
   throwsPawaysPhisto__5->GetYaxis()->SetTitle("CIS Calibration [ADC count/pC]");
   throwsPawaysPhisto__5->GetYaxis()->SetRange(1,1);
   throwsPawaysPhisto__5->GetYaxis()->CenterTitle(true);
   throwsPawaysPhisto__5->GetYaxis()->SetLabelFont(42);
   throwsPawaysPhisto__5->GetYaxis()->SetTitleOffset(1.2);
   throwsPawaysPhisto__5->GetYaxis()->SetTitleFont(42);
   throwsPawaysPhisto__5->GetZaxis()->SetLabelFont(42);
   throwsPawaysPhisto__5->GetZaxis()->SetTitleOffset(1);
   throwsPawaysPhisto__5->GetZaxis()->SetTitleFont(42);
   throwsPawaysPhisto__5->Draw("");
   
   Double_t Graph0_fx1001[27] = {
   1.656585e+09,
   1.657894e+09,
   1.658136e+09,
   1.658729e+09,
   1.658838e+09,
   1.658997e+09,
   1.659346e+09,
   1.659706e+09,
   1.6602e+09,
   1.660577e+09,
   1.660638e+09,
   1.661176e+09,
   1.661419e+09,
   1.66202e+09,
   1.662363e+09,
   1.662968e+09,
   1.663572e+09,
   1.663838e+09,
   1.664182e+09,
   1.664778e+09,
   1.665677e+09,
   1.666079e+09,
   1.666589e+09,
   1.667208e+09,
   1.667623e+09,
   1.668695e+09,
   1.669304e+09};
   Double_t Graph0_fy1001[27] = {
   1.283791,
   1.283696,
   1.283875,
   1.283965,
   1.283693,
   1.283549,
   1.283765,
   1.283723,
   1.283626,
   1.283921,
   1.283697,
   1.283505,
   1.283817,
   1.283701,
   1.283597,
   1.283733,
   1.283718,
   1.284015,
   1.283904,
   1.283588,
   1.28361,
   1.284015,
   1.283707,
   1.283733,
   1.283951,
   1.283886,
   1.283829};
   Double_t Graph0_fex1001[27] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph0_fey1001[27] = {
   0.008986535,
   0.008985869,
   0.008987128,
   0.008987754,
   0.008985852,
   0.008984841,
   0.008986356,
   0.008986061,
   0.008985384,
   0.008987448,
   0.008985883,
   0.008984532,
   0.008986721,
   0.008985908,
   0.008985176,
   0.00898613,
   0.008986024,
   0.008988103,
   0.008987327,
   0.008985113,
   0.008985268,
   0.008988108,
   0.008985948,
   0.008986128,
   0.008987657,
   0.0089872,
   0.008986804};
   TGraphErrors *gre = new TGraphErrors(27,Graph0_fx1001,Graph0_fy1001,Graph0_fex1001,Graph0_fey1001);
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
   
   TH1F *Graph_Graph01001 = new TH1F("Graph_Graph01001","Graph",100,1.655313e+09,1.670576e+09);
   Graph_Graph01001->SetMinimum(1.272672);
   Graph_Graph01001->SetMaximum(1.294852);
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
   
   Double_t Graph0_fx1002[27] = {
   1.656585e+09,
   1.657894e+09,
   1.658136e+09,
   1.658729e+09,
   1.658838e+09,
   1.658997e+09,
   1.659346e+09,
   1.659706e+09,
   1.6602e+09,
   1.660577e+09,
   1.660638e+09,
   1.661176e+09,
   1.661419e+09,
   1.66202e+09,
   1.662363e+09,
   1.662968e+09,
   1.663572e+09,
   1.663838e+09,
   1.664182e+09,
   1.664778e+09,
   1.665677e+09,
   1.666079e+09,
   1.666589e+09,
   1.667208e+09,
   1.667623e+09,
   1.668695e+09,
   1.669304e+09};
   Double_t Graph0_fy1002[27] = {
   1.283791,
   1.283696,
   1.283875,
   1.283965,
   1.283693,
   1.283549,
   1.283765,
   1.283723,
   1.283626,
   1.283921,
   1.283697,
   1.283505,
   1.283817,
   1.283701,
   1.283597,
   1.283733,
   1.283718,
   1.284015,
   1.283904,
   1.283588,
   1.28361,
   1.284015,
   1.283707,
   1.283733,
   1.283951,
   1.283886,
   1.283829};
   Double_t Graph0_fex1002[27] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph0_fey1002[27] = {
   0.008986535,
   0.008985869,
   0.008987128,
   0.008987754,
   0.008985852,
   0.008984841,
   0.008986356,
   0.008986061,
   0.008985384,
   0.008987448,
   0.008985883,
   0.008984532,
   0.008986721,
   0.008985908,
   0.008985176,
   0.00898613,
   0.008986024,
   0.008988103,
   0.008987327,
   0.008985113,
   0.008985268,
   0.008988108,
   0.008985948,
   0.008986128,
   0.008987657,
   0.0089872,
   0.008986804};
   gre = new TGraphErrors(27,Graph0_fx1002,Graph0_fy1002,Graph0_fex1002,Graph0_fey1002);
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
   
   TH1F *Graph_Graph_Graph010011002 = new TH1F("Graph_Graph_Graph010011002","Graph",100,1.655313e+09,1.670576e+09);
   Graph_Graph_Graph010011002->SetMinimum(1.272672);
   Graph_Graph_Graph010011002->SetMaximum(1.294852);
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
   
   Double_t Graph1_fx1003[27] = {
   1.656585e+09,
   1.657894e+09,
   1.658136e+09,
   1.658729e+09,
   1.658838e+09,
   1.658997e+09,
   1.659346e+09,
   1.659706e+09,
   1.6602e+09,
   1.660577e+09,
   1.660638e+09,
   1.661176e+09,
   1.661419e+09,
   1.66202e+09,
   1.662363e+09,
   1.662968e+09,
   1.663572e+09,
   1.663838e+09,
   1.664182e+09,
   1.664778e+09,
   1.665677e+09,
   1.666079e+09,
   1.666589e+09,
   1.667208e+09,
   1.667623e+09,
   1.668695e+09,
   1.669304e+09};
   Double_t Graph1_fy1003[27] = {
   1.291264,
   1.291299,
   1.291318,
   1.291309,
   1.291296,
   1.291298,
   1.291323,
   1.291297,
   1.291179,
   1.291292,
   1.291282,
   1.291266,
   1.291292,
   1.291287,
   1.29128,
   1.291313,
   1.291321,
   1.29133,
   1.291309,
   1.291311,
   1.291227,
   1.291247,
   1.291135,
   1.291158,
   1.291209,
   1.291257,
   1.29132};
   Double_t Graph1_fex1003[27] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph1_fey1003[27] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   gre = new TGraphErrors(27,Graph1_fx1003,Graph1_fy1003,Graph1_fex1003,Graph1_fey1003);
   gre->SetName("Graph1");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetMarkerStyle(20);
   gre->SetMarkerSize(1.3);
   
   TH1F *Graph_Graph11003 = new TH1F("Graph_Graph11003","Graph",100,1.655313e+09,1.670576e+09);
   Graph_Graph11003->SetMinimum(1.291115);
   Graph_Graph11003->SetMaximum(1.29135);
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
   
   TH2D *throwsPawaysPhisto_copy__6 = new TH2D("throwsPawaysPhisto_copy__6","",1,1.656626e+09,1.669849e+09,1,1.252537,1.330013);
   throwsPawaysPhisto_copy__6->SetDirectory(0);
   throwsPawaysPhisto_copy__6->SetStats(0);
   throwsPawaysPhisto_copy__6->SetLineWidth(2);
   throwsPawaysPhisto_copy__6->SetMarkerStyle(20);
   throwsPawaysPhisto_copy__6->SetMarkerSize(1.2);
   throwsPawaysPhisto_copy__6->GetXaxis()->SetTimeDisplay(1);
   throwsPawaysPhisto_copy__6->GetXaxis()->SetTimeFormat("#splitline{%b}{%Y} %F1970-01-01 00:00:00");
   throwsPawaysPhisto_copy__6->GetXaxis()->SetRange(1,1);
   throwsPawaysPhisto_copy__6->GetXaxis()->SetNdivisions(100505);
   throwsPawaysPhisto_copy__6->GetXaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__6->GetXaxis()->SetLabelOffset(0.025);
   throwsPawaysPhisto_copy__6->GetXaxis()->SetLabelSize(0.025);
   throwsPawaysPhisto_copy__6->GetXaxis()->SetTickLength(0.04);
   throwsPawaysPhisto_copy__6->GetXaxis()->SetTitleOffset(1);
   throwsPawaysPhisto_copy__6->GetXaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__6->GetYaxis()->SetTitle("CIS Calibration [ADC count/pC]");
   throwsPawaysPhisto_copy__6->GetYaxis()->SetRange(1,1);
   throwsPawaysPhisto_copy__6->GetYaxis()->CenterTitle(true);
   throwsPawaysPhisto_copy__6->GetYaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__6->GetYaxis()->SetTitleOffset(1.2);
   throwsPawaysPhisto_copy__6->GetYaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__6->GetZaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__6->GetZaxis()->SetTitleOffset(1);
   throwsPawaysPhisto_copy__6->GetZaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__6->Draw("sameaxis");
   
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
   entry=leg->AddEntry("Graph1","9671 Channel Average (RMS=0.03%)","p");
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
   TLatex *   tex = new TLatex(0.2,0.88,"ATLAS");
tex->SetNDC();
   tex->SetTextFont(72);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.29,0.88,"Preliminary");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.2,0.832,"Tile Calorimeter");
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
      tex = new TLatex(0.2,0.716,"July 1 - December 1, 2022");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
   c1_n1->Modified();
   c1_n1->cd();
   c1_n1->SetSelected(c1_n1);
}
