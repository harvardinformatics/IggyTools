import os.path as path
from iggytools.pref.fileClass import BasePrefFile
from iggytools.pref.varClass import PrefVar

class Fastqc_PrefFile(BasePrefFile):


    def __init__(self, prefDir):

        BasePrefFile.__init__(self, 
                              ID = 'Fastqc', 
                              filePath = path.join(prefDir, 'iggypipe_modules', 'fastqc_settings.yaml'), 
                              iggytool = 'iggypipe')

        self.vars = [ PrefVar( name = 'THREADS',
                               default = 4,
                               comment = 'Number of threads',
                               varType = int ),
                      
                      PrefVar( name = 'QUIET',
                               default = False,
                               comment = 'Quiet mode. Set to True to supress messages to stdout',
                               varType = bool),

                      PrefVar( name = 'NOEXTRACT',
                               default = True,
                               comment = 'Noextract. Set to True to leave .gz input files compressed',
                               varType = bool),

                      PrefVar( name = 'NOGROUP',
                               default = True,
                               comment = 'Nogroup. Set to True to disable grouping of bases for reads >50bp',
                               varType = bool),

                      PrefVar( name = 'SLURM_PARTITION',
                               default = 'general',
                               comment = 'Partition for slurm',
                               varType = str ) ]
