/*
 * Class that handles the communication with Tiledal modules
 *
 *  Implementation
 */



#include "TileCIS/TileDrawerModuleCIS.h"
#include <iostream>

using namespace std;

TileDrawerModuleCIS::TileDrawerModuleCIS(Configuration *configPointer){
  dbTileDrawer = 0;
  if(configPointer == 0){
    confDB = new Configuration("");
    m_initconfig = true;
  }else{
    confDB = configPointer;
    m_initconfig = false;
  }
  m_verbose = false;
}

TileDrawerModuleCIS::~TileDrawerModuleCIS(){
  if(m_initconfig==true){
    delete confDB;
  }
}


bool TileDrawerModuleCIS::SetDrawer(const char * drwid){
  if(!confDB->loaded()) {
    cerr << "Can not load database: " << endl; 
    return false;
  } 

  string drawer_label = drwid;
  drawer_label = "Tile" + drawer_label;
  
  if(m_verbose){
    cout << "Fetching from OKS DB data for module " << drawer_label << endl;
  }
  
  dbTileDrawer = confDB->get<Tiledal::TileDrawerModule>(drawer_label);  
  bool status;
  if(dbTileDrawer){
    if(m_verbose){
      cout << "Drawer correctly retrieved from the OKS" << endl;
    }
    status=true;
  }else{
    if(m_verbose){
      cerr << "Drawer NOT retrieved!\n" << endl;
    }
    status=false;
  }
  
  return status;
}


string TileDrawerModuleCIS::GetName(){
  if(dbTileDrawer!=0){
    return string(dbTileDrawer->UID()).substr(4);
  }else{
    return "";
  }
}


string TileDrawerModuleCIS::GetUID(){
  if(dbTileDrawer!=0){
    return dbTileDrawer->UID();
  }else{
    return "";
  }
}


Configuration * TileDrawerModuleCIS::GetDB(){
  return confDB;
}




// end of file
