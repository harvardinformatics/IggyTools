import os, sys, re 
import os.path as path
from collections import OrderedDict
from iggytools.iggypipeline.module.iggyMod import IggyMod
from iggytools.iggypipeline.module.argDefClass import ArgDef
from iggytools.iggypipeline.module.configClasses import BaseConfig, make_AD_dict
from iggytools.utils.util import mkdir_p, dict2namedtuple, filestem


class Trimmomatic(IggyMod):


    def __init__(self, pipe, outName = None):
        
        IggyMod.__init__(self, 'Trimmomatic', pipe, outName = outName)  #set self.modPref, and do other module initialization

        self.outputHelp = ["If input paramter 'read1' is specified:",
                           'outputs.R1_unpaired            Fastq file of R1 unpaired reads\n',
                           "If input paramters 'read1' and 'read2' are specified:",
                           'outputs.R1_unpaired            Fastq file of R1 unpaired reads',
                           'outputs.R1_paired              Fastq file of R1 paired reads',
                           'outputs.R2_unpaired            Fastq file of R1 unpaired reads',
                           'outputs.R2_paired              Fastq file of R2 paired reads']

    def argSetup(self):
        a = self.modConfig.argDefs

        if 'read1' not in a or not a['read1'].value:
            raise Exception('An R1 input file must be specified')

        if 'output-stem' in a and a['output-stem'].value:
            outStem = a['output-stem'].value
        else:
            outStem = filestem(a['read1'].value)

        # Setup outdir arg, self.modDir, 

        if 'outdir' in a and a['outdir'].value:
            self.modDir = a['outdir'].value  #set self.modDir to new module output directory
        else:
            a['outdir'].value = self.modDir
        
        # Setup steps arg
        if not a['steps'].value: #get default trimmomatic steps if none were given by user
            if a['read2'].value:
                a['steps'].value = self.pref.PAIRED_END_STEPS
            else:
                a['steps'].value = self.pref.SINGLE_END_STEPS                

        # Set module outputs
        outdir = a['outdir'].value

        outItems = dict( (x,None) for x in ['R1_paired', 'R1_unpaired', 'R2_paired', 'R2_unpaired'] )
        outItems['R1_unpaired'] = path.join(outdir, '%s.%s' % (outStem, 'R1.unpaired.tr.fastq'))

        if a['read2'].value:
            outItems['R1_paired'] = path.join(outdir, '%s.%s' % (outStem, 'R1.paired.tr.fastq'))
            outItems['R2_paired'] = path.join(outdir, '%s.%s' % (outStem, 'R2.paired.tr.fastq'))
            outItems['R2_unpaired'] = path.join(outdir, '%s.%s' % (outStem, 'R2.unpaired.tr.fastq'))

        self.outputs = dict2namedtuple(outItems)

        self.buildCommand()


    def modSetup(self):

        IggyMod.modSetup(self)

        a = self.modConfig.argDefs

        if not path.isfile(a['read1'].value):
            raise Exception('Cannot find input file %s' % a['read1'].value)

        if a['read2'].value and not path.isfile(a['read2'].value):
            raise Exception('Cannot find input file %s' % a['read2'].value)


    def setSlurmDefaults_from_modConfig(self):  #update slurm settings based on module inputs

        a = self.modConfig.argDefs  
        s = self.slurmConfig.argDefs

        s['job_name'].default = '%s_%s' % (self.name, self.pipe.name)

        if self.pref.SLURM_PARTITION:
            s['partition'].default = self.pref.SLURM_PARTITION

        for arg in s.itervalues():
            if arg.default is not None:
                arg.value = arg.default

        self.slurmConfig.argDefs = s



    def buildCommand(self):

        #example command: 
        #  java -jar /n/sw/centos6/trimmomatic-0.30.jar PE \
        #       -threads 16 \
        #       -phred64 \
        #       $Sample.R1.fastq $Sample.R2.fastq \
        #       $Outdir/$Sample.R1.paired.t.fastq $Outdir/$Sample.R1.unpaired.t.fastq \
        #       $Outdir/$Sample.R2.paired.t.fastq $Outdir/$Sample.R2.unpaired.t.fastq \
        #       ILLUMINACLIP:$TRIMMOMATIC/adapters/TruSeq3-PE.fa:2:30:10 \
        #       LEADING:10 TRAILING:10 SLIDINGWINDOW:4:15 MINLEN:36

        a = self.modConfig.argDefs

        command = 'java -jar /n/sw/centos6/Trimmomatic-0.32/trimmomatic-0.32.jar \\\n'

        if a['read2'].value:
            command += 'PE \\\n'
        else:
            command += 'SE \\\n'

        if a['threads'].value:
            command += '-threads %s \\\n' % a['threads'].value

        command += '-%s \\\n' % a['encoding'].value

        command += '%s \\\n' % a['read1'].value

        if a['read2'].value:
            command += '%s \\\n' % a['read2'].value

        for ftype in ['R1_paired', 'R1_unpaired', 'R2_paired', 'R2_unpaired']:
            fpath = getattr(self.outputs, ftype)
            if fpath is not None:
                command += '%s \\\n' % fpath

        command += '%s \\\n' % re.sub(',',' ',a['steps'].value)

        command += '\n'  #end line continuation

        self.command = command


    def get_argDefs(self):
        
        return make_AD_dict( 
            [ ArgDef('read1',               help = 'Read1 fastq file.', 
                                            type = str),
 
              ArgDef('-2','--read2',        help = 'Read2 fastq file.', 
                                            type = str),

              ArgDef('-s', '--steps',       help = 'String of comma-separated Trimmomatic steps. For single-end reads, default is %s. For paired end: %s' \
                                                    % (self.pref.SINGLE_END_STEPS, self.pref.PAIRED_END_STEPS),
                                            type = str),

              ArgDef('-e', '--encoding',    help = 'Fastq quality score encoding. Default: %default',
                                            type = str,
                                            choices = ['phred64', 'phred33'],
                                            default = self.pref.ENCODING),

              ArgDef('-m', '--output-stem', help='String used to name output files. By default, ' \
                                                  + 'output files are named by giving input files(s) a ".tr.fastq" extension.',
                                            type = str),

              ArgDef('-o', '--outdir',      help='Output directory. Default is current directory.',
                                            type = str),

              ArgDef('-t', '--threads',     help='Number of threads. Default: %(default)s',
                                            type = int,
                                            default = self.pref.THREADS) ] )


