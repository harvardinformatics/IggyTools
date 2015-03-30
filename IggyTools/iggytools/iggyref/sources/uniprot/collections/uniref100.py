
fileList = ['uniref100.fasta.gz', 'uniref100.release_note', 'uniref100.xml.gz']

fileProperties = dict()
for myfile in fileList:
    fileProperties[myfile] = dict()
    fileProperties[myfile]['ftpSubDir'] = 'uniref/uniref100'

tasks = [ dict(taskName = 'unzip', inFiles = 'uniref100.fasta.gz'),
          dict(taskName = 'unzip', inFiles = 'uniref100.xml.gz') ]

collectionProperties = dict(
    primaryID = 'uniref100',
    secondaryID = '',
    collectionType = 'database',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)
