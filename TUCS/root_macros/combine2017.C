#include "TCanvas.h"
#include "TLatex.h"
#include "TGraphErrors.h"
#include "TMath.h"
#include "TAxis.h"
#include <vector>

void combine2017()
{
 ////////////////////2017 /////////////////////////

  const int n3_points = 4; //A-cells
  double x3_vals[n3_points] =  {4.80,4.84,4.20,5.29};
  double y3_vals[n3_points] =  {67.50,57.71,61.37,67.35};
  double y3_errs[n3_points] =  {8.16,6.48,7.43,9.28};
  const int n2_points = 4; //E-cells
  double x2_vals[n2_points] =  {5.64,7.59,5.07,4.78};
  double y2_vals[n2_points] =  {60.50,105.16,91.50,78.36};
  double y2_errs[n2_points] =  {12.6,28.6,33.6,27.4};

  auto graph3 = new TGraphErrors(n3_points, y3_vals, x3_vals, y3_errs, nullptr);
  auto graph2 = new TGraphErrors(n2_points, y2_vals, x2_vals, y2_errs, nullptr);
  graph2 -> SetTitle("2017 Time const");

  graph3 -> SetMarkerStyle(kOpenSquare);
  graph3 -> SetMarkerColor(kBlue);
  graph3 -> SetLineColor(kBlue);
  graph2 -> GetXaxis()->SetTitle("Time Constant (days)");
  graph2 -> GetYaxis()->SetTitle("A-B");
  graph2 -> SetMarkerStyle(kOpenSquare);
  graph2 -> SetMarkerColor(kRed);
  graph2 -> SetLineColor(kRed);
  graph2 -> Draw("APE");
  graph3 -> Draw("P,same");
}
