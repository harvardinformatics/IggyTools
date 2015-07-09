"""
Created on Jul 9, 2015
Harvard FAS Informatics
All rights reserved.

@author: mclamp 
"""

import unittest
import os

from iggytools.utils.util                     import getUserHome
from iggytools.pref.iggytools_PrefClass       import Iggytools_Preferences
from iggytools.iggyseq.laneClass              import Lane
from iggytools.iggyseq.runClasses             import IlluminaNextGen, getSeqPref

class LaneClassTest(unittest.TestCase):

    def setUp(self):
      os.environ['IGGYPREFDIR']='./tests/data/iggytools_prefs/'
      prefdir = os.environ.get('IGGYPREFDIR',None)

      if prefdir is not None:
        if not os.path.exists(prefdir):
            raise Exception("IGGYPREFDIR %s does not exist" % prefdir)

      #iggyPref = Iggytools_Preferences(prefdir)
      #seqpref  = iggyPref.getPreferences()['iggyseq']

      runName  = "150527_NS500422_0126_AH2LC5AFXX"
      seqpref  = getSeqPref(prefdir)

      self.run  = IlluminaNextGen.getInstance(runName, pref = seqpref, verbose = False)


    def testCreateLane(self):

      lane = Lane(self.run)

      self.assertTrue(lane)

      lane.index1Length = 6
      lane.index2Length = 8

      self.assertTrue(lane.index1Length == 6) 
      self.assertTrue(lane.index2Length == 8) 

      self.assertTrue(len(lane.subIDs) == 0)

      self.assertTrue(len(lane.ssSampleLines) == 0)
      self.assertTrue(len(lane.ssLineIndices) == 0)

      self.assertTrue(lane.userLaneName is None)
      self.assertTrue(lane.machineLaneName is None)


      self.assertTrue(lane.Run.runName == "150527_NS500422_0126_AH2LC5AFXX")

    def tearDown(self):
        pass


    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
