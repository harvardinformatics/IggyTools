from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import os, logging, re, traceback, argparse, json, socket
import os.path as path
from iggytools.utils.util import Command_toStdout, Command_toFile, sbatch, printJobStatus, mkdir_p
from iggytools.pref.iggytools_PrefClass import Iggytools_Preferences
from iggytools.iggypipeline.module.configClasses import BaseConfig, SlurmConfig
from iggytools.iggypipeline.help.modHelp import modHelp

log = logging.getLogger('iggypipe')

class IggyMod:

    __metaclass__ = ABCMeta


    def __init__(self, modName, pipe, outName = None):

        self.pipe = pipe

        if outName:  #name used to create output directory
            self.outName = outName
        else:
            self.outName = modName

        self.name = modName  #module name (eg., Bowtie2, FastQC)

        self.modDir = path.join(self.pipe.pipeDir, self.outName)
        self.modID = None
        self.dbRecord = None

        self.db = pipe.db
        self.verbose = pipe.verbose
        self.pref = pipe.iggyPref['iggypipe'][modName] #get module preferences

        self.command = None
        self.jobID = None
        self.pid = None
        self.hostname = None

        self.outputs = None
        self.outputHelp = None

        self.slurmConfig = BaseConfig.getInstance('slurm', self)
        self.modConfig = BaseConfig.getInstance('module', self)


    def run(self):

        self.runType = 'local'
        self.hostname = socket.gethostname()

        self.modSetup()

        cmd = Command_toFile(self.command, path.join(self.modDir, 'stdout.txt'), append=False, echo=True)
        self.pid = cmd.pid

        if not self.dbRecord:
            self.db.write_new_module(self, )   #set self.modID. Set self.pipe.pipeID if unset.

        log.info('Running %s in pipeline %s:\n%s' % (self.name, self.pipe.name, self.command))

        self.writeParams()  #write params, pid to output dir

        cmd.run()

        self.dbRecord.status = 'ENDED'
        self.db.session.commit()

        log.info('Module %s (id: %s) in pipeline %s (id: %s) ended.' % (self.name, self.modID, self.pipe.name, self.pipe.pipeID))
        

    def argSetup(self):  # process/format module inputs, create output args, build module command
        pass


    def modSetup(self):  # create output directories, or additional module initialization

        if not path.isdir(self.modDir):  
            mkdir_p(self.modDir)


    def writeParams(self, slurm = False):  #write params, pid to output dir
        paramsLogFile = path.join( self.modDir, '%s_%s_inputs.txt' % (self.pipe.name, self.name) )
        
        with open(paramsLogFile, 'w') as fh:

            fh.write('\nModule Inputs:\n\n')
            fh.write( '\n'.join( [ '%s: %s' % (arg.name, arg.value) for arg in self.modConfig.argDefs.itervalues() if arg.value is not None] ) )
            
            if self.command:
                fh.write('\n\nCommand:\n\n')
                fh.write('%s' % self.command)

            if self.pid:
                fh.write('\nProcess ID: %s\n' % self.pid)
                fh.write('\nHost: %s\n\n' % socket.gethostname())

            elif slurm:
                fh.write('\n\nSlurm Parameters:\n\n')
                fh.write( '\n'.join( [ '%s: %s' % (arg.name, arg.value) for arg in self.slurmConfig.argDefs.itervalues() if arg.value is not None] ) )                
                fh.write('\nJob ID: %s\n\n' % self.jobID)
                

    @abstractmethod
    def get_argDefs(self):  # define module params, defaults.   
        pass


    @abstractmethod
    def setSlurmDefaults_from_modConfig(self):   # update slurm settings based on module inputs
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
        print '%sModule:              %s' % (indentStr, self.name)
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

        self.runType = 'slurm'

        self.slurmSetup()

        self.jobID = sbatch(self.slurmConfig.slurmScriptFile)

        self.db.write_new_module(self)

        self.writeParams(slurm = True)  #write params, jobID to output dir

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
        return '<%s(modID: %s, modDir: %s)>' % (self.name, self.modID, self.modDir)



