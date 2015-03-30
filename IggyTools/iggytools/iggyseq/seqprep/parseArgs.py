from iggytools.iggyseq.seqprep.dictOptParse import DictArgumentParser
from iggytools.iggyseq.runClasses import getSeqPref
import sys, re
import os.path as path

def parseArgs(argv, pref = None):

    if not pref:
        pref = getSeqPref()

    parser = DictArgumentParser(usage='usage: %(prog)s [options] <run_name>')

    #General options:
    parser.add_argument('runName', help ='Name of run to demultiplex.', action ='store', type = str)

    parser.add_argument('-p','--primary',help ='Directory containing run directory <run_name>. Default: %(default)s',
                        default = pref.PRIMARY_PARENT, action = 'store', type = str, dest = 'primaryParent', metavar = 'DIR')

    parser.add_argument('-s','--suffix', help = 'Suffix to add to run name to create output directory name. By default, no suffix is added.', 
                        default = None, action = 'store', type = str, metavar = 'SUFFIX')

    parser.add_argument('-l','--lanes', help = 'Comma-separated list of lanes to process. HiSeq only. ' + \
                        'By default, all lanes are processed. Example lane list: 2,3,4',
                        default = None, action = 'store', type = str, dest = 'lanesStr', metavar = 'LANES')

    parser.add_argument('-d','--noDbStore', help = 'Suppress database updates. Default: %(default)s',
                        default = pref.SEQPREP_DB_STORE, action = 'store_false', dest = 'dbStore')

    parser.add_argument('-v','--verbose', help = 'Verbose mode. Default: %(default)s',
                        default = False, action = 'store_true')

    parser.add_argument('-n','--numThreads', help = 'Number of threads. Default: %(default)s',
                        default = pref.SEQPREP_NUM_THREADS, action = 'store', type = int, dest = 'numThreads', metavar = 'NUM')

    parser.add_argument('-w','--watcherEmails', help = 'Comma-separated list of email addresses to send demultiplex summaries. Default: %(default)s',
                        default = pref.WATCHER_EMAILS, action = 'store', type = str, metavar = 'ADDRESSES')

    parser.add_argument('-u','--userEmails', help = 'Comma-separated list of email addresses to send demultiplex summaries ' + \
                        'and all seqprep notifications (warnings, errors, etc). Default: %(default)s',
                        default = pref.USER_EMAILS, action = 'store', type = str, metavar = 'ADDRESSES')

    #bcl2fastq options:
    parser.add_argument('-m','--mismatches', help = 'Number of mismatches allowed in index read. Default: %(default)s',
                        default = pref.SEQPREP_NUM_MISMATCHES, action = 'store', type = int, dest = 'numMismatches', metavar = 'NUM')

    parser.add_argument('-k','--customBasesMask', help = 'Custom bases mask. By default, mask is generated automatically from runinfo and samplesheet files.',
                        default = None, action = 'store', type = str, dest = 'customBasesMask', metavar = 'MASK')

    parser.add_argument('-b','--ignoreMissingBcl', help = 'Ignore missing BCL files. Default: %(default)s',
                        default = pref.SEQPREP_IGNORE_MISSING_BCL, action = 'store_true', dest = 'ignoreMissingBcl')

    parser.add_argument('-c','--ignoreMissingControl', help = 'Ignore missing control files. Default: %(default)s',
                        default = pref.SEQPREP_IGNORE_MISSING_CONTROL, action = 'store_true', dest = 'ignoreMissingBcl')

    parser.add_argument('-f','--withFailedReads', help = 'Include failed reads in demultiplexing results.. Default: %(default)s',
                        default = pref.SEQPREP_WITH_FAILED_READS, action = 'store_true', dest = 'withFailedReads')

    parser.add_argument('-t','--tileRegex', help = 'Regular expression for tile selection. Default: %(default)s',
                        default = pref.SEQPREP_TILE_REGEX, action = 'store', type = str, dest = 'tileRegex', metavar = 'REGEX')
    
    #NextSeq-specific options
    parser.add_argument('-g','--suppressAdapterTrimming', help = 'Suppress adapter trimming by removing adapters from samplesheet. ' + \
                        'NextSeq only. Default: %(default)s', default = pref.NEXTSEQ_SUPPRESS_ADAPTER_TRIMMING, action = 'store_true', 
                        dest = 'suppressAdapterTrimming')

    parser.add_argument('-z','--maskShortAdapterReads', help = 'Mask short adapter reads. NextSeq only. Default: 32 (Set by bcl2fastq)',
                        default = pref.NEXTSEQ_MASK_SHORT_ADAPTER_READS, action = 'store', type = int, dest = 'maskShortAdapterReads', 
                        metavar = 'MASKINTEGER')

    parser.add_argument('-r','--minTrimmedReadLength', help = 'Minimum trimmed read length.. NextSeq only. Default: 32 (Set by bcl2fastq)',
                        default = pref.NEXTSEQ_MIN_TRIMMED_READ_LENGTH, action = 'store', type = int, dest = 'minTrimmedReadLength', 
                        metavar = 'LENGTH')

    args = parser.parse_args(argv)

    if not re.match('[0-9]{6}_[0-9A-Za-z]+_', args['runName']): #matches from beg.
        raise Exception('Expected run name as argument, got %s. Use -h option to see usage.' % args.runName)

    return args
