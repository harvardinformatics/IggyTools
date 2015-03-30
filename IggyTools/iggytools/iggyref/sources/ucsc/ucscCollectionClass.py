import os.path as path
import types, re, glob, os, posixpath
from iggytools.iggyref.baseCollectionClass import baseCollection

# ucsc Collection class

def getVersion(name, regex):
    nameMatch = re.match(regex, name)
    if nameMatch:
        return int(nameMatch.group(1))
    else:
        return -1


def getLatestItem(itemList, regex, dirname):
    ver = -1
    latest = ''
    for item in itemList:
        itemVersion = getVersion(item, regex)
        if itemVersion > ver:
                latest = item
                ver = itemVersion
    if not latest:
        raise Exception('No item matching %s found in directory %s' % (regex, dirname))
    return latest



class ucscCollection(baseCollection):

    def __init__(self, primaryID, repo, ftpConn = None):
        baseCollection.__init__(self, primaryID, repo, ftpConn)

        # Set self.primaryID
        if 'primaryIDregex' in self.properties.keys() and self.properties['primaryIDregex']:
            # Find latest UCSC genome version, and set to primaryID
            primaryIDregex = self.properties['primaryIDregex']
            if not ftpConn:  #look in local filesystem to determine primaryID
                localSearchDir = path.join(self.repo.downloadDir, self.secondaryID)
                dirList = [x for x in os.listdir(localSearchDir) if path.isdir(path.join(localSearchDir,x))]
                self.primaryID = getLatestItem(dirList, primaryIDregex, localSearchDir)

            else:  #look at ftp site to determine lastest genome version
                ftpSearchDir = self.repo.properties['ftpPath']
                itemList = ftpConn.getDirContents(ftpSearchDir)
                self.primaryID = getLatestItem(itemList, primaryIDregex, ftpSearchDir)
        else:
            self.primaryID = self.properties['primaryID']

        self.setLocalDirs()

        # Map filename placeholders to versioned filenames
        fileMap = dict()
        rawFilenames = self.getRawFilenames()
        if 'SNPFILE' in rawFilenames:
            if not ftpConn: 
                searchDir = self.downloadDir
                fileList = [path.basename(x) for x in glob.glob(path.join(searchDir, 'snp*.txt.gz'))]  #glob pattern, not regex
            else:
                searchDir = posixpath.join(self.repo.properties['ftpPath'], self.primaryID, self.properties['fileProperties']['SNPFILE']['ftpSubDir'])
                fileList = ftpConn.getDirContents(searchDir)
            snpFileRegex = r'snp([0-9]{3,}).txt.gz'
            fileMap['SNPFILE'] = getLatestItem(fileList, snpFileRegex, searchDir)
        if 'UNZIPPEDSNPFILE' in rawFilenames:
            fileMap['UNZIPPEDSNPFILE'] = fileMap['SNPFILE'][:-3]   #crop '.gz' ending 
        if 'GENOME_FASTA_GZ' in rawFilenames:
            fileMap['GENOME_FASTA_GZ'] = self.primaryID + '.fa.gz'
        if 'GENOME_FASTA' in rawFilenames:
            fileMap['GENOME_FASTA'] = self.primaryID + '.fa'

        self.collectionSetup(fileMap)


    def setLocalDirs(self):
        self.downloadDir = path.join(self.repo.downloadDir, self.secondaryID, self.primaryID)
        self.finalDir = path.join(self.repo.finalDir, self.secondaryID, self.primaryID)


    def setLocalFilePath(self, File):
        if not File.localPath:
            File.localPath = path.join(self.downloadDir, File.name)


    def setFtpFilePath(self, File):
        File.ftpPath = posixpath.join(self.repo.properties['ftpPath'], self.primaryID, File.ftpSubDir, File.name)


    def setChecksumFtpFilePath(self, File):
        if not File.checksumFile: raise Exception('File.checksumFile must be set')
        File.checksumFtpPath = posixpath.join(self.repo.properties['ftpPath'], self.primaryID, File.ftpSubDir, File.checksumFile)

