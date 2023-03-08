import ROOT, json, os, argparse
from src.oscalls import getPlotDirectory, createDir
import sys

if sys.version_info[:1][0]==3:
    mypath="/afs/cern.ch/user/t/tilebeam/offline/lib/python%d.%d/site-packages" % sys.version_info[:2]
    sys.path.append(mypath)
    import pymysql
    python3 = True
else:
    import _mysql
    python3 = False

class NoiseOutput:
    """ Open log file and output ROOT file. 
        If the file name is empty or None, 
        do not open the file and do not write anything. """
    def __init__(self, summary_file_name, root_file_name, plot_directory):
        self.m_summary_file = None
        if summary_file_name:
            self.m_summary_file = open(summary_file_name, 'w')
        self.m_root_file = None
        if root_file_name:
            self.m_root_file = ROOT.TFile.Open(root_file_name, 'RECREATE')
        self.m_plot_directory = plot_directory

    """ Write a message to stdout and to the log file. """
    def print_log(self, msg):
        print(msg)
        if self.m_summary_file:
            self.m_summary_file.write(msg)
            self.m_summary_file.write('\n')
    
    """ Write a ROOT object to the ROOT file. """
    def add_root_object(self, obj):
        if self.m_root_file:
            self.m_root_file.cd()
            obj.Write()
    
    """ Add a named json string to the ROOT file. """
    def add_json(self, name, value):
        if self.m_root_file:
            self.m_root_file.cd()
            obj = ROOT.TNamed(name, json.dumps(value))
            obj.Write()

    """ Close output files. """
    def close(self):
        if self.m_summary_file:
            self.m_summary_file.close()
            self.m_summary_file = None
        if self.m_root_file:
            self.m_root_file.Close()
            self.m_root_file = None

    """ Save a plot to the plot directory as png. The extension '.png' will be appended to the name. """
    def plot(self, canvas, name):
        if self.m_plot_directory:
            plotFileName = os.path.join(self.m_plot_directory, name+".png")
            print("Saving file %s" % (plotFileName))
            canvas.Print(plotFileName)
    

def common_noise_arguments(title):
    argparser = argparse.ArgumentParser(description=title)

    # Mics. arguments
    argparser.add_argument('--verbose', required=False, action='store_true',
                           help='Verbose output', dest='verbose')

    mbts_grp = argparser.add_mutually_exclusive_group(required=False)
    mbts_grp.add_argument('--with_MBTS', action='store_true', help='With MBTS', dest='withMBTS')
    mbts_grp.add_argument('--without_MBTS', action='store_false', help='Without MBTS', dest='withMBTS')
    argparser.set_defaults(withMBTS=True)

    spec_mods_grp = argparser.add_mutually_exclusive_group(required=False)
    spec_mods_grp.add_argument('--with_special_mods', action='store_true', help='With Special Mods', dest='withSpecialMods')
    spec_mods_grp.add_argument('--without_special_mods', action='store_false', help='Without Special Mods', dest='withSpecialMods')
    argparser.set_defaults(withSpecialMods=True)

    run1_grp = argparser.add_mutually_exclusive_group(required=False)
    run1_grp.add_argument('--run1', action='store_false', help='Use run1', dest='RUN2')
    run1_grp.add_argument('--run2', action='store_true', help='Use run2', dest='RUN2')
    argparser.set_defaults(RUN2=True)
    
    # Processing arguments
    patch_bad_grp = argparser.add_mutually_exclusive_group(required=False)
    patch_bad_grp.add_argument('--patch_bad_values', action='store_true',
                               help='Apply patch to bad values from data', dest='patchBadValues')
    patch_bad_grp.add_argument('--do_not_patch_bad_values', action='store_false',
                               help='Do not apply patch to bad values from data', dest='patchBadValues')
    argparser.set_defaults(patchBadValues=False)
    
    argparser.add_argument('--bad_value_attribute', required=False, default='hfn',
                           type=str, help='Noise attribute used to determine if a channel needs patching', dest='badChannelAttribute')

    comparison_grp = argparser.add_mutually_exclusive_group(required=False)
    comparison_grp.add_argument('--noise_compare_relative', action='store_true',
                                help='Use relative comparison for noise', dest='noiseComparisonModeRelative')
    comparison_grp.add_argument('--noise_compare_absolute', action='store_false',
                       help='Use absolute comparison for noise', dest='noiseComparisonModeRelative')
    argparser.set_defaults(noiseComparisonModeRelative=True)

    # Bad channel arguments    
    argparser.add_argument('--bad_channel_schema', required=False, default='OFL',
                           type=str, help='Bad channel DB schema', dest='badChannelSchema')
    argparser.add_argument('--bad_channel_tag', required=False, default='UPD1',
                           type=str, help='Bad channel DB tag', dest='badChannelTag')

    # Output arguments
    argparser.add_argument('--output_directory', required=False, default='',
                           type=str, help='Output directory, if not specified use TUCSRESULTS', dest='outputDirectory')    
    argparser.add_argument('--plot_directory', required=False, default='',
                           type=str, help='Plot directory, if not specified use TUCS default', dest='plotDirectory')
    argparser.add_argument('--output_root', required=False, default='',
                           type=str, help='ROOT output file name in the output directory.', dest='outputRoot')

    # DB arguments
    use_sqlite_grp = argparser.add_mutually_exclusive_group(required=False)
    use_sqlite_grp.add_argument('--db_use_sqlite', action='store_true',
                                help='Use Sqlite database for comparison', dest='dbUseSqlite')
    use_sqlite_grp.add_argument('--db_use_oracle', action='store_false',
                                help='Use Oracle database for comparison', dest='dbUseSqlite')
    argparser.set_defaults(dbUseSqlite=True)
    
    argparser.add_argument('--db_conn', required=False, default='CONDBR2',
                           type=str, help='Database', dest='dbConn')
    
    argparser.add_argument('--db_folder_tag', required=False, default='RUN2-HLT-UPD1-01',
                           type=str, help='DB tag', dest='dbFolderTag')
    
    argparser.add_argument('--db_sqlite_file', required=False, default='',
                           type=str, help='Sqlite file for comparison', dest='dbSqliteFile')

    return argparser
    
def check_common_arguments(args, output):
    if args.dbUseSqlite and (('dbSqliteFile' not in args) or (args.dbSqliteFile == '')):
        output.print_log("Error: --db_sqlite_file required")
        exit(1)

def determine_output_directory(args):
    outputDirectory = os.getenv('TUCSRESULTS','.')
    if args.outputDirectory:
        outputDirectory = args.outputDirectory
    return outputDirectory

def determine_plot_directory(args):
    return args.plotDirectory or getPlotDirectory('noise')

def get_runs_in_period(start_date, end_date, min_events=0):
    if python3:
        db = pymsql.connect('pcata007.cern.ch', user='reader')
        db_cursor = db.cursor()
        db_cursor.execute("""select run from tile.comminfo where date>"%s" and date<"%s" and events > %d and type='Ped'""" % (start_date, end_date, min_events))
        res = db_cursor.fetchall()
        runs = [int(run[0]) for run in res.fetch_row(maxrows=0)]
        db_cursor.close()
        db.close()
        runs.sort()
    else:
        db = _mysql.connect('pcata007.cern.ch', user='reader')
        db.query("""select run from tile.comminfo where date>"%s" and date<"%s" and events > %d and type='Ped'""" % (start_date, end_date, min_events))
        res = db.store_result()    
        runs = [int(run[0]) for run in res.fetch_row(maxrows=0)]
        db.close()
        runs.sort()
    return runs

def get_runs_between(first_run, last_run, min_events=0, max_events=10000000):
    if python3:
        db = pymsql.connect('pcata007.cern.ch', user='reader')
        db_cursor = db.cursor()
        db_cursor.execute("""select run from tile.comminfo where run>=%d and run<=%d and events > %d and events < %d and type='Ped'""" % (first_run, last_run, min_events, max_events))
        res = db_cursor.fetchall()
        runs = [int(run[0]) for run in res.fetch_row(maxrows=0)]
        db_cursor.close()
        db.close()
        runs.sort()
    else:
        db = _mysql.connect('pcata007.cern.ch', user='reader')
        db.query("""select run from tile.comminfo where run>=%d and run<=%d and events > %d and events < %d and type='Ped'""" % (first_run, last_run, min_events, max_events))
        res = db.store_result()    
        runs = [int(run[0]) for run in res.fetch_row(maxrows=0)]
        db.close()
        runs.sort()
    return runs




