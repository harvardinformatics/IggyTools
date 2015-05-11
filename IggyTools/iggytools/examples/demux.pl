


#--------------------------------------------------
# Examples of demultiplexing from within python:
#--------------------------------------------------


# Create a new output directory by adding a suffix to the run name. Suppress adapter trimming (only applies to NextSeq runs).

from iggytools.iggyseq.runClasses import IlluminaNextGen
b = IlluminaNextGen.getInstance('150423_NS500422_0114_AH5YKCBGXX', verbose = True, suffix = '_2', suppressAdapterTrimming = True)
b.processRun()


# Demultiplex lanes 2-4 only.

from iggytools.iggyseq.runClasses import IlluminaNextGen
b = IlluminaNextGen.getInstance('150326_SN343_0511_BC6NB6ACXX', verbose = True, suffix = '_2', lanesStr='2,3,4')  #a run with no index, no samples
b.processRun()


# Regenerate a demultiplex summary. Suppress email to Christian (watcherEmails).

from iggytools.iggyseq.runClasses import IlluminaNextGen
b = IlluminaNextGen.getInstance('150423_NS500422_0114_AH5YKCBGXX', verbose = True, watcherEmails = [])
b.summarizeDemuxResults()
