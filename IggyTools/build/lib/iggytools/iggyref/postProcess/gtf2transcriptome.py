import os.path as path
import re, glob, logging
from iggytools.utils.util import shell, errScan

def gtf2transcriptome(gtfFile, genomeFastaFile, collObj, transcriptFastaFile):
    log = logging.getLogger("iggyref")
    log.info('Generating transcriptome from genome %s and annotation %s' % (genomeFastaFile, gtfFile))

    runID = 'tophat_' + collObj.repo.source + '_' + collObj.primaryID + '_' + path.splitext(path.basename(gtfFile))[0]
    logDir = path.join(collObj.repo.logDir, runID)
    logFile = path.join(logDir, 'log.txt')

    genomeFileStem = path.splitext(genomeFastaFile)[0]
    gtfFileStem = path.splitext(gtfFile)[0]
    transcriptFastaStem = path.splitext(transcriptFastaFile)[0]

    command = 'cd %s; ' % logDir
    command += 'module load centos6/bowtie2-2.2.1; module load centos6/tophat-2.0.11.Linux_x86_64; '
    command += 'bowtie2-build %s %s; ' % (genomeFastaFile, genomeFileStem)
    command += 'tophat -G %s --transcriptome-index=%s %s; ' % (gtfFile, transcriptFastaStem, genomeFileStem)

    shell(command, logFile, append=False)
    errScan(logFile)

    return transcriptFastaStem

