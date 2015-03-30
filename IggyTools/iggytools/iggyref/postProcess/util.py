import os.path as path
import re, gzip, tarfile, glob
from iggytools.utils.util import deleteItem, mkdir_p

def decompress(srcFile, destDir=None, destFile=None):
    if srcFile[-3:] != '.gz':
        raise Exception('Expected .gz extension on file to decompress: ' + srcFile)

    srcBaseName = path.basename(srcFile)
    srcDir = path.dirname(srcFile)
    srcStem = srcBaseName[:-3]   #srcStem = re.sub(r'\.gz$','', srcBaseName)       

    if not destFile:
        if destDir:
            destFile = path.join(destDir, srcStem)
        else:
            destFile = path.join(srcDir, srcStem)
    
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
    tar = tarfile.open(srcFile) #works with .tar and .tar.gz files
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

