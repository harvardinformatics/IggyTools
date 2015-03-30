
gzGenome = 'Caenorhabditis_elegans.PRIMARYID_PLACEHOLDER.dna_sm.toplevel.fa.gz'
gzGTF = 'Caenorhabditis_elegans.PRIMARYID_PLACEHOLDER.RELEASE_PLACEHOLDER.gtf.gz'
gzCDS = 'Caenorhabditis_elegans.PRIMARYID_PLACEHOLDER.cds.all.fa.gz'

codingSequence = gzCDS[:-3]
genome = gzGenome[:-3]

fileList = [gzGenome, gzGTF, gzCDS]  #files to be downloaded

fileProperties = dict()  
fileProperties[gzGenome] = dict( ftpSubDir = 'fasta/caenorhabditis_elegans/dna' )
fileProperties[gzGTF] = dict( ftpSubDir = 'gtf/caenorhabditis_elegans' )
fileProperties[gzCDS] = dict( ftpSubDir = 'fasta/caenorhabditis_elegans/cds' )

tasks = list()
for filename in fileList:
    fileProperties[filename]['checksumFile'] = 'CHECKSUMS'
    fileProperties[filename]['checksumType'] = 'sum' 
    tasks.append( dict(taskName = 'unzip', inFiles = filename, outFiles = filename[:-3]) )

tasks.append( dict(taskName = 'fasta2index', inFiles = genome ) )
tasks.append( dict(taskName = 'fasta2index', inFiles = codingSequence ) )

collectionProperties = dict(
    primaryID = 'worm',
    secondaryID = 'caenorhabditis_elegans',
    commonName = 'Worm',
    collectionType = 'genome',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)
