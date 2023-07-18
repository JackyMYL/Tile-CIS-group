#include "TCanvas.h"
#include "TLatex.h"
#include "TGraphErrors.h"
#include "TMath.h"
#include "TAxis.h"
#include <vector>

void combineAcells()
{

auto mycanvas = new TCanvas();

 const int n2_points = 12; //2015
  double x2_vals[n2_points] =  {0.77,1.56,1.48,1.60};
  double y2_vals[n2_points] =  {49.95, 51.64, 58.34, 55.94};
  double y2_errs[n2_points] =  {2.06, 1.90, 2.46, 2.16};
  double x2_errs[n2_points] =  {-0.004,-0.006,-0.007,-0.005};

  const int n4_points = 4; //2016
  double x4_vals[n4_points] =  {2.68,3.11,2.86,3.05};
  double y4_vals[n4_points] =  {187.26,207.70,209.56,201.70};
  double y4_errs[n4_points] =  {5.70,8.24,9.25,7.7};

  const int n6_points = 4; //2017
  double x6_vals[n6_points] = {4.80,4.84,4.20,5.29};
  double y6_vals[n6_points] = {67.50,57.71,61.37,67.35};
  double y6_errs[n6_points] = {8.16,6.48,7.43,9.28}; 

  auto graph2 = new TGraphErrors(n2_points, y2_vals, x2_vals, y2_errs, x2_errs);
  auto graph4 = new TGraphErrors(n4_points, y4_vals, x4_vals, y4_errs, nullptr);
  auto graph6 = new TGraphErrors(n6_points, y6_vals, x6_vals, y6_errs, nullptr);

  graph2 -> SetTitle("A-cells Time const");

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

  graph2 -> GetXaxis()->SetLimits(47,225); 
  graph2 -> Draw("APE");
  graph4 -> Draw("P,same");
  graph6 -> Draw("P,same*");
  mycanvas -> Update();


}
