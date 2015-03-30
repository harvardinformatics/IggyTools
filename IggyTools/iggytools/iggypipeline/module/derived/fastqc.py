import os, sys, re 
import os.path as path
from collections import OrderedDict
from iggytools.iggypipeline.module.iggyMod import IggyMod
from iggytools.iggypipeline.module.argDefClass import ArgDef
from iggytools.iggypipeline.module.configClasses import BaseConfig
from iggytools.utils.util import mkdir_p, dict2namedtuple


class Fastqc(IggyMod):


    def __init__(self, pipe):
        
        IggyMod.__init__(self, 'Fastqc', pipe)  #set self.pref, and do other module initialization

        self.modConfig = BaseConfig.getInstance('module', self, self.getArgDefs())

        self.outputHelp = ["outputs.fileList               List of zip file paths (one per input file)"]


    def argSetup(self):

        a = self.modConfig.argDefs

        if 'inFiles' not in a or not a['inFiles']:
            raise Exception('At least one input file must be specified')

        # Setup input files arg

        files = a['inFiles'].value

        if type( files ) != list:
            files = files.split(',') 

        if a['inputdir'].value:
            files = [ path.join(a['inputdir'].value, x) for x in files ]
        a['inFiles'].value = files

        # Setup outdir arg, update self.modDir

        if 'outdir' in a and a['outdir'].value:
            self.modDir = a['outdir'].value  #set new module output directory
        else:
            a['outdir'].value = self.modDir

        # Setup module outputs

        outItems = dict()
        outItems['fileList'] = list()

        for inFile in a['inFiles'].value:
            outItems['fileList'].append( path.join(a['outdir'].value, re.sub(r'\.fastq(\.gz)?$', '.zip', inFile)) )

        self.outputs = dict2namedtuple(outItems)

        self.modConfig.argDefs = a

        self.buildCommand()


    def modSetup(self):

        a = self.modConfig.argDefs

        for inFile in a['inFiles'].value:  
            if not path.isfile(inFile):
                raise Exception('Cannot find input file %s' % inFile)

        if not path.isdir(a['outdir'].value):  #create output dir
            mkdir_p(a['outdir'].value)


    def buildCommand(self):

        #example command: fastqc --threads 3 --noextract --nogroup --outdir $outdir $fastqfile

        a = self.modConfig.argDefs

        command = 'source new-modules.sh; module load fastqc/0.11.2-fasrc01 \n'
        command += 'fastqc \\\n'

        if a['outdir'].value:
            command += '  --outdir %s \\\n' % a['outdir'].value

        if a['threads'].value:
            command += '  --threads %s \\\n' % a['threads'].value

        if a['quiet'].value:
            command += '  --quiet \\\n'

        if a['noextract'].value:
            command += '  --noextract \\\n'

        if a['nogroup'].value:
            command += '  --nogroup \\\n'

        if a['inputdir']:
            inputFilePaths = [path.join(a['inputdir'].value,x) for x in a['inFiles'].value]
        else:
            inputFilePaths = a['inFiles'].value

        command += '  %s' % ' '.join(inputFilePaths)
        command += '\n'  #end line continuation

        self.command = command


    def getArgDefs(self):
        
        argDefs = OrderedDict( [
            ('inFiles', ArgDef('inFiles',        help = 'Comma-separted list of input files.', 
                                                       type = list)),

            ('inputdir',   ArgDef('-d', '--inputdir',  help = 'Directory containing input files. Default: current directory.',
                                                       type = str)),

            ('outdir',     ArgDef('-o', '--outdir',    help ='Directory where output files should be written. Default: <projDir>/fastqc: %(default)s.',
                                                       type = str, 
                                                       default = self.modDir)),
     
            ('threads',    ArgDef('-t', '--threads',   help ='Number of threads. Note: FastQC uses at most 3 threads per input file. Default: %(default)s.',
                                                       type = int, 
                                                       default = self.pref.THREADS)),

            ('quiet',      ArgDef('-q', '--quiet',     help = 'Suppress FastQC progress messages to stdout. Default: %(default)s.',
                                                       type = bool,
                                                       default = self.pref.QUIET)),

            ('noextract',  ArgDef('-x', '--noextract', help ='Do not uncompress the output file after creating it.',
                                                       type = bool,
                                                       default = self.pref.NOEXTRACT)),

            ('nogroup',    ArgDef('-n', '--nogroup',   help ='Disable grouping of bases for reads >50bp. Reports show data for every base in read.',
                                                       type = bool,
                                                       default = self.pref.NOGROUP)) ])

        return argDefs


    def setSlurmDefaults_from_modConfig(self):  #update slurm settings based on module inputs

        args = self.modConfig.argDefs  
        sargs = self.slurmConfig.argDefs

        # Threads: three per input file
        sargs['ntasks'].default = 3 * len(args['inFiles'].value)

        # Memory: 500 MB per input file
        sargs['mem'].default = 500 * len(args['inFiles'].value)

        # Time: 30 minutes per gigabyte of the largest input file
        maxBytes = 0
        for inFile in args['inFiles'].value:
            bytes = path.getsize(inFile)
            if bytes > maxBytes:
                maxBytes = bytes

        sargs['time'].default = self.getTime(int( maxBytes * 3 * 10^-8 ))  

        # Other param defaults
        sargs['job_name'].default = '%s_%s' % (self.name, self.pipe.name)

        if self.pref.SLURM_PARTITION:
            sargs['partition'].default = self.pref.SLURM_PARTITION

        for s in sargs.itervalues():
            if s.default is not None:
                s.value = s.default

        self.slurmConfig.argDefs = sargs

