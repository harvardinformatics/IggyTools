import os.path as path
from iggytools.pref.fileClass import BasePrefFile
from iggytools.pref.varClass import PrefVar

class Bowtie2_PrefFile(BasePrefFile):


    def __init__(self, prefDir):

        BasePrefFile.__init__(self, 
                              ID = 'Bowtie2', 
                              filePath = path.join(prefDir, 'iggypipe_modules', 'bowtie2_settings.yaml'), 
                              iggytool = 'iggypipe')

        self.vars = [ PrefVar( name = 'THREADS',
                               default = 16,
                               comment = 'Number of threads',
                               varType = int ),
                      
                      PrefVar( name = 'ENCODING',
                               default = 'phred33',
                               comment = 'Fastq quality score encoding',
                               varType = str),

                      PrefVar( name = 'SLURM_MEM',
                               default = 16000,
                               comment = 'Slurm memory reservation in MB',
                               varType = int),

                      PrefVar( name = 'SLURM_TIME',
                               default = '48:00',
                               comment = 'Slurm time parameter. See sbatch man page for accepted formats',
                               varType = str),

                      PrefVar( name = 'SLURM_PARTITION',
                               default = 'general',
                               comment = 'Partition for slurm',
                               varType = str ) ]
