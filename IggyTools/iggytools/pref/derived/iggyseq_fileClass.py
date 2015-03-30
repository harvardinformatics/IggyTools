import os.path as path
import re
from iggytools.utils.util import getUserHome, dict2namedtuple
from iggytools.pref.fileClass import BasePrefFile
from iggytools.pref.varClass import PrefVar

class Iggyseq_PrefFile(BasePrefFile):


    def __init__(self, prefDir):

        BasePrefFile.__init__(self, 
                              ID = 'iggyseq', 
                              filePath = path.join(prefDir, 'iggyseq_settings.yaml'), 
                              iggytool = 'iggyseq')

        self.vars = [ PrefVar( name = 'VERBOSE',
                               default = False,
                               comment = 'Iggyseq verbose mode',
                               varType = bool ),

                      PrefVar( name = 'PRIMARY_PARENT',
                               default = '/n/illumina01/primary_data',
                               comment = 'Directory where run directories with BCL files are located',
                               varType = str ),

                      PrefVar( name = 'MACHINE_TYPE',
                               default = dict(SN343 = 'HiSeq', D00365 = 'HiSeq', NS500422 = 'NextSeq'),
                               comment = 'Dictionary mapping machine name to machine type. (Keys are machine names, values are type',
                               varType = dict ),

                      PrefVar( name = 'USERS_FILE',
                               default = '/n/informatics/saved/seqhub_users_list.txt',
                               comment = 'File containing comma-separated email addresses to be sent all iggyseq notifications and demultiplex summaries',
                               varType = str ),

                      PrefVar( name = 'WATCHERS_FILE',
                               default = '/n/informatics/saved/seqprep_watchers_list.txt',
                               comment = 'File containing comma-separated email addresses to be sent demultiplex summaries only',
                               varType = str ), 

                      PrefVar( name = 'LOGDIR_PARENT',
                               default = '/n/informatics_external/seq/seqprep_log',
                               comment = 'Directory where run log directories are written',
                               varType = str ),

                      PrefVar( name = 'PROCESSING_PARENT', 
                               default = '/n/seqcfs/sequencing/analysis_in_progress',
                               comment = 'Directory where run processing directories are written',
                               varType = str ),

                      PrefVar( name = 'FINISHING_PARENT',
                               default = '/n/seqcfs/sequencing/analysis_finished',
                               comment = 'Directory where run finishing directories are written',
                               varType = str ),

                      PrefVar( name = 'FINAL_PARENT',
                               default = '/n/ngsdata',
                               comment = 'Directory where demultiplexed runs are written for download by users',
                               varType = str ),

                      PrefVar( name = 'SEQPREP_NUM_MISMATCHES',
                               default = 0,
                               comment = 'Number of mismatches allowed in barcodes when demultiplexing', 
                               varType = int ),

                      PrefVar( name = 'SEQPREP_NUM_THREADS',
                               default = 8,
                               comment = 'Number of threads for demultiplexing', 
                               varType = int ),

                      PrefVar( name = 'SEQPREP_IGNORE_MISSING_BCL',
                               default = True,
                               comment = 'Ignore missing BCL files',
                               varType = bool ),

                      PrefVar( name = 'SEQPREP_IGNORE_MISSING_CONTROL',
                               default = True,
                               comment = 'Ignore missing CONTROL files',
                               varType = bool ),

                      PrefVar( name = 'SEQPREP_WITH_FAILED_READS',
                               default = False,
                               comment = 'Include failed reads in demultiplex results',
                               varType = bool ),

                      PrefVar( name = 'SEQPREP_TILE_REGEX',
                               default = None,
                               comment = 'Regex for tile selection',
                               varType = str ),

                      PrefVar( name = 'SEQPREP_DB_STORE',
                               default = True,
                               comment = 'Update minilims upon completion of demultiplexing',
                               varType = bool ),

                      PrefVar( name = 'NEXTSEQ_MASK_SHORT_ADAPTER_READS',
                               default = 'None',
                               comment = 'For NextSeq, mask short adapter reads',
                               varType = int),

                      PrefVar( name = 'NEXTSEQ_SUPPRESS_ADAPTER_TRIMMING',
                               default = False,
                               comment = 'For NextSeq, suppress adater trimming',
                               varType = bool ),

                      PrefVar( name = 'NEXTSEQ_MIN_TRIMMED_READ_LENGTH',
                               default = 0,    #set to zero because of bcl2fastq bug. See seqprep doc for details
                               comment = 'For NextSeq, minimum trimmed read length',
                               varType = int ), 

                      PrefVar( name = 'SLURM_TIME',
                               default = '48:00:00', 
                               comment = 'Slurm time reservation in format HH:MM:SS',
                               varType = str ),

                      PrefVar( name = 'SLURM_MEM',
                               default = 10000,
                               comment = 'Slurm memory reservation in MB',
                               varType = int ),

                      PrefVar( name = 'SLURM_PARTITION',
                               default = 'general',
                               comment = 'SLURM PARTITION',
                               varType = str ) ]

    def getVars(self):

        self.fileSetup()  #ensure pref file exists

        self.load()  #read and process preferences 

        vDict = dict( [(x.name, x.value) for x in self.vars] )

        with open( vDict['USERS_FILE'] ) as fh:
            users_string = fh.read().rstrip()
        
        with open( vDict['WATCHERS_FILE'] ) as fh:
            watchers_string = fh.read().rstrip()

        vDict['USER_EMAILS']    = re.split("[,\s]+", users_string)
        vDict['WATCHER_EMAILS'] = re.split("[,\s]+", watchers_string)

        vDict['LOGFILE'] = path.join( vDict['LOGDIR_PARENT'], 'log.txt' )

        return dict2namedtuple( dict( [(name, value) for name,value in vDict.iteritems()] ) )


