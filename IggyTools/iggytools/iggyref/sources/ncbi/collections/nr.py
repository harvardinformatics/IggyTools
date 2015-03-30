
##
# NR blast index files
##

fileList = ['nr.' + str(x).zfill(2) + '.tar.gz' for x in range(0,32)]  #range right-endpoint not included

fileProperties = dict()
for myfile in fileList:
    fileProperties[myfile] = dict()
    fileProperties[myfile]['ftpSubDir'] = 'blast/db'
    fileProperties[myfile]['checksumFile'] = myfile + '.md5'

tasks = list()
for i, myfile in enumerate(fileList):
    tasks.append( dict(taskName = 'unzip-untar', inFiles = 'nr.' + str(i).zfill(2) + '.tar.gz') )

##
# NR fasta file
##

fileList.append('nr.gz')

fileProperties['nr.gz'] = dict()
fileProperties['nr.gz']['ftpSubDir'] = 'blast/db/FASTA'
fileProperties['nr.gz']['checksumFile'] = 'nr.gz.md5'

tasks.append( dict(taskName = 'unzip', inFiles = 'nr.gz') )

##

collectionProperties = dict(
    primaryID = 'nr',
    secondaryID = '',
    collectionType = 'database',
    aliasFileType = 'pal',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)
