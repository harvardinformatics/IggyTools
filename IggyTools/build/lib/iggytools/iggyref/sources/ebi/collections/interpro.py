

fileList = [ 'ParentChildTreeFile.txt',
             'entry.list',
             'feature.xml.gz',
             'interpro.xml.gz',
             'interpro2go',
             'match_complete.xml.gz',
             'names.dat',
             'protein2ipr.dat.gz',
             'release_notes.txt',
             'short_names.dat' ]

fileProperties = dict()
for myfile in fileList:
    fileProperties[myfile] = dict()
    fileProperties[myfile]['ftpSubDir'] = ''

tasks = [ dict(taskName = 'unzip', inFiles = 'feature.xml.gz', outFiles = 'feature.xml'),
          dict(taskName = 'unzip', inFiles = 'interpro.xml.gz', outFiles = 'interpro.xml'),
          dict(taskName = 'unzip', inFiles = 'match_complete.xml.gz', outFiles = 'match_complete.xml'),
          dict(taskName = 'unzip', inFiles = 'protein2ipr.dat.gz', outFiles = 'protein2ipr.dat') ]

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


