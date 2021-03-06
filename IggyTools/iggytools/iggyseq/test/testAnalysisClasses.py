"""
Created on Jul 2, 2015
Harvard FAS Informatics
All rights reserved.

@author: mclamp 
"""

import unittest
import os
import sys

scriptdir = os.path.dirname(os.path.realpath(__file__))

sys.path.append(scriptdir + "/../../../")

from iggytools.utils.util                     import getUserHome
from iggytools.pref.iggytools_PrefClass       import Iggytools_Preferences
from iggytools.iggyseq.runClasses             import IlluminaNextGen, getSeqPref
from iggytools.iggyseq.sampleSheetClasses     import BaseSampleSheet

class AnalysisClassesTest(unittest.TestCase):

    def setUp(self):

      self.scriptdir = os.path.dirname(os.path.realpath(__file__))

      os.environ['IGGYPREFDIR']  = self.scriptdir + "/../../../tests/data/iggytools_prefs/"

      prefdir = os.environ.get('IGGYPREFDIR',None)

      if prefdir is not None:
        if not os.path.exists(prefdir):
            raise Exception("IGGYPREFDIR %s does not exist" % prefdir)

      #iggyPref = Iggytools_Preferences(prefdir)
      #seqpref  = iggyPref.getPreferences()['iggyseq']

      runName  = "150527_NS500422_0126_AH2LC5AFXX"
      seqpref  = getSeqPref(prefdir)

      self.run  = IlluminaNextGen.getInstance(runName, pref = seqpref, verbose = True)


    def testProcessRun(self):
        pass

    def tearDown(self):
        pass


    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
