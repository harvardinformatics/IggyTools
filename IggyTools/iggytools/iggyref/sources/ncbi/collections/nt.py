

##
# NT fasta file
##

fileList = ['nt.gz']

fileProperties = dict()
fileProperties['nt.gz'] = dict()
fileProperties['nt.gz']['ftpSubDir'] = 'blast/db/FASTA'
fileProperties['nt.gz']['checksumFile'] = 'nt.gz.md5'

tasks = [ dict(taskName = 'unzip', inFiles = 'nt.gz', outFiles = 'nt.fa') ]

##
# NT db file properties
##

dbFileProp = dict()
dbFileProp['ftpSubDir'] = 'blast/db'

collectionProperties = dict(
    primaryID = 'nt',
    secondaryID = '',
    collectionType = 'database',
    aliasFileType = 'nal',
    fileList = fileList,
    fileProperties = fileProperties,
    dbFileProp = dbFileProp,
    tasks = tasks
)
