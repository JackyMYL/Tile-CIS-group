void HighgainDetAvg()
{
//=========Macro generated from canvas: c1_n1/c1
//=========  (Fri Mar  3 00:47:07 2023) by ROOT version 6.24/00
   TCanvas *c1_n1 = new TCanvas("c1_n1", "c1",1,1,800,578);
   gStyle->SetOptStat(0);
   c1_n1->SetHighLightColor(2);
   c1_n1->Range(1.653767e+09,77.80936,1.671636e+09,83.979);
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
   
   TH2D *throwsPawaysPhisto__7 = new TH2D("throwsPawaysPhisto__7","",1,1.656626e+09,1.669849e+09,1,78.7965,83.67052);
   throwsPawaysPhisto__7->SetStats(0);
   throwsPawaysPhisto__7->SetLineWidth(2);
   throwsPawaysPhisto__7->SetMarkerStyle(20);
   throwsPawaysPhisto__7->SetMarkerSize(1.2);
   throwsPawaysPhisto__7->GetXaxis()->SetTimeDisplay(1);
   throwsPawaysPhisto__7->GetXaxis()->SetTimeFormat("#splitline{%b}{%Y} %F1970-01-01 00:00:00");
   throwsPawaysPhisto__7->GetXaxis()->SetRange(1,1);
   throwsPawaysPhisto__7->GetXaxis()->SetNdivisions(100505);
   throwsPawaysPhisto__7->GetXaxis()->SetLabelFont(42);
   throwsPawaysPhisto__7->GetXaxis()->SetLabelOffset(0.025);
   throwsPawaysPhisto__7->GetXaxis()->SetLabelSize(0.025);
   throwsPawaysPhisto__7->GetXaxis()->SetTickLength(0.04);
   throwsPawaysPhisto__7->GetXaxis()->SetTitleOffset(1);
   throwsPawaysPhisto__7->GetXaxis()->SetTitleFont(42);
   throwsPawaysPhisto__7->GetYaxis()->SetTitle("CIS Calibration [ADC count/pC]");
   throwsPawaysPhisto__7->GetYaxis()->SetRange(1,1);
   throwsPawaysPhisto__7->GetYaxis()->CenterTitle(true);
   throwsPawaysPhisto__7->GetYaxis()->SetLabelFont(42);
   throwsPawaysPhisto__7->GetYaxis()->SetTitleOffset(1.2);
   throwsPawaysPhisto__7->GetYaxis()->SetTitleFont(42);
   throwsPawaysPhisto__7->GetZaxis()->SetLabelFont(42);
   throwsPawaysPhisto__7->GetZaxis()->SetTitleOffset(1);
   throwsPawaysPhisto__7->GetZaxis()->SetTitleFont(42);
   throwsPawaysPhisto__7->Draw("");
   
   Double_t Graph0_fx1004[27] = {
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
   Double_t Graph0_fy1004[27] = {
   81.35168,
   81.34795,
   81.36901,
   81.36443,
   81.36292,
   81.33907,
   81.3401,
   81.32051,
   81.35043,
   81.3868,
   81.33913,
   81.33408,
   81.37452,
   81.34234,
   81.3495,
   81.3519,
   81.34476,
   81.3668,
   81.36753,
   81.34709,
   81.34023,
   81.3707,
   81.36795,
   81.36209,
   81.35599,
   81.34086,
   81.3461};
   Double_t Graph0_fex1004[27] = {
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
   Double_t Graph0_fey1004[27] = {
   0.5694618,
   0.5694357,
   0.5695831,
   0.5695511,
   0.5695404,
   0.5693735,
   0.5693806,
   0.5692436,
   0.569453,
   0.5697076,
   0.5693739,
   0.5693386,
   0.5696216,
   0.5693964,
   0.5694465,
   0.5694633,
   0.5694134,
   0.5695676,
   0.5695727,
   0.5694296,
   0.5693817,
   0.5695949,
   0.5695757,
   0.5695347,
   0.5694919,
   0.569386,
   0.5694227};
   TGraphErrors *gre = new TGraphErrors(27,Graph0_fx1004,Graph0_fy1004,Graph0_fex1004,Graph0_fey1004);
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
   
   TH1F *Graph_Graph01004 = new TH1F("Graph_Graph01004","Graph",100,1.655313e+09,1.670576e+09);
   Graph_Graph01004->SetMinimum(80.63074);
   Graph_Graph01004->SetMaximum(82.07703);
   Graph_Graph01004->SetDirectory(0);
   Graph_Graph01004->SetStats(0);
   Graph_Graph01004->SetLineWidth(2);
   Graph_Graph01004->SetMarkerStyle(20);
   Graph_Graph01004->SetMarkerSize(1.2);
   Graph_Graph01004->GetXaxis()->SetNdivisions(509);
   Graph_Graph01004->GetXaxis()->SetLabelFont(42);
   Graph_Graph01004->GetXaxis()->SetTitleOffset(1);
   Graph_Graph01004->GetXaxis()->SetTitleFont(42);
   Graph_Graph01004->GetYaxis()->SetNdivisions(305);
   Graph_Graph01004->GetYaxis()->SetLabelFont(42);
   Graph_Graph01004->GetYaxis()->SetTitleOffset(1);
   Graph_Graph01004->GetYaxis()->SetTitleFont(42);
   Graph_Graph01004->GetZaxis()->SetLabelFont(42);
   Graph_Graph01004->GetZaxis()->SetTitleOffset(1);
   Graph_Graph01004->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_Graph01004);
   
   gre->Draw("e3");
   
   Double_t Graph0_fx1005[27] = {
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
   Double_t Graph0_fy1005[27] = {
   81.35168,
   81.34795,
   81.36901,
   81.36443,
   81.36292,
   81.33907,
   81.3401,
   81.32051,
   81.35043,
   81.3868,
   81.33913,
   81.33408,
   81.37452,
   81.34234,
   81.3495,
   81.3519,
   81.34476,
   81.3668,
   81.36753,
   81.34709,
   81.34023,
   81.3707,
   81.36795,
   81.36209,
   81.35599,
   81.34086,
   81.3461};
   Double_t Graph0_fex1005[27] = {
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
   Double_t Graph0_fey1005[27] = {
   0.5694618,
   0.5694357,
   0.5695831,
   0.5695511,
   0.5695404,
   0.5693735,
   0.5693806,
   0.5692436,
   0.569453,
   0.5697076,
   0.5693739,
   0.5693386,
   0.5696216,
   0.5693964,
   0.5694465,
   0.5694633,
   0.5694134,
   0.5695676,
   0.5695727,
   0.5694296,
   0.5693817,
   0.5695949,
   0.5695757,
   0.5695347,
   0.5694919,
   0.569386,
   0.5694227};
   gre = new TGraphErrors(27,Graph0_fx1005,Graph0_fy1005,Graph0_fex1005,Graph0_fey1005);
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
   
   TH1F *Graph_Graph_Graph010041005 = new TH1F("Graph_Graph_Graph010041005","Graph",100,1.655313e+09,1.670576e+09);
   Graph_Graph_Graph010041005->SetMinimum(80.63074);
   Graph_Graph_Graph010041005->SetMaximum(82.07703);
   Graph_Graph_Graph010041005->SetDirectory(0);
   Graph_Graph_Graph010041005->SetStats(0);
   Graph_Graph_Graph010041005->SetLineWidth(2);
   Graph_Graph_Graph010041005->SetMarkerStyle(20);
   Graph_Graph_Graph010041005->SetMarkerSize(1.2);
   Graph_Graph_Graph010041005->GetXaxis()->SetNdivisions(509);
   Graph_Graph_Graph010041005->GetXaxis()->SetLabelFont(42);
   Graph_Graph_Graph010041005->GetXaxis()->SetTitleOffset(1);
   Graph_Graph_Graph010041005->GetXaxis()->SetTitleFont(42);
   Graph_Graph_Graph010041005->GetYaxis()->SetNdivisions(305);
   Graph_Graph_Graph010041005->GetYaxis()->SetLabelFont(42);
   Graph_Graph_Graph010041005->GetYaxis()->SetTitleOffset(1);
   Graph_Graph_Graph010041005->GetYaxis()->SetTitleFont(42);
   Graph_Graph_Graph010041005->GetZaxis()->SetLabelFont(42);
   Graph_Graph_Graph010041005->GetZaxis()->SetTitleOffset(1);
   Graph_Graph_Graph010041005->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_Graph_Graph010041005);
   
   gre->Draw("p");
   
   Double_t Graph1_fx1006[27] = {
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
   Double_t Graph1_fy1006[27] = {
   81.23217,
   81.23654,
   81.2356,
   81.23621,
   81.23431,
   81.23466,
   81.23752,
   81.23261,
   81.23411,
   81.23204,
   81.23382,
   81.23278,
   81.23343,
   81.23766,
   81.23541,
   81.23508,
   81.23699,
   81.23715,
   81.23525,
   81.2356,
   81.22998,
   81.23219,
   81.22314,
   81.22712,
   81.22933,
   81.2308,
   81.23325};
   Double_t Graph1_fex1006[27] = {
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
   Double_t Graph1_fey1006[27] = {
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
   gre = new TGraphErrors(27,Graph1_fx1006,Graph1_fy1006,Graph1_fex1006,Graph1_fey1006);
   gre->SetName("Graph1");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetMarkerStyle(20);
   gre->SetMarkerSize(1.3);
   
   TH1F *Graph_Graph11006 = new TH1F("Graph_Graph11006","Graph",100,1.655313e+09,1.670576e+09);
   Graph_Graph11006->SetMinimum(81.22168);
   Graph_Graph11006->SetMaximum(81.23912);
   Graph_Graph11006->SetDirectory(0);
   Graph_Graph11006->SetStats(0);
   Graph_Graph11006->SetLineWidth(2);
   Graph_Graph11006->SetMarkerStyle(20);
   Graph_Graph11006->SetMarkerSize(1.2);
   Graph_Graph11006->GetXaxis()->SetNdivisions(509);
   Graph_Graph11006->GetXaxis()->SetLabelFont(42);
   Graph_Graph11006->GetXaxis()->SetTitleOffset(1);
   Graph_Graph11006->GetXaxis()->SetTitleFont(42);
   Graph_Graph11006->GetYaxis()->SetNdivisions(305);
   Graph_Graph11006->GetYaxis()->SetLabelFont(42);
   Graph_Graph11006->GetYaxis()->SetTitleOffset(1);
   Graph_Graph11006->GetYaxis()->SetTitleFont(42);
   Graph_Graph11006->GetZaxis()->SetLabelFont(42);
   Graph_Graph11006->GetZaxis()->SetTitleOffset(1);
   Graph_Graph11006->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_Graph11006);
   
   gre->Draw("p");
   
   TH2D *throwsPawaysPhisto_copy__8 = new TH2D("throwsPawaysPhisto_copy__8","",1,1.656626e+09,1.669849e+09,1,78.7965,83.67052);
   throwsPawaysPhisto_copy__8->SetDirectory(0);
   throwsPawaysPhisto_copy__8->SetStats(0);
   throwsPawaysPhisto_copy__8->SetLineWidth(2);
   throwsPawaysPhisto_copy__8->SetMarkerStyle(20);
   throwsPawaysPhisto_copy__8->SetMarkerSize(1.2);
   throwsPawaysPhisto_copy__8->GetXaxis()->SetTimeDisplay(1);
   throwsPawaysPhisto_copy__8->GetXaxis()->SetTimeFormat("#splitline{%b}{%Y} %F1970-01-01 00:00:00");
   throwsPawaysPhisto_copy__8->GetXaxis()->SetRange(1,1);
   throwsPawaysPhisto_copy__8->GetXaxis()->SetNdivisions(100505);
   throwsPawaysPhisto_copy__8->GetXaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__8->GetXaxis()->SetLabelOffset(0.025);
   throwsPawaysPhisto_copy__8->GetXaxis()->SetLabelSize(0.025);
   throwsPawaysPhisto_copy__8->GetXaxis()->SetTickLength(0.04);
   throwsPawaysPhisto_copy__8->GetXaxis()->SetTitleOffset(1);
   throwsPawaysPhisto_copy__8->GetXaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__8->GetYaxis()->SetTitle("CIS Calibration [ADC count/pC]");
   throwsPawaysPhisto_copy__8->GetYaxis()->SetRange(1,1);
   throwsPawaysPhisto_copy__8->GetYaxis()->CenterTitle(true);
   throwsPawaysPhisto_copy__8->GetYaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__8->GetYaxis()->SetTitleOffset(1.2);
   throwsPawaysPhisto_copy__8->GetYaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__8->GetZaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__8->GetZaxis()->SetTitleOffset(1);
   throwsPawaysPhisto_copy__8->GetZaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__8->Draw("sameaxis");
   
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
   entry=leg->AddEntry("Graph1","9605 Channel Average (RMS=0.04%)","p");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(20);
   entry->SetMarkerSize(1.3);
   entry->SetTextFont(62);
   entry=leg->AddEntry("Graph0","Single Channel (Long Barrel, C-Side) (RMS=0.03%)","ep");

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
      tex = new TLatex(0.2,0.774,"High-Gain ADCs");
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
