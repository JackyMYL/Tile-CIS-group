// TileDetector.cxx

#include "TileCIS/TileDetector.h"

#include <vector>
using namespace std;


// PMT

TilePMT::TilePMT(){
  _name = "PMT";
}

TilePMT::TilePMT(int section, int Drawer, int Tower, int ID){
  SetID(ID); 
  _name = "PMT";
  _myID.Section = section;
  _myID.Drawer  = Drawer;
  _myID.Tower   = Tower;
}

CommandStatus TilePMT::_Broadcast(TileCommand *command,
                                         TileTarget *target){
  return _Execute(command,target);
}

CommandStatus TilePMT::_Execute(TileCommand *command,
                                       TileTarget *target){
  target->SetUsed();
  TileTarget *newtarget = TheTargetHandler.NewTarget(&_myID);
  newtarget->Param = target->Param;

  return command->Execute(newtarget);
}


// Tower


TileTower::TileTower(){
  _name = "Tower";
}

TileTower::TileTower(int section, int Drawer, int ID){
  SetID(ID); 
  _name="Tower";
  _myID.Section=section;
  _myID.Drawer=Drawer;
}

CommandStatus TileTower::_Execute(TileCommand *command,TileTarget *target){
  CommandStatus s(true);
  if(target->PMT == 0){
    vector<DetectorObject*>::iterator b=constituents.begin();
    for(; b!=constituents.end();++b){
      (*b)->Execute(command,target);
    }
  }else
    if (target->PMT <= (int)constituents.size()){
      target->SetUsed();
      TileTarget *newtarget=TheTargetHandler.NewTarget(&(constituents.at(target->PMT-1)->_myID));
      newtarget->Param=target->Param;
      command->Execute(newtarget);
    } 

  return s;
}

// TileDrawer

TileDrawer::TileDrawer(){
  _name = "Drawer";
}

TileDrawer::TileDrawer(int section, int ID){
  section = section;
  SetID(ID);
  _name = "Drawer";
}

CommandStatus TileDrawer::_Broadcast(TileCommand *command,TileTarget *target){
  return command->Execute(target);
}

CommandStatus TileDrawer::_Execute(TileCommand *command, TileTarget *target){
  if (target->PMT == 0 && target->Tower < 1){
    target->SetUsed();
    TileTarget *newtarget=TheTargetHandler.NewTarget(target);
    SetToMyID(*newtarget);
    return command->Execute(newtarget);
  }
  
  vector<DetectorObject*>::iterator b=constituents.begin();
  for (;b!=constituents.end();++b){
    if((*b)->_myID.Tower > -1){
      if((*b)->SameID(target))
        (*b)->Execute(command,target);
    }else{
      if (target->Tower < 0)
        if ((*b)->SameID(target))
          (*b)->Execute(command,target);
    }
  }

  return CommandStatus(true);
}

// TileSection


TileSection::TileSection(){
  _name = "Section";
}

TileSection::TileSection(int ID){
  SetID(ID);
  _name = "Section";
}

CommandStatus TileSection::_Broadcast(TileCommand *command,TileTarget *target){
  return command->Execute(target);
}

CommandStatus TileSection::_Execute(TileCommand *command, TileTarget *target){
  if(target->Drawer == 0 && target->PMT == 0){
    target->SetUsed();
    TileTarget *newtarget = TheTargetHandler.NewTarget(target);
    SetToMyID(*newtarget);
    return command->Execute(newtarget);
  }else{
    vector<DetectorObject*>::iterator b=constituents.begin();
    for(; b != constituents.end(); ++b){
      if((*b)->SameID(target)){
        target->SetUsed();
        TileTarget *newtarget=TheTargetHandler.NewTarget(target);
        SetToMyID(*newtarget);
        (*b)->Execute(command,newtarget);
        }
      }
    }
  return CommandStatus(true);
}

// TileCal


TileCal::TileCal(){
  _name="Cal";
}


// End of file
