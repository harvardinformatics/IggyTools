#!/usr/bin/env python
import os, sys, logging, re, traceback, time, socket
import os.path as path
from iggytools.iggypipeline.DBclass import iggypipeDB 
from iggytools.utils.util import mkdir_p, copy, email, getUserHome, procStatus
from iggytools.pref.iggytools_PrefClass import Iggytools_Preferences
from iggytools.iggypipeline.iggyPipeClass import getLogger
from iggytools.iggypipeline.sqlalchemy_models import ModuleRecord, PipelineRecord
from daemon import runner
from datetime import datetime


class IggyPipeDaemon(object):

    def __init__(self, prefDir = None, verbose = False):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = path.join( getUserHome(), '.iggypipe_daemon_pid' )
        self.pidfile_timeout = 5

        #load preferences
        prefObj = Iggytools_Preferences(prefDir = prefDir)
        self.iggyPref = prefObj.getPreferences()

        self.pref = self.iggyPref['iggypipe']['iggypipe']

        self.verbose = verbose

        #self.logFile = path.join(self.pref.LOG_DIR, 'iggypipe_daemon.log')
        #self.log = getLogger(self.pref, self.logFile, 'iggypipe_daemon')


    def run(self):

        self.db = iggypipeDB(self.pref)        

        print 'pidfile_path: %s' % self.pidfile_path 

        while True:

            if self.verbose:
                print datetime.strftime( datetime.now(), '%Y-%m-%d %H:%M:%S' )

            #record time of last iteration
            filepath = path.join( getUserHome(), '.iggypipe_daemon_lastiter' )
            f = open(filepath, 'w')
            f.write(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
            f.close()


            res = self.db.session.query(ModuleRecord).filter( (ModuleRecord.status == 'NEW')
                                                              | (ModuleRecord.status == 'PENDING')
                                                              | (ModuleRecord.status == 'RUNNING') )
            modRecords = res.all()

            for modRecord in modRecords:

                if modRecord.runType == 'local' and modRecord.hostname == socket.gethostname():

                    if modRecord.pid:
                        if path.isfile('/proc/%d/status' % modRecord.pid):
                            if procStatus(modRecord.pid) == 'Z':            
                                modRecord.status = 'ZOMBIE'
                            else:
                                modRecord.status = 'RUNNING'
                        else:
                            modRecord.status = 'ENDED'            

                    else:  # no pid is available
                        modRecord.status = 'NULL'

                elif modRecord.runType == 'slurm':
                    pass  #todo: query db for job status

                self.db.session.commit()

            time.sleep(15)


app = IggyPipeDaemon()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
