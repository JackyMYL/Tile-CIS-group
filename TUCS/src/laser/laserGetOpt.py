# @author:  Rute Pedro, Miguel Medeiros
# @date:    end 2018
# @purpose: New class to parse global and macro-specific arguments to laser macros

import argparse

# Laser Argument class
class laserArgs(object):


    def __init__(self, verbose=False):
        print("\n Initialising laser arguments class \n")
        self.verbose = verbose
        self.parser  = argparse.ArgumentParser(description='\n Laser argument parser \n', formatter_class=argparse.RawTextHelpFormatter)
        self.add_defaults()


    # Add default arguments common to all macros
    def add_defaults(self):

        self.parser.add_argument("-d","--date",    type=str, default=None, required=False, help="Initial date of the period to analyse")
        self.parser.add_argument("-e","--enddate", type=str, default='',   required=False, help="End date of the period to analyse")
#        self.parser.add_argument("-R","--Run",     dest='types', action='append_const', const=int,    required=False, help="Run number")
        self.parser.add_argument("-R","--Run",     dest='Run', action='append', required=False, help="Run number")
        self.parser.add_argument("-f","--filter",  type=str, default=' ',  required=False, help="Position of the laser filter wheel")
        self.parser.add_argument("-D","--Diode",   type=int, default=0,    required=False, help="Diode number")
        self.parser.add_argument("-r","--region",  type=str, default=None, required=False, help="TileCal Region, ex:LBA_m22_c09")
        self.parser.add_argument("-direct","--direct",  action='store_true',   required=False, help="Use Direct method")
        self.parser.add_argument("-p","--pisa",     action='store_true',   required=False, help="Use Pisa/Statistical method")
        self.parser.add_argument("-n","--png",      action='store_false',  required=False, help="By default plots in eps/pdf, unless `--png` flag specified\n")
        self.parser.add_argument("-t","--outputTag", type=str, default='', required=False, help="Adds this string to the plot folder and output file\n")


    # Get default arguments common to all macros and set them as globals
    def get_defaults(self):
        global date
        global enddate
        global twoinput
        global filt_pos
        global diode
        global region
        global doDirect
        global usePisa
        global plotEps
        global outputTag
        global runs

        date       = self.args.date
        enddate    = self.args.enddate
        run_list   = self.args.Run
        filt_pos   = self.args.filter
        diode      = self.args.Diode
        region     = self.args.region
        doDirect   = self.args.direct
        usePisa    = self.args.pisa
        plotEps    = self.args.png
        outputTag  = self.args.outputTag

        if enddate != '':
            twoinput = True
        else:
            twoinput = False

        if 'runs' not in globals():
            runs = []

        if isinstance(run_list,list):
            for run in run_list:
                runs.append(int(run))
            print(runs)
        # Some print out
        if self.verbose:

            print(" --- Setting default arguments --- ")
            print("TileCal region: {}".format("All" if region==None else region))
            print("Data period to define run set: initial date {} and end date {} --- Extra run: {}".format(date, enddate if enddate!='' else "today", run_list if len(runs)!=0 else "No"))
            print("Normalising PMTs signals to diode: {}".format(diode))
            print("Using laser runs taken with filter: {}{}{}".format(filt_pos," (high gain run)" if filt_pos==8 else "", " (low gain run)" if filt_pos==6 else ""))
            print("Analysis method: {} Pisa/Statistical {}".format("Direct" if doDirect else "Combined",usePisa))
            print("Output tag defined: {}".format(outputTag))


    # Method to add extra arguments specific to some macros
    def add_local_arg(self, arg, default='', action='store', nargs="", arghelp="", required=False):

        if nargs=="":
            self.parser.add_argument(arg, default=default, action=action, required=required, help=arghelp)
        else:
            self.parser.add_argument(arg, default=default, action=action, nargs=nargs, required=required, help=arghelp)


    # Get arguments from parser
    def args_from_parser(self):
        self.args = self.parser.parse_args()

        self.get_defaults()
        return self.args
