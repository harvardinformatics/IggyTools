
##
# NT blast index files
##

fileList = ['nt.' + str(x).zfill(2) + '.tar.gz' for x in range(0,28)]  #range right-endpoint not included

fileProperties = dict()
for myfile in fileList:
    fileProperties[myfile] = dict()
    fileProperties[myfile]['ftpSubDir'] = 'blast/db'
    fileProperties[myfile]['checksumFile'] = myfile + '.md5'

tasks = list()
for i, myfile in enumerate(fileList):
    tasks.append( dict(taskName = 'unzip-untar', inFiles = 'nt.' + str(i).zfill(2) + '.tar.gz') )

##
# NR fasta file
##

fileList.append('nt.gz')

fileProperties['nt.gz'] = dict()
fileProperties['nt.gz']['ftpSubDir'] = 'blast/db/FASTA'
fileProperties['nt.gz']['checksumFile'] = 'nt.gz.md5'

tasks.append( dict(taskName = 'unzip', inFiles = 'nt.gz') )


collectionProperties = dict(
    primaryID = 'nt',
    secondaryID = '',
    collectionType = 'database',
    aliasFileType = 'nal',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)


