
##
# NR fasta file
##

fileList = ['nr.gz']

fileProperties = dict()
fileProperties['nr.gz'] = dict()
fileProperties['nr.gz']['ftpSubDir'] = 'blast/db/FASTA'
fileProperties['nr.gz']['checksumFile'] = 'nr.gz.md5'

tasks = [ dict(taskName = 'unzip', inFiles = 'nr.gz', outFiles = 'nr.fa') ]

##
# NR db file properties
##

dbFileProp = dict()
dbFileProp['ftpSubDir'] = 'blast/db'

collectionProperties = dict(
    primaryID = 'nr',
    secondaryID = '',
    collectionType = 'database',
    aliasFileType = 'pal',
    fileList = fileList,
    fileProperties = fileProperties,
    dbFileProp = dbFileProp,
    tasks = tasks
)
