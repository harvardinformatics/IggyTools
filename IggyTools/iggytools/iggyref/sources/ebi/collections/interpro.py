from iggytools.utils.util import isGZippedFile

fileList = [ 'ParentChildTreeFile.txt',
             'entry.list',
             'feature.xml.gz',
             'interpro.xml.gz',
             'interpro2go',
             'match_complete.xml.gz',
             'names.dat',
             'protein2ipr.dat.gz',
             'release_notes.txt',
             'short_names.dat' ]  # files to be downloaded

fileProperties = dict()
for myfile in fileList:
    fileProperties[myfile] = dict()
    fileProperties[myfile]['ftpSubDir'] = ''

tasks = list()
for filename in [x for x in fileList if isGZippedFile(x)]:
    tasks.append( dict(taskName = 'unzip', inFiles = filename) )

collectionProperties = dict(
    primaryID = 'interpro',
    primaryIDtype = 'compound',
    primaryIDregex = r'interpro([0-9]{2,}\.[0-9]+)',
    primaryIDminVersion = 48.0,
    ftpSubDirRegex = r'([0-9]{2,}\.[0-9]+)',
    requiredFileRegex = r'interpro\.xml\.gz',
    secondaryID = '',
    collectionType = 'database',
    ftpPartialPath = 'databases/interpro',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)


