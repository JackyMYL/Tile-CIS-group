// Class TileTarget implementation


#include "TileCIS/TileTarget.h"

#include <iostream>
using namespace std;

using namespace std;



TileTarget::TileTarget():Section(0),Drawer(0),Tower(-1),PMT(0),
                         Param(-99999),_used(false), Param2(-1) {
}

TileTarget::TileTarget(int section, int drawer, int tower, int pmt):
                        Section(section),Drawer(drawer),Tower(tower),
                        PMT(pmt),Param(-99999),_used(false),Param2(-1){
}
    
TileTarget::TileTarget(int section, int drawer, int tower, int pmt,
                       float param, int param2)
                       : Section(section), Drawer(drawer),Tower(tower),
                         PMT(pmt) ,Param(param) , Param2(param2),_used(false) {
}
    
TileTarget::TileTarget(int section, int drawer, int pmt):Section(section),
                       Drawer(drawer),Tower(-1),PMT(pmt),Param(-99999), Param2(-1),
                       _used(false){
}
    
void TileTarget::Print() {
  cout<<"Target: "<<Section<<" "<<Drawer<<" ";
  if(Tower>-1)
    cout<<Tower<<" ";
  cout<<PMT<<" ";
  if(Param!=-99999)
    cout<<Param<<" ";
  if (Param2 != -1)
    cout << Param2<< " ";
  cout<<endl;
}

void TileTarget::CopyParameters(TileTarget &x){
  x.Section = Section;
  x.Drawer  = Drawer;
  x.Tower   = Tower;
  x.PMT     = PMT;    
  x.Param   = Param;    
  x.Param2  = Param2;    
}

// target Handle


TileTargetHandler::~TileTargetHandler() {
  vector<TileTarget*>::iterator b=Targets.begin();
  for(; b != Targets.end(); b++)
    delete *b;

  Targets.clear();
}

void TileTargetHandler::AddTarget(TileTarget *target){
  Targets.push_back(target);
}

TileTarget *TileTargetHandler::NewTarget(TileTarget *target){
  TileTarget *t= NewTarget(0,0,0,0);
  target->CopyParameters(*t);
  return t;
}

TileTarget *TileTargetHandler::NewTarget(int section,int Drawer,
                                         int Tower, int PMT){
  TileTarget *target=new TileTarget(section,Drawer,Tower,PMT);
  AddTarget(target);
  return target;
}

TileTarget *TileTargetHandler::NewTarget(int section,int Drawer,
                                         int Tower, int PMT,float Param){
  TileTarget *target=new TileTarget(section,Drawer,Tower,PMT,Param);
  AddTarget(target);
  return target;
}

TileTarget *TileTargetHandler::NewTarget(int section,int Drawer, int PMT){
  TileTarget *target=new TileTarget(section,Drawer,PMT);
  AddTarget(target);
  return target;
}

void TileTargetHandler::Cleanup(){
  vector<TileTarget*>::iterator b=Targets.end();
  for(; b != Targets.begin(); b--) 
    if((*b)->CheckUsed()) {
      TileTarget *target=*b;
      //Not sure if this works... this might invalidate the iterator.
      Targets.erase(b);
      delete target;
    }
}

// end of file
