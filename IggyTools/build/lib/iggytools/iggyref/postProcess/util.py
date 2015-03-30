import os.path as path
import re, gzip, tarfile, glob
from iggytools.utils.util import deleteItem, mkdir_p

def decompress(srcFile, destDir=None, destFile=None):
    fileBasename = path.basename(srcFile)
    if fileBasename[-3:] != '.gz':
        raise Exception('Expected .gz extensino on file to ecompress: ' + srcFile)

    if not destFile:
        if destDir:
            fileStem = fileBasename[:-3]   #fileStem = re.sub(r'\.gz$','', fileBasename)
            destFile = path.join(destDir, fileStem)
        else:
            raise Exception('Either a destination directory or file must be specified.')
    
    fin = gzip.open(srcFile, 'r')
    fout = open(destFile, 'w')

    for line in fin:
        fout.write(line)

    fin.close()
    fout.close()

    return destFile


def untar(srcFile, destDir = None):
    if not destDir:
        destDir = path.dirname(srcFile)

    mkdir_p(destDir) #not clearing destDir as it may contain unrelated files
    tar = tarfile.open(srcFile)
    tar.extractall(destDir)
    tar.close()
    return destDir

def concatFiles(inDir, outFile = None, outDir = None, ext = '.fa'):
    if not ext:
        raise Exception('An non-empty extension string must be specified.')

    if outFile == None:
        outFilename = path.basename(inDir.rstrip('/')) + ext
        if outDir:
            outFile = path.join(outDir, outFilename)
        else:
            outFile = path.join( path.dirname(inDir), outFilename )

    files = glob.glob(path.join(inDir, '*' + ext))
    with open(outFile, 'w') as fout:
        for afile in files:
            with open(afile, 'r') as fin:
                for line in fin:
                    fout.write(line)
    return outFile

