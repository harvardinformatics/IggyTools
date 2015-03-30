import os.path as path
from iggytools.utils.util import md5Checksum, sumChecksum

class rFile(object):
    def __init__(self, name, fprop = None):
        self.name = name
        self.ftpSubDir = ''
        self.checksumFile  = ''
        self.checksumType = ''
        if fprop:
            if 'ftpSubDir' in fprop.keys():
                self.ftpSubDir = fprop['ftpSubDir']
            if 'checksumFile' in fprop.keys():
                self.checksumFile = fprop['checksumFile']
            if 'checksumType' in fprop.keys():
                self.checksumType = fprop['checksumType']
        self.ftpPath = None
        self.remoteTimeString = None
        self.localPath = None
        self.localChecksum = None
        self.remoteChecksum = ''
        self.prevChecksum = ''

    def setLocalChecksum(self):
        if self.checksumType in ['', 'md5', 'md5sum']:
            self.localChecksum = md5Checksum(self.localPath)
        elif self.checksumType == 'sum':
            self.localChecksum = sumChecksum(self.localPath)
        else:
            raise Exception('Unrecognized checksum type: %s (filename: %s)' % (self.checksumType, self.name))

    def __repr__(self):
        return '<rFile(%s)>' % self.name

