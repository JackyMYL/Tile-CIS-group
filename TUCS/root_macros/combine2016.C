#include "TCanvas.h"
#include "TLatex.h"
#include "TGraphErrors.h"
#include "TMath.h"
#include "TAxis.h"
#include <vector>
void combine2016()
{

  auto mycanvas = new TCanvas();
  const int n1_points = 4; //A-cells
  double x1_vals[n1_points] = {2.68,3.11,2.86,3.05};
  double y1_vals[n1_points] = {187.26,207.70,209.56,201.70};
  double y1_errs[n1_points] = {5.70,8.24,9.25,7.7};
  //  double x1_errs[n1_points] = {;

  const int n2_points = 4; //E-cells
  double x2_vals[n2_points] = {3.36,4.20,4.30,5.25};
  double y2_vals[n2_points] = {230.46,271.26,244.21,271.22};
  double y2_errs[n2_points] = {12.4,21.9,13.80,18.18};

  auto graph1 = new TGraphErrors(n1_points, y1_vals, x1_vals, y1_errs, nullptr);
  auto graph2 = new TGraphErrors(n2_points, y2_vals, x2_vals, y2_errs, nullptr);
  graph1 -> SetTitle("2016 Time const");

  graph1 -> SetMarkerStyle(kOpenCircle);
  graph1 -> SetMarkerColor(kBlue);
  graph1 -> SetLineColor(kBlue);
  // graph1 -> GetXaxis()->SetMinimum(180.0);
 
  graph2 -> SetMarkerStyle(kOpenSquare);
  graph2 -> SetMarkerColor(kRed);
  graph2 -> SetLineColor(kRed);
  graph1 -> GetXaxis()->SetTitle("Time Constant (days)");
  graph1 -> GetYaxis()->SetTitle("A-B");
  graph1 -> Draw("APE");
  graph2 -> Draw("P,same");
  // graph1 -> GetYaxis->SetRangeUser(-4.5,4.5);
  graph1 -> GetXaxis()->SetLimits(170,300); 
  graph1 -> Draw("APE");
  graph2 -> Draw("P,same");
  mycanvas -> Update();



}
