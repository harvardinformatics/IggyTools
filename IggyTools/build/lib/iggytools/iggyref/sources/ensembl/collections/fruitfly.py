
gzGenome = 'Drosophila_melanogaster.PRIMARYID_PLACEHOLDER.dna_sm.toplevel.fa.gz'
gzGTF = 'Drosophila_melanogaster.PRIMARYID_PLACEHOLDER.RELEASE_PLACEHOLDER.gtf.gz'
gzCDS = 'Drosophila_melanogaster.PRIMARYID_PLACEHOLDER.cds.all.fa.gz'

codingSequence = gzCDS[:-3]
genome = gzGenome[:-3]

fileList = [gzGenome, gzGTF, gzCDS] #files to be downloaded

fileProperties = dict()  #properies of downloaded/derived files
fileProperties[gzGenome] = dict( ftpSubDir = 'fasta/drosophila_melanogaster/dna' )
fileProperties[gzGTF] = dict( ftpSubDir = 'gtf/drosophila_melanogaster' )
fileProperties[gzCDS] = dict( ftpSubDir = 'fasta/drosophila_melanogaster/cds' )

tasks = list()
for filename in fileList:
    fileProperties[filename]['checksumFile'] = 'CHECKSUMS'
    fileProperties[filename]['checksumType'] = 'sum' 
    tasks.append( dict(taskName = 'unzip', 
                       inFiles = filename,
                       outFiles = filename[:-3]) )

tasks.append( dict(taskName = 'fasta2index',
                  inFiles = genome ) )
tasks.append( dict(taskName = 'fasta2index',
                  inFiles = codingSequence ) )

collectionProperties = dict(
    primaryID = 'fruitfly',
    secondaryID = 'drosophila_melanogaster',
    commonName = 'Fruit fly',
    collectionType = 'genome',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)

