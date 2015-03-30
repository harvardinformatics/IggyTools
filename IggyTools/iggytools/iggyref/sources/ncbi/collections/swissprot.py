
fileList = ['swissprot.tar.gz']

fileProperties = dict()
for myfile in fileList:
    fileProperties[myfile] = dict()
    fileProperties[myfile]['ftpSubDir'] = 'blast/db'
    fileProperties[myfile]['checksumFile'] = myfile + '.md5'

tasks = list()
for myfile in fileList:
    tasks.append( dict(taskName = 'unzip-untar', inFiles = myfile) )

collectionProperties = dict(
    primaryID = 'swissprot',
    secondaryID = '',
    collectionType = 'database',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)


