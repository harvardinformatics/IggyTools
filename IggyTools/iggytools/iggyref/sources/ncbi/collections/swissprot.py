
##
# Swissprot fasta file, db file
##

fileList = ['swissprot.gz', 'swissprot.tar.gz']

fileProperties = dict()

fileProperties['swissprot.gz'] = dict()
fileProperties['swissprot.gz']['ftpSubDir'] = 'blast/db/FASTA'
fileProperties['swissprot.gz']['checksumFile'] = 'swissprot.gz.md5'


fileProperties['swissprot.tar.gz'] = dict()
fileProperties['swissprot.tar.gz']['ftpSubDir'] = 'blast/db'
fileProperties['swissprot.tar.gz']['checksumFile'] = 'swissprot.tar.gz.md5'


tasks = [ dict(taskName = 'unzip', inFiles = 'swissprot.gz', outFiles = 'swissprot.fa'),
          dict(taskName = 'unzip-untar', inFiles = 'swissprot.tar.gz') ]


collectionProperties = dict(
    primaryID = 'swissprot',
    secondaryID = '',
    collectionType = 'database',
    aliasFileType = None,
    fileList = fileList,
    fileProperties = fileProperties,
    dbFileProp = None,
    tasks = tasks
)


