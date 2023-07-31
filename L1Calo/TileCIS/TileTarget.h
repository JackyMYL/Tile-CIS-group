// Class that handles the target of the commands

#ifndef TileTargetH
#define TileTargetH

#include <vector>

class TileTarget {
public:

  TileTarget();
  TileTarget(int section, int drawer, int tower, int pmt);
  TileTarget(int section, int drawer, int tower, int pmt, float param, int param2 = -1);
  TileTarget(int section, int drawer, int pmt);

  
  void SetParam(float val){Param=val; };
  void SetParam2(int val){Param2=val; };
  void SetUsed ()         {_used=true;};

  bool CheckUsed(){return _used;};
  
  void CopyParameters(TileTarget &x);
  
  void Print();
  
  int   Section;
  int   Drawer;
  int   Tower;
  int   PMT;
  float Param;
  bool _used;
  int   Param2; // For the digitizer to set, when changing the phases

  virtual ~TileTarget() { }
};

class TileTargetHandler {
public:
  TileTargetHandler(){};
  ~TileTargetHandler();
  
  
  void AddTarget(TileTarget *target);

  TileTarget *NewTarget(TileTarget *target);
  TileTarget *NewTarget(int section,int Drawer, int Tower,int PMT);
  TileTarget *NewTarget(int section,int Drawer, int Tower,int PMT,float Param);
  TileTarget *NewTarget(int section,int Drawer, int PMT);

  void Cleanup();
  
  std::vector< TileTarget*> Targets;
};

static TileTargetHandler TheTargetHandler;


#endif
