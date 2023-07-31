#ifndef TileStateH
#define TileStateH

#include <vector>
#include <iostream>
#include "TileConfiguration/TileRCDError.h" //ERS Messages




class PMTState
{

        private:

                int _dac;
                int _trigger;
                int _csmall;
                int _clarge;

        public:
                // Add arguments to PMT state (section, module, PMT); create logic on the setting of values (if bad ... set to 0 so nothing is inhected )
                PMTState(int section, int drawer, int PMT);

                // Make public variables read in from PMT state constructor
                int section;
                int drawer;
                int PMT;
                // More flexibility
                bool isoff; //Needs to be static for compilation
                float k; //Define what this is for each PMT based on physics (for now set to 1)
                


                //Peter
                //Initialize at -1 and then set with the following functions 

                // Generalize this condition to a list of bad modules to be disables 
                // Add cout statements to check that this works properly 
		//bool condition = true;





                int  get_dac(){return _dac;};
                void set_dac(int value);


                int  get_trigger(){return _trigger;};
                void set_trigger(int value);

                int  get_csmall(){return k*_csmall;};
                void set_csmall(int value);

                int  get_clarge(){return k*_clarge;};
                void set_clarge(int value);
};

class DrawerState
{

        private:

                int _section;
                int _drawer;
                int _broadcast;
                int _tube;

        public:

                DrawerState(int section, int drawer);

	        std::vector< PMTState > pmt;

                bool     AnyDACIsDifferentFrom(int value);
                bool AnyTriggerIsDifferentFrom(int value);
                bool  AnyCSmallIsDifferentFrom(int value);
                bool  AnyCLargeIsDifferentFrom(int value);

                int  get_broadcast(){return _broadcast;};
                int  get_tube(){return _tube;};

                void set_broadcast(int value){_broadcast = value;};
                void set_tube(int value){_tube = value;};
                void set_dac(int value);
                void set_trigger(int value);
                void set_csmall(int value);
                void set_clarge(int value);

		void ShowInConsole(bool LikeTrigger);

};

class SectionState
{

        private:

                int _section;

        public:

	        SectionState(int section);

                bool AnyDrawerBroadcastIsDifferentFrom(int value);
                bool            AnyTubeIsDifferentFrom(int value);
                bool             AnyDACIsDifferentFrom(int value);
                bool         AnyTriggerIsDifferentFrom(int value);
                bool          AnyCSmallIsDifferentFrom(int value);
                bool          AnyCLargeIsDifferentFrom(int value);

                void set_DrawerBroadcast(int value);
                void set_tube   (int value);
                void set_dac    (int value);
                void set_trigger(int value);
                void set_csmall (int value);
                void set_clarge (int value);

                int  get_section(){return _section;};

                std::vector<DrawerState> drawer;

		void ResetAll();
};

#endif
