import os, sys, logging, re, argparse
import os.path as path
from collections import OrderedDict
from iggytools.iggypipeline.module.iggyMod import IggyMod
from iggytools.iggypipeline.module.argDefClass import ArgDef
from iggytools.iggypipeline.module.configClasses import BaseConfig
from iggytools.utils.util import mkdir_p, dict2namedtuple


class Bowtie2(IggyMod):


    def __init__(self, pipe):
        
        IggyMod.__init__(self, 'Bowtie2', pipe)  #set self.pref, plus other module initialization

        self.modConfig = BaseConfig.getInstance('module', self, self.getArgDefs())

        self.outputHelp = ['outputs.samFile                SAM alignment file',
                           'outputs.metricsFile            Alignment metrics file']

    def argSetup(self):

        a = self.modConfig.argDefs

        # Setup module outputs

        outItems = dict()
        outItems['samFile'] = a['sam'].value
        outItems['metricsFile'] = a['met_file'].value

        self.outputs = dict2namedtuple(outItems)

        # create bowtie command from input args
        self.buildCommand()


    def buildCommand(self):

        #example command:     
        # bowtie2 -x $ReferenceDir/chromFa -q --phred33 --threads $Numthreads \
        #         --met-file $Sample.lane$Lane.stats.txt \
        #         -1 $Indir/$Sample.R1.fastq \
        #         -2 $Indir/$Sample.R2.fastq 

        a = self.modConfig.argDefs

        self.command = 'source new-modules.sh; module load bowtie2/2.2.2-fasrc01; cd %s \n' % self.modDir
        self.command += 'bowtie2 -q --time \\\n'

        self.command += '  --%s \\\n' % a['encoding'].value

        for name in ['index_stem', 'read1', 'read2', 'unpaired', 'sam']:
            if a[name].value is not None: 
                self.command += '  %s %s \\\n' % (a[name].args[0], a[name].value)

        for name in ['threads', 'met_file']:
            if a[name].value is not None:
                self.command += '  --%s %s \\\n' % (re.sub('_','-',name), a[name].value)

        self.command += '\n'  #end line continuation


    def getArgDefs(self):
        
        #arg name (first element in tuple) must not contain dashes
        argDefs = OrderedDict( [

            ('index_stem', ArgDef('-x', '--index-stem',  help = 'The basename of the index for the reference genome',
                                                         type = str)),

            ('read1',      ArgDef('-1', '--read1',       help = 'Comma-separated string of files containing mate 1s',
                                                         type = str)),

            ('read2',      ArgDef('-2', '--read2',       help = 'Comma-separated string of files containing mate 2s',
                                                         type = str)),

            ('unpaired',   ArgDef('-U', '--unpaired',    help = 'Comma-separated string of files containing unpaired reads to be aligned',
                                                         type = str)),

            ('sam',        ArgDef('-S', '--sam',         help="SAM output file",
                                                         type = str,
                                                         default = path.join(self.modDir, 'alignment_bt2.sam'))),

            ('encoding',   ArgDef('-e', '--encoding',    help = 'Fastq quality score encoding. Default: %default',
                                                         type = str,
                                                         choices = ['phred64', 'phred33'],
                                                         default = self.pref.ENCODING)),

            ('threads',    ArgDef('-t', '--threads',     help = 'Number of threads. Default: %(default)s',
                                                         type = int,
                                                         default = self.pref.THREADS)),

            ('met_file',   ArgDef('-m', '--met-file',    help="Alignment metrics output file.",
                                                         type = str,
                                                         default = path.join(self.modDir, 'metrics_bt2.txt'))) ])

        return argDefs


    def setSlurmDefaults_from_modConfig(self):  #update slurm settings based on module inputs

        a = self.modConfig.argDefs  
        s = self.slurmConfig.argDefs

        s['ntasks'].default = a['threads'].value
        s['mem'].default = self.pref.SLURM_MEM
        s['time'].default = self.pref.SLURM_TIME
        s['job_name'].default = '%s_%s' % (self.name, self.pipe.name)
        s['partition'].default = self.pref.SLURM_PARTITION

        for arg in s.itervalues():
            if arg.default is not None:
                arg.value = arg.default

        self.slurmConfig.argDefs = s

