
gzGenome = 'Homo_sapiens.PRIMARYID_PLACEHOLDER.dna_sm.primary_assembly.fa.gz'
gzGTF = 'Homo_sapiens.PRIMARYID_PLACEHOLDER.RELEASE_PLACEHOLDER.gtf.gz'
gzCDS = 'Homo_sapiens.PRIMARYID_PLACEHOLDER.cds.all.fa.gz'

codingSequence = gzCDS[:-3]
genome = gzGenome[:-3]

fileList = [gzGenome, gzGTF, gzCDS]  #files to be downloaded

fileProperties = dict()  
fileProperties[gzGenome] = dict( ftpSubDir = 'fasta/homo_sapiens/dna' )
fileProperties[gzGTF] = dict( ftpSubDir = 'gtf/homo_sapiens' )
fileProperties[gzCDS] = dict( ftpSubDir = 'fasta/homo_sapiens/cds' )

tasks = list()
for filename in fileList:
    fileProperties[filename]['checksumFile'] = 'CHECKSUMS'
    fileProperties[filename]['checksumType'] = 'sum' 
    tasks.append( dict(taskName = 'unzip', inFiles = filename, outFiles = filename[:-3]) )

tasks.append( dict(taskName = 'fasta2index', inFiles = genome ) )
tasks.append( dict(taskName = 'fasta2index', inFiles = codingSequence ) )


collectionProperties = dict(
    primaryID = 'human',
    secondaryID = 'homo_sapiens',
    commonName = 'Human',
    collectionType = 'genome',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)
