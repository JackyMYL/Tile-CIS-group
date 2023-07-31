#include "TileCIS/TileState.h"
#include <iostream>

PMTState::PMTState(int section, int drawer, int channel)
{
        _dac = -1;
        _trigger = -1;
        _csmall = -1;
        isoff = true;
        //Use constructor to load the file  to load in the file 
        //_isoff = (section == 1) && (drawer == 13) && (PMT == 0);
        std::cout << section << " " << drawer << " " << channel;
        // Multiplier for amount of charge based on Cs, Laser constants
        //Read in a file with constants for (section, drawer, channel)
        k = 1;

}


void PMTState::set_dac(int value)
{
        std::cout << "TileState.cxx set_dac()" << isoff;
        if (isoff)
        {
                _dac = 0;
                std::cout << "Skip ... setting _dac to zero";
        } else
                {
                        _dac = value;
                }
}

void PMTState::set_trigger(int value)
{
        if (isoff)
        {
                _trigger = 0;
                std::cout << "Skip ... setting _trigger to zero";
        } else 
        {
                _trigger = value;
        }
}

void PMTState::set_csmall(int value)
{
        if (isoff)
        {
                _csmall = 0;
                std::cout << "Skip ... setting _csmall to zero";
        } else
        {
                _csmall = k*value;
        }
}

void PMTState::set_clarge(int value)
{ 
        std::cout << "set_clarge() multiplier: k = " << k;
        if (isoff)
        {
                _clarge = 0;
                std::cout << "Skip ... setting _clarge to zero";
        } else
        {
                _clarge = k*value;
        }
}

DrawerState::DrawerState(int section, int drawer) //Add another argument here  "int module" to add logic based on (section, module, PMT)
                                     //Then change the PMTState() defaults or how and when the function applies 
{
        _section = section;
        _drawer = drawer;
        _broadcast = -1;
        _tube = -1;

        if (section > 0 && section < 3)
                for (int i = 0; i < 45; i++) pmt.push_back(PMTState(section, drawer, i));
                //Peter
                //Here we call on the DrawerState constructor which has a list of PMTs in the drawer
                // Given information: section (EBA, LBA, EBC, LBC); PMT number (excluding blank slots)
                // Need: module number!!!!

        if (section > 2 && section < 5)
                for (int i = 0; i < 32; i++) pmt.push_back(PMTState(section, drawer, i));
}
//Peter
//THis is the contrsuctor. When do we call DrawerState() to initilize it in the main funciton, though??????


bool DrawerState::AnyDACIsDifferentFrom(int value)
{
        for (unsigned int i = 0; i < pmt.size(); i++)
                if (pmt[i].get_dac() != value) return true;

        return false;
}

bool DrawerState::AnyTriggerIsDifferentFrom(int value)
{
        for (unsigned int i = 0; i < pmt.size(); i++)
                if (pmt[i].get_trigger() != value) return true;

        return false;
}

bool DrawerState::AnyCSmallIsDifferentFrom(int value)
{
        for (unsigned int i = 0; i < pmt.size(); i++)
                if (pmt[i].get_csmall() != value) return true;

        return false;
}

bool DrawerState::AnyCLargeIsDifferentFrom(int value)
{
        for (unsigned int i = 0; i < pmt.size(); i++)
                if (pmt[i].get_clarge() != value) return true;

        return false;
}

void DrawerState::set_dac(int value)
{
        for (unsigned int i = 0; i < pmt.size(); i++) pmt[i].set_dac(value);
}

void DrawerState::set_trigger(int value)
{
        for (unsigned int i = 0; i < pmt.size(); i++) pmt[i].set_trigger(value);
}

void DrawerState::set_csmall(int value)
{
        for (unsigned int i = 0; i < pmt.size(); i++) pmt[i].set_csmall(value);
}

void DrawerState::set_clarge(int value)
{
        for (unsigned int i = 0; i < pmt.size(); i++) pmt[i].set_clarge(value);
}

SectionState::SectionState(int section)
{
        _section = section;

        for (int i = 0; i < 64; i++)
                drawer.push_back(DrawerState(section, i));
}

bool SectionState::AnyDrawerBroadcastIsDifferentFrom(int value)
{
        for (int i = 0; i < 64; i++)
                if (drawer[i].get_broadcast() != value) return true;

        return false;
}

bool SectionState::AnyTubeIsDifferentFrom(int value)
{
        for (int i = 0; i < 64; i++)
                if (drawer[i].get_tube() != value) return true;

        return false;
}

bool SectionState::AnyDACIsDifferentFrom(int value)
{
        for (int i = 0; i < 64; i++)
                if (drawer[i].AnyDACIsDifferentFrom(value)) return true;

        return false;
}

bool SectionState::AnyTriggerIsDifferentFrom(int value)
{
        for (int i = 0; i < 64; i++)
                if (drawer[i].AnyTriggerIsDifferentFrom(value)) return true;

        return false;
}

bool SectionState::AnyCSmallIsDifferentFrom(int value)
{
        for (int i = 0; i < 64; i++)
                if (drawer[i].AnyCSmallIsDifferentFrom(value)) return true;

        return false;
}

bool SectionState::AnyCLargeIsDifferentFrom(int value)
{
        for (int i = 0; i < 64; i++)
                if (drawer[i].AnyCLargeIsDifferentFrom(value)) return true;

        return false;
}

void SectionState::set_DrawerBroadcast(int value)
{
        for (int i = 0; i < 64; i++) drawer[i].set_broadcast(value);
}

void SectionState::set_tube(int value)
{
        for (int i = 0; i < 64; i++) drawer[i].set_tube(value);
}

void SectionState::set_dac(int value)
{
        for (int i = 0; i < 64; i++) drawer[i].set_dac(value);
}

void SectionState::set_trigger(int value)
{
        for (int i = 0; i < 64; i++) drawer[i].set_trigger(value);
}

void SectionState::set_csmall(int value)
{
        for (int i = 0; i < 64; i++) drawer[i].set_csmall(value);
}

void SectionState::set_clarge(int value)
{
        for (int i = 0; i < 64; i++) drawer[i].set_clarge(value);
}

void SectionState::ResetAll()
{
	set_dac(0);
	set_trigger(0);
	set_csmall(0);
	set_clarge(0);
	set_DrawerBroadcast(0);
}

void DrawerState::ShowInConsole(bool LikeTrigger)
{

  int chan[45] = {1, 14, 15, 26, 27, 40, 43,
                  4, 3, 8, 7, 13, 12, 18, 17, 22, 23, 30, 29, 36, 35, 42, 41,
                  46, 45,
                  2, 5, 6, 9, 10, 11, 16, 19, 20, 21, 24, 25, 28, 31, 34, 37, 38, 39, 48, 47};

  int  pos[45] = {6, 19, 33, 47, 61, 79, 101,
                  2, 8, 14, 20, 26, 32, 38, 45, 52, 59, 66, 74, 81, 89, 98, 108,
                  101, 109,
                  1, 5, 10, 14, 20, 24, 30, 34, 40, 44, 50, 56, 62, 68, 74, 82, 88, 96, 102, 110};

  std::string s,sd;
  char cd[3];
  int d[48] = {0},i;

  int index2pmt[48] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,0,0,32,33,34,35,
                       36,37,38,39,40,41,0,42,43,44,45};

  int index;
  for (i = 0; i < 48; i++)
  {
    index = index2pmt[i];
    if (index != 0) d[i] = pmt[index-1].get_dac();
  }

  std::cout << "\n";
  std::cout << "+-----------------------------------------------------------------------------------------------------------------+\n";

  if (LikeTrigger)
    s =        "|     1C5     |    2C5           3C5     |     4C5           5C5     |         6C5                   7C5          |\n";
  else
    s =        "|     C01     |    C14           C15     |     C26           C27     |         C40                   C43          |\n";

  std::cout << s;
  std::cout << "|             |            |             |             |             |                    |                       |\n";
  s =          "|             |                          |                           |                                            |\n";

  for (i = 0; i < 7; i++) {sprintf(cd,"%d",d[chan[i]-1]); sd = cd; s.replace(pos[i],sd.size(),sd);}

  std::cout << s;
  std::cout << "|-----------------------------------------------------------------------------------------------------------------|\n";

  if (LikeTrigger)
    s =        "| 1C4   1C3 | 2C4   2C3 | 3C4   3C3 | 4C4    4C3  | 5C4    5C3  | 6C4     6C3 |  7C4     7C3  |   8C4       8C3   |\n";
  else
    s =        "| C04   C03 | C08   C07 | C13   C12 | C18    C17  | C22    C23  | C30     C29 |  C36     C35  |   C42       C41   |\n";

  std::cout << s;
  std::cout << "|     |     |     |     |     |     |      |      |      |      |      |      |       |       |         |         |\n";
  s =          "|           |           |           |             |             |             |               |                   |\n";

  for (i = 7; i < 23; i++) {sprintf(cd,"%d",d[chan[i]-1]); sd = cd; s.replace(pos[i],sd.size(),sd);}

  std::cout << s;
  std::cout << "|         +-        +---        +---        +-----      +-------      +-------     +----------    +---------------|\n";

  if (LikeTrigger)
    s =        "|         |         |           |           |           |             |            |              |  9C6     9C5  |\n";
  else
    s =        "|         |         |           |           |           |             |            |              |  C46     C45  |\n";

  std::cout << s;
  std::cout << "|    |    |    |    |     |     |     |     |     |     |      |      |     |      |      |       |       |       |\n";
  s =          "|         |         |           |           |           |             |            |              |               |\n";

  for (i = 23; i < 25; i++) {sprintf(cd,"%d",d[chan[i]-1]); sd = cd; s.replace(pos[i],sd.size(),sd);}

  std::cout << s;
  std::cout << "|-----------------------------------------------------------------------------------------------------------------|\n";
  if (LikeTrigger)
    s =        "|1C2 1C1| 2C2 2C1 | 3C2 3C1 | 4C2 4C1 | 5C2 5C1 | 6C2   6C1 | 7C2   7C1 | 8C2     8C1 | 9C2     9C1 | 9C4     9C3 |\n";
  else
    s =        "|C02 C05| C06 C09 | C10 C11 | C16 C19 | C20 C21 | C24   C25 | C28   C31 | C34     C37 | C38     C39 | C48     C47 |\n";

  std::cout << s;
  std::cout << "|   |   |    |    |    |    |    |    |    |    |     |     |     |     |      |      |      |      |      |      |\n";
  s =          "|       |         |         |         |         |           |           |             |             |             |\n";

  for (i = 25; i < 45; i++) {sprintf(cd,"%d",d[chan[i]-1]); sd = cd; s.replace(pos[i],sd.size(),sd);}

  std::cout  << s;
  std::cout << "+-----------------------------------------------------------------------------------------------------------------+\n";
  std::cout << "\n";

}
