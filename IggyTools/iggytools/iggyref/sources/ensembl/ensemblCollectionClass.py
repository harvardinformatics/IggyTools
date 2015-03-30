import os.path as path
import os, types, re, glob, ftplib, posixpath
from iggytools.iggyref.baseCollectionClass import baseCollection
from iggytools.utils.util import flatlist

# ensembl Collection class

def releaseMatch(name, minVersion = None):
    match = re.match(r'release-([0-9]+)$', name)
    if not match:
        return -1

    version = float(match.group(1))

    if minVersion and version < minVersion:
        return -1
    else:
        return version


def getPrimaryID(fileList, regex, searchDir): #determine primaryID from filename

    if len(fileList) == 0:
        raise Exception('Found no file with which to determine primaryID. searchDir: %s' % (searchDir))

    return re.search(r'\.([^.]+)' + regex,fileList[0]).group(1)


def getSearchPattern(fileList):

    pattern = dict()

    if sum([bool(re.match(r'.+\.dna_sm\.primary_assembly\.fa\.gz', x)) for x in fileList]) > 0:
        pattern['glob'] = '*.dna_sm.primary_assembly.fa.gz'
        pattern['regex'] = r'\.dna_sm\.primary_assembly\.fa\.gz'

    elif sum([bool(re.match(r'.+\.dna_sm\.toplevel\.fa\.gz', x)) for x in fileList]) > 0:
        pattern['glob'] = '*.dna_sm.toplevel.fa.gz'
        pattern['regex'] = r'\.dna_sm\.toplevel\.fa\.gz'

    else: 
        raise Exception('Unable to deteremine search string for file list: %s' % ', '.join(fileList))

    return pattern



class ensemblCollection(baseCollection):

    def __init__(self, primaryID, repo, ftpConn = None):
        baseCollection.__init__(self, primaryID, repo, ftpConn)
                        
        #set primaryID and localCollectionDir
        pattern = getSearchPattern(self.properties['fileList'])
        if not ftpConn:  #look in local file system for top-level release dir
            localSearchDir = self.repo.downloadDir
            dirList = [x for x in os.listdir(localSearchDir) if path.isdir(path.join(localSearchDir,x))] #***
            version = -1
            releaseDir = ''
            for mydir in dirList:
                ver = releaseMatch(mydir, minVersion = 77)
                if ver > version:
                    releaseDir = mydir
                    version = ver
            if not releaseDir:
                raise Exception('No release dir found in ensembl repository directory %s' % self.repo.downloadDir)

            self.downloadDir = path.join(self.repo.downloadDir, releaseDir, self.secondaryID)
            files = glob.glob(path.join(self.downloadDir, pattern['glob']))
            self.primaryID = getPrimaryID(files, pattern['regex'], self.downloadDir)

        else:  #look at the collection's ftp path to determine release dir

            #find latest release directory
            releaseDir = ''
            version = -1
            ftpSearchDir = self.repo.properties['ftpPath']
            itemList = ftpConn.getDirContents(ftpSearchDir)
            for item in itemList:  
                ver = releaseMatch(item, minVersion = 77)
                if ver == -1: 
                    continue
                try:
                    if len(ftpConn.getDirContents(posixpath.join(ftpSearchDir,item), 'fasta')) == 0:  
                        continue #item does not contain fasta directory
                except ftplib.error_perm:
                    continue #item was a file, not a directory
                if ver > version:
                    version = ver
                    releaseDir = item
            if not releaseDir:
                raise Exception('releaseDir not found in %s' % ftpSearchDir)
            self.collectionFtpPath = posixpath.join(ftpSearchDir, releaseDir)

            pathMatch = re.match('.*/(release-([0-9]+))', self.collectionFtpPath)
            releaseDir = pathMatch.group(1)
            version = pathMatch.group(2)
            self.downloadDir = path.join(self.repo.downloadDir, releaseDir, self.secondaryID)

            ftpSearchDir = posixpath.join(self.collectionFtpPath,'fasta',self.secondaryID.lower(),'dna')
            files = ftpConn.getDirContents(ftpSearchDir, pattern['regex'])
            self.primaryID = getPrimaryID(files, pattern['regex'], ftpSearchDir)

        # Map filename placeholders to versioned filenames
        fileMap = dict()
        rawFilenames = self.getRawFilenames()
        for rawName in rawFilenames:
            parts = rawName.split('PRIMARYID_PLACEHOLDER')
            tempName = self.primaryID.join(parts)
            parts = tempName.split('RELEASE_PLACEHOLDER')
            fileMap[rawName] = str(int(version)).join(parts)

        self.finalDir = path.join(self.repo.finalDir, releaseDir, self.secondaryID)
        self.collectionSetup(fileMap)


    def setLocalFilePath(self, File):
        if not File.localPath:
            File.localPath = path.join(self.downloadDir, File.name)


    def setFtpFilePath(self, File):
        File.ftpPath = posixpath.join(self.collectionFtpPath, File.ftpSubDir, File.name)


    def setChecksumFtpFilePath(self, File):
        if not File.checksumFile: raise Exception('File.checksumFile must be set')
        File.checksumFtpPath = posixpath.join(self.collectionFtpPath, File.ftpSubDir, File.checksumFile)
