// Class TileCommand implementation

#include "TileCIS/TileCommand.h"
#include <iostream>
using namespace std;

#define MS20 20

int   index2pmt[48] = { 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,
                       13,14,15,16,17,18,19,20,21,22,23,24,
                       25,26,27,28,29,30,31, 0, 0,32,33,34,
                       35,36,37,38,39,40,41,0,42,43,44,45};
/* 19/07/2007
int e_index2pmt[48] = { 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,
                        0, 0,11,12,13,14, 0, 0,15,16,17,18,
                        0, 0, 0, 0,19,20, 0, 0,21,22, 0, 0,
                       23,24, 0, 0,25,26,27,28, 0, 0, 0, 0};
*/
int e_index2pmt[48] = { 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,
                       13,14,15,16,17,18, 0, 0,19,20,21,22,
                        0, 0, 0, 0,23,24, 0, 0,25,26, 0, 0,
                       27,28, 0, 0,29,30,31,32, 0, 0, 0, 0};


TileCommand::TileCommand(string name, int waittime, MessageList *ml,
                         SectionState *state, bool verbose): _name(name),
                         _waittime(waittime),_ml(ml),_state(state),
                         _verbose(verbose){
}


CommandStatus TileCommand::Execute(TileTarget *target){
  CommandStatus s = _Execute(target);
  target->SetUsed();
  return s;
}


void TileCommand::SetBroadcast(TileTarget target){
  if (target.PMT == 0 && target.Tower < 1)  
    target.Param = 0;
  else
    target.Param = 1;

  cDrawerBroadcast bc(_ml,_state,_verbose);
  bc.Execute(&target);

  if (target.Param == 1){
    target.Param = target.PMT;
    cSetTube tb(_ml,_state,_verbose);
    tb.Execute(&target);
  }
}


// Drawer

cDrawerBroadcast::cDrawerBroadcast(MessageList *ml, SectionState *state,
                                   bool verbose):TileCommand("DrawerBroadcast",
                                   MS20,ml,state,verbose){
}


CommandStatus cDrawerBroadcast::_Execute(TileTarget *target){
  if (target->Param < 0 || target->Param > 1){
    cout << "Error: command " << _name << ", wrong parameter value: "
         << target->Param << endl;
    return CommandStatus(false);
  }

  if (target->Drawer == 0){
    if (_state->AnyDrawerBroadcastIsDifferentFrom((int)target->Param)){
      _ml->push_back(ttc_message(target->Drawer, 0xC8, (int)target->Param, MS20));
      _state->set_DrawerBroadcast((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") " << endl;
        target->Print();
      }
    }
    return CommandStatus(true);
  }

  if (target->Drawer != 0){
    if (_state->drawer[target->Drawer-1].get_broadcast()!=(int)target->Param){
      _ml->push_back(ttc_message(target->Drawer, 0xC8, (int)target->Param, MS20));
      _state->drawer[target->Drawer-1].set_broadcast((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") " << endl;
        target->Print();
      }
    }
  }

  return CommandStatus(true);
}


// Tube

cSetTube::cSetTube(MessageList *ml, SectionState *state, bool verbose):
                   TileCommand("SetTube",MS20,ml,state,verbose){
}


CommandStatus cSetTube::_Execute(TileTarget *target){
  if (target->Section < 3 && index2pmt[target->PMT-1] == 0){
    cout << "Error: command:" << _name << ", PMT "
         << target->PMT << "does not exist in this partition" << endl;
    return CommandStatus(false);
  }

  if (target->Section > 2 && e_index2pmt[target->PMT-1] == 0){
    cout << "Error: command:" << _name << ", PMT " << target->PMT 
         << "does not exist in this partition" << endl;
    return CommandStatus(false);
  }

  if (target->PMT == 0){
    cout << "Error: command:" << _name << ", PMT value should be > 0" << endl;
    return CommandStatus(false);
  }

  if (target->Drawer == 0){
    if (_state->AnyTubeIsDifferentFrom((int)target->Param)){
      _ml->push_back(ttc_message(target->Drawer, 0xC4, (int)target->Param, MS20));
      _state->set_tube((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
    return CommandStatus(true);
  }

  if (target->Drawer != 0){
    if (_state->drawer[target->Drawer-1].get_tube() != (int)target->Param){
      _ml->push_back(ttc_message(target->Drawer, 0xC4, (int)target->Param, MS20));
      _state->drawer[target->Drawer-1].set_tube((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
  }

  return CommandStatus(true);
}


// DAC

/*
void cSetDAC::SetBroadcast(TileTarget target){
  if (target.PMT == 0 && target.Tower < 1)  
    target.Param = 0;
  else
    target.Param = 1;

  cDrawerBroadcast bc(_ml,_state,_verbose);
  bc.Execute(&target);

  if (target.Param == 1){
    target.Param = target.PMT;
    cSetTube tb(_ml,_state,_verbose);
    tb.Execute(&target);
  }
}
*/

cSetDAC::cSetDAC(MessageList *ml, SectionState *state, bool verbose):
                 TileCommand("SetDAC",MS20,ml,state,verbose){
}


CommandStatus cSetDAC::_Execute(TileTarget *target){
  if (target->Param < 0 || target->Param > 1023){
    cout << "Error: wrong DAC value: " << target->Param << endl;
    return CommandStatus(false);
  }
  int dac_low = (int)(target->Param) & 0xff;
  int dac_high = ((int)(target->Param)>>8) & 0x3;


  if (target->Drawer == 0 && target->PMT == 0 && target->Tower < 1){
    if (_state->AnyDACIsDifferentFrom((int)target->Param)){
      SetBroadcast(*target);

      _ml->push_back(ttc_message(target->Drawer, 0xF8 | dac_high, dac_low, MS20));
      _state->set_dac((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
    return CommandStatus(true);
  }

  if (target->Drawer != 0 && target->PMT == 0 && target->Tower < 1){
    if (_state->drawer[target->Drawer-1].AnyDACIsDifferentFrom((int)target->Param)){
      SetBroadcast(*target);
      //      _ml->push_back(ttc_message(target->Drawer, 0xF8, (int)target->Param, MS20));
      _ml->push_back(ttc_message(target->Drawer, 0xF8 | dac_high, dac_low, MS20));
      _state->drawer[target->Drawer-1].set_dac((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
    return CommandStatus(true);
  }

  if (target->Drawer != 0 && target->PMT != 0){
    int ipmt;
    if (_state->get_section() < 3){
      ipmt = index2pmt[target->PMT-1];
      if (ipmt == 0){
        cout << "Warning: PMT " << target->PMT << " does not exist" << endl;
        return CommandStatus(false);
        }
    }else{
      ipmt = e_index2pmt[target->PMT-1];
      if (ipmt == 0){
        cout << "Warning: PMT " << target->PMT << " does not exist" << endl;
        return CommandStatus(false);
      }
    }

    if (_state->drawer[target->Drawer-1].pmt[ipmt-1].get_dac() != target->Param){
      SetBroadcast(*target);
      //      _ml->push_back(ttc_message(target->Drawer, 0xF8, (int)target->Param, MS20));
      _ml->push_back(ttc_message(target->Drawer, 0xF8 | dac_high, dac_low, MS20));
      _state->drawer[target->Drawer-1].pmt[ipmt-1].set_dac((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
  }

  return CommandStatus(true);
}


// Trigger

/*
void cEnableTrigger::SetBroadcast(TileTarget target){
  if (target.PMT == 0 && target.Tower < 1)
    target.Param = 0;
  else
    target.Param = 1;

  cDrawerBroadcast bc(_ml,_state,_verbose);
  bc.Execute(&target);

  if (target.Param == 1){
    target.Param = target.PMT;
    cSetTube tb(_ml,_state,_verbose);
    tb.Execute(&target);
  }
}
*/

cEnableTrigger::cEnableTrigger(MessageList *ml, SectionState *state,
                               bool verbose):TileCommand("SetTrigger",
                               MS20,ml,state,verbose){
}

CommandStatus cEnableTrigger::_Execute(TileTarget *target){
  if (target->Param < 0 || target->Param > 1) return CommandStatus(false);

  if (target->Drawer == 0 && target->PMT == 0 && target->Tower < 1){
    if (_state->AnyTriggerIsDifferentFrom((int)target->Param)){
      SetBroadcast(*target);
      _ml->push_back(ttc_message(target->Drawer, 0xFC, (int)target->Param, MS20));
      _state->set_trigger((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
    return CommandStatus(true);
  }

  if (target->Drawer != 0 && target->PMT == 0 && target->Tower < 1){
    if (_state->drawer[target->Drawer-1].AnyTriggerIsDifferentFrom((int)target->Param)){
      SetBroadcast(*target);
      _ml->push_back(ttc_message(target->Drawer, 0xFC, (int)target->Param, MS20));
      _state->drawer[target->Drawer-1].set_trigger((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
    return CommandStatus(true);
  }

  if (target->Drawer != 0 && target->PMT != 0){
    int ipmt;
    if (_state->get_section() < 3){
      ipmt = index2pmt[target->PMT-1];
      if (ipmt == 0)
        return CommandStatus(false);
    }else{
      ipmt = e_index2pmt[target->PMT-1];
      if (ipmt == 0)
        return CommandStatus(false);
    }

    if (_state->drawer[target->Drawer-1].pmt[ipmt-1].get_trigger() != (int)target->Param){
      SetBroadcast(*target);
      _ml->push_back(ttc_message(target->Drawer, 0xFC, (int)target->Param, MS20));
      _state->drawer[target->Drawer-1].pmt[ipmt-1].set_trigger((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
  }

  return CommandStatus(true);
}


// Small Capacitor

/*
void cSetCSmall::SetBroadcast(TileTarget target){
  if (target.PMT == 0 && target.Tower < 1)
    target.Param = 0;
  else
    target.Param = 1;

  cDrawerBroadcast bc(_ml,_state,_verbose);
  bc.Execute(&target);

  if (target.Param == 1){
    target.Param = (float)target.PMT;
    cSetTube tb(_ml,_state,_verbose);
    tb.Execute(&target);
  }
}
*/
 

cSetCSmall::cSetCSmall(MessageList *ml, SectionState *state, bool verbose):
                       TileCommand("SetCSmall",MS20,ml,state,verbose){
}

CommandStatus cSetCSmall::_Execute(TileTarget *target){
  if (target->Param < 0 || target->Param > 1) return CommandStatus(false);

  if (target->Drawer == 0 && target->PMT == 0 && target->Tower < 1){
    if (_state->AnyCSmallIsDifferentFrom((int)target->Param)){
      SetBroadcast(*target);
      _ml->push_back(ttc_message(target->Drawer, 0xF0, (int)target->Param, MS20));
      _state->set_csmall((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
    return CommandStatus(true);
  }

  if (target->Drawer != 0 && target->PMT == 0 && target->Tower < 1){
    if (_state->drawer[target->Drawer-1].AnyCSmallIsDifferentFrom((int)target->Param)){
      SetBroadcast(*target);
      _ml->push_back(ttc_message(target->Drawer, 0xF0, (int)target->Param, MS20));
      _state->drawer[target->Drawer-1].set_csmall((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
    return CommandStatus(true);
  }

  if (target->Drawer != 0 && target->PMT != 0){
    int ipmt;
    if (_state->get_section() < 3){
      ipmt = index2pmt[target->PMT-1];
      if (ipmt == 0)
        return CommandStatus(false);
    }else{
      ipmt = e_index2pmt[target->PMT-1];
      if (ipmt == 0) return CommandStatus(false);
    }

    if (_state->drawer[target->Drawer-1].pmt[ipmt-1].get_csmall() != (int)target->Param){
      SetBroadcast(*target);
      _ml->push_back(ttc_message(target->Drawer, 0xF0, (int)target->Param, MS20));
      _state->drawer[target->Drawer-1].pmt[ipmt-1].set_csmall((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
  }

  return CommandStatus(true);
}


// Large Capacitor

/*
void cSetCLarge::SetBroadcast(TileTarget target){
  if (target.PMT == 0 && target.Tower < 1)
    target.Param = 0;
  else
    target.Param = 1;

  cDrawerBroadcast bc(_ml,_state,_verbose);
  bc.Execute(&target);
  if (target.Param == 1){
    target.Param = (float)target.PMT;
    cSetTube tb(_ml,_state,_verbose);               
    tb.Execute(&target);
  }
}
*/

cSetCLarge::cSetCLarge(MessageList *ml, SectionState *state, bool verbose):
                       TileCommand("SetCLarge",MS20,ml,state,verbose){
}


CommandStatus cSetCLarge::_Execute(TileTarget *target){
  if (target->Param < 0 || target->Param > 1) return CommandStatus(false);

  if (target->Drawer == 0 && target->PMT == 0 && target->Tower < 1){
    if (_state->AnyCLargeIsDifferentFrom((int)target->Param)){
      SetBroadcast(*target);
      _ml->push_back(ttc_message(target->Drawer, 0xF4, (int)target->Param, MS20));
      _state->set_clarge((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
    return CommandStatus(true);
  }

  if (target->Drawer != 0 && target->PMT == 0 && target->Tower < 1){
    if (_state->drawer[target->Drawer-1].AnyCLargeIsDifferentFrom((int)target->Param)){
      SetBroadcast(*target);
      _ml->push_back(ttc_message(target->Drawer, 0xF4, (int)target->Param, MS20));
      _state->drawer[target->Drawer-1].set_clarge((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
    return CommandStatus(true);
  }

  if (target->Drawer != 0 && target->PMT != 0){
    int ipmt;
    if (_state->get_section() < 3){
      ipmt = index2pmt[target->PMT-1];
      if (ipmt == 0)
        return CommandStatus(false);
    }else{
      ipmt = e_index2pmt[target->PMT-1];
      if (ipmt == 0)
        return CommandStatus(false);
    }
    if (_state->drawer[target->Drawer-1].pmt[ipmt-1].get_clarge() != (int)target->Param){
      SetBroadcast(*target);
      _ml->push_back(ttc_message(target->Drawer, 0xF4, (int)target->Param, MS20));
      _state->drawer[target->Drawer-1].pmt[ipmt-1].set_clarge((int)target->Param);
      if (_verbose){
        cout << "Command " << _name << "(" << _waittime << ") ";
        target->Print();
      }
    }
  }
  return CommandStatus(true);
}
//Peter//
// Note that set_clarge() if called on drawer or PMT essentailly just uses for loops to inject charges
// So, that means we have to go to TileCIS/TileState.cxx and write additional logic in the injector stages
// Do it in DrawerState::set_clarge(), for this is has a fixed drawer at all times, and it will call on the drawer version,
// after which each individual PMT is called
// We still need a way to do it if only single PMTs are called, but this can be done with additionall logic
// directly in the above file. (So there are two cases)
// 1. If anything but the exact PMT is called, then set_clarge will degenerate into loops over PMTs and logic can be 
//      applied directly in TileState.cxx
// 2. If the PMT iwith all of its information is accessed directly, then it calls the fundamental set_clarge() function from
//    the header file in TileState.cxx ( this file cannot be directly modified ...). Hence, we apply addtional logic 
//    in the last IF statement for each of the injection protocols 
// In this script, then, the following functions need to be edited, as well as their corresponding functions in TileState.cxx
// 1. cSetCSmall()
// 2. cSetCLarge()
// 3. cSetDAC()
// cSetCharge just calls its Large and Small partners, so there is no direct editing that really needs to be done here (PMTscan) 
// What does energy scan call in terms of CIS? I cannot find any functions in TileDigiTTCModuleCIFFormat.cxx

// Charge


int cSetCharge::charge2dac(double charge){
  double cap, dacval;
  if (charge < 10){
    cap = 5.2;
  }else{
    cap = 100.0;
  }
  
  dacval = (charge * 1023.0) / (2.0 * 4.096 * cap);
  if(dacval > 1023.0)
    dacval = 1023.0;
    
  return (int) dacval; 
}

 
cSetCharge::cSetCharge(MessageList *ml, SectionState *state, bool verbose):
                       TileCommand("SetCharge",MS20,ml,state,verbose){
}

CommandStatus cSetCharge::_Execute(TileTarget *target){
  if (target->Param < 0 || target->Param > 800)
    return CommandStatus(false);

  TileTarget  t(target->Section,target->Drawer,target->Tower,target->PMT);
  cSetCSmall cs(_ml,_state,_verbose);
  cSetCLarge cl(_ml,_state,_verbose);

  if (target->Param < 10){
    t.Param = 1;
    cs.Execute(&t);
    t.Param = 0;
    cl.Execute(&t);
  }else{
    t.Param = 0;
    cs.Execute(&t);
    t.Param = 1;
    cl.Execute(&t);
  }

  t.Param = (float)charge2dac(target->Param);
  cSetDAC sd(_ml,_state,_verbose);
  sd.Execute(&t);

  return CommandStatus(true);
}

cSetPhase::cSetPhase(MessageList *ml, SectionState *state, bool verbose):
                 TileCommand("SetPhase",MS20,ml,state,verbose){
}


CommandStatus cSetPhase::_Execute(TileTarget *target){
  // target->Param is the delay, target->Param2 is the digitizer ([0,8], 0 being the CIS phase)

  int l,m,n;
  
  n = ( (int) target->Param) % 15;
  m = ((( (int) target->Param) )/15 - n + 14) % 16;
  l = n*16 + m;

  _ml->push_back(ttc_message(target->Drawer, 1, l, MS20, target->Param2, 0));
  if ( (target->Param >= 90) && (target->Param <= 209) ) {
    _ml->push_back(ttc_message(target->Drawer, 0x0a, 0x01, MS20, target->Param2));
  } else if (target->Param != 0) {
    _ml->push_back(ttc_message(target->Drawer, 0x0a, 0x00, MS20, target->Param2));
  }
  
  if (_verbose){
    cout << "Command " << _name << "(" << _waittime << ") ";
    target->Print();
  }

  return CommandStatus(true);
}

cSetPipeline::cSetPipeline(MessageList *ml, SectionState *state, bool verbose):
                 TileCommand("SetPipeline",MS20,ml,state,verbose){
}


CommandStatus cSetPipeline::_Execute(TileTarget *target){
  // target->Param is the pipeline, target->Param2 is the digitizer ([0,8], 0 being the CIS pipeline)

  _ml->push_back(ttc_message(target->Drawer, 0x2, target->Param, MS20, target->Param2, 1));
  
  if (_verbose){
    cout << "Command " << _name << "(" << _waittime << ") ";
    target->Print();
  }

  return CommandStatus(true);
}

//  end of file
