import os, sys, logging, re, traceback, getpass
import os.path as path
from iggytools.iggypipeline.DBclass import iggypipeDB 
from iggytools.utils.util import mkdir_p, copy, email
from iggytools.pref.iggytools_PrefClass import Iggytools_Preferences
from iggytools.iggypipeline.module.derived.fastqc import Fastqc
from iggytools.iggypipeline.module.derived.trimmomatic import Trimmomatic
from iggytools.iggypipeline.module.derived.bowtie2 import Bowtie2
from iggytools.iggypipeline.help.pipeHelp import pipeHelp
from iggytools.iggypipeline.help.modHelp import modHelp


class IggyPipe(object):


    def __init__(self, name = None, pipeDir = None, pipeParentDir = None, prefDir = None, notify = True, verbose = True):

        self.availModNames = ['Fastqc', 'Trimmomatic', 'Bowtie2']
        self.pipeID = None

        #load preferences
        prefObj = Iggytools_Preferences(prefDir = prefDir)
        self.prefDir = path.expanduser(prefObj.prefDir)
        self.iggyPref = prefObj.getPreferences()

        self.pref = self.iggyPref['iggypipe']['iggypipe']

        #set pipe name, pipeDir.
        if name:
            self.name = name
        else:
            self.name = 'iggyproj'

        if pipeDir:  # set output directory
            self.pipeDir = path.expanduser(pipeDir)
        elif pipeParentDir:
            self.pipeDir = path.join( path.expanduser(pipeParentDir), self.name )
        else:
            self.pipeDir = path.join(self.pref.RESULTS_DIR, self.name)

        mkdir_p(self.pipeDir)

        self.db = iggypipeDB(self.pref)
        
        self.logFile = path.join(self.pref.LOG_DIR, 'iggypipe.log') # logging setup
        self.log = getLogger(self.pref, self.logFile, 'iggypipe')

        self.verbose = verbose  #true is pipeline is created in the interpreter.
        self.notify = notify   # optional override of notify setting in preferences file.
        self.users = getpass.getuser()  #user to send iggypipe notifications

        self.modules = list()


    def help(self):

        print pipeHelp
        print "Available modules: %s" % ', '.join(self.availModNames)
        print modHelp


    def view(self):
        
        indent = 4

        print '\nPipe name:           %s' % self.name
        print 'Pipe output dir:     %s' % self.pipeDir
        print 'Preferences dir:     %s' % self.prefDir
        print 'Log file:             %s' % self.logFile
        print 'Notify:              %s\n' % self.notify
        
        for mod in self.modules:
            print '%sModule: %s' % (' '*indent, mod.name)
            mod.view(indent)
            mod.sview(indent)


    def add(self, modName, outName = None):

        if modName not in self.availModNames:
            raise Exception('Module %s not found. Available modules: %s' % (modName, ', '.join(self.availModNames)))

        m = globals()[modName](pipe = self, outName = outName)  

        self.modules.append(m)

        return m
        

    def run(self):
        
        self.db.write_new_pipe(self)

        for mod in self.modules:
            mod.run()

        self.db.write_pipe_record(self, status = 'COMPLETED')

        #if notify, send email that pipeline finished
        email(self.users, 'IggyPipe Notification', '\nPipeline %s completed.\n\n' % self.name \
                                                   + 'Pipeline ID: %s\n\n' % self.pipeID \
                                                   + 'Modules: %s\n\n' % '\n'.join(['%s:\n%s\n' % (x.name, x.modConfig.args2str()) for x in self.modules]))

    def srun(self):

        self.db.write_new_pipe(self)

        for mod in self.modules:
            mod.srun()


    def status(self):  #show status of cluster jobs

        for mod in self.modules():
            print '\nModule: %s' % (mod.name)
            mod.status()


    def __repr__(self):
        if self.pipeID:
            return '<IggyPipe(%s, pipeID: %s)>' % (self.name, self.pipeID)
        else:
            return '<IggyPipe(%s)>' % (self.name)



def getLogger(pref, logFile, logName):

    mkdir_p( path.dirname(logFile) )

    logging.basicConfig(filename = logFile,
                        format = '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s',
                        datefmt = '%m/%d/%Y %I:%M:%S %p',
                        level = pref.LOGGING_LEVEL)
    log = logging.getLogger(logName)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(pref.LOGGING_LEVEL)
    sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'))

    log.addHandler(sh)

    return log
