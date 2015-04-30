import os.path as path
from iggytools.pref.fileClass import BasePrefFile
from iggytools.pref.varClass import PrefVar

class Trimmomatic_PrefFile(BasePrefFile):


    def __init__(self, prefDir):

        BasePrefFile.__init__(self, 
                              ID = 'Trimmomatic', 
                              filePath = path.join(prefDir, 'iggypipe_modules', 'trimmomatic_settings.yaml'), 
                              iggytool = 'iggypipe')

        self.vars = [ PrefVar( name = 'THREADS',
                               default = 5,
                               comment = 'Number of threads',
                               varType = int ),
                      
                      PrefVar( name = 'PAIRED_END_STEPS',
                               default = 'ILLUMINACLIP:/n/sw/centos6/Trimmomatic-0.32/adapters/TruSeq3-PE.fa:2:30:10,' \
                                             + 'LEADING:10,TRAILING:10,SLIDINGWINDOW:4:15,MINLEN:36',
                               comment = 'Trimmomatic steps for paired end reads',
                               varType = str),

                      PrefVar( name = 'SINGLE_END_STEPS',
                               default = 'ILLUMINACLIP:/n/sw/centos6/Trimmomatic-0.32/adapters/TruSeq3-SE.fa:2:30:10,' \
                                             + 'LEADING:10,TRAILING:10,SLIDINGWINDOW:4:15,MINLEN:36',
                               comment = 'Trimmomatic steps for single end reads',
                               varType = str),

                      PrefVar( name = 'ENCODING',
                               default = 'phred33',
                               comment = 'Fastq quality score encoding',
                               varType = str),

                      PrefVar( name = 'SLURM_PARTITION',
                               default = 'serial_requeue',
                               comment = 'Slurm partition',
                               varType = str ) ]
