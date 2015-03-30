from iggytools.utils.util import isGZippedFile

fileList = [ 'chromFa.tar.gz',
             'uniProtToUcscGenes.txt', 
             'SNPFILE', 
             'refGene.txt.gz', 
             'ensGene.txt.gz', 
             'mrna.fa.gz', 
             'refMrna.fa.gz' ]  #files to be downloaded

fileProperties = dict()  #properties of downloaded/derived files
fileProperties['chromFa.tar.gz']         = dict( ftpSubDir = 'bigZips', checksumFile = 'md5sum.txt' )
fileProperties['refGene.txt.gz']         = dict( ftpSubDir = 'database' )
fileProperties['ensGene.txt.gz']         = dict( ftpSubDir = 'database' )
fileProperties['SNPFILE']                = dict( ftpSubDir = 'database' )
fileProperties['uniProtToUcscGenes.txt'] = dict( ftpSubDir = 'UCSCGenes' )
fileProperties['mrna.fa.gz']             = dict( ftpSubDir = 'bigZips', checksumFile = 'mrna.fa.gz.md5' )
fileProperties['refMrna.fa.gz']          = dict( ftpSubDir = 'bigZips', checksumFile = 'refMrna.fa.gz.md5' )

tasks = list()
for filename in [x for x in fileList if isGZippedFile(x)]:
    tasks.append( dict(taskName = 'unzip', inFiles = filename,  outFiles = filename[:-3]) )

tasks += [ dict(taskName = 'unzip',             inFiles = 'SNPFILE'),
           dict(taskName = 'unzip-untar-merge', inFiles = 'chromFa.tar.gz', outFiles = ['chromFa', 'chromFa.fa']),
           dict(taskName = 'txt2gtf',           inFiles = 'refGene.txt',    outFiles = 'refGene.gtf'),
           dict(taskName = 'txt2gtf',           inFiles = 'ensGene.txt',    outFiles = 'ensGene.gtf'),
           dict(taskName = 'fasta2index',       inFiles = 'chromFa.fa'),
           dict(taskName = 'fasta2index',       inFiles = 'mrna.fa'),
           dict(taskName = 'fasta2index',       inFiles = 'refMrna.fa') ]

collectionProperties = dict(
    primaryID = 'mouse',
    primaryIDregex = '^mm([0-9]{1,2})$',
    secondaryID = 'Mus_musculus',
    commonName = 'Mouse',
    collectionType = 'genome',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)

