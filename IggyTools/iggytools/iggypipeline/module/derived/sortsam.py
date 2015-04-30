import os, sys, logging, re, argparse
import os.path as path
from collections import OrderedDict
from iggytools.iggypipeline.module.iggyMod import IggyMod
from iggytools.iggypipeline.module.argDefClass import ArgDef
from iggytools.iggypipeline.module.configClasses import BaseConfig, make_AD_dict
from iggytools.utils.util import mkdir_p, dict2namedtuple, filestem


class SortSam(IggyMod):


    def __init__(self, pipe, outName = None):
        
        IggyMod.__init__(self, 'SortSam', pipe, outName = outName)  #set self.pref, plus other module initialization

        self.outputHelp = ['outputs.samFile                SAM alignment file', #***
                           'outputs.metricsFile            Alignment metrics file'] #***


    def argSetup(self):

        a = self.modConfig.argDefs

        sam = a['sam_in'].value

        if not sam:
            raise Exception('An input sam file must be specified')

        if not a['bam_out_stem'].value:
            a['bam_out_stem'].value = path.join(self.modDir, '%s.sorted' % filestem(sam))
        
        # Setup module outputs

        outItems = dict()
        outItems['bam'] = a['bam_out_stem'].value + '.bam'

        self.outputs = dict2namedtuple(outItems)
        
        self.buildCommand()  # create command from input args


    def buildCommand(self):

        #example command:     
        #   samtools view -uS myfile.sam | samtools sort - myfile.sorted 

        a = self.modConfig.argDefs

        sam = a['sam_in'].value
        bam = a['bam_out_stem'].value

        self.command = 'source new-modules.sh; module load bib/2015.02.27-fasrc01; cd %s \n' % self.modDir
        self.command += 'samtools view -uS %s | samtools sort - %s \n' % (sam, bam)


    def setSlurmDefaults_from_modConfig(self):  #update slurm settings based on module inputs

        a = self.modConfig.argDefs  
        s = self.slurmConfig.argDefs

        s['ntasks'].default     = self.pref.THREADS
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

            [ ArgDef('-i', '--sam-in',  help = 'The sam file to sort (required)', 
                                         type = str),

              ArgDef('-o', '--bam-out-stem',  help = 'Sorted bam file stem (full path)',
                                         type = str) ] )


