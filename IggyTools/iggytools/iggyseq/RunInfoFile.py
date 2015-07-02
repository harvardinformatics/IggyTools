from lxml import etree

class RunInfoFile:

    def __init__(self, file):

        self.file                     = file

    def parse(self):

      with open (self.file, 'r') as myfile:
        xmlstr=myfile.read().replace('\n', '')

      root      = etree.fromstring(xmlstr)

      datetext  = root.find('Run/Date').text
      reads     = root.find('Run/Reads').getchildren()

      rdict     = dict()

      # Example rdict is {'Read1': {'num_cycles': '76', 'is_index': 'N'}, 'Read2': {'num_cycles': '76', 'is_index': 'N'}}

      for read in reads:

        if 'Number' not in read.attrib:
            raise Exception("Error reading RunInfoFile %s - no Number element for read"%self.file)

        if 'IsIndexedRead' not in read.attrib:
            raise Exception("Error reading RunInfoFile %s - no IsIndexedRead element for read"%self.file)

        if 'NumCycles' not in read.attrib:
            raise Exception("Error reading RunInfoFile %s - no NumCycles element for read"%self.file)

        read_num = read.attrib['Number']

        rdict["Read" + read_num] = dict()
        rdict["Read" + read_num]['is_index']   = read.attrib['IsIndexedRead']
        rdict["Read" + read_num]['num_cycles'] = read.attrib['NumCycles']
      
      return rdict, datetext

