import os.path as path
from iggytools.pref.fileClass import BasePrefFile
from iggytools.pref.varClass import PrefVar

class SortSam_PrefFile(BasePrefFile):


    def __init__(self, prefDir):

        BasePrefFile.__init__(self, 
                              ID = 'SortSam', 
                              filePath = path.join(prefDir, 'iggypipe_modules', 'sortsam_settings.yaml'), 
                              iggytool = 'iggypipe')

        self.vars = [ PrefVar( name = 'THREADS',
                               default = 5,
                               comment = 'Number of threads',
                               varType = int ),
                      
                      PrefVar( name = 'SLURM_MEM',
                               default = 5000,
                               comment = 'Slurm memory reservation in MB',
                               varType = int),

                      PrefVar( name = 'SLURM_TIME',
                               default = '6:00:00',
                               comment = 'Slurm time parameter. See sbatch man page for accepted formats',
                               varType = str),

                      PrefVar( name = 'SLURM_PARTITION',
                               default = 'serial_requeue',
                               comment = 'Slurm partition', 
                               varType = str ) ]

