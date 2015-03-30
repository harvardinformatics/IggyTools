import os.path as path
import types
from iggytools.iggyref.baseCollectionClass import baseCollection

# ncbi Collection class

class ncbiCollection(baseCollection):
    def __init__(self, primaryID, repo, ftpConn = None):
        baseCollection.__init__(self, primaryID, repo, ftpConn)
        self.collectionSetup()


    def setLocalFilePath(self, File):
        if not File.localPath:
            File.localPath = path.join(self.downloadDir, File.name)

    def setFtpFilePath(self, File):
        File.ftpPath = path.join(File.ftpSubDir, File.name)

    def setChecksumFtpFilePath(self, File):
        if not File.checksumFile: raise Exception('File.checksumFile must be set')
        File.checksumFtpPath = path.join(File.ftpSubDir, File.checksumFile)

