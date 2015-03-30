import sys, os, stat, glob
from lxml import etree
import os.path as path
from iggytools.utils.util import md5Checksum, recursiveChmod

def setPermissions(item):

    filePermissions = stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IROTH

    if path.isfile(item):

        os.chmod(item, filePermissions)

    elif path.isdir(item):

        dirPermissions = stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IXGRP|stat.S_IRUSR|stat.S_IROTH|stat.S_IXOTH
        recursiveChmod(item, filePermissions, dirPermissions)


def parseRunInfo(rifile):

    with open (rifile, 'r') as myfile:
        xmlstr=myfile.read().replace('\n', '')

    root = etree.fromstring(xmlstr)
    datetext=root.find('Run/Date').text

    reads = root.find('Run/Reads').getchildren()

    rdict = dict()
    for read in reads:
        read_num = read.attrib['Number']
        rdict["Read" + read_num] = dict()
        rdict["Read" + read_num]['is_index'] = read.attrib['IsIndexedRead']
        rdict["Read" + read_num]['num_cycles'] = read.attrib['NumCycles']

    return rdict, datetext

def fastqGz_checksums(myDir):
    # Calculate md5sum checksums on any .fastq.gz files in myDir. Saves checksums to md5sum.txt in myDir
    # Writing md5sum.txt to the same directory as the input files avoids ambiguity that could arise if samples 
    # with the same name are run in different lanes. 

    outFile = file(path.join(myDir,'md5sum.txt'), 'w')
    files = [f for f in glob.glob(path.join(myDir, '*.fastq.gz')) if path.isfile(f)]
    checksums = [(path.basename(fname), md5Checksum(fname)) for fname in files]

    for pair in checksums:
        outFile.write('%s\t%s\n' % pair)

    outFile.close()


