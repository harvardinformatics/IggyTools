import os, glob, sys, logging, re, traceback
import os.path as path
from iggytools.utils.util import flatten, unique, intersect
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
        if 'secondaryID' in self.properties:
            self.secondaryID = self.properties['secondaryID']
        self.type = self.properties['collectionType']

        self.repo = repo
        self.ftp = ftpConn
        self.Tasks = list()

        self.downloadFiles = list()
        self.modifiedFiles = list()

        if 'tasks' in self.properties: #ensure task file lists are type list
            for taskDict in self.properties['tasks']:        
                if type(taskDict['inFiles']) != list: 
                    taskDict['inFiles'] = [taskDict['inFiles']]
                if 'outFiles' in taskDict and type(taskDict['outFiles']) != list: 
                    taskDict['outFiles'] = [taskDict['outFiles']]

        self.setLocalDirs()


    def setLocalDirs(self):
        self.downloadDir = path.join(self.repo.downloadDir, self.primaryID)
        self.finalDir = path.join(self.repo.finalDir, self.primaryID)


    def collectionSetup(self, fileMap = None):
        if fileMap:
            self.translateRawFilenames(fileMap)

        self.setDownloadFiles()  # Create File objs
        self.setTasks() # Create Task objs 


    def translateRawFilenames(self, fileMap):
        def mapFile(x):
            if x in fileMap:
                return fileMap[x]
            else:
                return x

        self.properties['fileList'] = map(mapFile, self.properties['fileList'])  #translate download-file list

        if 'tasks' in self.properties: #translate task filenames
            for taskDict in self.properties['tasks']:
                taskDict['inFiles'] = map(mapFile, taskDict['inFiles'])
                if 'outFiles' in taskDict:
                    taskDict['outFiles'] = map(mapFile, taskDict['outFiles'])

        fileProp = self.properties['fileProperties'] #translate fileProperties keys
        for raw in intersect(fileMap, fileProp):
            fileProp[fileMap[raw]] = fileProp.pop(raw)
                

    def getRawFilenames(self):
        taskDict_filenames = list()

        if 'tasks' in self.properties:
            for taskDict in self.properties['tasks']:
                taskDict_filenames += taskDict['inFiles']
                if 'outFiles' in taskDict:
                    taskDict_filenames += taskDict['outFiles']

        return unique(self.properties['fileList'] + self.properties['fileProperties'].keys() + taskDict_filenames)
    

    def setDownloadFiles(self):
        for filename in self.properties['fileList']:
            if filename in self.properties['fileProperties']:
                File = rFile(filename, self.properties['fileProperties'][filename])
            else:
                File = rFile(filename)
            self.setLocalFilePath(File)
            self.downloadFiles.append(File)


    def setTasks(self):
        if 'tasks' in self.properties:
            for taskDict in self.properties['tasks']:
                taskInstance = baseTask.getInstance(taskDict, self)
                self.Tasks.append(taskInstance)


    def setLocalFilePath(self, File):
        raise NotImplementedError("Implemented by subclass")


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
        return unique(flatten(self.downloadFiles + [Task.inFiles + Task.outFiles for Task in self.Tasks]))


    def __repr__(self):
        if self.secondaryID:
            return '<Collection(%s, %s, %s)>' % (self.primaryID, self.secondaryID, self.repo.source)
        else:
            return '<Collection(%s, %s)>' % (self.primaryID, self.repo.source)

