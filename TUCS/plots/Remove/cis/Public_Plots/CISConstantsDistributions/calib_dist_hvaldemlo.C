void calib_dist_hvaldemlo()
{
//=========Macro generated from canvas: c1_n2/c1
//=========  (Fri Mar  3 19:51:04 2023) by ROOT version 6.24/00
   TCanvas *c1_n2 = new TCanvas("c1_n2", "c1",1,1,800,578);
   gStyle->SetOptStat(0);
   c1_n2->SetHighLightColor(2);
   c1_n2->Range(1.132833,-6.075949,1.455167,31.89873);
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
   
   TH1D *hvaldemlo__8 = new TH1D("hvaldemlo__8","",15,1.17796,1.41004);
   hvaldemlo__8->SetBinContent(0,45);
   hvaldemlo__8->SetBinContent(1,45);
   hvaldemlo__8->SetMinimum(0);
   hvaldemlo__8->SetMaximum(30);
   hvaldemlo__8->SetEntries(47);
   hvaldemlo__8->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   hvaldemlo__8->SetLineColor(ci);
   hvaldemlo__8->SetLineWidth(2);
   hvaldemlo__8->SetMarkerStyle(20);
   hvaldemlo__8->SetMarkerSize(1.2);
   hvaldemlo__8->GetXaxis()->SetTitle("Mean Dem. Low-GainCIS Constant [ADC counts / pC]");
   hvaldemlo__8->GetXaxis()->CenterTitle(true);
   hvaldemlo__8->GetXaxis()->SetNdivisions(509);
   hvaldemlo__8->GetXaxis()->SetLabelFont(42);
   hvaldemlo__8->GetXaxis()->SetTitleOffset(1);
   hvaldemlo__8->GetXaxis()->SetTitleFont(42);
   hvaldemlo__8->GetYaxis()->SetTitle("Number of ADC Channels");
   hvaldemlo__8->GetYaxis()->SetNdivisions(305);
   hvaldemlo__8->GetYaxis()->SetLabelFont(42);
   hvaldemlo__8->GetYaxis()->SetTitleOffset(1.4);
   hvaldemlo__8->GetYaxis()->SetTitleFont(42);
   hvaldemlo__8->GetZaxis()->SetLabelFont(42);
   hvaldemlo__8->GetZaxis()->SetTitleOffset(1);
   hvaldemlo__8->GetZaxis()->SetTitleFont(42);
   hvaldemlo__8->Draw("");
   TLatex *   tex = new TLatex(0.18,0.785,"Dem. Low-Gain");
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
      tex = new TLatex(0.59,0.865,"Mean  1.18");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.59,0.825,"RMS/Mean  0.657%");
tex->SetNDC();
   tex->SetTextFont(42);
   tex->SetTextSize(0.035);
   tex->SetLineWidth(2);
   tex->Draw();
   c1_n2->Modified();
   c1_n2->cd();
   c1_n2->SetSelected(c1_n2);
}
