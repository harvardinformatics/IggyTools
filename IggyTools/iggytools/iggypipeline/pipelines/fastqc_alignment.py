
from iggytools.iggypipeline.iggyPipeClass import IggyPipe

myfastq = '/n/informatics/IggyTools/iggytools/iggypipeline/test/samp1.fastq'
index = '/n/regal/informatics_public/ref/ensembl/release-79/homo_sapiens/Homo_sapiens.GRCh38.cds.all'

pipe = IggyPipe('Analysis1', pipeDir = '/n/informatics/IggyTools/iggytools/iggypipeline/test')
pipe.help()

#add fastqc module
fastqc = pipe.add('Fastqc')
fastqc.help()
fastqc.input(inFiles = myfastq)  
fastqc.view()

#add bowtie module
bowtie = pipe.add('Bowtie2')
bowtie.input(unpaired = myfastq, index_stem = index)

#view all module, slurm settings
pipe.view()

pipe.run()  # run locally
pipe.srun()  # run on slurm

