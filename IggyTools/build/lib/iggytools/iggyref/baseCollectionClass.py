import os, glob, sys, logging, re, traceback
import os.path as path
from iggytools.utils.util import flatten, unique
from iggytools.iggyref.taskClasses import baseTask
from iggytools.iggyref.rFileClass import rFile

log = logging.getLogger('iggyref')

class baseCollection(object):

    @classmethod
    def getInstance(cls, primaryID, repo, ftpConn = None):
        modulepath = 'iggytools.iggyref.sources.%s.%sCollectionClass' % ((repo.source,)*2)
        try:
            mod = __import__(modulepath,fromlist=['%sCollectionClass'%repo.source])
            klass = getattr(mod, '%sCollection' % repo.source)
        except ImportError:
            log.error("Unable to import %s: %s" % (modulepath, traceback.format_exc()))
        try:
            return klass(primaryID, repo, ftpConn)
        except:
            log.error("Unable to instantiate class in %s: %s" % (modulepath, traceback.format_exc()))

    def __init__(self, primaryID, repo, ftpConn=None):
        collMod = __import__('iggytools.iggyref.sources.%s.collections.%s' % (repo.source, primaryID),fromlist=[primaryID])
        self.properties = getattr(collMod,'collectionProperties')
        self.primaryID = primaryID
        self.secondaryID = ''
        if 'secondaryID' in self.properties.keys():
            self.secondaryID = self.properties['secondaryID']
        self.type = self.properties['collectionType']

        self.Files = list()
        for filename in self.properties['fileList']:
            self.Files.append(rFile(filename, self.properties['fileProperties'][filename]))

        self.Tasks = list()
        if 'tasks' in self.properties.keys():
            for taskDict in self.properties['tasks']:
                taskInstance = baseTask.getInstance(taskDict, self.Files, self.properties['fileProperties'])
                self.Tasks.append(taskInstance)

        self.repo = repo
        self.ftp = ftpConn
        self.modifiedFiles = list()

    def setFtpFilePath(self, File):
        raise NotImplementedError("Implemented by subclass")

    def setChecksumFtpFilePath(self, File):
        raise NotImplementedError("Implemented by subclass")

    def setRemoteTimeString(self, File):
        File.remoteTimeString = self.ftp.getTimeString(File.ftpPath)
        if not File.remoteTimeString:
            raise Exception('Unable to get timestring for remote file: ' + File.ftpPath)

    def setRemoteChecksum(self, File):
        if not File.checksumFile: 
            return
        self.setChecksumFtpFilePath(File)
        File.remoteChecksum = self.ftp.getChecksum(File)
        if not File.remoteChecksum: 
            raise Exception("Unable to retrieve checksum for file '%s' from remote checksumFile '%s'" % (File.name, File.checksumFtpPath))
    
    def allFiles(self):
        return unique(flatten(self.Files + [Task.inFiles + Task.outFiles for Task in self.Tasks]))

    def __repr__(self):
        return '<Collection(%s, %s, %s)>' % (self.primaryID, self.secondaryID, self.repo.source)

