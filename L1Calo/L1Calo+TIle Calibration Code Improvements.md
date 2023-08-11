### L1Calo+TIle Calibration Cod Improvements

# General Description of the Project

Currently, the Tile Charge Injection System is used in PMT Scan calibrations with L1Calo. We inject a fixed amount of charge (200pC) using the 3-in-1 cards to simulate a signal from a PMT. L1Calo reads out the signal through tigger cables. From Tile calibration, we should know the corresponding energy we inject for each charge pulse. L1Calo reads out the energy they see, and then we can compare the signals from the Tile side. The key difference between the two calibration schemes is that for each cell (i.e. each PMT) Tile gives a calibration constant, whereas (beacuase the data seen in L1Calo is less granular) L1Calo calibrates to the *sum* of energies seen in roughly 5 PMTs. Therefore, there may be some difference between the two calibration methods. 

In light of the above, L1Calo would like to improve their calibration inputs with respect to Tile. The hypothesis is that if we can mimic shower shape of jets more accurately during calibration, this may mitigate the spread of these calibration constants. Due to expectation that more energy would be deposited in A or B/C layers than D layers of the detector because the former are closer to the collision point, we would like to modify the amount of charge simulated in the PMT scans. This amount of charge should depend on the scintilator degradation (Cs-137 alibration constant) and PMT drift (laser calibration constant), accordingly. One should also account for malfunctioning 3-in-1 cards by disabling them, for they would not give accurate information for the L1Calo calibration constant.

Thus, the two goals of the calibration code edits are to add the following functionalities
* Disable/enable 3-in-1 cards based on such a list for Tile
* Specify a constant multiple to each amount of charge injected

More information:
* PMT Scans/Tile Trigger: https://twiki.cern.ch/twiki/bin/viewauth/Atlas/TileTriggerBadChannels
* L1Calo Constant Derivation: https://indico.cern.ch/event/1259323/contributions/5290008/attachments/2604358/4497755/TILEcalibration.pdf

# L1Calo+Tile Calibration Scripts

The baseline code for is a C++ library called atlas-tile-online. It contains many subfolders corresponding to different parts of Tile such as the Trigger, CIS, Laser, etc. These libraries define the baseline commands and parameters that higher level scripts will use to interact with Tile from the control room. There are thousands of lines. The important folder for us is TileCIS.

The main steering file is from takecalib suite at Point 1. This defines the types of calibration runs that are taken /det/l1calo/scripts/takeCalib/L1CaloRunTypes.py

The Tile part of the calibration is generated on the fly (i.e. a new script is written by this java code to call the calibration code each time a user runs it) by /det//l1calo/scripts/tileCisSetup.sh calling Java code JPanelCIS
https://gitlab.cern.ch/atlas-tile-online/TileIgui/-/blob/master/src/JPanelCIS.java

The important takeaway of this structure is that the down-to-eath code is the C++, while the aloof guiding scripts are Python or Java. 

For reference, the key differences between the types of joint runs are here:
* Energy  scan fires all PMTs changing injected charge every N events
* PMT scan fires only one PMT to check the input from individual PMTs
* phos4scan presumably varies the sampling phase in L1Calo

# Changes to TileCIS Implementation

To achieve the above, all edits have been made in the atlas-tile-online/TileCIS implementation. The important scripts are TileCIS/TileState.h and src/TileState.cxx. The code and header files are split up as a matter of style. No real code should be in the header file apart from declarations made in the class.

To gain access to this GitLab, please email Oleg (Oleg.Solovyanov@cern.ch).

The Old Implementation: TileCIS consists of all code specifying the settings sent to the 3-in-1 cards during the usual CIS calibration. The PMTState, DrawerState, and SectionState classes contain information about the state of the DAC, the amount of charge, and other parameters. Essentially, the fundamental class is the PMTState; the latter two recursively fill vectors containing many PMTs.

The New Implementation: In PMTState, we add two new parameters: (1) k, a constant for multiplying the amoutn of charge for each PMT by a fixed value and (2) _isoff, a Boolean switch to declare if a certain PMT is off or on. The definitions of **** in the TileState.cxx file use the logic of these class-level variables to decide whether to set a charge or not, and if so multiplied by what factor. To accommodate these changes, a few more class-level variables have to be retained from DrawerState and SectionState in the class definitions in the main file so that PMTState has enough information to know which PMT is being addressed. 

# How to Run the Code

First, compile the code:= by going to lxplus. Make sure the TDAQ version is what you require. As of 31-7-2023, the code below can be copied and pasted
```
source /afs/cern.ch/atlas/project/TicalOnline/tilercd/tile-10.0.0.0/installed/setup.sh tile-10.0.0.0

mkdir -p tilercd/tile-10-00-00
cd tilercd/tile-10-00-00
cat > CMakeLists.txt <<!
project(test)
cmake_minimum_required(VERSION 3.14.0)
find_package(TDAQ)
set(tile_DIR /afs/cern.ch/atlas/project/TicalOnline/tilercd/tile-10.0.0.0/installed/share/cmake/tile/x86_64-centos7-gcc11-opt)
tdaq_work_area(tile 10.0.0.0)
!
git clone https://:@gitlab.cern.ch:8443/atlas-tile-online/TileCIS.git

cmake_config
 cd x86_64-centos7-gcc11-opt/
make
```

Copy the patch of the code to the patches folder. The script will automatically override the legacy version at Building 175. Remove it after you are done to not interfere with other possible tests done on the setup. The directory is 

```
/afs/cern.ch/atlas/project/TicalOnline/patches/tile-10.0.0.0/installed/x86_64-centos7-gcc11-opt/lib/
```
Due to file permissions, it is best to navigate to this folder and ```scp source target`` with your lxplus as the source and this one as the target (replace source and target with the correct addresses).

To test the code from your terminal, ssh into the tilerod account. Then use the interactive Igui to start the run. Print ```cout``` commands from the C++ should be storedunder the ```/logs``` directory. 
```
ssh -XY tilerod@pctil-b175-01
tilerod@pctil-b175-01 > tile10
tilerod@pctil-b175-01 > runme
```
In case of any trouble operating the setup or if you have any questions, contact Henric Wilkens (Henric.Wilkens@cern.ch).

