

#Show usage info for seqprep command:

seqprep -h


#--------------------------------------------------
# Examples of demultiplexing from the commandline:
#--------------------------------------------------

# Create a new output directory by adding a suffix to the run name.

seqprep 150326_SN343_0511_BC6NB6ACXX --suffix '_test1' --verbose


# Allow 1 mismatch in index and suppress adapter trimming, creating new output directory with suffix '_2'

seqprep 150305_NS500422_0094_AH57JTBGXX --verbose --mismatches 1 --suppressAdapterTrimming --suffix '_2'


# Only demultiplex lanes 2-4. Create new output directory with suffix '_2'. Suppress email to Christian (watcherEmails).

seqprep 150326_SN343_0511_BC6NB6ACXX --suffix '_2' --verbose --watcherEmails='' --lanes '2,3,4'


#--------------------------------------------------
# View demultiplexing log file for a run:
#--------------------------------------------------

more /n/informatics_external/seq/seqprep_log/150305_NS500422_0094_AH57JTBGXX

more /n/informatics_external/seq/seqprep_log/150305_NS500422_0094_AH57JTBGXX_test1  #if '_test1' suffix had been added