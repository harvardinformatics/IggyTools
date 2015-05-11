import sys, gzip, re, os
from os import path
from iggytools.utils.util import mkdir_p

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict # for python 2.6 or earlier, use backport


import locale  #for printing of commas in numbers using format()
ignored = locale.setlocale(locale.LC_ALL, '') # empty string for platform's default setting 


def count(gzFastqFile, outDir, threshold = 1000000):  # tally barcodes in a fastq.gz file. 

    counts = dict()
    highCountSummary = list()  #Summary of high-count barcodes (where count > threshold)

    for line in gzip.open(gzFastqFile, 'rb'):

        matchObj = re.match('@(ILLUMINA|NS|HISEQ).+:([ACGTN+]+)$', line) # matches from beginning of line

        if matchObj:
            index = matchObj.group(2)
            if index in counts:
                counts[index] += 1
            else:
                counts[index] = 1

    # sort dict by count
    orderedCounts = OrderedDict(sorted(counts.items(), key=lambda t: t[1], reverse=True))

    # Write counts to file
    if not path.isdir(outDir):
        mkdir_p(outDir)

    f = open(path.join(outDir,'Undetermined_index_counts.txt'),'w')
    fTop = open(path.join(outDir,'Undetermined_index_counts_Top100.txt'),'w')

    f.write('Index\tCount\n')
    fTop.write('Index\tCount\n')

    i = 1;
    for index in orderedCounts:

        line = '%s\t%s' % (index, format(orderedCounts[index], 'n'))
               
        f.write(line + '\n')

        if i <= 100:
            fTop.write(line)

            if orderedCounts[index] > threshold and not re.match('(N+|A+|G+|T+|C+)$', index, re.IGNORECASE): #do not report indices that are all one character
                highCountSummary.append(line)

            i += 1

    f.close() 
    fTop.close()

#    if highCountSummary:
#        highCountSummary = ['Index\tCount'] + highCountSummary

    return highCountSummary
