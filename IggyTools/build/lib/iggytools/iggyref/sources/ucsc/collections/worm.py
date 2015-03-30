
import re

fileList = [ 'chromFa.tar.gz',   #files to be downloaded
             'refGene.txt.gz', 
             'ensGene.txt.gz', 
             'mrna.fa.gz', 
             'refMrna.fa.gz' ]  

fileProperties = dict()  #properties of downloaded/derived files
fileProperties['chromFa.tar.gz']         = dict( ftpSubDir = 'bigZips', checksumFile = 'md5sum.txt' )
fileProperties['refGene.txt.gz']         = dict( ftpSubDir = 'database' )
fileProperties['ensGene.txt.gz']         = dict( ftpSubDir = 'database' )
fileProperties['mrna.fa.gz']             = dict( ftpSubDir = 'bigZips', checksumFile = 'mrna.fa.gz.md5' )
fileProperties['refMrna.fa.gz']          = dict( ftpSubDir = 'bigZips', checksumFile = 'refMrna.fa.gz.md5' )

tasks = list()
for filename in [x for x in fileList if re.search(r'(?<!\.tar)\.gz$', x, re.IGNORECASE)]:
    tasks.append( dict(taskName = 'unzip', inFiles = filename,  outFiles = filename[:-3]) )

tasks += [ dict(taskName = 'unzip-untar-merge', inFiles = 'chromFa.tar.gz',              outFiles = ['chromFa', 'chromFa.fa']),
           dict(taskName = 'txt2gtf',           inFiles = ['refGene.txt', 'chromFa.fa'], outFiles = 'refGene.gtf'),
           dict(taskName = 'txt2gtf',           inFiles = ['ensGene.txt', 'chromFa.fa'], outFiles = 'ensGene.gtf'),
           dict(taskName = 'fasta2index',       inFiles = 'chromFa.fa'),
           dict(taskName = 'fasta2index',       inFiles = 'mrna.fa'),
           dict(taskName = 'fasta2index',       inFiles = 'refMrna.fa') ]

collectionProperties = dict(
    primaryID = 'worm',
    primaryIDregex = '^ce([0-9]{2,})',
    secondaryID = 'Caenorhabditis_elegans',
    commonName = 'Worm',
    collectionType = 'genome',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)


