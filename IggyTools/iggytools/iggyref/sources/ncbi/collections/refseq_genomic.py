
fileList = ['refseq_genomic.' + str(x).zfill(2) + '.tar.gz' for x in range(0,154)]  #range right-endpoint not included

fileProperties = dict()
for myfile in fileList:
    fileProperties[myfile] = dict()
    fileProperties[myfile]['ftpSubDir'] = 'blast/db'
    fileProperties[myfile]['checksumFile'] = myfile + '.md5'

tasks = list()
for i, myfile in enumerate(fileList):
    tasks.append( dict(taskName = 'unzip-untar', inFiles = 'refseq_genomic.' + str(i).zfill(2) + '.tar.gz') )


collectionProperties = dict(
    primaryID = 'refseq_genomic',
    secondaryID = '',
    collectionType = 'database',
    aliasFileType = 'nal',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)

