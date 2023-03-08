from src.GenericWorker import GenericWorker
import os
import ROOT
import datetime

class UseDQMF(GenericWorker):
    '''
    Add runs from DQMF
    '''

    def __init__(self, output, user_name, run_number, stream, server='atlasdqm.cern.ch', source='tier0', run_type='Ped', verbose=False):
        self.m_output = output
        self.m_user_name = user_name
        self.m_run_type = run_type
        self.m_run_number = run_number
        self.m_stream = stream
        self.m_server = server
        self.m_source = source
        self.m_verbose = verbose
        self.m_proxy = None
        self.m_run_cache = {}

    # ---- Implementation of Worker ----

    def ProcessStart(self):
        self.m_output.print_log("UseDQMF Opening connection, server: %s source: %s stream: %s user: %s" % (self.m_server, self.m_source, self.m_stream, self.m_user_name))
        conn_str = 'https://%s:%s@%s' % (self.m_user_name, os.getenv('DQMPWD'), self.m_server)
        try:
            self.m_proxy = xmlrpclib.ServerProxy(conn_str)
            # get run info
            run_spec = {'stream':self.m_stream, 'source':self.m_source, 'run_list':[self.m_run_number] }
            run_infos = self.m_proxy.get_run_information(run_spec)
            self.m_output.print_log("DQMF run info: %s" % str(run_infos))
            run_info = run_infos[str(self.m_run_number)]
            if self.m_verbose:
                self.m_output.print_log("DQMF Run %d of type %s read from stream %s, time: %s" % (self.m_run_number, self.m_run_type, self.m_stream, run_info[4]))
            self.m_run_cache[self.m_run_number] = Run(self.m_run_number, self.m_run_type, time=datetime.datetime.fromtimestamp(int(run_info[4])), data={'stream':self.m_stream, 'source':self.m_source})
        except Exception as ex:
            self.m_output.print_log("UseDQMF: Error: Unable to open connection : %s" % (str(ex)))

    def ProcessStop(self):
        self.m_proxy = None
        
    def ProcessRegion(self, region):
        for run_number in self.m_run_cache:
            run = self.m_run_cache[run_number]
            region.AddEvent(Event(run, {}))
            
