import os.path as path
import types
from iggytools.iggyref.baseCollectionClass import baseCollection

# ncbi Collection class

class ncbiCollection(baseCollection):
    def __init__(self, primaryID, repo, ftpConn = None):
        baseCollection.__init__(self, primaryID, repo, ftpConn)

        for File in self.allFiles():
            File.localPath = path.join(self.repo.downloadDir, self.primaryID, File.name)

    def setFtpFilePath(self, File):
        File.ftpPath = path.join(File.ftpSubDir, File.name)

    def setChecksumFtpFilePath(self, File):
        if not File.checksumFile: raise Exception('File.checksumFile must be set')
        File.checksumFtpPath = path.join(File.ftpSubDir, File.checksumFile)

