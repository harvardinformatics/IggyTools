

fileList = [ 'active_site.dat.gz', 
             'Pfam-A.hmm.gz', 
             'Pfam-A.hmm.dat.gz' ]

fileProperties = dict()
for myfile in fileList:
    fileProperties[myfile] = dict()
    fileProperties[myfile]['ftpSubDir'] = ''

tasks = [ dict(taskName = 'unzip', inFiles = 'active_site.dat.gz', outFiles = 'active_site.dat'),
          dict(taskName = 'unzip', inFiles = 'Pfam-A.hmm.gz', outFiles = 'Pfam-A.hmm'),
          dict(taskName = 'unzip', inFiles = 'Pfam-A.hmm.dat.gz', outFiles = 'Pfam-A.hmm.dat') ]

collectionProperties = dict(
    primaryID = 'pfam',
    primaryIDtype = 'ftpSubDir',
    primaryIDregex = r'Pfam([0-9]{2,}\.[0-9]+)',
    primaryIDminVersion = 26.0,
    ftpSubDirRegex = r'Pfam([0-9]{2,}\.[0-9]+)',
    requiredFileRegex = r'Pfam-A\.hmm\.gz',
    secondaryID = '',
    collectionType = 'database',
    ftpPartialPath = 'databases/interpro',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)

