#ifndef TILEDETECTOR_H
#define TILEDETECTOR_H

#include "TileCIS/DetectorObject.h"

class TilePMT : public DetectorObject{
public:
  TilePMT();
  TilePMT(int section, int Drawer, int Tower, int ID);
  
  
  void SetID(int ID)       {_myID.PMT = ID;};
  int  GetID(TileTarget x) {return x.PMT;};
  int  GetID()             {return GetID(_myID);};
  void SetToMyID(TileTarget &x) {x.PMT = _myID.PMT;};

  CommandStatus _Broadcast(TileCommand *command, TileTarget *target);
  CommandStatus _Execute  (TileCommand *command, TileTarget *target);
  
};



class TileTower : public DetectorObject{
public:
  TileTower();
  TileTower(int section, int Drawer, int ID);

  
  void SetID(int ID)       {_myID.Tower=ID;};
  int  GetID(TileTarget x) {return x.Tower;};
  int  GetID()             {return GetID(_myID);};
  void SetToMyID(TileTarget &x){x.Tower=_myID.Tower;};

  
  CommandStatus _Execute(TileCommand *command,TileTarget *target);
};

class TileDrawer : public DetectorObject{
public:
  TileDrawer();
  TileDrawer(int section, int ID);
  virtual ~TileDrawer(){};

  
  void SetID(int ID) { _myID.Drawer=ID;};
  int  GetID(TileTarget x) { return x.Drawer;};
  int  GetID() { return GetID(_myID);};
  void SetToMyID(TileTarget &x){x.Drawer=_myID.Drawer;};

  
  virtual CommandStatus _Broadcast(TileCommand *command, TileTarget *target);
  virtual CommandStatus _Execute  (TileCommand *command, TileTarget *target);
};



class TileSection : public DetectorObject{
public:
  TileSection();
  TileSection(int ID);
  virtual ~TileSection(){};

  
  void SetToMyID(TileTarget &x){x.Section = _myID.Section;};
  void SetID(int ID) { _myID.Section=ID;};
  int  GetID(TileTarget x) { return x.Section;};
  int  GetID() { return GetID(_myID);};

  
  virtual CommandStatus _Broadcast(TileCommand *command, TileTarget *target);
  virtual CommandStatus _Execute  (TileCommand *command, TileTarget *target);
};



class TileCal : public DetectorObject{
public:
  TileCal();

  
  void SetID(int ID) {ID =ID;};
  int  GetID(TileTarget x) {x = x; return -999;};
  int  GetID() { return -999;};
  void SetToMyID(TileTarget &x){x=x;};
};

#endif
