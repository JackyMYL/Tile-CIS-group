void calib_dist_hvaldem()
{
//=========Macro generated from canvas: c1_n2/c1
//=========  (Fri Mar  3 20:13:27 2023) by ROOT version 6.24/00
   TCanvas *c1_n2 = new TCanvas("c1_n2", "c1",1,1,800,578);
   gStyle->SetOptStat(0);
   c1_n2->SetHighLightColor(2);
   c1_n2->Range(38.91667,-6.075949,43.08333,31.89873);
   c1_n2->SetFillColor(0);
   c1_n2->SetBorderMode(0);
   c1_n2->SetBorderSize(0);
   c1_n2->SetTickx(1);
   c1_n2->SetTicky(1);
   c1_n2->SetLeftMargin(0.14);
   c1_n2->SetRightMargin(0.14);
   c1_n2->SetTopMargin(0.05);
   c1_n2->SetBottomMargin(0.16);
   c1_n2->SetFrameBorderMode(0);
   c1_n2->SetFrameBorderMode(0);
   
   TH1D *hvaldem__7 = new TH1D("hvaldem__7","",15,39.5,42.5);
   hvaldem__7->SetBinContent(0,45);
   hvaldem__7->SetBinContent(1,45);
   hvaldem__7->SetMinimum(0);
   hvaldem__7->SetMaximum(30);
   hvaldem__7->SetEntries(47);
   hvaldem__7->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   hvaldem__7->SetLineColor(ci);
   hvaldem__7->SetLineWidth(2);
   hvaldem__7->SetMarkerStyle(20);
   hvaldem__7->SetMarkerSize(1.2);
   hvaldem__7->GetXaxis()->SetTitle("Mean Dem. High-GainCIS Constant [ADC counts / pC]");
   hvaldem__7->GetXaxis()->CenterTitle(true);
   hvaldem__7->GetXaxis()->SetNdivisions(509);
   hvaldem__7->GetXaxis()->SetLabelFont(42);
   hvaldem__7->GetXaxis()->SetTitleOffset(1);
   hvaldem__7->GetXaxis()->SetTitleFont(42);
   hvaldem__7->GetYaxis()->SetTitle("Number of ADC Channels");
   hvaldem__7->GetYaxis()->SetNdivisions(305);
   hvaldem__7->GetYaxis()->SetLabelFont(42);
   hvaldem__7->GetYaxis()->SetTitleOffset(1.4);
   hvaldem__7->GetYaxis()->SetTitleFont(42);
   hvaldem__7->GetZaxis()->SetLabelFont(42);
   hvaldem__7->GetZaxis()->SetTitleOffset(1);
   hvaldem__7->GetZaxis()->SetTitleFont(42);
   hvaldem__7->Draw("");
   TLatex *   tex = new TLatex(0.18,0.785,"Dem. High-Gain");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.18,0.825,"Tile Calorimeter");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.18,0.745,"February 2022");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.59,0.865,"Mean  39.5");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.59,0.825,"RMS/Mean  0.253%");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
   c1_n2->Modified();
   c1_n2->cd();
   c1_n2->SetSelected(c1_n2);
}
