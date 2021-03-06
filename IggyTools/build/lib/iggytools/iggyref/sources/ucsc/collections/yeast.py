import re

fileList = [ 'chromFa.tar.gz',   #files to be downloaded
             'ensGene.txt.gz', 
             'mrna.fa.gz' ]

fileProperties = dict()  #properties of downloaded/derived files
fileProperties['chromFa.tar.gz']         = dict( ftpSubDir = 'bigZips', checksumFile = 'md5sum.txt' )
fileProperties['ensGene.txt.gz']         = dict( ftpSubDir = 'database' )
fileProperties['mrna.fa.gz']             = dict( ftpSubDir = 'bigZips', checksumFile = 'mrna.fa.gz.md5' )

tasks = list()
for filename in [x for x in fileList if re.search(r'(?<!\.tar)\.gz$', x, re.IGNORECASE)]:
    tasks.append( dict(taskName = 'unzip', inFiles = filename,  outFiles = filename[:-3]) )

tasks += [ dict(taskName = 'unzip-untar-merge', inFiles = 'chromFa.tar.gz',              outFiles = ['chromFa', 'chromFa.fa']),
           dict(taskName = 'txt2gtf',           inFiles = ['ensGene.txt', 'chromFa.fa'], outFiles = 'ensGene.gtf'),
           dict(taskName = 'fasta2index',       inFiles = 'chromFa.fa'),
           dict(taskName = 'fasta2index',       inFiles = 'mrna.fa') ]

collectionProperties = dict(
    primaryID = 'yeast',
    primaryIDregex = '^sacCer([0-9]+)',
    secondaryID = 'Saccharomyces_cerevisiae',
    commonName = 'Yeast',
    collectionType = 'genome',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)

