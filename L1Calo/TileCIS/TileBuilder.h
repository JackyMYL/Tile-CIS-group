// Class that builds a TileCal detector, his PMTs, Towers, Drawers, Sections...

#ifndef TILEBUILDER_H
#define TILEBUILDER_H

#include "TileCIS/DetectorObject.h"


class DetectorBuilder{
public:
  DetectorBuilder() {};
  virtual DetectorObject *Build() = 0;
};

class TileBuilder: public DetectorBuilder{
public:

  TileBuilder() {};

  DetectorObject *BuildPMT    (int section, int Drawer, int tower, int ID);
  DetectorObject *BuildTower  (int section, int Drawer, int ID);
  DetectorObject *BuildDrawer (int section, int ID);
  DetectorObject *BuildSection(int ID);
  DetectorObject *Build       ();
};

#endif
