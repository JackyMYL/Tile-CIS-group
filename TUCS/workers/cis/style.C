{
  //// style /////////////////////////////////////////////////
  // use plain black on white colors
  Int_t icol=0;
  gStyle->SetFrameBorderMode(icol);
  gStyle->SetCanvasBorderMode(icol);
  gStyle->SetPadBorderMode(icol);
  gStyle->SetPadColor(icol);
  gStyle->SetCanvasColor(icol);
  gStyle->SetStatColor(icol);
  gStyle->SetFillColor(icol);
  gStyle->SetFrameFillColor(icol);
  gStyle->SetHistFillColor(icol);
  gStyle->SetTitleFillColor(icol);

//   // set the paper & margin sizes
  gStyle->SetPaperSize(20,26);
//   gStyle->SetPadTopMargin(0.05);
//   gStyle->SetPadRightMargin(0.05);
//   gStyle->SetPadBottomMargin(0.16);
//   gStyle->SetPadLeftMargin(0.12);

  // use large fonts
  //Int_t font=72;
  Int_t font=42;
  Double_t tsize=0.05;
  gStyle->SetTextFont(font);
  gStyle->SetTextSize(tsize);
  gStyle->SetLabelFont(font,"x");
  gStyle->SetLabelFont(font,"y");
  gStyle->SetLabelFont(font,"z");
  gStyle->SetTitleFont(font,"x");
  gStyle->SetTitleFont(font,"y");
  gStyle->SetTitleFont(font,"z");
  gStyle->SetLabelSize(0.9*tsize,"x");
  gStyle->SetLabelSize(0.9*tsize,"y");
  gStyle->SetLabelSize(0.9*tsize,"z");
  gStyle->SetTitleSize(0.9*tsize,"x");
  gStyle->SetTitleSize(0.9*tsize,"y");
  gStyle->SetTitleSize(0.9*tsize,"z");

  // use bold lines and markers
  gStyle->SetMarkerStyle(20);
  gStyle->SetMarkerSize(1.2);
  gStyle->SetHistLineWidth(2.);
  gStyle->SetLineStyleString(2,"[12 12]"); // postscript dashes

  // get rid of X error bars and y error bar caps
//  gStyle->SetErrorX(0.001);

// do not display any of the standard histogram decorations
//  gStyle->SetOptTitle(0);
//  gStyle->SetOptStat(1111);
//  gStyle->SetOptStat(0);
//  gStyle->SetOptFit(1111);
//  gStyle->SetOptFit(0);

  // put tick marks on top and RHS of plots
  gStyle->SetPadTickX(1);
  gStyle->SetPadTickY(1);
  ////////////////////////////////////////////////////////////

  // rainbow palette
  gStyle->SetPalette(1);

//   gStyle->SetOptStat(1111111);  // Set stat options
//   gStyle->SetStatY(0.9);  // Set y-position (fraction of pad size)
//   gStyle->SetStatX(0.9);  // Set x-position (fraction of pad size)
//   gStyle->SetStatW(0.4);  // Set width of stat-box (fraction of pad size)
//   gStyle->SetStatH(0.2);  // Set height of stat-box (fraction of pad size)



}
