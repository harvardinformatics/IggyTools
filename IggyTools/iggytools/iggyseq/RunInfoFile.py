import sys, os, stat, glob, re
from lxml import etree
import os.path as path
from iggytools.utils.util import md5Checksum, recursiveChmod, dict2namedtuple


class RunInfoFile:

    def __init__(self, file):

        self.file                     = file

    def parse(self):
     
      with open (self.file, 'r') as myfile:
        xmlstr=myfile.read().replace('\n', '')

      root      = etree.fromstring(xmlstr)
      datetext  = root.find('Run/Date').text

      reads = root.find('Run/Reads').getchildren()

      rdict = dict()

      for read in reads:

        read_num = read.attrib['Number']

        rdict["Read" + read_num] = dict()
        rdict["Read" + read_num]['is_index'] = read.attrib['IsIndexedRead']
        rdict["Read" + read_num]['num_cycles'] = read.attrib['NumCycles']
      
      return rdict, datetext
