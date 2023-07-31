//Nov-2019 by Andrey Ryzhov and Humphry Tlou - updated ttcvi to ttc class

#include <iostream>
#include <sstream>
#include <fstream>
#include <cmdl/cmdargs.h>
#include <readline/readline.h>
#include <readline/history.h>
#include <stdio.h>
#include <algorithm>
#include <string>
#include <filesystem>

#include "TileCIS/pipeline.h"
#include "TileCIS/TileBuilder.h"
#include "TileVMEboards/TileTTC.h"
#include "TileVMEboards/3in1ttc.h"
#include "RCDLtp/RCDLtp.h"
#include "RCDVme/RCDCmemSegment.h"

extern unsigned long vme_a24_base();
// b_go_mode. Changed for the SHAFT 04/02/2008
#define B_GO_MODE  0xD

#define PROMPT  "cis> "

#define ARG_DRW "values: <0 - 64>, default value:  0 (broadcast )."
#define ARG_TWR "values: <0 - 09>, default value: -1 (don't care), type 0 to broadcast."
#define ARG_PMT "values: <0 - 48>, default value:  0 (broadcast )."
#define ARG_VBS "turn on 'verbose' mode."

/*********************************************************************************/
/***************************** Commands definition *******************************/
/*********************************************************************************/

#define RESET_ALL "ResetAll"
#define INJECT    "Inject"
#define C_SMALL   "SetCSmall"
#define C_LARGE   "SetCLarge"
#define DAC       "SetDAC"
#define CHARGE    "SetCharge"
#define TRIGGER   "TrgOut"
#define SHOW_DRW  "ShowDrawer"
#define DELAY     "i3Delay"
#define EXECUTE   "Execute"
#define EXIT      "Exit"

/*********************************************************************************/
/****************************** Readline interface *******************************/
/*********************************************************************************/

const char *commands[] = {RESET_ALL,
                          INJECT   ,
                          C_SMALL  ,
                          C_LARGE  ,
		          DAC      ,
		          CHARGE   ,
		          TRIGGER  ,
		          SHOW_DRW ,
		          DELAY    ,
			  EXECUTE  ,
		          EXIT     ,
			  (const char *)NULL};

static char *line_read = (char *)NULL;

char *rl_gets()
{
	if (line_read)
    	{
      		free(line_read);
      		line_read = (char *)NULL;
    	}
  
  	line_read = readline(PROMPT);
  	if (line_read && *line_read) add_history(line_read);

  	return (line_read);
}

char *dupstr(const char *s)
{
  	char *r = new char[strlen(s)+1];
  	strcpy(r,s);

  	return (r);
}

char *command_generator(const char *text, int state)
{
  	static int list_index, len;
  	char *name;

  	if (!state)
    	{
       		list_index = 0;
       		len = strlen(text);
    	}

  	while (commands[list_index] != NULL)
    	{
		name = (char *)commands[list_index];
       		list_index++;
       		if (strncmp(name, text, len) == 0)
         	return (dupstr(name));
    	}
  	
  	return ((char *)NULL);
}

char **cmd_completion (const char *text, int start, int end)
{
	char **matches = (char **)NULL;
	int pos = end; pos = start;
	if (pos == 0) matches = rl_completion_matches(text, command_generator);

	return (matches);
}

void init_readline()
{
	rl_attempted_completion_function = cmd_completion;
}

/*********************************************************************************/
/******************************* CmdLine interface *******************************/
/*********************************************************************************/

void CmdLineError(int value)
{
	value = value; 
	//just to avoid to quit the application
}

char **GetCmd(const string &s, int &_argc)
{

        /*********************** command line to string **********************/
	
	//char *cs = rl_gets();
	//string s = cs;

        /*********************** create list of strings ***********************/

	vector<string> t;

        unsigned int ptr = 0;
        while (ptr < s.size())
        {
                if (s[ptr] != ' ')
                {
                        string ts;
                        while (s[ptr] != ' ' && ptr < s.size())
                        {
                                ts += s[ptr];
                                ptr++;
                        }
                        t.push_back(ts);
                }
                else ptr++;
        }
	
        /************************* fill argc & *argv[] ************************/

	_argc = t.size();
        char **_argv = new char*[_argc];

        for (int i = 0; i < _argc; i++)
        {
                _argv[i] = new char[t[i].size()+1];
                for (unsigned int j = 0; j < t[i].size(); j++)
                {
                        _argv[i][j] = t[i][j];
                }
		_argv[i][t[i].size()] = '\0';
        }

	return _argv;
}

/*********************************************************************************/
/***************************** Command implemenattion ****************************/
/*********************************************************************************/

int cmdResetAll(int argc, char **argv, bool &verbose)
{
        CmdArgBool _verbose ('v', "verbose", ARG_VBS);

        CmdLine cmdl(*argv,&_verbose, NULL);
        cmdl.description("Reset all drawers in the partition");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        _verbose = false;

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;

	string p;
        for (int i = 1; i < argc; i++)
        {
                p = argv[i];
                if (p == "-h") ret = 0;
        }

        verbose = _verbose;

        return ret;
}

int cmdInject(int argc, char **argv, float &param, bool &verbose)
{
        CmdArgFloat  _param   ('a', "parameter", "parameter", "values: '0' to stop, '1' to start, default value: '1'");
        CmdArgBool   _verbose ('v', "verbose"  , ARG_VBS);

        CmdLine cmdl(*argv,&_param,&_verbose, NULL);
        cmdl.description("Cofigure TTC to inject charge and send trigger");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        _param = 1; _verbose = false;

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;

	string p;
        for (int i = 1; i < argc; i++)
        {
                p = argv[i];
                if (p == "-h") ret = 0;
        }

        param = _param; verbose = _verbose;

        return ret;
}

int cmdSetCSmall(int argc, char **argv, int &drawer, int &tower, int &pmt, float &param, bool &verbose)
{
        CmdArgInt    _drawer  ('d', "drawer"   , "drawer"   , ARG_DRW);
        CmdArgInt    _tower   ('t', "tower"    , "tower"    , ARG_TWR);
        CmdArgInt    _pmt     ('p', "PMT"      , "PMT"      , ARG_PMT);
        CmdArgFloat  _param   ('a', "parameter", "parameter", "values: '0' to disable, '1' to enable, default value: '1'");
        CmdArgBool   _verbose ('v', "verbose"  , ARG_VBS);

        CmdLine cmdl(*argv,&_drawer,&_tower,&_pmt,&_param,&_verbose, NULL);
        cmdl.description("Enable/Disable small capacitor");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        _drawer = 0; _tower = -1; _pmt = 0; _param = 1; _verbose = false;

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;

	string p;
        for (int i = 1; i < argc; i++)
        {
                p = argv[i];
                if (p == "-h") ret = 0;
        }

        drawer = _drawer; tower = _tower; pmt = _pmt; param = _param; verbose = _verbose;

        return ret;
}

int cmdSetCLarge(int argc, char **argv, int &drawer, int &tower, int &pmt, float &param, bool &verbose)
{
        CmdArgInt    _drawer  ('d', "drawer"   , "drawer"   , ARG_DRW);
        CmdArgInt    _tower   ('t', "tower"    , "tower"    , ARG_TWR);
        CmdArgInt    _pmt     ('p', "PMT"      , "PMT"      , ARG_PMT);
        CmdArgFloat  _param   ('a', "parameter", "parameter", "values: '0' to disable, '1' to enable, default value: '1'");
        CmdArgBool   _verbose ('v', "verbose"  , ARG_VBS);

        CmdLine cmdl(*argv,&_drawer,&_tower,&_pmt,&_param,&_verbose, NULL);
        cmdl.description("Enable/Disable large capacitor");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        _drawer = 0; _tower = -1; _pmt = 0; _param = 1; _verbose = false;

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;

	string p;
        for (int i = 1; i < argc; i++)
        {
                p = argv[i];
                if (p == "-h") ret = 0;
        }

        drawer = _drawer; tower = _tower; pmt = _pmt; param = _param; verbose = _verbose;

        return ret;
}

int cmdSetDAC(int argc, char **argv, int &drawer, int &tower, int &pmt, float &param, bool &verbose)
{
        CmdArgInt    _drawer  ('d', "drawer"   , "drawer"   , ARG_DRW);
        CmdArgInt    _tower   ('t', "tower"    , "tower"    , ARG_TWR);
        CmdArgInt    _pmt     ('p', "PMT"      , "PMT"      , ARG_PMT);
        CmdArgFloat  _param   ('a', "DAC"      , "DAC"      , "values: <0 - 1023>, default value: 0");
        CmdArgBool   _verbose ('v', "verbose"  , ARG_VBS);

        CmdLine cmdl(*argv,&_drawer,&_tower,&_pmt,&_param,&_verbose, NULL);
        cmdl.description("Set the DAC value");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        _drawer = 0; _tower = -1; _pmt = 0; _param = 0; _verbose = false;

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;

	string p;
        for (int i = 1; i < argc; i++)
        {
                p = argv[i];
                if (p == "-h") ret = 0;
        }

        drawer = _drawer; tower = _tower; pmt = _pmt; param = _param; verbose = _verbose;

        return ret;
}

int cmdSetCharge(int argc, char **argv, int &drawer, int &tower, int &pmt, float &param, bool &verbose)
{
        CmdArgInt    _drawer  ('d', "drawer"   , "drawer"   , ARG_DRW);
        CmdArgInt    _tower   ('t', "tower"    , "tower"    , ARG_TWR);
        CmdArgInt    _pmt     ('p', "PMT"      , "PMT"      , ARG_PMT);
        CmdArgFloat  _param   ('a', "charge"   , "charge"   , "values: <0.0 - 800.0>, default value: 0.0");
        CmdArgBool   _verbose ('v', "verbose"  , ARG_VBS);

        CmdLine cmdl(*argv,&_drawer,&_tower,&_pmt,&_param,&_verbose, NULL);
        cmdl.description("Set the injected charge in pC");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        _drawer = 0; _tower = -1; _pmt = 0; _param = 0.0; _verbose = false;

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;

	string p;
        for (int i = 1; i < argc; i++)
        {
                p = argv[i];
                if (p == "-h") ret = 0;
        }

        drawer = _drawer; tower = _tower; pmt = _pmt; param = _param; verbose = _verbose;

        return ret;
}

int cmdTrgOut(int argc, char **argv, int &drawer, int &tower, int &pmt, float &param, bool &verbose)
{
        CmdArgInt    _drawer  ('d', "drawer"   , "drawer"   , ARG_DRW);
        CmdArgInt    _tower   ('t', "tower"    , "tower"    , ARG_TWR);
        CmdArgInt    _pmt     ('p', "PMT"      , "PMT"      , ARG_PMT);
        CmdArgFloat  _param   ('a', "parameter", "parameter", "values: '0' to disable, '1' to enable, default value: '1'");
        CmdArgBool   _verbose ('v', "verbose"  , ARG_VBS);

        CmdLine cmdl(*argv,&_drawer,&_tower,&_pmt,&_param,&_verbose, NULL);
        cmdl.description("Enable/Disable trigger output");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        _drawer = 0; _tower = -1; _pmt = 0; _param = 1; _verbose = false;

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;

	string p;
        for (int i = 1; i < argc; i++)
        {
                p = argv[i];
                if (p == "-h") ret = 0;
        }

        drawer = _drawer; tower = _tower; pmt = _pmt; param = _param; verbose = _verbose;

        return ret;
}

int cmdShowDrawer(int argc, char **argv, int &drawer)
{
        CmdArgInt  _drawer  ('d', "drawer"   , "drawer"   , "values: <1 - 64>");

        CmdLine cmdl(*argv,&_drawer, NULL);
        cmdl.description("Show the state of the drawer");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        _drawer = 0;

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;

	string p;
        for (int i = 1; i < argc; i++)
        {
                p = argv[i];
                if (p == "-h") ret = 0;
        }

        drawer = _drawer;

        return ret;
}

int cmdi3Delay(int argc, char **argv, float &param)
{
        CmdArgFloat  _param   ('a', "delay", "delay", "i3Delay value, default value: 150");

        CmdLine cmdl(*argv,&_param,NULL);
        cmdl.description("Set i3Delay value");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        _param = 150;

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;
	
	string p;
	for (int i = 1; i < argc; i++)
	{
		p = argv[i];
		if (p == "-h") ret = 0;
	}

        param = _param;

        return ret;
}

int cmdExecute(int argc, char **argv, string &fname)
{
	CmdArgStr _fname('f', "file", "file", "file name");

	CmdLine cmdl(*argv,&_fname,NULL);
        cmdl.description("Execute script file");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        _fname = "";

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;

        string p;
        for (int i = 1; i < argc; i++)
        {
                p = argv[i];
                if (p == "-h") ret = 0;
        }

        fname = _fname;

        return ret;
}

int cmdExit(int argc, char **argv)
{
        CmdLine cmdl(*argv, NULL);
        cmdl.description("Quit tilecis application");
        cmdl.quit_handler(CmdLineError);

        CmdArgvIter arg_iter(argc-1,argv+1);

        int ret = 1;
        if (cmdl.parse(arg_iter) != 0) ret = 0;

	string p;
        for (int i = 1; i < argc; i++)
        {
                p = argv[i];
                if (p == "-h") ret = 0;
        }

        return ret;
}

/******************************************************************************/
/***************************** auxiliar functions *****************************/
/******************************************************************************/

void Inject(int sync, TileTTC &myttc, int i3delay, int select_ttc)
{
	myttc.b_go_clear(0);
        myttc.b_go_clear(1);
        myttc.b_go_clear(2);
        myttc.b_go_clear(3);

	if (sync)
        {
                myttc.b_go_mode(0,B_GO_MODE,0,10);
                myttc.b_go_short(0,0x1);         // reset bcid every orbit

                myttc.b_go_mode(1,B_GO_MODE,40,10);    // 1us delay after orbit
                myttc.b_go_fill(1,0x0,0xC0,0x0); // load set tp_high

                myttc.b_go_mode(2,B_GO_MODE,2000,10);  // 50us delay for charging, not OK for 22us?
                myttc.b_go_fill(2,0x0,0xC0,0x1); // load set tp_low
		
				myttc.b_go_mode(3,B_GO_MODE,2000+i3delay,10);

				if (select_ttc == 1) {//for ALTI, board configured during myttc.reset(); //run trigger
					LVL1::AltiModule* alti = myttc.getALTI();
					if (alti) {
						if ( alti->BSYConstLevelRegWrite(false) !=  LVL1::AltiModule::SUCCESS) {
							cout << "Error during BSYConstLevelRegWrite(false)" << endl;
						}	
						      // disable MEM snapshot
						if ((alti->PRMModeWrite("SNAPSHOT")) != LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::PRMModeWrite(SNAPSHOT)" << endl;
						}
						if ((alti->PRMEnableWrite(false)) != LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::PRMEnableWrite(false)" << endl;
						}
								
						// disable MEM pattern generation
						if ( alti->PRMModeWrite("PATTERN") !=  LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::PRMModeWrite(PATTERN)" << endl;
						}
						if ( alti->PRMEnableWrite(false) !=  LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::PRMEnableWrite(false)" << endl;
						}
						
						// write MEM pattern generation control configuration
						if (alti->PRMRepeatWrite(true) != LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::PRMRepeatWrite(true)" << endl;
						}

						//5 lines PG start addres = 0, last = 4
						if ( alti->PRMStartAddressWrite(0) != 0) {
						cout << "TileTTC::AltiModule::PRMStartAddressWrite(0)" << endl;
						}
						if ( alti->PRMStopAddressWrite(4) != 0) {
						cout << "TileTTC::AltiModule::PRMStopAddressWrite(4)" << endl;
						}


						std::ostringstream name;
						name << "/tmp/pg_template_for_tile_alti_tilecis_X";
						
						std::ofstream fout(name.str().c_str());
						std::filesystem::permissions(name.str(),
										std::filesystem::perms::owner_read | std::filesystem::perms::owner_write | std::filesystem::perms::group_read | std::filesystem::perms::group_read | std::filesystem::perms::others_read | std::filesystem::perms::others_write, 
										std::filesystem::perm_options::add);

						if(fout) {   
							        fout << "1 0000 0x00 0000 0000 40" << std::endl;
									//fout << "0 0000 0x00 0000 0000 2082" << std::endl;
									fout << "0 0000 0x00 0000 0000 " << 2000+i3delay << std::endl;
									fout << "0 0000 0x32 0000 0001 1" << std::endl;
									fout << "0 0000 0x32 0000 0000 4" << std::endl;
									//fout << "0 0000 0x00 0000 0000 1434" << std::endl; 
									fout << "0 0000 0x00 0000 0000 " << 3561-45-2000-i3delay << std::endl;    
									fout.close();
						} else {
							cout << "TileTTC::AltiModule::Can't create file - /tmp/pg_template_for_tile_alti_tilecis_X" <<  ")" << endl;
						}
					
						std::ifstream inf(name.str().c_str(), std::ifstream::in);
						// create CMEM segement
						std::string snam = "AltiCalib";
						RCD::CMEMSegment* segment = new RCD::CMEMSegment(snam, sizeof(u_int)*LVL1::AltiModule::MAX_MEMORY, true);
						
						
						if (inf) {
							if ((*segment)() == CMEM_RCC_SUCCESS) {
							if ((alti->PRMWriteFile(segment, inf)) != LVL1::AltiModule::SUCCESS) {
								cout << "TileTTC::AltiModule::PRMWriteFile(segment, inf))" << endl;
							}
							} else {
							cout << "TileTTC::AltiModule::Can't create CMEM segment" << endl;
							}
						} else {
							cout << "TileTTC::AltiModule::Can't open file - /tmp/pg_template_for_tile_alti_tilecis_X" <<  ")" << endl;
						}
						
						//enable masking
						//Note: an internal ORBIT signal is generated if input_orbit = PG and if the ORBIT signal is masked in the Pattern Generator
						if ( alti->SIGOutputSelectOrbitWrite("PATTERN") !=  LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::SIGOutputSelectOrbitWrite(PATTERN)" << endl;
						}

						if ( alti->SIGOutputSelectTestTriggerWrite(0, "PATTERN") !=  LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::SIGOutputSelectTestTriggerWrite(0, PATTERN)" << endl;
						}

						if ( alti->SIGOutputSelectL1aWrite("PATTERN") !=  LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::SIGOutputSelectL1aWrite(PATTERN)" << endl;
						}

						if ( alti->SIGOutputSelectTriggerTypeWrite("PATTERN") !=  LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::SIGOutputSelectTriggerTypeWrite(PATTERN)" << endl;
						}
						
						// start pattern generator
						if ( alti->PRMModeWrite("PATTERN") !=  LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::PRMModeWrite(PATTERN)" << endl;
						}
						if ( alti->PRMEnableWrite(true) !=  LVL1::AltiModule::SUCCESS) {
						cout << "TileTTC::AltiModule::PRMEnableWrite(true)" << endl;
						}
						
						if (segment) delete segment;
						std::system(("rm " + name.str()).c_str());	
					}

				}
        }
	else
	{
		myttc.b_go_mode(0,B_GO_MODE,0,0);
		myttc.b_go_mode(1,B_GO_MODE,0,0);
		myttc.b_go_mode(2,B_GO_MODE,0,0);
		myttc.b_go_mode(3,B_GO_MODE,0,0);
	}
}

void ResetAll(TileTTC &myttc, int select_ttc)
{

        /************************** resetting TTC ***************************/

  	myttc.set_orbit(1);
  	myttc.set_rate(0);
  	myttc.set_delay(100);
  	myttc.reset();

        myttc.b_long(0x0,0,6,0);       // reset all
        myttc.b_long(0x0,0,3,0xAB);    // get both BCid and EVid

        /************************** clear broadcast ***************************/

        tin1ttc tctrl(&myttc, 0x0); // ttcrx = 0 , all drawers

        tctrl.set_multi(1); // disable broadcast
        for(int j=1; j<49; j++)
        {
                tctrl.set_tube(j); // select card
                tctrl.set_mse (1); // enable response to the broadcast
        }
        tctrl.set_multi(0); // enable broadcast

        /***************************** reset all ******************************/

	tctrl.set_delay(40000);
        tctrl.set_dac(0);
        tctrl.set_mb_times(0,0,0,0);
	tctrl.set_delay(100);
        tctrl.set_csmall(0);
        tctrl.set_clarge(0);
        tctrl.set_trigger(0);

	/**************************** free busy *******************************/
	if (select_ttc == 0){//for TTCvi

	    RCD::LTP *ltp = new RCD::LTP();
  	    ltp->Open(0xF00000);
  	    ltp->Reset();
  	    ltp->OM_master_lemo();
  	    ltp->BUSY_disable_constant_level();
  	    ltp->IO_disable_busy_gating(RCD::LTP::TR1);

	    delete ltp;
	} else if (select_ttc == 1) {//for ALTI, board configured during myttc.reset();
		LVL1::AltiModule* alti = myttc.getALTI();
    	if (alti) {
	    	if (alti->BSYConstLevelRegWrite(false) !=  LVL1::AltiModule::SUCCESS) { //false in constructor after configuration: bsy_data_vme                 = false;
				cout << "Error during BSYConstLevelRegWrite(false)" << endl;
			}
			if (alti->BSYMaskingTTREnableWrite(1, false) !=  LVL1::AltiModule::SUCCESS) {
				cout << "Error during BSYMaskingTTREnableWrite(1, false)" << endl;
			}			
		}
	} else {
	    cout << "invalid select ttc" << endl;
	    exit (1);
	    //invalid configuration - do nothing
	}

	/*************************** reset b_gos ******************************/

	Inject(0,myttc,150, select_ttc);
}

void ShowDrawer(int drawer, SectionState *state)
{
	 state->drawer[drawer-1].ShowInConsole(false);
}

void open_file(const string &fname, vector<ifstream *> &files)
{
	ifstream *fs = new ifstream(fname.c_str());
        if (fs->is_open()) files.push_back(fs);
        else
        {
        	cout << "Error: could not open file '" << fname << "'" << endl;
                delete fs;
        }
}

int main(int argc, char *argv[])
{
	/*************************** parse parameters ************************/

	//CmdArgInt  section ('p', "partition", "partition", "LBA = 1, LBC = 2, EBA = 3, EBC = 4");
	CmdArgStr    filename('f', "file"     , "file"     , "CIS script file name"              );	
	CmdArgStr    selectTTC    ('t', "ttc", "ttc", "select TTC: TTCVI or ALTI");
	CmdArgInt    addr         ('a', "address","address","slot number (dec) or VME address (hex - required '0x')");


	//	CmdLine cmdl(*argv,&section,&filename,NULL);
	CmdLine cmdl(*argv,&filename, &selectTTC, &addr,NULL);
	cmdl.description("Command line based program to charge injection (TileCal)");

	CmdArgvIter arg_iter(argc-1,argv+1);

	//	section  = 1;
	filename = "";
	// selectTTC   = "TTCVI";
	// addr        = 0xA00000;
	selectTTC   = "ALTI";
	addr        = 5;

	cmdl.parse(arg_iter);

  	string mselectTTC(selectTTC);

  	std::transform(mselectTTC.begin(), mselectTTC.end(), mselectTTC.begin(), ::toupper); // change mselectTTC to UpperCase

	unsigned long addrToConstructor = 0;
	int select_ttc = 0;
  	if (addr >= 0 && addr < 1) {
    	addrToConstructor = 0xA00000;
      	select_ttc = 0;
  	} else if (addr >= 1 && addr < 32) {
     	addrToConstructor = addr;
      	select_ttc = 1;
  	} else if (addr >= 0x20 && addr < 0x1000000) {
      	addrToConstructor = addr;
      	select_ttc = 0;
  	} else if (addr >= 0x1000000) {
      	addrToConstructor = addr>>23;
      	select_ttc = 1;
  	}	

    if ((select_ttc == 0 && mselectTTC != "TTCVI") || (select_ttc == 1 && mselectTTC != "ALTI")) {
		cout << "Address " << ((addr<32) ? "" : "0x") << ((addr<32) ? dec : hex) << addr << " is not valid for " << mselectTTC << endl;
		exit (1);
	}

	/*************************** script queue ****************************/

	vector<ifstream *> in;

	string fname(filename);
	if (fname != "") open_file(fname,in);

	/********************* variables initializations **********************/
	
	init_readline();

	int section;
	string str_section = getenv("TDAQ_PARTITION")?getenv("TDAQ_PARTITION"):"";
	if(str_section == ""){
	  cout << "tilecis: TDAQ partition must be set first" << endl;
	  return 1;
	}

	if(str_section.find("LBA") != string::npos){
	  section = 1;
	}else if(str_section.find("LBC") != string::npos){
	  section = 2;
	}else if(str_section.find("EBA") != string::npos){
	  section = 3;
	}else if(str_section.find("EBC") != string::npos){
	  section = 4;
	}

	TileBuilder Builder;
	DetectorObject *TheTileSection = Builder.BuildSection(section);

	MessageList ml;
	SectionState *state = new SectionState(section);




	//int i3delay = 150;
	int i3delay = 82; //for ALTI
	int injecting = 0;


	dbRead *db  = new dbRead(section);
	TileTTC myttc(select_ttc, 1, addrToConstructor + vme_a24_base(), addrToConstructor, true); //useDVS mode = true to configure ALTI standalone


	pipeline p(db, &myttc);

	
	string cmd; int drawer, tower, pmt; bool verbose; float param;

	char aux[512]; 
	while (1)
	{

	if (in.size() > 0)
	{
		in[in.size()-1]->getline(aux,512);
		cmd = aux;
		if (in[in.size()-1]->eof())
		{
			in[in.size()-1]->close();
			delete in[in.size()-1];
			in.pop_back();
			continue;
		}
	}
	else
	{
		char *cs = rl_gets();
        	cmd = cs;
	}

	int _argc;
	char **_argv = GetCmd(cmd,_argc);

        TileCommand *command;
	string c = _argv[0];

	if (c == RESET_ALL)
	{
		if (cmdResetAll(_argc,_argv,verbose))
		{
			ResetAll(myttc, select_ttc); state->ResetAll();
		}
		continue;
	}
	else if (c == INJECT)
	{
		if (cmdInject(_argc,_argv,param,verbose))
		{
			injecting = (int)param; Inject((int)param,myttc,i3delay, select_ttc);
		}
		continue;
	}
	else if (c == C_SMALL)
	{
		if (cmdSetCSmall(_argc,_argv,drawer,tower,pmt,param,verbose))
		{
			command = new cSetCSmall(&ml,state,false);
		} 
		else continue;
	}
	else if (c == C_LARGE)
	{
		if (cmdSetCLarge(_argc,_argv,drawer,tower,pmt,param,verbose))
		{
			command = new cSetCLarge(&ml,state,false);
		} 
		else continue;
	}
	else if (c == DAC)
	{
		if (cmdSetDAC(_argc,_argv,drawer,tower,pmt,param,verbose))
		{
			command = new cSetDAC(&ml,state,false);
		} 
		else continue;
	}
	else if (c == CHARGE)
	{
		if (cmdSetCharge(_argc,_argv,drawer,tower,pmt,param,verbose))
		{
			command = new cSetCharge(&ml,state,false);
		} 
		else continue;
	}
	else if (c == TRIGGER)
	{
		if (cmdTrgOut(_argc,_argv,drawer,tower,pmt,param,verbose))
		{
			command = new cEnableTrigger(&ml,state,false);
		} 
		else continue;
	}
	else if (c == SHOW_DRW)
	{
		if (cmdShowDrawer(_argc,_argv,drawer))
		{
			ShowDrawer(drawer,state);
		} 
		continue;
	}
	else if (c == DELAY)
	{
		if (cmdi3Delay(_argc,_argv,param))
		{
			i3delay = (int)param; Inject(injecting,myttc,i3delay, select_ttc);
		} 
		continue;
	}
	else if (c == EXECUTE)
	{
		if (cmdExecute(_argc,_argv,fname))
		{
			open_file(fname,in);	
		}
		continue;
	}
	else if (c == EXIT)
	{
		if (cmdExit(_argc,_argv))
		{
			return 0;
		} 
		continue;
	}
	else{cout << "'" << c << "': " << "commad not found" << endl; continue;}

	/*************************** get target *******************************/

	TileTarget *target = new TileTarget(0,drawer,tower,pmt,param);

	/********************** building message list *************************/

	TheTileSection->Execute(command,target);

	delete target;
	delete command;

	/*********************** executing message list ***********************/

	p.verbose = verbose;
	p.execute(ml);

	for (int i = 0; i < _argc; i++) delete[] _argv[i];
	delete[] _argv;

	}
}
