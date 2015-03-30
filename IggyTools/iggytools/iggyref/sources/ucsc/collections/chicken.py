from iggytools.utils.util import isGZippedFile

fileList = [ 'GENOME_FASTA_GZ',
             'SNPFILE', 
             'refGene.txt.gz', 
             'ensGene.txt.gz', 
             'mrna.fa.gz', 
             'refMrna.fa.gz' ]  #files to be downloaded

fileProperties = dict() 
fileProperties['GENOME_FASTA_GZ'] = dict( ftpSubDir = 'bigZips', checksumFile = 'md5sum.txt' )
fileProperties['SNPFILE']         = dict( ftpSubDir = 'database' )
fileProperties['refGene.txt.gz']  = dict( ftpSubDir = 'database' )
fileProperties['ensGene.txt.gz']  = dict( ftpSubDir = 'database' )
fileProperties['mrna.fa.gz']      = dict( ftpSubDir = 'bigZips', checksumFile = 'mrna.fa.gz.md5' )
fileProperties['refMrna.fa.gz']   = dict( ftpSubDir = 'bigZips', checksumFile = 'refMrna.fa.gz.md5' )

tasks = list()
for filename in [x for x in fileList if isGZippedFile(x)]:
    tasks.append( dict(taskName = 'unzip', inFiles = filename,  outFiles = filename[:-3]) )

tasks += [ dict(taskName = 'unzip',       inFiles = 'GENOME_FASTA_GZ'),
           dict(taskName = 'unzip',       inFiles = 'SNPFILE'),
           dict(taskName = 'txt2gtf',     inFiles = 'refGene.txt', outFiles = 'refGene.gtf'),
           dict(taskName = 'txt2gtf',     inFiles = 'ensGene.txt', outFiles = 'ensGene.gtf'),
           dict(taskName = 'fasta2index', inFiles = 'GENOME_FASTA'),
           dict(taskName = 'fasta2index', inFiles = 'mrna.fa'),
           dict(taskName = 'fasta2index', inFiles = 'refMrna.fa') ]

collectionProperties = dict(
    primaryID = 'chicken',
    primaryIDregex = '^galGal([0-9]{1,2})$',
    secondaryID = 'Gallus_gallus',
    commonName = 'Chicken',
    collectionType = 'genome',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)

