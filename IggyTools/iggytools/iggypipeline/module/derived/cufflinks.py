import os, sys, logging, re, argparse
import os.path as path
from collections import OrderedDict
from iggytools.iggypipeline.module.iggyMod import IggyMod
from iggytools.iggypipeline.module.argDefClass import ArgDef
from iggytools.iggypipeline.module.configClasses import BaseConfig, make_AD_dict
from iggytools.utils.util import mkdir_p, dict2namedtuple


class Cufflinks(IggyMod):


    def __init__(self, pipe, outName = None):
        
        IggyMod.__init__(self, 'Cufflinks', pipe, outName = outName)  #set self.pref, plus other module initialization

        self.outputHelp = ['outputs.genes_fpkm_tracking       Gene-level expression',
                           'outputs.isoforms_fpkm_tracking    Transcript-level expression',
                           'outputs.transcripts_gtf           Assembled transcripts']

    def argSetup(self):

        a = self.modConfig.argDefs

        if not a['aligned_reads'].value:
            raise Exception('The aligned reads input parameter must be set for Cufflinks')

        if a['GTF'].value and a['GTF_guide'].value:
            raise Exception('Only one of the Cufflinks input parameters GTF and GTF-guide may be specified')

        # Setup module outputs

        outItems = dict()
        outItems['genes_fpkm_tracking'] = path.join(self.modDir, 'genes.fpkm_tracking')
        outItems['isoforms_fpkm_tracking'] = path.join(self.modDir, 'isoforms.fpkm_tracking')
        outItems['transcripts_gtf'] = path.join(self.modDir, 'transcripts.gtf')

        self.outputs = dict2namedtuple(outItems)
        
        self.buildCommand()  # create cufflinks command from input args


    def buildCommand(self):

        #example command:     
        #cufflinks --GTF $Gff \
        #          --num-threads $Numthreads \
        #          --output-dir $Outdir/$Sample \
        #          $Sample/accepted_hits.bam 

        a = self.modConfig.argDefs

        self.command = 'source new-modules.sh; module load cufflinks/2.2.1-fasrc01; cd %s \n' % self.modDir
        self.command += 'cufflinks \\\n'

        for name in ['GTF', 'GTF_guide', 'frag_bias_correct', 'num_threads', 'output_dir']:
            if a[name].value is not None:
                self.command += '  --%s %s \\\n' % (re.sub('_','-',name), a[name].value)

        self.command += '  %s' % a['aligned_reads'].value  
        self.command += '\n'  #end line continuation


    def setSlurmDefaults_from_modConfig(self):  #update slurm settings based on module inputs

        a = self.modConfig.argDefs  
        s = self.slurmConfig.argDefs

        s['ntasks'].default     = a['num_threads'].value
        s['mem'].default        = self.pref.SLURM_MEM
        s['time'].default       = self.pref.SLURM_TIME
        s['job_name'].default   = '%s_%s' % (self.name, self.pipe.name)
        s['partition'].default  = self.pref.SLURM_PARTITION

        for arg in s.itervalues():
            if arg.default is not None:
                arg.value = arg.default

        self.slurmConfig.argDefs = s


    def get_argDefs(self):

        return make_AD_dict(

            [ ArgDef('-r', '--aligned-reads',      help = 'SAM or BAM file of aligned reads (required).',
                                                   type = str),

              ArgDef('-t', '--GTF',                help = 'GTF or GFF annotation file. Use with RABT or ab initio assembly is not supported.',
                                                   type = str),                                                   

              ArgDef('-g', '--GTF-guide',          help = 'GTF or GFF annotation file for RABT assembly.',
                                                   type = str),

              ArgDef('-b', '--frag-bias-correct',  help = 'Genome fasta file to use for bias detection and correction',
                                                   type = str),

              ArgDef('-p', '--num-threads',        help = 'Number of threads',
                                                   type = str,
                                                   default = self.pref.THREADS),

              ArgDef('-o', '--output-dir',         help = 'Output directory', 
                                                   type = str, 
                                                   default = self.modDir) ] )

