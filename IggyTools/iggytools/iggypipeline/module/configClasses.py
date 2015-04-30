from collections import OrderedDict
import os, logging, re, traceback, argparse, json, getpass, copy
import os.path as path
from iggytools.utils.util import mkdir_p
from iggytools.iggypipeline.module.argDefClass import ArgDef
from abc import ABCMeta, abstractmethod


class BaseConfig:

    __metaclass__ = ABCMeta

    @classmethod
    def getInstance(cls, cType, mod):

        if cType == 'module':
            return ModConfig(mod, mod.get_argDefs())
        elif cType == 'slurm':
            return SlurmConfig(mod, slurmArgDefs)


    def __init__(self, mod, argDefs):

        self.mod = mod
        self.pipe = mod.pipe

        self.argDefs = argDefs

        self.args = OrderedDict()
        self.argsJson = None

        #create parser from arg definitions
        self.parser = argparse.ArgumentParser()
        for argDef in self.argDefs.itervalues():
            argDef.add(self.parser)  #add arg to parser


    def setValues(self, **namedArgs): 

        for name, arg in self.argDefs.iteritems(): #to namedArgs, add any missing args that had default values

            if name in namedArgs:
                inputValue = namedArgs[name]

                if 'type' in arg.kwargs and arg.kwargs['type'] == list and type(inputValue) != list: #if list is required, 'cast' non-lists nicely
                    
                        inputValue = [inputValue]

                arg.value = inputValue

            elif arg.default is not None and arg.default != arg.value:
                arg.value = arg.default

        self.argsJson = json.dumps( [(arg.name, arg.value) for arg in self.argDefs.itervalues() if arg.value is not None] )


    def showValues(self, indent = 0): #display current settings

        if not any([x.value for x in self.argDefs.itervalues()]):
            raise Exception('No input arguments set. Use module.input() to set inputs, or module.help() for more information.')

        print self.args2str(indent)


    @abstractmethod
    def showDefs(self):
        pass


    def args2str(self, indent = 0):

        argStr = ''
        indentStr = ' ' * indent

        for name, arg in self.argDefs.iteritems():
            if arg.value is not None:
                nameLabel = '%s:' % name
                argStr += '%s%s %s\n' % (indentStr, nameLabel.ljust(20),arg.value)

        return argStr



class ModConfig(BaseConfig):


    def __init__(self, mod, argDefs):

        BaseConfig.__init__(self, mod, argDefs)


    def showDefs(self):

        print '\n%s Inputs:\n' % (self.mod.name.capitalize())

        for arg in self.argDefs.itervalues():
            arg.show()
            print ''
        print ''

        if self.mod.outputHelp:
            print '\n%s Output Attributes:\n' % self.mod.name.capitalize()
            for line in self.mod.outputHelp:
                print "    %s" % line
            print ''



class SlurmConfig(BaseConfig):


    def __init__(self, mod, slurmArgDefs):

        BaseConfig.__init__(self, mod, slurmArgDefs)

        self.slurmScript = None
        self.slurmScriptFile = None


    def showDefs(self):  #display slurm param definitions

        print '\nSlurm Inputs:\n'
        for arg in self.argDefs.itervalues():
            arg.show()
            print ''

        print "\nUse module.input() to set module inputs, then module.slurmShow() to view default/recommended slurm parameters"


    def showValues(self, indent = 0): #display current slurm params

        if not any([x.value for x in self.argDefs.itervalues()]):
            raise Exception("No slurm parameters set. Use module.input() to set module inputs, then module.slurmHelp() and module.slurmShow() to view slurm parameters")

        BaseConfig.showValues(self, indent) 


    def buildSlurmScript(self):

        s = self.argDefs

        script = '#!/bin/bash\n\n'
        script +='#SBATCH --nodes=%s\n' % s['nodes'].value

        if s['ntasks'].value:     script += '#SBATCH --tasks-per-node=%s\n'  % s['ntasks'].value
        if s['mem'].value:        script += '#SBATCH --mem=%s\n'             % s['mem'].value
        if s['time'].value:       script += '#SBATCH --time=%s\n'            % s['time'].value
        if s['partition'].value:  script += '#SBATCH --partition=%s\n'       % s['partition'].value
        if s['job_name'].value:   script += '#SBATCH --job-name=%s\n'        % s['job_name'].value
        if s['mail-type'].value:  script += '#SBATCH --mail-type=%s\n'       % ','.join(s['mail-type'].value)
        if s['error'].value:      script += '#SBATCH --error=%s\n'           % s['error'].value
        if s['output'].value:     
            script += '#SBATCH --output=%s\n'          % s['output'].value
        else:
            script += '#SBATCH --output=%s\n'          % path.join(self.mod.modDir, 'stdout.txt')

        #script += '\nset -eu\n\n'  
        script += self.mod.command + '\n'

        self.slurmScript = script


    def writeSlurmScript(self):

        fname = path.join(self.mod.modDir, 'slurm_%s_%s.sh' % (self.mod.name, self.pipe.name))
        mkdir_p( self.mod.modDir )

        with open(fname, 'w') as f:
            f.write( self.slurmScript )
            f.write( '#This script was generated by iggypipe\n' )

        self.slurmScriptFile = fname            



#convert an argDef list to orderedDict
def make_AD_dict(argDefList): 

    ordDict = OrderedDict()

    for argDef in argDefList:
        ordDict.update( {argDef.name: argDef} )

    return ordDict



# See sbatch man page for doc on slurm parameters
slurmArgDefs =    OrderedDict([ ('nodes',   ArgDef( '-N', '--nodes',
                                                    help = 'Request that a minimum of _nodes_ nodes be allocated to this job.',
                                                    type = int, 
                                                    default = 1 )),
                                                                         
                             ('ntasks',     ArgDef( '--tasks-per-node',   
                                                    help = 'Specify the number of tasks to be launched per node.',
                                                    type = int)),

                             ('mem',        ArgDef( '--mem',
                                                    help = 'Specify the real memory required per node in MB.',
                                                    type = int)),
                                                                         
                             ('time',       ArgDef( '-t', '--time',
                                                    help = 'Run time limit. Accepted formats: min, min:sec, hrs:min:sec, ' \
                                                              + 'days-hrs, days-hrs:min and days-hrs:min:sec.',
                                                    type = str)),
                                                                         
                             ('partition',  ArgDef( '-p', '--partition',  
                                                    help = 'Request a specific partition.',
                                                    type = str)),
                                                                         
                             ('job_name',   ArgDef( '-J', '--job-name', 
                                                    help = 'Specify a name for the job allocation.',
                                                    type = str)),
                                                                         
                             ('output',     ArgDef( '-o', '--output',
                                                    help = "Connect the batch script's stdout to a file named _output_. %j is replaced " \
                                                               + "by the job ID. Unless a stderr file is specified " \
                                                               + "with -e/--error, both stdout and stderr is written to _output_.", 
                                                    type = str)),

                             ('error',      ArgDef( '-e', '--error',
                                                    help = "Connect the batch script's stder to a file named _error_. %j is replaced by the job ID.",
                                                    type = str)),

                             ('mail-type',  ArgDef( '--mail-type',
                                                    help = 'Events triggering slurm notficaiton. Accepted values include: ' \
                                                               + 'BEGIN, END, FAIL, TIME_LIMIT_80, TIME_LIMIT_90.',
                                                    type = list)) ])
