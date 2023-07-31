// Class that handles the commands given

#ifndef TileCommandH
#define TileCommandH

#include "TileCIS/TileTarget.h"
#include "TileCIS/TileState.h"
#include "TileCIS/pipeline.h"

class CommandStatus{
public:
  CommandStatus(      ): _success(true){};
  CommandStatus(bool s): _success( s  ){};

  bool IsSuccessful() { return _success; };
  bool _success;
};

class TileCommand{
public:
  TileCommand(std::string name, int waittime, MessageList *ml, SectionState *state, bool verbose);

  virtual ~TileCommand(){};
  CommandStatus Execute(TileTarget *target);
  virtual CommandStatus _Execute(TileTarget *target) = 0;

  std::string   _name;
  int           _waittime;
  MessageList*  _ml;
  SectionState* _state;
  bool          _verbose;

 protected:
  virtual void SetBroadcast(TileTarget target);

};

/******************************* Commands *************************************/


class cDrawerBroadcast : public TileCommand{
public:
  cDrawerBroadcast(MessageList *ml, SectionState *state, bool verbose);
  virtual CommandStatus _Execute(TileTarget *target);
};


class cSetTube : public TileCommand{
public:
  cSetTube(MessageList *ml, SectionState *state, bool verbose);
  virtual CommandStatus _Execute(TileTarget *target);
};  

  
class cSetDAC : public TileCommand{
private:
  //  void SetBroadcast(TileTarget target);
  
public:
  cSetDAC(MessageList *ml, SectionState *state, bool verbose);
	CommandStatus _Execute(TileTarget *target);
};


class cEnableTrigger: public TileCommand{
private:
  // 	void SetBroadcast(TileTarget target);
  
public:
	cEnableTrigger(MessageList *ml, SectionState *state, bool verbose);
	virtual CommandStatus _Execute(TileTarget *target);
};


class cSetCSmall: public TileCommand{
private:
  //void SetBroadcast(TileTarget target);

public:
  cSetCSmall(MessageList *ml, SectionState *state, bool verbose);
  virtual CommandStatus _Execute(TileTarget *target);
};


class cSetCLarge: public TileCommand{
private:
  //void SetBroadcast(TileTarget target);
  
public:
  cSetCLarge(MessageList *ml, SectionState *state, bool verbose);
  virtual CommandStatus _Execute(TileTarget *target);
};


class cSetCharge: public TileCommand{
private:
  int charge2dac(double charge);

public:
  cSetCharge(MessageList *ml, SectionState *state, bool verbose);
  virtual CommandStatus _Execute(TileTarget *target);

};

class cSetPhase : public TileCommand{
private:
  //  void SetBroadcast(TileTarget target);
  
public:
  cSetPhase(MessageList *ml, SectionState *state, bool verbose);
	CommandStatus _Execute(TileTarget *target);
};

class cSetPipeline : public TileCommand{
private:
  //  void SetBroadcast(TileTarget target);
  
public:
  cSetPipeline(MessageList *ml, SectionState *state, bool verbose);
	CommandStatus _Execute(TileTarget *target);
};

#endif

