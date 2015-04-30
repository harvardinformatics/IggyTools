
from iggytools.iggypipeline.iggyPipeClass import IggyPipe

inFasta = '/odyssey/informatics/examples/iggy/c_elegans.smallRNA.R1.fastq.gz'

stem = '/n/regal/informatics_public/ref/ensembl/release-79/caenorhabditis_elegans/Caenorhabditis_elegans.WBcel235'
index = stem + '.dna_sm.toplevel'
gtf = stem + '.79.gtf'

pipe = IggyPipe('celegans_pipeline', pipeParentDir = '~/test')

b = pipe.add('Bowtie2')
b.input(unpaired = inFasta, index_stem = index)
b.run()

s = pipe.add('SortSam')
s.input(sam_in = b.outputs.samFile)
s.run()

c = pipe.add('Cufflinks')
c.input(aligned_reads = s.outputs.bam)
c.run()

#pipe.run()   #run all modules in pipeline
