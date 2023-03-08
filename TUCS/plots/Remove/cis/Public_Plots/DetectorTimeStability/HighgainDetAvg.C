void HighgainDetAvg()
{
//=========Macro generated from canvas: c1_n1/c1
//=========  (Fri Mar  3 19:51:14 2023) by ROOT version 6.24/00
   TCanvas *c1_n1 = new TCanvas("c1_n1", "c1",1,1,800,578);
   gStyle->SetOptStat(0);
   c1_n1->SetHighLightColor(2);
   c1_n1->Range(1.636347e+09,77.82405,1.682116e+09,83.99485);
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
   
   TH2D *throwsPawaysPhisto__11 = new TH2D("throwsPawaysPhisto__11","",1,1.64367e+09,1.677539e+09,1,78.81138,83.68631);
   throwsPawaysPhisto__11->SetStats(0);
   throwsPawaysPhisto__11->SetLineWidth(2);
   throwsPawaysPhisto__11->SetMarkerStyle(20);
   throwsPawaysPhisto__11->SetMarkerSize(1.2);
   throwsPawaysPhisto__11->GetXaxis()->SetTimeDisplay(1);
   throwsPawaysPhisto__11->GetXaxis()->SetTimeFormat("#splitline{%b}{%Y} %F1970-01-01 00:00:00");
   throwsPawaysPhisto__11->GetXaxis()->SetRange(1,1);
   throwsPawaysPhisto__11->GetXaxis()->SetNdivisions(100506);
   throwsPawaysPhisto__11->GetXaxis()->SetLabelFont(42);
   throwsPawaysPhisto__11->GetXaxis()->SetLabelOffset(0.025);
   throwsPawaysPhisto__11->GetXaxis()->SetLabelSize(0.025);
   throwsPawaysPhisto__11->GetXaxis()->SetTickLength(0.04);
   throwsPawaysPhisto__11->GetXaxis()->SetTitleOffset(1);
   throwsPawaysPhisto__11->GetXaxis()->SetTitleFont(42);
   throwsPawaysPhisto__11->GetYaxis()->SetTitle("CIS Calibration [ADC count/pC]");
   throwsPawaysPhisto__11->GetYaxis()->SetRange(1,1);
   throwsPawaysPhisto__11->GetYaxis()->CenterTitle(true);
   throwsPawaysPhisto__11->GetYaxis()->SetLabelFont(42);
   throwsPawaysPhisto__11->GetYaxis()->SetTitleOffset(1.2);
   throwsPawaysPhisto__11->GetYaxis()->SetTitleFont(42);
   throwsPawaysPhisto__11->GetZaxis()->SetLabelFont(42);
   throwsPawaysPhisto__11->GetZaxis()->SetTitleOffset(1);
   throwsPawaysPhisto__11->GetZaxis()->SetTitleFont(42);
   throwsPawaysPhisto__11->Draw("");
   
   Double_t Graph0_fx1004[7] = {
   1.675363e+09,
   1.67551e+09,
   1.675708e+09,
   1.676062e+09,
   1.67675e+09,
   1.676979e+09,
   1.677522e+09};
   Double_t Graph0_fy1004[7] = {
   81.34795,
   81.33356,
   81.35564,
   81.34798,
   81.34045,
   81.3435,
   81.3524};
   Double_t Graph0_fex1004[7] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph0_fey1004[7] = {
   0.5694356,
   0.5693349,
   0.5694895,
   0.5694358,
   0.5693831,
   0.5694045,
   0.5694668};
   TGraphErrors *gre = new TGraphErrors(7,Graph0_fx1004,Graph0_fy1004,Graph0_fex1004,Graph0_fey1004);
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
   
   TH1F *Graph_Graph01004 = new TH1F("Graph_Graph01004","Graph",100,1.675147e+09,1.677738e+09);
   Graph_Graph01004->SetMinimum(80.64813);
   Graph_Graph01004->SetMaximum(82.04122);
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
   
   Double_t Graph0_fx1005[7] = {
   1.675363e+09,
   1.67551e+09,
   1.675708e+09,
   1.676062e+09,
   1.67675e+09,
   1.676979e+09,
   1.677522e+09};
   Double_t Graph0_fy1005[7] = {
   81.34795,
   81.33356,
   81.35564,
   81.34798,
   81.34045,
   81.3435,
   81.3524};
   Double_t Graph0_fex1005[7] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph0_fey1005[7] = {
   0.5694356,
   0.5693349,
   0.5694895,
   0.5694358,
   0.5693831,
   0.5694045,
   0.5694668};
   gre = new TGraphErrors(7,Graph0_fx1005,Graph0_fy1005,Graph0_fex1005,Graph0_fey1005);
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
   
   TH1F *Graph_Graph_Graph010041005 = new TH1F("Graph_Graph_Graph010041005","Graph",100,1.675147e+09,1.677738e+09);
   Graph_Graph_Graph010041005->SetMinimum(80.64813);
   Graph_Graph_Graph010041005->SetMaximum(82.04122);
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
   
   Double_t Graph1_fx1006[7] = {
   1.675363e+09,
   1.67551e+09,
   1.675708e+09,
   1.676062e+09,
   1.67675e+09,
   1.676979e+09,
   1.677522e+09};
   Double_t Graph1_fy1006[7] = {
   81.25401,
   81.24812,
   81.24663,
   81.2588,
   81.24883,
   81.24323,
   81.24229};
   Double_t Graph1_fex1006[7] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph1_fey1006[7] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   gre = new TGraphErrors(7,Graph1_fx1006,Graph1_fy1006,Graph1_fex1006,Graph1_fey1006);
   gre->SetName("Graph1");
   gre->SetTitle("Graph");
   gre->SetFillStyle(1000);
   gre->SetMarkerStyle(20);
   gre->SetMarkerSize(1.3);
   
   TH1F *Graph_Graph11006 = new TH1F("Graph_Graph11006","Graph",100,1.675147e+09,1.677738e+09);
   Graph_Graph11006->SetMinimum(81.24064);
   Graph_Graph11006->SetMaximum(81.26046);
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
   
   TH2D *throwsPawaysPhisto_copy__12 = new TH2D("throwsPawaysPhisto_copy__12","",1,1.64367e+09,1.677539e+09,1,78.81138,83.68631);
   throwsPawaysPhisto_copy__12->SetDirectory(0);
   throwsPawaysPhisto_copy__12->SetStats(0);
   throwsPawaysPhisto_copy__12->SetLineWidth(2);
   throwsPawaysPhisto_copy__12->SetMarkerStyle(20);
   throwsPawaysPhisto_copy__12->SetMarkerSize(1.2);
   throwsPawaysPhisto_copy__12->GetXaxis()->SetTimeDisplay(1);
   throwsPawaysPhisto_copy__12->GetXaxis()->SetTimeFormat("#splitline{%b}{%Y} %F1970-01-01 00:00:00");
   throwsPawaysPhisto_copy__12->GetXaxis()->SetRange(1,1);
   throwsPawaysPhisto_copy__12->GetXaxis()->SetNdivisions(100506);
   throwsPawaysPhisto_copy__12->GetXaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__12->GetXaxis()->SetLabelOffset(0.025);
   throwsPawaysPhisto_copy__12->GetXaxis()->SetLabelSize(0.025);
   throwsPawaysPhisto_copy__12->GetXaxis()->SetTickLength(0.04);
   throwsPawaysPhisto_copy__12->GetXaxis()->SetTitleOffset(1);
   throwsPawaysPhisto_copy__12->GetXaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__12->GetYaxis()->SetTitle("CIS Calibration [ADC count/pC]");
   throwsPawaysPhisto_copy__12->GetYaxis()->SetRange(1,1);
   throwsPawaysPhisto_copy__12->GetYaxis()->CenterTitle(true);
   throwsPawaysPhisto_copy__12->GetYaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__12->GetYaxis()->SetTitleOffset(1.2);
   throwsPawaysPhisto_copy__12->GetYaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__12->GetZaxis()->SetLabelFont(42);
   throwsPawaysPhisto_copy__12->GetZaxis()->SetTitleOffset(1);
   throwsPawaysPhisto_copy__12->GetZaxis()->SetTitleFont(42);
   throwsPawaysPhisto_copy__12->Draw("sameaxis");
   
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
   entry=leg->AddEntry("Graph1","9644 Channel Average (RMS=0.04%)","p");
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
   TLatex *   tex = new TLatex(0.2,0.832,"Tile Calorimeter");
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
