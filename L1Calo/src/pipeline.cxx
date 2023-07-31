#include "TileCIS/pipeline.h"
#include "TileCIS/TileDrawerModuleCIS.h"

#include "Tiledal/TileDrawerModule.h" 

#include <iostream>

/* Obsolete 
#define TTCVI_LONG 0xC0
#define TTCVI_B_DATA(rx,ext,sa,data) (1<<31)|(rx<<17)|(ext<<16)|(sa<<8)|data
#define TTCVI_ADDR 0xA00000
*/


extern unsigned long vme_a24_base();

inline bool MsgFIFO::can_pop()
{
        if (q.empty() == true) return false;

        struct timeval tv;
        gettimeofday(&tv,(struct timezone*)NULL);

        if (tv.tv_sec == next_time.tv_sec)
                return tv.tv_usec > next_time.tv_usec;
        else
                return tv.tv_sec  > next_time.tv_sec;
}

inline void MsgFIFO::pop()
{
        struct timeval tv;
        gettimeofday(&tv,(struct timezone*)NULL);

        int us = tv.tv_usec + (q.front()).time*1000;

        next_time.tv_sec  = tv.tv_sec + us/1000000;
        next_time.tv_usec = us % 1000000;

        q.pop();
}

pipeline::pipeline(dbRead *db, TileTTC *ttc)
{
	verbose = false;
	dbr     = db;
	myttc   = ttc;
	//        ttcvi_addr = vme_a24_base() + TTCVI_ADDR;
}

void pipeline::execute(MessageList &ml)
{
        bool bc_on = false;
        bool first = true;

        //if (verbose) cout << "\nDrawer  Message    Data\n" << endl;
	cout << "Sending data to drawer, be patient" << endl;

        for (MessageList::iterator i = ml.begin(); i < ml.end(); i++)
        {
                if (i->drawer_ID == 0)
                {
                        if ((first == false) && (bc_on == false)) go();
                        bcFIFO.push(*i);
                        bc_on = true;
                        first = false;
                }
                else
                {
                        if (bc_on == true) go_bc();
                        vFIFO[i->drawer_ID-1].push(*i);
                        bc_on = false;
                        first = false;
                }
        }

        if (bc_on == false) go(); else go_bc();
	ml.clear();

	//if (verbose) cout << "\n";
	cout << "sending done" << endl;

}

const string pipeline::msg2string(int sub_addr)
{
        switch (sub_addr)
        {
                case 0xC0: return "SET___TP";
                case 0xC4: return "SET_TUBE";
                case 0xC8: return "SETMULTI";
                case 0xCC: return "SET__RXW";
                case 0xD0: return "BACKLOAD";
                case 0xD4: return "LOAD_CAN";
                case 0xD8: return "RESET_SM";
                case 0xDC: return "RESETCAN";
                case 0xE0: return "SET_INTG";
                case 0xE4: return "SET__ITR";
                case 0xE8: return "SET___SW";
                case 0xEC: return "SET__MSE";
                case 0xF0: return "C__SMALL";
                case 0xF4: return "C__LARGE";
                case 0xF8: return "SET__DAC";
                case 0xFC: return "SET__TRG";
                default  : return "__NAN___";
        }
}

void pipeline::go()
{

        while (empty() == false)
        {
                for (int i = 0; i < 64; i++)// all 64 drawers
                {
                        if (vFIFO[i].can_pop())
                        {
                                send(vFIFO[i].front());
                                vFIFO[i].pop();
                        }
                }
        }

}

void pipeline::go_bc()
{
        while (bcFIFO.empty() == false)
        {
                while (bcFIFO.can_pop() == false){};

                send(bcFIFO.front());
                bcFIFO.pop();
        }
}

inline bool pipeline::empty()
{
        for (int i = 0; i < 64; i++)
                if (vFIFO[i].empty() == false) return false;

        return true;
}

inline void pipeline::send(ttc_message &m)
{
	int theTTCrx = 0;
	if (m.type == TTC_MESSAGE_DIGI)
		if (m.digitizer == 0)
			theTTCrx = 0;
		else
			theTTCrx = (dbr->get_digi_ttcrx(m.drawer_ID, m.digitizer));
	else
		theTTCrx = (dbr->get_ttcrx(m.drawer_ID));

	if ((m.type == TTC_MESSAGE_DIGI) && (theTTCrx == 0) && (m.digitizer != 0)) {
		// Digitizer not existent
	} else {
	  //		*(unsigned int *)(ttcvi_addr + TTCVI_LONG)=TTCVI_B_DATA(theTTCrx,m.ext, m.sub_add,m.data);
	  myttc->b_long_f(theTTCrx, m.ext, m.sub_add, m.data);  // Trying blong_f() Henric 25/03/2022
		
	}
	
	
        if (verbose && (m.type == TTC_MESSAGE_DRAWER)) cout << dbr->index2string(m.drawer_ID) << " (TTCRX = " << theTTCrx << ")   " << msg2string(m.sub_add) << "   " << m.data << " (ext = " <<m.ext << ")" << endl;
        else if (verbose) cout << dbr->index2string(m.drawer_ID) << "   DIGI_TTCRX: " << theTTCrx << "   " << msg2string(m.sub_add) << "   " << m.data << " (ext = " << m.ext << ")"<< endl;
}

dbRead::dbRead(int sector, Configuration *confDB)
  : m_db(confDB)
{
	_sector = sector;

	for (int i = 0; i < 65; i++)
	{
		ttcrx[i] = 0;
		 used[i] = false;
	}

	used[0] = true;
}

inline int dbRead::get_ttcrx(int index)
{
	if (used[index] == false)
	{
		m_db.SetDrawer(index2string(index).c_str());
		const Tiledal::TileDrawerModule *dm = m_db.GetModule();

		ttcrx[index] = dm->get_mb_ttcrx();
		used[index] = true;
	}
	
	return ttcrx[index];
}

inline int dbRead::get_digi_ttcrx(int index, int digi)
{
	int ttcrx = 0;
	m_db.SetDrawer(index2string(index).c_str());
	const Tiledal::TileDrawerModule *dm = m_db.GetModule();
	switch (digi) {
		case 0:
			ttcrx = dm->get_digi_ttcrx_1();
			break;
		case 1:
			ttcrx = dm->get_digi_ttcrx_2();
			break;
		case 2:
			ttcrx = dm->get_digi_ttcrx_3();
			break;
		case 3:
			ttcrx = dm->get_digi_ttcrx_4();
			break;
		case 4:
			ttcrx = dm->get_digi_ttcrx_5();
			break;
		case 5:
			ttcrx = dm->get_digi_ttcrx_6();
			break;
		case 6:
			ttcrx = dm->get_digi_ttcrx_7();
			break;
		case 7:
			ttcrx = dm->get_digi_ttcrx_8();
			break;
		default:
			cout << "ERROR: Trying to access ttcrx for digitizer " << digi+1 << " at drawer " << index << endl;
			break;
	}
	return ttcrx;
}

const string dbRead::index2string(int index)
{
	string drawer;
	
	if (_sector == 1 || _sector == 2)
		drawer = "LB";
	else
		drawer = "EB";

	if (_sector == 1 || _sector == 3)
		drawer = drawer + "A";
	else
		drawer = drawer + "C";

	if (index < 10) drawer = drawer + "0";

	stringstream si;
        si << index;

	drawer = drawer + si.str();

	return drawer;
}
