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

        # Find latest UCSC genome version, and set to primaryID
        primaryIDregex = self.properties['primaryIDregex']
        if not ftpConn:  #look in local filesystem to determine primaryID
            localSearchDir = path.join(self.repo.downloadDir, self.secondaryID)
            dirList = [x for x in os.listdir(localSearchDir) if path.isdir(path.join(localSearchDir,x))]
            self.primaryID = getLatestItem(dirList, primaryIDregex, localSearchDir)

        else:  #look at ftp site to determine primaryID
            ftpSearchDir = self.repo.properties['ftpPath']
            itemList = ftpConn.getDirContents(ftpSearchDir)
            self.primaryID = getLatestItem(itemList, primaryIDregex, ftpSearchDir)

        localCollectionDir = path.join(self.repo.downloadDir, self.secondaryID, self.primaryID)

        # Replace filename placeholders with latest versioned filenames
        snpFileRegex = r'snp([0-9]{3,}).txt.gz'
        snpFile = [x for x in self.allFiles() if x.name == 'SNPFILE']
        if snpFile:
            snpFile = snpFile[0]
            if not ftpConn: 
                searchDir = localCollectionDir
                fileList = [path.basename(x) for x in glob.glob(path.join(searchDir, 'snp*.txt.gz'))]  #glob, not regex
            else:
                searchDir = posixpath.join(self.repo.properties['ftpPath'], self.primaryID, snpFile.ftpSubDir)
                fileList = ftpConn.getDirContents(searchDir)

            snpFile.name = getLatestItem(fileList, snpFileRegex, searchDir)

        unzipped_snpFile = [x for x in self.allFiles() if x.name == 'UNZIPPEDSNPFILE']
        if unzipped_snpFile:
            unzipped_snpFile = unzipped_snpFile[0]
            unzipped_snpFile.name = snpFile.name[:-3]   #crop '.gz' ending 

        # Set local file paths
        for File in self.allFiles():
            File.localPath = path.join(localCollectionDir, File.name)

    def setFtpFilePath(self, File):
        File.ftpPath = posixpath.join(self.repo.properties['ftpPath'], self.primaryID, File.ftpSubDir, File.name)

    def setChecksumFtpFilePath(self, File):
        if not File.checksumFile: raise Exception('File.checksumFile must be set')
        File.checksumFtpPath = posixpath.join(self.repo.properties['ftpPath'], self.primaryID, File.ftpSubDir, File.checksumFile)

