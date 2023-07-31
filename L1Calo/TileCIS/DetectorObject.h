#ifndef DetectorObjectH
#define DetectorObjectH

#include <vector>
#include <iostream>
#include <string>

#include "TileCIS/TileCommand.h"
#include "TileCIS/TileTarget.h"

class DetectorObject{
public:
  // Contructor
  DetectorObject(){};
  virtual ~DetectorObject();
  
  // Virtual Sets
  virtual void SetID(int ID)            = 0;
  virtual int  GetID(TileTarget x)      = 0;
  virtual int  GetID()                  = 0;
  virtual void SetToMyID(TileTarget &x) = 0;

  virtual bool SameID(TileTarget *target);

  CommandStatus Execute(TileCommand *command, TileTarget *target);

  virtual CommandStatus _Execute(TileCommand *command, TileTarget *target);



  void AddObject(DetectorObject *obj);

  std::vector<DetectorObject*> constituents;
  TileTarget _myID;
  std::string _name;
};

#endif
