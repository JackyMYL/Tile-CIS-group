/*
 * Class that handles the communication with Tiledal modules
 *
 * This class is based on TileDVS/DB_TileDrawerModules.h
 *
 * This way, TileCIS is not dependent of TileDVS
 */



#ifndef TILEDRAWERMODULECIS
#define TILEDRAWERMODULECIS

#include <string>

#include "config/Configuration.h"
#include "Tiledal/TileDrawerModule.h"
#include "Tiledal/TileCal_RODModule.h"

class TileDrawerModuleCIS{

public:
  // Constructor & destructor
  TileDrawerModuleCIS(Configuration * configPointer = 0);
  ~TileDrawerModuleCIS();
  
  // Set methods
  bool SetDrawer (const char * drwid);
  void SetVerbose(bool verbose){m_verbose = verbose;};
  
  // Get methods
  std::string GetName();
  std::string GetUID();
  Configuration *GetDB();
  const Tiledal::TileDrawerModule *GetModule(){return dbTileDrawer;};
  
private:
  Configuration * confDB;
  const Tiledal::TileDrawerModule *dbTileDrawer;
  
  bool m_verbose;
  bool m_initconfig;

};

#endif //define TILEDRAWERMODULECIS

// End of file
