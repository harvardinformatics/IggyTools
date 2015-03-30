from iggytools.utils.util import isGZippedFile

fileList = [ 'active_site.dat.gz', 
             'Pfam-A.hmm.gz', 
             'Pfam-A.hmm.dat.gz' ]  # files to be downloaded

fileProperties = dict()
for myfile in fileList:
    fileProperties[myfile] = dict()
    fileProperties[myfile]['ftpSubDir'] = ''

tasks = list()
for filename in [x for x in fileList if isGZippedFile(x)]:
    tasks.append( dict(taskName = 'unzip', inFiles = filename) )

collectionProperties = dict(
    primaryID = 'pfam',
    primaryIDtype = 'ftpSubDir',
    primaryIDregex = r'Pfam([0-9]{2,}\.[0-9]+)',
    primaryIDminVersion = 26.0,
    ftpSubDirRegex = r'Pfam([0-9]{2,}\.[0-9]+)',
    requiredFileRegex = r'Pfam-A\.hmm\.gz',
    secondaryID = '',
    collectionType = 'database',
    ftpPartialPath = 'databases/Pfam/releases',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)

