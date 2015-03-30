import os, glob, sys, logging, re, traceback
import os.path as path
from iggytools.config.config import get_iggyref_preferences
from iggytools.iggyref.FTPclass import iggyrefFTP
from iggytools.iggyref.DBclass import iggyrefDB
from iggytools.iggyref.rFileClass import rFile
from iggytools.iggyref.baseCollectionClass import baseCollection
from iggytools.iggyref.depGraph.graphClasses import depGraph
from iggytools.utils.util import intersect, flatten, rsync, mkdir_p, unique, insert

class Repo(object):
    def __init__(self, source, customPrefDir = None):
        config = get_iggyref_preferences(customPrefDir)
        self.source = source
        repoPropertiesMod = __import__('iggytools.iggyref.sources.%s.properties' % self.source,fromlist=['properties'])
        self.properties = getattr(repoPropertiesMod,'repoProperties')
        self.logDir = path.join(config.LOG_DIR, self.source)
        self.tempDir = path.join(config.TEMP_DIR, self.source)
        self.downloadDir = path.join(config.DOWNLOAD_DIR, self.source) 
        self.intermedDir = path.join(config.INTERMED_DIR, self.source)
        if config.DEBUG:
            self.intermedDir = path.join(config.DEBUG_DIR, self.source)
        else:
            self.finalDir = path.join(config.REPO_DIR, self.source) 
        mkdir_p(self.logDir)
        mkdir_p(self.tempDir)
        mkdir_p(self.downloadDir)
        mkdir_p(self.finalDir)

        logging.basicConfig(filename = path.join(config.LOG_DIR, 'iggyref.log'),
                            format = '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s',
                            datefmt = '%m/%d/%Y %I:%M:%S %p',
                            level = config.LOG_LEVEL)
        self.log = logging.getLogger('iggyref')
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(config.LOG_LEVEL)
        sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'))
        self.log.addHandler(sh)
        self.config = config
        self.Collections = list()
        self.modifiedCollections = dict()
        self.db = None
        self.ftp = None

    def updateSpeciesTable(self, C):
        if C.type == 'genome':
            self.db.addSpeciesCommonName(C.secondaryID, C.properties['commonName'])

    def downloadCollections(self, force=False):
        if not self.db: self.db =  iggyrefDB(self.config)
        if not self.ftp: self.ftp = iggyrefFTP(self.properties['ftpSite'], path.join(self.tempDir, 'temp_ftp'))

        for primaryID in self.properties['selectedCollections']:
            C = baseCollection.getInstance(primaryID, self, self.ftp)
            if not C: raise Exception('Unable to instantiate Collection object for %s from %s' % (primaryID, self.source))
            self.Collections.append(C)
            self.updateSpeciesTable(C)

            self.log.debug('Collection to download: ' + primaryID)
            self.log.debug('Filenames: ' + ', '.join(map(str,C.Files)))

            for File in C.Files:
                C.setFtpFilePath(File)
                #get remote timestamp. Get checksum from any previous download of this file
                C.setRemoteTimeString(File)
                self.log.debug('Remote TimeString for file %s: %s' % (File.ftpPath, File.remoteTimeString))
                C.setRemoteChecksum(File)
                self.log.debug('Remote checksum for file %s: %s' % (File.ftpPath, File.remoteChecksum))
                File.prevChecksum = self.db.getFileAttribute(File, C, 'download_ended', 'checksum')  #checksum of file the last time it was downloaded

                #check if we need to download this file, based on timestamps and checksums
                if not force and path.isfile(File.localPath):
                    #compare stored timestring to remote timestring:
                    prevTimeString = self.db.getFileAttribute(File, C, 'download_ended', 'remoteTimeString') #remote timestamp from previous download
                    self.log.debug('TimeString of %s in DB: %s' % (File.name, prevTimeString))
                    if prevTimeString and File.remoteTimeString == prevTimeString:  #then do not download this file
                        self.log.debug('Not downloading %s since remote, local timestrings match (%s).' % (File.name, prevTimeString))
                        continue

                    #check if remote checksum has changed since previous download
                    if File.prevChecksum and File.prevChecksum == File.remoteChecksum: #then file has not changed. Update timestring in DB and do not download file.
                        self.db.writeFileRecord(File, C, status='download_ended', addendum='timestring_updated')
                        continue

                self.downloadFile(File, C)
            self.db.writeCollectionRecord(C, 'download_complete')
        self.ftp.closeFtp()

    def downloadFile(self, File, C):
        fileIsModified = True
        downloadAttempts = 0

        while True: #attempt to download file
            self.db.writeFileRecord(File, C, status='downloading')
            self.log.info('Downloading %s to %s ...' % (File.ftpPath, File.localPath))
            downloadAttempts += 1
            try:
                self.ftp.copyFile(File.ftpPath, File.localPath)  # copyFile() will attempt to download file three times, then raise an exception.
            except:
                self.db.writeFileRecord(File, C, status='download_fail')
                self.db.writeCollectionRecord(C, 'download_fail', addendum=File.name)
                errStr = "Unable to download %s: %s" % (File.ftpPath, traceback.format_exc())
                self.log.error(errStr)
                raise Exception(errStr)

            File.setLocalChecksum()
            self.log.debug('Download ended.')
            self.db.writeFileRecord(File, C, status='download_ended')

            if not File.remoteChecksum: #if no remote checksum exists, determine if file has changed based on comparison to checksum from previous download
                if File.prevChecksum and File.prevChecksum == File.localChecksum: #then file has not changed, so no postprocessing is needed. Update checksum in DB.
                    self.db.writeFileRecord(File, C, status='download_ended', addendum='checksum_updated')
                    fileIsModified = False
                break
            elif File.remoteChecksum == File.localChecksum: #download successful
                self.log.debug("Local and remote checksums for %s agree." % File.ftpPath)
                self.db.writeFileRecord(File, C, status='download_ended', addendum='remote_checksum_verified')
                break

            if downloadAttempts > 2: #report failure
                self.db.writeFileRecord(File, C, status='remote_checksum_fail', addendum='local:%s, remote:%s' % (File.localChecksum,File.remoteChecksum))
                self.db.writeCollectionRecord(C, 'download_fail', addendum=File.name)
                errStr = "Downloaded file '%s' failed remote/local checksum comparison\n" % File.ftpPath + \
                        'Local checksum: _%s_\n' % File.localChecksum + \
                        'Remote checksum: _%s_\n'  % File.remoteChecksum
                self.log.error(errStr)
                raise Exception(errStr)

        if fileIsModified:
            C.modifiedFiles.append(File)

    def postProcessCollections(self, force=False):
        if self.Collections:  #self.Collections will exist if self.downloadCollections() was run
            for C in self.Collections:
                self.postProcess(C, force=force)
        else:
            for primaryID in self.properties['selectedCollections']:
                C = baseCollection.getInstance(primaryID, self, self.ftp)
                self.postProcess(C, force=True)

        #update final repository
        self.log.info('Rsyncing %s to %s' % (self.downloadDir, self.intermedDir))
        rsync(self.downloadDir, self.intermedDir, path.join(self.logDir, 'rsync.log'))
        self.log.info('Inserting %s contents to %s' % (self.intermedDir, self.finalDir))
        insert(self.intermedDir, self.finalDir)
        if self.db: self.db.close()

    def postProcess(self, C, force=False):
        if not self.db: self.db = iggyrefDB(self.config)
        self.updateSpeciesTable(C)

        if force: #force post-postprocessing of all files
            C.modifiedFiles = C.Files
        elif not C.modifiedFiles or not C.Tasks: # then no post-processsing to be done
            self.db.writeCollectionRecord(C,'postprocessing_complete')
            return

        self.db.writeCollectionRecord(C, 'postprocessing')
        self.log.debug('Collection to post-process: ' + C.primaryID)
        self.log.debug('Modified files (all files if force=True): ' + ', '.join(map(str,C.modifiedFiles)))

        G = depGraph()
        for T in C.Tasks:
            G.addTask(T) #add task to dependency graph

        G.setExpired(C.modifiedFiles)  #mark descendants of modified files as expired.
        for File in unique(flatten([t.outFiles for t in C.Tasks])): #mark any missing output files as expired.
            if not path.exists(File.localPath):
                G.setExpired(File)

        for T in G.orderedTasks(): #run tasks, ordered by dependancy
            self.log.info('Postprocessing %s, %s, %s. Task: %s -- %s -- %s ...' % (C.primaryID, C.secondaryID, C.repo.source,
                                                                               T.taskName, ','.join(map(str,T.inFiles)), ','.join(map(str,T.outFiles))))
            for outFile in T.outFiles:
                self.db.writeFileRecord(outFile, C, status='postprocessing')
            T.run(C)
            for outFile in T.outFiles:
                self.db.writeFileRecord(outFile, C, status='postprocessing_complete')

        self.db.writeCollectionRecord(C,'postprocessing_complete')

    def update(self):
        self.downloadCollections()
        self.postProcessCollections()

    def __repr__(self):
        return '<Repo(%s)>' % (self.source)
