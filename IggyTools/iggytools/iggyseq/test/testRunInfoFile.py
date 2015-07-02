"""
Created on Jul 2, 2015
Harvard FAS Informatics
All rights reserved.

@author: mclamp 
"""

import unittest
import os

from iggytools.pref.iggytools_PrefClass       import Iggytools_Preferences
from iggytools.iggyseq.RunInfoFile            import RunInfoFile 

class RunInfoFileTest(unittest.TestCase):

    def setUp(self):
      os.environ['IGGYPREFDIR']='./tests/data/iggytools_prefs/'
      prefdir = os.environ.get('IGGYPREFDIR',None)

      if prefdir is not None:
        if not os.path.exists(prefdir):
            raise Exception("IGGYPREFDIR %s does not exist" % prefdir)

      self.file = "./iggytools/iggyseq/test/data/H2LC5AFXX.RunInfo.xml"

    def testRunInfoFile(self):
      rif  = RunInfoFile(self.file)

      (rdict, datetext) = rif.parse()

      self.assertTrue(datetext == "150527")
     
      print rdict 

    def tearDown(self):
        pass

    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
