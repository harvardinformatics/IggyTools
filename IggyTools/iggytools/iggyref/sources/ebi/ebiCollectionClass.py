import os.path as path
import os, types, re, glob, ftplib, posixpath
from iggytools.iggyref.baseCollectionClass import baseCollection

# ebi Collection class

def getVersion(name, regex):
    nameMatch = re.match(regex, name)
    if nameMatch:
        verString = nameMatch.group(1)
        if '.' in verString:
            return float(verString)
        else:
            return int(verString)
    else:
        return -1

def getLatestItem_local(localSearchDir, regex, minVersion):
    ver = float(minVersion)
    latest = ''
    dirList = [x for x in os.listdir(localSearchDir) if path.isdir(path.join(localSearchDir,x))]
    for item in dirList:
        itemVersion = getVersion(item, regex)
        if itemVersion > ver:
                latest = item
                ver = itemVersion
    if not latest:
        raise Exception('No item matching %s found in %s' % (regex, localSearchDir))
    return latest

def getLatestItem_remote(ftpSearchDir, itemRegex, minVersion, ftpConn, requiredFileRegex):
    ver = float(minVersion)
    latest = ''
    try:
        itemList = ftpConn.getDirContents(ftpSearchDir)
    except:
        raise Exception('Unable to get dir contents of %s' % (ftpSearchDir))
    for item in itemList:
        itemVersion = getVersion(item, itemRegex)
        if itemVersion == -1:
            continue  #no match
        elif itemVersion > ver:
            try:
                if len(ftpConn.getDirContents(posixpath.join(ftpSearchDir,item), requiredFileRegex)) == 0:
                    continue #item does not contain required file
            except ftplib.error_perm:
                continue #item was a file, not a directory 
            latest = item
            ver = itemVersion
    if not latest:
        raise Exception('No latest item found in %s' % ftpSearchDir)
    return latest


class ebiCollection(baseCollection):
    def __init__(self, primaryID, repo, ftpConn = None):
        baseCollection.__init__(self, primaryID, repo, ftpConn)
        self.ftpPartialPath = self.properties['ftpPartialPath']

        # Find latest version in order to set primaryID

        if ftpConn: #look at ftp site to deteremine latest version
            ftpSearchDir = posixpath.join(self.repo.properties['ftpPath'], self.properties['ftpPartialPath'])
            latestSubDir = getLatestItem_remote(ftpSearchDir, self.properties['ftpSubDirRegex'], self.properties['primaryIDminVersion'], ftpConn, self.properties['requiredFileRegex'])
            primaryIDtype = self.properties['primaryIDtype']
            if primaryIDtype == 'ftpSubDir':
                self.primaryID = latestSubDir
            elif primaryIDtype == 'compound':
                self.primaryID = self.primaryID + latestSubDir
            else:
                raise Exception('Unrecognized primaryIDtype: %s' % primaryIDtype)
            self.collectionFtpPath = posixpath.join(ftpSearchDir, latestSubDir)

        else:  #look in local filesystem to determine latest version
            self.primaryID = getLatestItem_local(self.repo.downloadDir, self.properties['primaryIDregex'], self.properties['primaryIDminVersion'])

        self.setLocalDirs()
        self.collectionSetup()

    def setLocalFilePath(self, File):
        if not File.localPath:
            File.localPath = path.join(self.downloadDir, File.name)

    def setFtpFilePath(self, File):
        File.ftpPath = posixpath.join(self.collectionFtpPath, File.ftpSubDir, File.name)

    def setChecksumFtpFilePath(self, File):
        if not File.checksumFile: raise Exception('File.checksumFile must be set')
        File.checksumFtpPath = posixpath.join(self.collectionFtpPath, File.ftpSubDir, File.checksumFile)

