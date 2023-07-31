// TileBuilder.cxx

#include <iostream>
using namespace std;

#include "TileCIS/TileBuilder.h"
#include "TileCIS/TileDetector.h"

#define N_TowersInDrawerLB 9
#define N_TowersInDrawerEB 7

#define N_PMTsInDrawerLB   48
#define N_PMTsInDrawerEB   48

#define N_DrawersInSection 64
#define N_Sections 4


DetectorObject *TileBuilder::BuildPMT(int section, int Drawer, int tower, int ID){
  #ifdef VERBOSE
    cout << "Building PMT " << ID << endl;
  #endif

  return new TilePMT(section, Drawer, tower, ID);
}


DetectorObject *TileBuilder::BuildTower(int section, int Drawer, int ID){
  #ifdef VERBOSE
    cout << "Building Tower " << ID << endl;
  #endif

  TileTower *t = new TileTower(section, Drawer, ID);

  int LBMap[][6] = {{ 5, 2, 3, 4, 1,-1},
                    { 9, 6, 7, 8,14,-1},
                    {11,10,13,12,15,-1},
                    {19,16,17,18,26,-1},
                    {21,20,23,22,27,-1},
                    {25,24,29,30,40,-1},
                    {31,28,35,36,43,-1},
                    {37,34,41,42,-1,-1},
                    {39,38,45,46,47,48}};

  int EBMap[][6] = {{ 5, 6, 3, 4,17,-1},
                    { 9,10,18,-1,-1,-1},
                    { 7, 8,15,16,37,-1},
                    {11,12,23,24,38,-1},
                    {21,22,33,34,-1,-1},
                    {29,30,43,44,41,42},
                    {13,14, 1, 2,-1,-1}};

  int i=0;

  if (section == 3 || section == 4) {
    while(EBMap[ID-1][i] != -1 && i < 6){
      t->AddObject(BuildPMT(section,Drawer,ID,EBMap[ID-1][i]));
      i++;
    }
  } else if (section == 1 || section == 2) {
    while(LBMap[ID-1][i]!=-1 && i<6){
      t->AddObject(BuildPMT(section,Drawer,ID,LBMap[ID-1][i]));
      i++;
    }
  }

  return t;
}


DetectorObject *TileBuilder::BuildDrawer(int section, int ID){
  #ifdef VERBOSE
    cout << "Building Drawer " << ID << endl;
  #endif

  TileDrawer *d = new TileDrawer(section,ID);

  int NTowers = N_TowersInDrawerLB;
  int NPMTs   = N_PMTsInDrawerLB; // modified N_TowersInDrawerLB

  if (section == 3 || section == 4){
    NTowers = N_TowersInDrawerEB;
    NPMTs   = N_PMTsInDrawerEB;
  }

  int i;

  for (i = 1; i <= NTowers; i++)
    d->AddObject(BuildTower(section,ID,i));

  for (i = 1; i <= NPMTs; i++)
    d->AddObject(BuildPMT(section,ID,-999,i));

  return d;
}


DetectorObject *TileBuilder::BuildSection(int ID){

  TileSection *s = new TileSection(ID);

  #ifdef VERBOSE
    cout << "Building Section " << ID << endl;
  #endif

  for (int i = 1; i <= N_DrawersInSection; i++)
    s->AddObject(BuildDrawer(ID,i));

  return s;
}


DetectorObject *TileBuilder::Build(){
  #ifdef VERBOSE
    cout << "Building Tile " << endl;
  #endif

  TileCal *TheTile = new TileCal();
  for (int i = 1; i <= N_Sections; i++)
    TheTile->AddObject(BuildSection(i));

  return TheTile;
}

// End of file
