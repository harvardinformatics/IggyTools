from iggytools.utils.util import isGZippedFile

fileList = [ 'chromFa.tar.gz',
             'refGene.txt.gz', 
             'ensGene.txt.gz', 
             'mrna.fa.gz', 
             'refMrna.fa.gz' ]  #files to be downloaded

fileProperties = dict()  
fileProperties['chromFa.tar.gz']         = dict( ftpSubDir = 'bigZips', checksumFile = 'md5sum.txt' )
fileProperties['refGene.txt.gz']         = dict( ftpSubDir = 'database' )
fileProperties['ensGene.txt.gz']         = dict( ftpSubDir = 'database' )
fileProperties['mrna.fa.gz']             = dict( ftpSubDir = 'bigZips', checksumFile = 'mrna.fa.gz.md5' )
fileProperties['refMrna.fa.gz']          = dict( ftpSubDir = 'bigZips', checksumFile = 'refMrna.fa.gz.md5' )

tasks = list()
for filename in [x for x in fileList if isGZippedFile(x)]:
    tasks.append( dict(taskName = 'unzip', inFiles = filename) )

tasks += [ dict(taskName = 'unzip-untar-merge', inFiles = 'chromFa.tar.gz', outFiles = ['chromFa', 'chromFa.fa']),
           dict(taskName = 'txt2gtf',           inFiles = 'refGene.txt',    outFiles = 'refGene.gtf'),
           dict(taskName = 'txt2gtf',           inFiles = 'ensGene.txt',    outFiles = 'ensGene.gtf'),
           dict(taskName = 'fasta2index',       inFiles = 'chromFa.fa'),
           dict(taskName = 'fasta2index',       inFiles = 'mrna.fa'),
           dict(taskName = 'fasta2index',       inFiles = 'refMrna.fa') ]

collectionProperties = dict(
    primaryID = 'galGal3',
    secondaryID = 'Gallus_gallus',
    commonName = 'Chicken',
    collectionType = 'genome',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)


