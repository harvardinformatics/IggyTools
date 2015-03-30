import os.path as path
import re, glob, logging, os, imp
from iggytools.utils.util import shell, errScan, mkdir_p, get_3p_dirname

def fasta2index(fastaFile, C):
    log = logging.getLogger("iggyref")

    runID = 'bowtie2_' + C.primaryID + '_' + path.splitext(path.basename(fastaFile))[0]
    logDir = path.join(C.repo.logDir, runID)
    mkdir_p(logDir)
    logFile = path.join(logDir, 'log.txt')

    log.info('Generating index for fasta file %s. Bowtie2 log file: %s' % (fastaFile, logFile))

    fastaFileStem = path.splitext(fastaFile)[0]

    savedPath = os.getcwd()
    os.chdir(logDir)

    iggytools_srcDir = imp.find_module('iggytools')[1]
    bowtieDir = path.join(iggytools_srcDir, 'thirdparty', get_3p_dirname(), 'bowtie2-2.2.4')

#    command = 'module load centos6/bowtie2-2.2.1; '
#    command += 'bowtie2-build %s %s; ' % (fastaFile, fastaFileStem)

    command = '%s %s %s' % (path.join(bowtieDir, 'bowtie2-build'), fastaFile, fastaFileStem)
    shell(command, logFile, append=False)
    errScan(logFile)

    os.chdir(savedPath)

    return fastaFileStem

