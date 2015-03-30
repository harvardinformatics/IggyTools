
gzGenome = 'Saccharomyces_cerevisiae.PRIMARYID_PLACEHOLDER.dna_sm.toplevel.fa.gz'
gzGTF = 'Saccharomyces_cerevisiae.PRIMARYID_PLACEHOLDER.RELEASE_PLACEHOLDER.gtf.gz'
gzCDS = 'Saccharomyces_cerevisiae.PRIMARYID_PLACEHOLDER.cds.all.fa.gz'

codingSequence = gzCDS[:-3]
genome = gzGenome[:-3]

fileList = [gzGenome, gzGTF, gzCDS]  #files to be downloaded

fileProperties = dict()
fileProperties[gzGenome] = dict( ftpSubDir = 'fasta/saccharomyces_cerevisiae/dna' )
fileProperties[gzGTF] = dict( ftpSubDir = 'gtf/saccharomyces_cerevisiae' )
fileProperties[gzCDS] = dict( ftpSubDir = 'fasta/saccharomyces_cerevisiae/cds' )

tasks = list()
for filename in fileList:
    fileProperties[filename]['checksumFile'] = 'CHECKSUMS'
    fileProperties[filename]['checksumType'] = 'sum' 
    tasks.append( dict(taskName = 'unzip', inFiles = filename, outFiles = filename[:-3]) )

tasks.append( dict(taskName = 'fasta2index', inFiles = genome ) )
tasks.append( dict(taskName = 'fasta2index', inFiles = codingSequence ) )

collectionProperties = dict(
    primaryID = 'yeast',
    secondaryID = 'saccharomyces_cerevisiae',
    commonName = 'Yeast',
    collectionType = 'genome',
    fileList = fileList,
    fileProperties = fileProperties,
    tasks = tasks
)

