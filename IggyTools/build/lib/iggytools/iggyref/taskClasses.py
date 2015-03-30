import logging, traceback, re
import os.path as path
from iggytools.utils.util import flatten
from iggytools.iggyref.rFileClass import rFile
from iggytools.iggyref.postProcess.genePred2gtf import genePred2gtf
from iggytools.iggyref.postProcess.fasta2index import fasta2index
from iggytools.iggyref.postProcess.util import decompress, untar, concatFiles

log = logging.getLogger('iggyref')

class baseTask(object):

    @classmethod
    def getInstance(cls, taskDict, Files, fileProperties):
        taskName = taskDict['taskName']
        if taskName.lower() == 'unzip':
            return Unzip(taskDict, Files, fileProperties)
        elif taskName.lower() == 'unzip-untar':
            return Unzip_untar(taskDict, Files, fileProperties)
        elif taskName.lower() == 'unzip-untar-merge':
            return Unzip_untar_merge(taskDict, Files, fileProperties)
        elif taskName.lower() in ['unzip-txt2gtf', 'txt2gtf']:
            return Txt2gtf(taskDict, Files, fileProperties)
        elif taskName.lower() == 'fasta2index':
            return Fasta2index(taskDict, Files, fileProperties)
        else:
            raise Exception('Unrecognized taskName: %s' % taskName)

    def __init__(self, taskDict, Files, fileProperties):
        inFileNames = taskDict['inFiles']
        if type(inFileNames) != list: inFileNames = [inFileNames]

        outFileNames = list()
        if 'outFiles' in taskDict.keys():
            outFileNames = taskDict['outFiles']
        if type(outFileNames) != list: outFileNames = [outFileNames]

        filesNames = [x.name for x in Files]

        self.inFiles = list()
        for filename in inFileNames:
            try:
                File = Files[filesNames.index(filename)]
            except:
                try: 
                    File = rFile(filename, fileProperties[filename])
                except:
                    File = rFile(filename)
            self.inFiles.append(File)

        self.outFiles = list()
        for filename in outFileNames:
            try:
                File = Files[filesNames.index(filename)]
            except:
                try: 
                    File = rFile(filename, fileProperties[filename])
                except:
                    File = rFile(filename)
            self.outFiles.append(File)

    def validateInOut(self, numIn, numOut):
        if len(self.inFiles) not in flatten([numIn]):
            raise Exception('Expected %s input files for task %s, found %s: %s'%(numIn, self.taskName, len(self.inFiles), ', '.join(map(str,self.inFiles))))
        if len(self.outFiles) not in flatten([numOut]):
            raise Exception('Expected %s output files for task %s, found %s: %s'%(numIn, self.taskName, len(self.outFiles), ', '.join(map(str,self.outFiles))))

    def validateExt(self, filename, extensions, C):
        if type(extensions) != list: extensions = [extensions]
        ignored, ext = path.splitext(filename)
        if ext.lower() not in [x.lower() for x in extensions]:
            raise Exception('Expected file extension(s) %s. Found extension %s. Collection, Task: %s, %s' % (', '.join(extensions), ext, C, self))
    
    def __repr__(self):
        return '<Task(%s -- %s -- %s)>' % (self.taskName, ','.join(map(str,self.inFiles)), ','.join(map(str,self.outFiles)))


class Unzip(baseTask):
    def __init__(self, taskDict, Files, fileProperties):
        baseTask.__init__(self, taskDict, Files, fileProperties)
        self.taskName = 'unzip'

    def run(self, C = None):
        self.validateInOut(1,1) # 1 input, 1 output
        decompress(self.inFiles[0].localPath, destFile = self.outFiles[0].localPath)


class Unzip_untar(baseTask):
    def __init__(self, taskDict, Files, fileProperties):
        baseTask.__init__(self, taskDict, Files, fileProperties)
        self.taskName = 'unzip-untar'

    def run(self, C = None):
        self.validateInOut(1,[0,1]) # 1 input, 0 or 1 outputs 
        if len(self.outFiles) == 0:
            untar(self.inFiles[0].localPath, destDir = None)  #unzip to input file directory. 
        elif len(self.outFiles) == 1:
            untar(self.inFiles[0].localPath, destDir = self.outFiles[0].localPath)


class Unzip_untar_merge(baseTask):
    def __init__(self, taskDict, Files, fileProperties):
        baseTask.__init__(self, taskDict, Files, fileProperties)
        self.taskName = 'unzip-untar-merge'  

    def run(self, C = None):
        self.validateInOut(1,2) # 1 input, 2 outputs
        untarredDir = untar(self.inFiles[0].localPath, self.outFiles[0].localPath)
        concatFiles(untarredDir, outFile = self.outFiles[1].localPath)


class Txt2gtf(baseTask):
    def __init__(self, taskDict, Files, fileProperties):
        baseTask.__init__(self, taskDict, Files, fileProperties)
        self.taskName = 'txt2gtf'  

    def run(self, C):
        self.validateInOut(2,1) # 2 inputs, 1 output

        inFile0 = self.inFiles[0].localPath
        if re.search(r'\.gz$', inFile0, re.IGNORECASE):
            genePredFile = inFile0[:-3]
            decompress(inFile0, destFile = genePredFile)
        else:
            genePredFile = inFile0

        inFile1 = self.inFiles[1].localPath
        if re.search(r'\.gz$', inFile1, re.IGNORECASE):
            genomeFastaFile = inFile1[:-3]
            decompress(inFile1, destFile = genomeFastaFile)
        else:
            genomeFastaFile = inFile1

        gtfFile = self.outFiles[0].localPath

        self.validateExt(genomeFastaFile, ['.fa', '.fasta'], C)
        self.validateExt(genePredFile, '.txt', C)
        self.validateExt(gtfFile, '.gtf', C)

        genePred2gtf(genePredFile, C.repo.source, outFile = gtfFile)


class Fasta2index(baseTask):
    def __init__(self, taskDict, Files, fileProperties):
        baseTask.__init__(self, taskDict, Files, fileProperties)
        self.taskName = 'fasta2index'  

    def run(self, C):
        self.validateInOut(1,0) # 1 input, 0 outputs
        inFile = self.inFiles[0].localPath
        if re.search(r'\.gz$', inFile, re.IGNORECASE):
            decompress(inFile, destFile = inFile[:-3])
            inFile = inFile[:-3]
        fasta2index(inFile, C)
