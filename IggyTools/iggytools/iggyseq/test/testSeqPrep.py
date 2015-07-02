"""
Created on Jun 29, 2015
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: aaronkitzmiller
"""

from iggytools.utils.util                     import getUserHome
from iggytools.pref.iggytools_PrefClass       import Iggytools_Preferences
from iggytools.iggyseq.runClasses             import IlluminaNextGen, getSeqPref
from iggytools.iggyseq.sampleSheetClasses     import BaseSampleSheet

import unittest
import os

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def testNextSeqSeqPrep(self):

      os.environ['IGGYPREFDIR']='./tests/data/iggytools_prefs/'
      prefdir = os.environ.get('IGGYPREFDIR',None)

      if prefdir is not None:
        if not os.path.exists(prefdir):
            raise Exception("IGGYPREFDIR %s does not exist" % prefdir)

      runName  = "150527_NS500422_0126_AH2LC5AFXX"
      seqpref  = getSeqPref(prefdir)

      r        = IlluminaNextGen.getInstance(runName, pref = seqpref, verbose=True)
      r.processRun()

    def tearDown(self):
        pass


    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
