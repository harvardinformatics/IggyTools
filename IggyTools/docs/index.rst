=========
IggyTools
=========

To setup IggyTools, use:
    ``source /n/informatics/iggy/setup.sh``

SeqPrep
-------

Use the command ``seqprep`` to demultiplex runs. To see usage, type:
    ``seqprep -h``

The following are a few example calls to seqprep:
    ``seqprep 150305_D00365_0435_BH2LLNBCXX --suffix '_test1' --verbose --lanes 2``

    ``seqprep 150305_NS500422_0094_AH57JTBGXX --verbose --mismatches 1 --suppressAdapterTrimming --suffix '_test1'``

To run an hourly cron job which runs seqprep on new runs, add the following line to your crontab file:
    ``0 * * * * /n/informatics/iggy/IggyTools/iggytools/bin/cron_seqprep.sh``


Notes
------
A note on the NextSeq bcl2fastq2 parameter --minimum-trimmed-read-length (which corresponds to seqprep parameter --minTrimmedReadLength):
When using the --use-bases-mask option, this option must be manually set to be less than or equal to the minimum read length. 
Otherwise, bcl2fastq 2.15.0 will N-pad the reads to the default minimum trimmed read length of 32 basepairs.

More information about this bug is in the bcl2fastq release notes:
  http://support.illumina.com/content/dam/illumina-support/documents/documentation/software_documentation/bcl2fastq/bcl2fastq2-v2.15.0-customer-release-notes-15053886-b.pdf

As a workaround, SeqPrep passes a value of 0 to bcl2fastq2 for the minimum trimmed read length.
