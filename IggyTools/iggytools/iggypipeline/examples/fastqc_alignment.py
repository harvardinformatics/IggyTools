from iggytools.iggypipeline.iggyPipeClass import IggyPipe

myfastq = '/n/informatics/iggy/IggyTools/iggytools/iggypipeline/test/samp1.fastq'
index = '/n/regal/informatics_public/ref/ensembl/release-79/homo_sapiens/Homo_sapiens.GRCh38.cds.all'

pipe = IggyPipe('Analysis1', pipeDir = '~/iggypipe_test/')  #create a new pipeline
pipe.help()                       #print pipeline parameters and methods

fastqc = pipe.add('Fastqc')       #add fastqc module
fastqc.help()                     #print fastqc input paraemtes, methods and default settings
fastqc.input(inFiles = myfastq)   #set input parameters
fastqc.view()                     #view current input settings

bowtie = pipe.add('Bowtie2')      #add bowtie module
bowtie.input(unpaired = myfastq, index_stem = index)   #set inputs

pipe.view()                       #view all module, slurm settings

pipe.run()                        # run locally
pipe.srun()                       # run on slurm
