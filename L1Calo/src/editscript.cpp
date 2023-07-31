/**
* Expert panel to TileCIS 
*
* Author: Rodrigo Araujo Pereira
* Email: rodrigo.araujo.pereira@cern.ch
* Date: 20/09/2009
* Last Update: 21/09/2009
*
**/

#include <iostream>
#include <fstream>
#include <string>
#include <stdlib.h> 
#include <vector>
#include <QtGui>
#include <QValidator>
#include <QIntValidator>
#include <QFileDialog>

#include "TileCIS/editscript.h"

using namespace std;

//ofstream script;
QString filescripturl;

EditScript::EditScript(QWidget *parent) : QDialog(parent)
{
  setupUi(this);

  //Mask the inputlineEdit
    MaskInputLine();
    
  //Set the ComboBox	
  directoryComboBox->addItem(QDir::currentPath());
  directoryComboBox->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred); 
  
  //SignalSlots
  connect(okButton, SIGNAL(clicked()), this, SLOT(saveScript()));
  connect(okButton2, SIGNAL(clicked()), this, SLOT(saveScript()));
  connect(cancelButton, SIGNAL(clicked()), this, SLOT(reject()));
  connect(cancelButton2, SIGNAL(clicked()), this, SLOT(reject()));
  connect(browseButton, SIGNAL(clicked()), this, SLOT(browse()));
  connect(helpButton, SIGNAL(clicked()), this, SLOT(help()));
}

void EditScript::saveScript()
{
    QString message;
    ofstream script;
    bool group[11] = {false, false, false, false, false, false, false, false, false, false, false};

    
    QByteArray ba = filescripturl.toLatin1();
    
    if(filescripturl=="") //If don't have a script selected
    {
    		message = "Please select a pattern script";
		MsgBox(message, 2);
    }
    else if( groupOnePMT->isChecked() || groupTriggerTower->isChecked() || groupOneDrawerDacCap->isChecked() || groupDrawerPhase->isChecked() || groupOneDrawer->isChecked() || groupAll->isChecked() || groupL1RoI->isChecked() || groupSimpleJet->isChecked() || groupPMTScan->isChecked() || groupEnergyScan->isChecked() || groupPipeline->isChecked() )
    {

    	if(CheckLineEdit(message))
	{	
    //Script head
	HeadScript(script, ba.data());
	
    //Read the GroupBox Infos
	ReadInfos(group, script);	 
		   
		message = "Script Save";
		MsgBox(message, 1);
		
		EndScript(script, group);
		script.close();
	}
	else{
		MsgBox(message, 2);
	}

    }
    else{
    	message = "The PatternScript hasn't been modified";
	MsgBox(message, 1);
    }
}

bool EditScript::ReadSaveGroupOnePMT(ofstream &script)
{
      int drawer, pmt;
	  double charge;	
      bool result=true;
      
      charge	= lineChargeOnePMT->text().toDouble();    
      drawer	= lineDrawerOnePMT->text().toInt();
      pmt		= linePMTOnePMT->text().toInt();
      
	  script<<"\n";
      script<<"	a = CisOnePMT();\n";
      script<<"	a.charge.value = "<<charge<<";\n";
      script<<"	a.pmt.value = "<<pmt<<";\n";
      script<<"	a.drawer.value = "<<drawer<<";\n";

      return result;
}

bool EditScript::ReadSaveGroupTriggerTower(ofstream &script)
{
	bool result=true;
	int drawer, tower;
	double charge;
	
	drawer = lineDrawerTriggerTower->text().toInt();
	charge = lineChargeTriggerTower->text().toDouble();
	tower  = lineTowerTriggerTower->text().toInt();
	
	script<<"\n";
	script<<"	b = CisTriggerTower();\n";
	script<<"	b.drawer.value = "<<drawer<<";\n";
	script<<"	b.charge.value = "<<charge<<";\n";
	script<<"	b.tower.value = "<<tower<<";\n";
	script<<"	b.pmtindex.value = 0;\n";
	
	return result;
}
  
bool EditScript::ReadSaveGroupOneDrawerDacCap(ofstream &script)
{
	bool result = true;
	int drawer, dac;

	drawer = lineDrawerOneDrawerDacCap->text().toInt();
	dac = lineDACOneDrawerDacCap->text().toInt();
	
	script<<"\n";
	script<<"	c = CisOneDrawerDacCap();\n";
	script<<"	c.drawer.value = "<<drawer<<";\n";
	script<<"	c.dac.value = "<<dac<<";\n";
	
	if(radioButton_smallCapOneDrawerDacCap->isChecked()){
		script<<"	c.smallCap.value = True;\n";
	}
	else{
		script<<"	c.smallCap.value = False;\n";
	}
	if(radioButton_largeCapOneDrawerDacCap->isChecked()){
		script<<"	c.largeCap.value = True;\n";
	}
	else{
		script<<"	c.largeCap.value = False;\n";
	}

      return result;	
}

bool EditScript::ReadSaveGroupDrawerPhase(ofstream &script)
{
	bool result=true;
	int drawer, phase, phaseStep;

	drawer = lineDrawerDrawerPhase->text().toInt();
	phase = linePhaseDrawerPhase->text().toInt();
	phaseStep = linePhaseStepDrawerPhase->text().toInt();
	
	script<<"\n";
	script<<"	d = CisDrawerPhase();\n";
	script<<"	d.drawer.value = "<<drawer<<";\n";
	script<<"	d.phase.value = "<<phase<<";\n";
	script<<"	d.phaseStep.value = "<<phaseStep<<";\n";
	
	return result;
}  

bool EditScript::ReadSaveGroupOneDrawer(ofstream &script)
{
	bool result=true;
	int drawer; 
	double charge;
	
	drawer = lineDrawerOneDrawer->text().toInt();
	charge = lineChargeOneDrawer->text().toDouble();
	
	script<<"\n";
	script<<"	e = CisOneDrawer();\n";
	script<<"	e.drawer.value = "<<drawer<<";\n";
	script<<"	e.charge.value = "<<charge<<";\n";
	
	return result;
}  

bool EditScript::ReadSaveGroupAll(ofstream &script)
{
	bool result=true;
	int dac;
	
	dac = lineDACAll->text().toInt();
	
	script<<"\n";
	script<<"	f = CisAll();\n";
	script<<"	f.dac.value = "<<dac<<";\n";
	
	if(radioButton_smallCapAll->isChecked()){
		script<<"	f.smallCap.value = True;\n";
	}
	else{
		script<<"	f.smallCap.value = False;\n";
	}
	if(radioButton_largeCapAll->isChecked()){
		script<<"	f.largeCap.value = True;\n";
	}
	else{
		script<<"	f.largeCap.value = False;\n";
	}
	
	return result;
}  

bool EditScript::ReadSaveGroupL1RoI(ofstream &script)
{
	bool result=true;
	double chargeIso, chargeCore;
	double phi, eta;
	
	chargeIso  = lineChargeIsoL1RoI->text().toDouble();
	chargeCore = lineChargeCoreL1RoI->text().toDouble();
	phi	   = linePhiL1RoI->text().toDouble();
	eta	   = lineEtaL1RoI->text().toDouble();

	script<<"\n";
	script<<"	g = CisL1Roi();\n";
	script<<"	g.eta.value = "<<eta<<";\n";
	script<<"	g.phi.value = "<<phi<<";\n";
	script<<"	g.chargeiso.value = "<<chargeIso<<";\n";
	script<<"	g.chargecore.value = "<<chargeCore<<";\n";
	
	return result;
}

bool EditScript::ReadSaveGroupSimpleJet(ofstream &script)
{
	bool result=true;
	int nRings;
	double eta, phi, power, maxcharge;
	
	maxcharge	= linemaxChargeSimpleJet->text().toDouble();
	nRings		= linenRingsSimpleJet->text().toInt();
	phi			= linePhiSimpleJet->text().toDouble();
	eta			= lineEtaSimpleJet->text().toDouble();
	power		= linePowerSimpleJet->text().toDouble();
		
	script<<"\n";
	script<<"	h = CisSimpleJet();\n";
	script<<"	h.maxCharge.value = "<<maxcharge<<";\n";
	script<<"	h.eta.value = "<<eta<<";\n";
	script<<"	h.phi.value = "<<phi<<";\n";
	script<<"	h.nRings.value = "<<nRings<<";\n";
	script<<"	h.power.value = "<<power<<";\n";
		
	return result;
}
  
bool EditScript::ReadSaveGroupPMTScan(ofstream &script)
{
	bool result=true;
	int charge, step;
	
	charge     = lineChargePMTScan->text().toInt();
	step	   = lineStepPMTScan->text().toInt();

	script<<"\n";
	script<<"	l = CisTriggerTower();\n";
	script<<"	l.drawer.value = 0;\n";
	script<<"	l.charge.value = "<<charge<<";\n";
	script<<"	l.tower.value = -1;\n";
	script<<"	l.pmtindex.value = (((i/"<<step<<")%6)+1);\n";
		
	return result;
}
  
bool EditScript::ReadSaveGroupEnergyScan(ofstream &script)
{
	bool result=true;
	int energyStep, eventStep, events;
	string line, straux;
  	string::iterator it;      
  	vector<int> charge, step;
	vector<string> small, large;	

//Read, Separate and save the EnergyLine	
	line = lineEnergyStepEnergyScan->text().toStdString();

	for(it = line.begin(); it < line.end(); it++){

        	if( (*it!=',') && (*it!=' ') ){	    
		    straux = straux + *it;	   
		}
		if( *it==',' ){
			charge.push_back(atoi(straux.c_str()));
			straux.clear();//="";
		}
	} 
	charge.push_back(atoi(straux.c_str()));
	line.clear();
	straux.clear();

//Read, Separate and save the StepLine
	line = lineEventStepEnergyScan->text().toStdString();

	for(it = line.begin(); it < line.end(); it++){

        	if( (*it!=',') && (*it!=' ') ){	    
		    straux = straux + *it;	   
		}
		if( *it==',' ){
			step.push_back(atoi(straux.c_str()));
			straux.clear();//="";
		}
	} 
	step.push_back(atoi(straux.c_str()));
	line.clear();
	straux.clear();

//Read, Separate and save the smallCap booleans
	line = linesmallCapEnergyScan->text().toStdString();

	for(it = line.begin(); it < line.end(); it++){

        	if( (*it!=',') && (*it!=' ') ){	    
		    straux = straux + *it;	   
		}
		if( *it==',' ){
			small.push_back(straux);
			straux.clear();//="";
		}
	} 
	small.push_back(straux);
	line.clear();
	straux.clear();

//Read, Separate and save the largeCap booleans
	line = linelargeCapEnergyScan->text().toStdString();

	for(it = line.begin(); it < line.end(); it++){

        	if( (*it!=',') && (*it!=' ') ){	    
		    straux = straux + *it;	   
		}
		if( *it==',' ){
			large.push_back(straux);
			straux.clear();//="";
		}
	} 
	large.push_back(straux);
	line.clear();
	straux.clear();

	if( (charge.size() != step.size()) || (small.size() != charge.size()) || (large.size()!=charge.size()) || (small.size() != step.size()) || (large.size()!= step.size()) )
		return false;

   if(charge.size() == 1){

	energyStep = charge[0];
	eventStep  = step[0];
	events     = eventStep;
	script<<"\n";
	script<<"	j = CisAll();\n";
	
	script<<"	j.smallCap.value = "<< small[0] <<";\n";
	script<<"	j.largeCap.value = "<< large[0] <<";\n";
	
	
	script<<"\n";
	script<<"	if i<"<<eventStep<<":\n";
	script<<"		j.dac.value = "<<energyStep<<";\n";
	
	for (int aux= energyStep*2; aux <= 1023 ; aux = aux+energyStep )
	{
		script<<"	elif i>="<<events;
		events = events+eventStep;
		script<<" and i<"<<events<<":\n";
		script<<"		j.dac.value = "<<aux<<";\n";
	}

	script<<"	else:\n";
	script<<"		j.dac.value = 1023;\n";
   }
   else{
	script<<"\n";
	script<<"	j = CisAll();\n";		
	script<<"\n";

	for (int i = 0; i < charge.size(); i++)
	{
	   if(i==0){
		script<<"	if i < "<< step[0] <<":\n";
		script<<"		j.dac.value = "<< charge[0] <<";\n";		
	   }
	   else if( i != charge.size()-1 )
	   {		
		script<<"	elif i >= "<< step[i-1];
		script<<" and i < "<< (step[i]+step[i-1]) <<":\n";
		script<<"		j.dac.value = "<< charge[i] <<";\n";
           }
	   else{
		script<<"	else:\n";
		script<<"		j.dac.value = "<< charge[i] <<";\n";
	   }	

		script<<"		j.smallCap.value = "<< small[i] << ";\n";
		script<<"		j.largeCap.value = "<< large[i] << ";\n";
	}
   }
		
	return result;
}


bool EditScript::ReadSaveGroupPipeline(ofstream &script)
{
	bool result=true;
	int pipe;
	
	pipe = linePipePipeline->text().toInt();
	
	script<<"\n";
	script<<"	p = CisPipe();\n";
	script<<"	print \"The current Pipeline is %s.\" % p.pipe.value;\n";
	script<<"	p.pipe.value = "<<pipe<<";\n";
	script<<"	print \"The new value of Pipeline is %s.\" % p.pipe.value;\n";
	
	return result;
}

void EditScript::ReadInfos(bool *group, ofstream &script)
{
//Read the GroupBox Infos
	if(groupOnePMT->isChecked())
		group[0] = ReadSaveGroupOnePMT(script);

	if(groupTriggerTower->isChecked())
		group[1] = ReadSaveGroupTriggerTower(script);

	if(groupOneDrawerDacCap->isChecked())
		group[2] = ReadSaveGroupOneDrawerDacCap(script);
	
	if(groupDrawerPhase->isChecked())
		group[3] = ReadSaveGroupDrawerPhase(script);

	if(groupOneDrawer->isChecked())
		group[4] = ReadSaveGroupOneDrawer(script);
	
	if(groupAll->isChecked())
		group[5] = ReadSaveGroupAll(script);
		      
	if(groupL1RoI->isChecked())
		group[6] = ReadSaveGroupL1RoI(script);
		      
	if(groupSimpleJet->isChecked())
		group[7] = ReadSaveGroupSimpleJet(script);
	      
	if(groupPMTScan->isChecked())
		group[8] = ReadSaveGroupPMTScan(script);
		      
	if(groupEnergyScan->isChecked())
		group[9] = ReadSaveGroupEnergyScan(script);

	if(groupPipeline->isChecked())
		group[10] = ReadSaveGroupPipeline(script);
}

void EditScript::HeadScript(ofstream &script, char *file)
{
    //ofstream script;
	script.open(file);

	if(!(lineInjectionPeriod->text()==""))
	{
		script<<"\n";
		script<<"from PythonCisParamFormat import *;\n";
		script<<"\n";
		script<<"my_injectionPeriod = "<<lineInjectionPeriod->text().toInt()<<";\n";
		script<<"\n";
		script<<"def run(i):\n";
	}
	else if(groupPMTScan->isChecked())
	{
		//Script PMTScan header
		script<<"\n";
		script<<"from PythonCisParamFormat import *;\n";
		script<<"\n";
		script<<"my_injectionPeriod = 10;\n";  // Injection Period default to PMTScan
		script<<"\n";
		script<<"def run(i):\n";
	}
	else
	{
    	//Script head
		script<<"\n";
		script<<"from PythonCisParamFormat import *;\n";
		script<<"\n";
		script<<"my_injectionPeriod = 1;\n";  // Injection Period default
		script<<"\n";
		script<<"def run(i):\n";
		//script<<"\n";
	}
}

void EditScript::EndScript(ofstream &script, bool *group)
{
	bool comma = false;
	
	script<<"\n";
	script<<"	return [";
	
	if(group[10]){			//CisPipe
		script<<"p";
		comma = true;	
	}
	
	if(group[0] && comma){		//CisOnePMT
		script<<", a";
	}
	else if (group[0]){script<<"a"; comma = true;}
			
	if(group[1] && comma){		//CisTriggerTower
		script<<", b";
	}
	else if (group[1]){script<<"b"; comma = true;}
		
	if(group[2] && comma ){		//CisOneDrawerDacCap
		script<<", c";	
	}
	else if (group[2]){script<<"c"; comma = true;}
		
	if(group[3] && comma){		//CisDrawerPhase
		script<<", d";	
	}
	else if (group[3]){script<<"d"; comma = true;}
	
	if(group[4] && comma){		//CisOneDrawer
		script<<", e";	
	}
	else if (group[4]){script<<"e"; comma = true;}
	
	if(group[5] && comma){		//CisAll
		script<<", f";
	}
	else if (group[5]){script<<"f"; comma = true;}
	
	if(group[6] && comma){		//CisL1RoI
		script<<", g";
	}
	else if (group[6]){script<<"g"; comma = true;}
	
	if(group[7] && comma){		//CisSimpleJet  
		script<<", h";
	}
	else if (group[7]){script<<"h"; comma = true;}
	
	if(group[8] && comma){		//CisPMTScan
		script<<", l";	
	}
	else if (group[8]){script<<"l"; comma = true;}
	
	if(group[9] && comma){		//CisEnergyScan
		script<<", j";
	}
	else if (group[9]){script<<"j"; comma = true;}
	
	script<<"];\n";
}

void EditScript::MsgBox(QString message, int icon)
{
	QMessageBox  msgBox;
	
	if(icon==2){
	//Seta o texto da mensagem a ser exibida
		msgBox.setText(message);
		msgBox.setIcon(QMessageBox::Warning);
		msgBox.setWindowTitle("Error");
	}
	else if(icon==1)
	{
	//Seta o texto da mensagem a ser exibida
		msgBox.setText(message);
		msgBox.setIcon(QMessageBox::Information);
		msgBox.setWindowTitle("Info");
	}
	//Mostra a mensagem
		msgBox.exec();
}
  
bool EditScript::CheckLineEdit(QString &message)
{
	bool result = true;
	
	if( groupOnePMT->isChecked() && ((!lineChargeOnePMT->hasAcceptableInput()) || (!lineDrawerOnePMT->hasAcceptableInput()) || (!linePMTOnePMT->hasAcceptableInput())) ){
		message = "Error in CISOnePMT Box \n"; 
		result=false;
	}
	if( groupTriggerTower->isChecked() && ((!lineDrawerTriggerTower->hasAcceptableInput()) || (!lineChargeTriggerTower->hasAcceptableInput()) || (!lineTowerTriggerTower->hasAcceptableInput())) ){
		message = "Error in CISTriggerTower Box \n"; 
		result=false;
	}	
	if( groupOneDrawerDacCap->isChecked() && ((!lineDrawerOneDrawerDacCap->hasAcceptableInput()) || (!lineDACOneDrawerDacCap->hasAcceptableInput())) ){
		message = "Error in CISOneDrawerDacCap Box \n"; 
		result=false;
	}	
	if( groupOneDrawerDacCap->isChecked() && ((!radioButton_smallCapOneDrawerDacCap->isChecked()) && (!radioButton_largeCapOneDrawerDacCap->isChecked())) ){
		message = "Error in CISOneDrawerDacCap\n Please Select one Cap  \n"; 
		result=false;
	}				
	if( groupDrawerPhase->isChecked() &&( /*(!lineDrawerDrawerPhase->hasAcceptableInput()) ||*/ (linePhaseDrawerPhase->text()=="") || (linePhaseStepDrawerPhase->text()=="")) ){
		message = "Error in CISDrawerPhase Box \n";
		result=false;
	}	
	if( groupOneDrawer->isChecked() && ((!lineDrawerOneDrawer->hasAcceptableInput()) || (!lineChargeOneDrawer->hasAcceptableInput())) ){
		message = "Error in CISOneDrawer Box \n";
		result=false;
	}	
	if( groupAll->isChecked() && (!lineDACAll->hasAcceptableInput()) ){
		message = "Error in CISAll Box \n";
		result=false;
	}	
	if( groupAll->isChecked() && ((!radioButton_smallCapAll->isChecked()) && (!radioButton_largeCapAll->isChecked())) ){
		message = "Error in CISAll\n Please Select one Cap  \n"; 
		result=false;
	}	
	if( groupL1RoI->isChecked() && ((!lineChargeIsoL1RoI->hasAcceptableInput()) || (!lineChargeCoreL1RoI->hasAcceptableInput()) || (!linePhiL1RoI->hasAcceptableInput()) || (!lineEtaL1RoI->hasAcceptableInput())) ){
		message = "Error in CISL1RoI Box \n";
		result = false;
	}
	if( groupSimpleJet->isChecked() && ((!linemaxChargeSimpleJet->hasAcceptableInput()) || (linenRingsSimpleJet->text()=="") || (!lineEtaSimpleJet->hasAcceptableInput()) || (!linePhiSimpleJet->hasAcceptableInput()) || (linePowerSimpleJet->text()=="")) ){
		message = "Error in CISSimpleJet Box \n";
		result=false;
	}
	if( groupPMTScan->isChecked() && ((!lineChargePMTScan->hasAcceptableInput()) || (lineStepPMTScan->text()=="")) ){
		message = "Error in CISPMTScan Box \n";
		result=false;
	}	
	if( groupEnergyScan->isChecked() && ( /*(!lineEnergyStepEnergyScan->hasAcceptableInput()) ||*/ (lineEventStepEnergyScan->text()=="")) ){
		message = "Error in CISEnergyScan Box \n";
		result=false;
	}	
	if( groupEnergyScan->isChecked() && linesmallCapEnergyScan->text()=="" && linelargeCapEnergyScan->text()=="" ){
		message = "Error in CISEnergyScan Capacitor \n"; 
		result=false;
	}
	if( groupPipeline->isChecked() && (linePipePipeline->text()=="")  ){
		message = "Error in CISPipe Box \n";
		result=false;
	}
	if( !(lineInjectionPeriod->text() == "") && (lineInjectionPeriod->text().toInt()==0) ){
		message = "Error in Injection Period \n";
		result=false;
	}
	return	result;
}

void EditScript::MaskInputLine()
{
	lineChargeOnePMT->setValidator(new QDoubleValidator(0, 800, 1, this));
	lineDrawerOnePMT->setValidator(new QIntValidator(1, 64, this));
	linePMTOnePMT->setValidator(new QIntValidator(1, 48, this));
	
	lineDrawerTriggerTower->setValidator(new QIntValidator(1, 64, this));
	lineChargeTriggerTower->setValidator(new QDoubleValidator(0, 800, 1, this));
	lineTowerTriggerTower->setValidator(new QIntValidator(1, 9, this));
	
	lineDrawerOneDrawerDacCap->setValidator(new QIntValidator(1, 64, this));
	lineDACOneDrawerDacCap->setValidator(new QIntValidator(0, 1023, this));
	
	lineDrawerDrawerPhase->setValidator(new QIntValidator(1, 64, this));
	//linePhaseDrawerPhase->setValidator(new QIntValidator(, , this));
	//linePhaseStepDrawerPhase->setValidator(new QIntValidator(, , this));
	
	lineDrawerOneDrawer->setValidator(new QIntValidator(1, 64, this));
	lineChargeOneDrawer->setValidator(new QDoubleValidator(0, 800, 1, this));
	
	lineDACAll->setValidator(new QIntValidator(0, 1023, this));
	
	linePhiL1RoI->setValidator(new QDoubleValidator(-6.28, 6.28, 2, this));
	lineEtaL1RoI->setValidator(new QDoubleValidator(0.0, 1.7, 1, this));
	lineChargeIsoL1RoI->setValidator(new QDoubleValidator(0, 800, 1, this));
	lineChargeCoreL1RoI->setValidator(new QDoubleValidator(0, 800, 1, this));
	
	linemaxChargeSimpleJet->setValidator(new QDoubleValidator(0, 800, 1, this));
	lineEtaSimpleJet->setValidator(new QDoubleValidator(0.0, 1.7, 1, this));
	linePhiSimpleJet->setValidator(new QDoubleValidator(-6.28, 6.28, 2, this));
	//linenRingsSimpleJet->setValidator(new QIntValidator(, , this));
	//linePowerSimpleJet->setValidator(new QDoubleValidator(, , this));
	
	lineChargePMTScan->setValidator(new QIntValidator(0, 800, this));
	//lineStepPMTScan->setValidator(new QIntValidator(0, 10000, this));
	
	QRegExp rx("[0-9]{1,4},[0-9]{1,4},[0-9]{1,4},[0-9]{1,4},[0-9]{1,4},[0-9]{1,4},[0-9]{1,4},[0-9]{1,4},[0-9]{1,4},[0-9]{1,4}");
	QRegExp rx1("(true|false),(true|false),(true|false),(true|false),(true|false),(true|false),(true|false),(true|false),(true|false),(true|false)");

	QValidator *validator1= new QRegExpValidator(rx1, this);
        QValidator *validator = new QRegExpValidator(rx, this);
	lineEnergyStepEnergyScan->setValidator(validator);
	lineEventStepEnergyScan->setValidator(validator);
	linesmallCapEnergyScan->setValidator(validator1);
	linelargeCapEnergyScan->setValidator(validator1);
	///lineEnergyStepEnergyScan->setValidator(new QIntValidator(0, 1023, this));
	//lineEventStepEnergyScan->setValidator(new QIntValidator(0, 1023, this));
	
	//linePipePipeline->setValidator(new QIntValidator( , ,this));

	//lineInjectionPeriod->setValidator(new QIntValidator( 1, 200,this));
}

void EditScript::browse()
{
     filescripturl = QFileDialog::getOpenFileName(this, tr("TileCISPanel"), QDir::currentPath(), tr("Python Script (*.py)")); 
     if (!filescripturl.isEmpty()) {
         directoryComboBox->addItem(filescripturl);
         directoryComboBox->setCurrentIndex(directoryComboBox->currentIndex() + 1);
     }
}

void EditScript::help()
{
     QDesktopServices::openUrl(QUrl(tr("https://twiki.cern.ch/twiki/bin/view/Atlas/TileCIS")));
}
