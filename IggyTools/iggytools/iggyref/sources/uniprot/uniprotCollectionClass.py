import os.path as path
import os, types, posixpath
from iggytools.iggyref.baseCollectionClass import baseCollection

# uniprot Collection class

class uniprotCollection(baseCollection):
    def __init__(self, primaryID, repo, ftpConn = None):
        baseCollection.__init__(self, primaryID, repo, ftpConn)
        self.setLocalDirs()
        self.collectionSetup()

    def setLocalFilePath(self, File):
        if not File.localPath:
            File.localPath = path.join(self.downloadDir, File.name)

    def setFtpFilePath(self, File):
        File.ftpPath = posixpath.join(self.repo.properties['ftpPath'], File.ftpSubDir, File.name)

    def setChecksumFtpFilePath(self, File):
        if not File.checksumFile: raise Exception('File.checksumFile must be set')
        File.checksumFtpPath = posixpath.join(self.repo.properties['ftpPath'], File.ftpSubDir, File.checksumFile)


