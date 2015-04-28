import os.path as path
import types
from iggytools.iggyref.baseCollectionClass import baseCollection
from iggytools.utils.util import parse_NCBI_aliasFile, extractFromTar


# ncbi Collection class

class ncbiCollection(baseCollection):

    def __init__(self, primaryID, repo, ftpConn = None):

        collMod = __import__('iggytools.iggyref.sources.%s.collections.%s' % (repo.source, primaryID),fromlist=[primaryID])
        collProp = getattr(collMod,'collectionProperties')
        
        if collProp['aliasFileType']:
            aliasFilename = '%s.%s' % (primaryID, collProp['aliasFileType'])
            dbFile_ftpSubDir = collProp['dbFileProp']['ftpSubDir']
        
            if not ftpConn:  #look at local pal/nal flie for file list
                aliasFile = path.join(repo.downloadDir, aliasFilename)

            else: #get remote pal/nal file

                firstDBFilename = '%s.00.tar.gz' % primaryID
                firstDBFile_remote = path.join( dbFile_ftpSubDir, firstDBFilename )
                firstDBFile_local = path.join( repo.tempDir, firstDBFilename )
                ftpConn.copyFile(firstDBFile_remote, firstDBFile_local)            

                extractFromTar(firstDBFile_local, aliasFilename, repo.tempDir)
                aliasFile = path.join(repo.tempDir, aliasFilename)

                
            #set collection fileList from .pal/.nal alias file
            dbFiles = ['%s.tar.gz' % x for x in parse_NCBI_aliasFile(aliasFile)]
            collProp['fileList'] += dbFiles

            for filename in dbFiles:

                #set file properties
                collProp['fileProperties'][filename]                  = dict()
                collProp['fileProperties'][filename]['ftpSubDir']     = dbFile_ftpSubDir
                collProp['fileProperties'][filename]['checksumFile']  = '%s.md5' % filename

                #add task 
                collProp['tasks'].append( dict(taskName = 'unzip-untar', inFiles = filename) )

        baseCollection.__init__(self, primaryID, repo, ftpConn = ftpConn, collectionProperties = collProp)

        self.setLocalDirs()
        self.collectionSetup()


    def setLocalFilePath(self, File):
        if not File.localPath:
            File.localPath = path.join(self.downloadDir, File.name)


    def setFtpFilePath(self, File):
        File.ftpPath = path.join(File.ftpSubDir, File.name)


    def setChecksumFtpFilePath(self, File):
        if not File.checksumFile: raise Exception('File.checksumFile must be set')
        File.checksumFtpPath = path.join(File.ftpSubDir, File.checksumFile)

