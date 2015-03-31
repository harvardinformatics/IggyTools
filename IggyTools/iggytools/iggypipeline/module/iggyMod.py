from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import os, logging, re, traceback, argparse, json
import os.path as path
from iggytools.utils.util import Command_toStdout, Command_toFile, sbatch, printJobStatus, mkdir_p
from iggytools.pref.iggytools_PrefClass import Iggytools_Preferences
from iggytools.iggypipeline.module.configClasses import BaseConfig, SlurmConfig, get_slurmArgDefs
from iggytools.iggypipeline.help.modHelp import modHelp

log = logging.getLogger('iggypipe')

class IggyMod:

    __metaclass__ = ABCMeta


    def __init__(self, modName, pipe):

        self.pipe = pipe

        self.name = modName
        self.modDir = path.join(self.pipe.pipeDir, modName)
        self.modID = None

        self.db = pipe.db
        self.verbose = pipe.verbose
        self.pref = pipe.iggyPref['iggypipe'][modName] #get module preferences

        self.slurmConfig = SlurmConfig(self, get_slurmArgDefs())

        self.command = None
        self.processID = None
        self.jobID = None

        self.outputs = None
        self.outputHelp = None


    def run(self):

        if not self.modID:
            self.db.write_new_module(self)

        self.modSetup()

        log.info('Running %s in pipeline %s:\n%s' % (self.name, self.pipe.name, self.command))

        cmd = Command_toFile(self.command, path.join(self.modDir, 'stdout_stderr.txt'), append=False, echo=True)
        self.processID = cmd.pid

        self.db.write_module_record(self, status = 'STARTED')

        cmd.run()

        self.db.write_module_record(self, status = 'COMPLETED')

        log.info('Module %s (id: %s) in pipeline %s (id: %s) completed.' % (self.name, self.modID, self.pipe.name, self.pipe.pipeID))
        

    def argSetup(self): # process/format module inputs, create output args, build module command
        pass


    def modSetup(self): # create output directories, or additional module initialization

        if not path.isdir(self.modDir):  
            mkdir_p(self.modDir)


    @abstractmethod
    def setSlurmDefaults_from_modConfig(self):   #update slurm settings based on module inputs
        pass


    def input(self, **namedArgs):  #set module inputs
        if self.verbose:
            print 'Updating module settings. Use module.view() to view.'

        self.modConfig.setValues(**namedArgs)  
        self.argSetup()

        if self.verbose:
            print 'Updating slurm settings from module settings. Use module.sview() to view.'

        self.setSlurmDefaults_from_modConfig()

        self.slurmConfig.setValues()


    def sinput(self, **namedArgs):  #set slurm params
        if self.verbose:
            print 'Updating slurm settings. Use module.sview() to view.'

        self.slurmConfig.setValues(**namedArgs)  


    def view(self, indent = 0):   #display current module settings

        indentStr = ' '* indent

        print ''
        print '%sModule name:         %s' % (indentStr, self.name)
        print '%sModule output dir:   %s\n' % (indentStr, self.modDir)

        self.modConfig.showValues(indent)  


    def sview(self, indent = 0):   #display current slurm settings

        self.slurmConfig.showValues(indent)   


    def help(self):

        self.modConfig.showDefs()  #display module input information

        print modHelp


    def shelp(self):   #display slurm input information

        self.slurmConfig.showDefs() 


    #-----------------------
    #  Slurm methods
    #-----------------------


    def slurmSetup(self):

        self.modSetup()

        self.slurmConfig.buildSlurmScript()

        self.slurmConfig.writeSlurmScript()   

    
    def srun(self):

        self.slurmSetup()

        self.jobID = sbatch(self.slurmConfig.slurmScriptFile)

        with open(path.join(self.modDir, 'slurm_%s_%s_jobID.txt' % (self.name, self.pipe.name)), 'w') as fh:
            fh.write(str(self.jobID))
        
        self.db.write_new_module(self, status = 'SUBMITTED')

        if self.verbose:
            print 'Submitted job %s' % self.jobID

    def status(self):
        
        if not self.jobID:
            raise Exception('No job submitted')

        printJobStatus(self.jobID)
    

    def kill(self):

        if not self.jobID:
            raise Exception('No job submitted')

        Command_toStdout('scancel %s' % self.jobID).run()


    def getTime(self, time):  #bound and format slurm time

        t = int(time)

        if t < 10:
            return '10'
        elif t > 60:
            return '%s:%s' % ( int(t / 60), mod(t % 60) )  # format 'hours:minutes'                                                                                          


    def __repr__(self):
        return '<%s(modID: %s)>' % (self.name, self.modID)



