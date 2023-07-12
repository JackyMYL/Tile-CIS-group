#include "TCanvas.h"
#include "TLatex.h"
#include "TGraphErrors.h"
#include "TMath.h"
#include "TAxis.h"
#include <vector>
void combine2015()
{

  auto mycanvas = new TCanvas();
  const int n1_points = 4; //A-cells
  double x1_vals[n1_points] = {0.77,1.56,1.48,1.60};
  double y1_vals[n1_points] = {49.95, 51.64, 58.34, 55.94};
  double y1_errs[n1_points] = {2.06, 1.90, 2.46, 2.16};
  double x1_errs[n1_points] = {-0.004,-0.006,-0.007,-0.005};
  const int n2_points = 4; //E-cells
  double x2_vals[n2_points] = {1.56,1.48,1.79,1.52};
  double y2_vals[n2_points] = {55.80, 61.74, 51.83, 56.58};
  double y2_errs[n2_points] = {3.64, 4.07, 2.66, 2.60};
  double x2_errs[n2_points] = {-0.01,-0.02,-0.02,-0.02};

  auto graph1 = new TGraphErrors(n1_points, y1_vals, x1_vals, y1_errs, x1_errs);
  auto graph2 = new TGraphErrors(n2_points, y2_vals, x2_vals, y2_errs, x2_errs);
  graph1 -> SetTitle("2015 Time const");

  graph1 -> SetMarkerStyle(kOpenCircle);
  graph1 -> SetMarkerColor(kBlue);
  graph1 -> SetLineColor(kBlue);
  graph2 -> SetMarkerStyle(kOpenSquare);
  graph2 -> SetMarkerColor(kRed);
  graph2 -> SetLineColor(kRed);
  // graph1 -> GetXaxis()->SetRange(10,100);
  graph1 -> GetXaxis()->SetTitle("Time Constant (days)");
  graph1 -> GetYaxis()->SetTitle("A-B");
  graph1 -> Draw("APE");
  graph2 -> Draw("P,same");
  graph1 -> GetXaxis()->SetLimits(45,70); 
  graph1 -> Draw("APE");
  graph2 -> Draw("P,same");
  mycanvas -> Update();
}
