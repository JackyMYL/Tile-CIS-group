// DetectorObject.cxx

#include "TileCIS/DetectorObject.h"
using namespace std;

DetectorObject::~DetectorObject(){
  vector<DetectorObject*>::iterator b = constituents.begin();
  for(; b != constituents.end(); b++){
    delete *b;
  }
}
    

bool DetectorObject::SameID(TileTarget *target){
  int ID = GetID(*target);
  return ID == 0 || ID == GetID();
}

CommandStatus DetectorObject::Execute(TileCommand *command, TileTarget *target){
  if (SameID(target) == false){
    cout << "Warning: Target does not belong to the sender." << endl; 
    return CommandStatus(false);
  }
  return _Execute(command, target);
  
}

CommandStatus DetectorObject::_Execute(TileCommand *command, TileTarget *target){
  CommandStatus s;
  vector<DetectorObject*>::iterator b = constituents.begin();
  for (; b != constituents.end(); b++){
    if ((*b)->SameID(target)){
      target->SetUsed(); 
      TileTarget *newtarget = TheTargetHandler.NewTarget(target);
      SetToMyID(*newtarget);
      s._success = s._success && ((*b)->Execute(command, newtarget))._success;
    }
  }

  return s;
}


void DetectorObject::AddObject(DetectorObject *obj){
  constituents.push_back(obj);
}

// End of file
