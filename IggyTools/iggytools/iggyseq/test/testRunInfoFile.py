"""
Created on Jul 2, 2015
Harvard FAS Informatics
All rights reserved.

@author: mclamp 
"""

import unittest
import sys
import os
import re

from iggytools.pref.iggytools_PrefClass       import Iggytools_Preferences
from iggytools.iggyseq.RunInfoFile            import RunInfoFile 

class RunInfoFileTest(unittest.TestCase):

    def setUp(self):
      self.scriptdir = os.path.dirname(os.path.realpath(__file__))

      os.environ['PYTHONPATH']   = self.scriptdir + "../../../"
      os.environ['IGGYPREFDIR']  = self.scriptdir + "/../../../tests/data/iggytools_prefs/"

      prefdir = os.environ.get('IGGYPREFDIR',None)

      if prefdir is not None:
        if not os.path.exists(prefdir):
            raise Exception("IGGYPREFDIR %s does not exist" % prefdir)


    def testRunInfoFile0(self):
      file0 = self.scriptdir + "/data/H2LC5AFXX.RunInfo.xml"
      rif0  = RunInfoFile(file0)

      (rdict, datetext) = rif0.parse()

      self.assertTrue(datetext == "150527")
    
    def testRunInfoFile1(self): 
      file1 = self.scriptdir + "/data/H2LC5AFXX.bad1.RunInfo.xml"
      rif1  = RunInfoFile(file1)

      caught = False

      try:
        (rdict, datetext) = rif1.parse()
      except Exception as e:

        if re.search('Number element', str(e), re.I):
           caught = True

      self.assertTrue(caught)


    def testRunInfoFile2(self):
      file2 = self.scriptdir + "/data/H2LC5AFXX.bad2.RunInfo.xml"
      rif2  = RunInfoFile(file2)

      caught = False

      try:
        (rdict, datetext) = rif2.parse()
      except Exception as e:
        if re.search('NumCycles element', str(e), re.I):
           caught = True

      self.assertTrue(caught)



    def tearDown(self):
        pass

    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
