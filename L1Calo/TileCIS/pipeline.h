#ifndef __PIPELINE_H__
#define __PIPELINE_H__

#include <queue>
#include <vector>
#include <string>

#include <sys/time.h>
#include "TileCIS/TileDrawerModuleCIS.h"
#include "TileVMEboards/TileTTC.h"
using namespace std;

enum ttc_message_type {TTC_MESSAGE_DRAWER, TTC_MESSAGE_DIGI};

class ttc_message
{

	public:

		inline ttc_message(int _drawer_ID, int _sub_add, int _data, int _time, int _digitizer = -1, int _ext = 1):
			drawer_ID(_drawer_ID), sub_add(_sub_add), data(_data), time(_time), digitizer(_digitizer), ext(_ext) {
			if (_digitizer > -1)
				type = TTC_MESSAGE_DIGI;
			else
				type = TTC_MESSAGE_DRAWER;
		};

        	int drawer_ID;
        	int sub_add;
        	int data;
        	int time; //in ms

		int digitizer; // Digitizer to send command to, if appropriate
		int ext; // external?

		ttc_message_type type;
};

typedef vector<ttc_message> MessageList;

class MsgFIFO
{

private:

	queue<ttc_message> q;

	struct timeval next_time;

public:

	MsgFIFO(){gettimeofday(&next_time,(struct timezone*)NULL);};

	inline void         push (ttc_message &msg){q.push(msg);};
	inline void         pop  ();
	inline ttc_message& front(){return q.front();};

	inline bool empty  (){return q.empty();};
	inline bool can_pop();

};

class dbRead
{

private:

	int  ttcrx[65];
	bool used [65];
	bool digi_used [65][8];
	bool digi_ttcrx [65][8];

	int _sector;

	TileDrawerModuleCIS m_db;

public:

	dbRead(int sector, Configuration *confDb = 0);

	inline int get_ttcrx(int index);
	inline int get_digi_ttcrx(int index, int digi);
	const string index2string(int index);

};

class pipeline
{

private:

  //	unsigned long ttcvi_addr;
	dbRead *dbr;
        TileTTC *myttc;

	MsgFIFO  vFIFO[64];
	MsgFIFO bcFIFO; //broadcast

	const string msg2string(int sub_addr);

	inline bool empty();

	void go   ();
	void go_bc();

	inline void send(ttc_message &m);

public:

        pipeline(dbRead *db, TileTTC * myttc);

	bool verbose;

	void execute(MessageList &ml);

};

#endif
