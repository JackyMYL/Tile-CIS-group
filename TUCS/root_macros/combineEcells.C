#include "TCanvas.h"
#include "TLatex.h"
#include "TGraphErrors.h"
#include "TMath.h"
#include "TAxis.h"
#include <vector>

void combineEcells()
{

auto mycanvas = new TCanvas();

  const int n2_points = 12;
  double x2_vals[n2_points] = {1.56,1.48,1.79,1.52};
  double y2_vals[n2_points] = {55.80, 61.74, 51.83, 56.58};
  double y2_errs[n2_points] = {3.64, 4.07, 2.66, 2.60};
  double x2_errs[n2_points] = {-0.01,-0.02,-0.02,-0.02};

  const int n4_points = 4;
  double x4_vals[n4_points] = {3.36,4.20,4.30,5.25};
  double y4_vals[n4_points] = {230.46,271.26,244.21,271.22};
  double y4_errs[n4_points] = {12.4,21.9,13.80,18.18};

  const int n6_points = 4;
  double x6_vals[n6_points] =  {5.64,7.59,5.07,4.78};
  double y6_vals[n6_points] =  {60.50,105.16,91.50,78.36};
  double y6_errs[n6_points] =  {12.6,28.6,33.6,27.4};

  auto graph2 = new TGraphErrors(n2_points, y2_vals, x2_vals, y2_errs, x2_errs);
  auto graph4 = new TGraphErrors(n4_points, y4_vals, x4_vals, y4_errs, nullptr);
  auto graph6 = new TGraphErrors(n6_points, y6_vals, x6_vals, y6_errs, nullptr);

  graph2 -> SetTitle("E-cells Time const");

  graph2 -> SetMarkerStyle(kOpenSquare);
  graph2 -> SetMarkerColor(kBlue);
  graph2 -> SetLineColor(kBlue);
  graph2 -> GetXaxis()->SetTitle("Time Constant (days)");
  graph2 -> GetYaxis()->SetTitle("A-B");

  graph4 -> SetMarkerStyle(kOpenSquare);
  graph4 -> SetMarkerColor(kRed);
  graph4 -> SetLineColor(kRed);

  // graph6 -> SetMarkerStyle(kOpenTriangle);
  graph6 -> SetMarkerColor(kGreen);
  graph6 -> SetLineColor(kGreen);

  graph2 -> Draw("APE");
  graph4 -> Draw("P,same");
  graph6 -> Draw("P,same*");

  graph2 -> GetXaxis()->SetLimits(45,300); 
  graph2 -> Draw("APE");
  graph4 -> Draw("P,same");
  graph6 -> Draw("P,same*");
  mycanvas -> Update();















}
