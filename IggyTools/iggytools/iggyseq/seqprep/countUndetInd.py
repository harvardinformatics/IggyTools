import sys, gzip, re, os
from os import path
from iggytools.utils.util import mkdir_p

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict # for python 2.6 or earlier, use backport


def count(gzFastqFile, outDir):  #tally barcodes in a fastq.gz file

    counts = dict()

    for line in gzip.open(gzFastqFile, 'rb'):

        matchObj = re.match('@(ILLUMINA|NS500422).+:([ACGTN+]+)$', line) #matches from beginning of line

        if matchObj:
            index = matchObj.group(2)
            if index in counts:
                counts[index] += 1
            else:
                counts[index] = 1

    #sort dict by count
    orderedCounts = OrderedDict(sorted(counts.items(), key=lambda t: t[1], reverse=True))

    #write counts to file
    if not path.isdir(outDir):
        mkdir_p(outDir)

    f = open(path.join(outDir,"Undetermined_index_counts.txt"),'w')
    fTop = open(path.join(outDir,"Undetermined_index_counts_Top100.txt"),'w')

    f.write("Index\tCount\n")
    fTop.write("Index\tCount\n")

    i = 1;
    for index in orderedCounts:

        line = "%s\t%d\n" % (index, orderedCounts[index])

        f.write(line)

        if i <= 100:
            fTop.write(line)
        i += 1

    f.close() 
    fTop.close()
