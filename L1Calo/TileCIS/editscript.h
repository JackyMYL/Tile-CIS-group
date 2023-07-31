/**
* Expert panel to TileCIS 
*
* Author: Rodrigo Araujo Pereira
* Email: rodrigo.araujo.pereira@cern.ch
* Date: 20/09/2009
* Last Update: 21/09/2009
*
**/

#ifndef EDITSCRIPT_H
#define EDITSCRIPT_H

#include <QDialog>
#include <qmessagebox.h>

#include "ui_TileCISPanel.h"

using namespace std;

class EditScript : public QDialog, public Ui::TileCISPanel
{
  Q_OBJECT
  
  public:
	EditScript(QWidget *parent = 0);

  private slots:
  
  void saveScript();
  void browse();
  void help();	
  bool ReadSaveGroupOnePMT(ofstream &script);
  bool ReadSaveGroupTriggerTower(ofstream &script);
  bool ReadSaveGroupOneDrawerDacCap(ofstream &script);
  bool ReadSaveGroupDrawerPhase(ofstream &script);
  bool ReadSaveGroupOneDrawer(ofstream &script);
  bool ReadSaveGroupAll(ofstream &script);
  bool ReadSaveGroupL1RoI(ofstream &script);
  bool ReadSaveGroupSimpleJet(ofstream &script);
  bool ReadSaveGroupPMTScan(ofstream &script);
  bool ReadSaveGroupEnergyScan(ofstream &script);
  bool ReadSaveGroupPipeline(ofstream &script);
  void ReadInfos(bool *group, ofstream &script);
  void HeadScript(ofstream &script, char *file);
  void EndScript(ofstream &script, bool *group);
  void MsgBox(QString message, int icon);
  bool CheckLineEdit(QString &message);
  void MaskInputLine();
};

#endif
