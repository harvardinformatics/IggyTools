=========
IggyTools
=========

To setup IggyTools, use:
    ``source /n/informatics/iggy/setup.sh``

SeqPrep
-------

Use the command ``seqprep`` to demultiplex runs. To see usage and default parameters, type:
    ``seqprep -h``

Below is an example seqprep command for a HiSeq run:
    ``seqprep 150305_D00365_0435_BH2LLNBCXX --suffix '_test1' --verbose --lanes 2``
And a NextSeq run:
    ``seqprep 150305_NS500422_0094_AH57JTBGXX --verbose --mismatches 1 --suppressAdapterTrimming --suffix '_test1'``
However most runs will require no extra options.
    ``seqprep 150305_NS500422_0094_AH57JTBGXX``
Although it's probably a good idea to use ``--verbose`` so you can see log information echoed stdout. Also, if you must reprocess a run,
it's a good idea to use ``--suffix`` to tack a string onto the end of the output run folder name, so that previous results are not overwritten.

To create run an hourly cron job which runs seqprep on new runs in /n/illumina01/primary_data, add the following line to your crontab file.
    ``0 * * * * /n/informatics/iggy/IggyTools/iggytools/bin/cron_seqprep.sh``

Once a run has begun processing, seqprep_seen.txt will be written to the run folder. If you want this cron job to process a run again,
delete this file from the run's primray_data folder.

To see the current state of a processing run, look at log.txt in its log folder:
   ``/n/informatics_external/seq/seqprep_log/<run_name>``

Note that if you started processing with the seqprep and specified a suffix, the log folder name will be ``<run_name><suffix>``.


Notes
------
Regarding the NextSeq bcl2fastq2 parameter --minimum-trimmed-read-length (which corresponds to seqprep parameter --minTrimmedReadLength):
When using the --use-bases-mask option, this option must be manually set to be less than or equal to the minimum read length. 
Otherwise, bcl2fastq 2.15.0 will N-pad the reads to the default minimum trimmed read length of 32 basepairs.

More information about this bug is in the bcl2fastq release notes:
  http://support.illumina.com/content/dam/illumina-support/documents/documentation/software_documentation/bcl2fastq/bcl2fastq2-v2.15.0-customer-release-notes-15053886-b.pdf

As a workaround, SeqPrep passes a value of 0 to bcl2fastq2 for the minimum trimmed read length.
