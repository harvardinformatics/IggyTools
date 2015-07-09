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
from iggytools.iggyseq.runClasses             import IlluminaNextGen, getSeqPref
from iggytools.iggyseq.seqUtil                import parseRunName, parseRunInfo

class SeqUtilTest(unittest.TestCase):

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


    def testParseRunName(self):

      run  = self.run
      name = run.runName
 
      self.assertTrue(name == "150527_NS500422_0126_AH2LC5AFXX")

      namehash = parseRunName(name)

      # NamedTuple(pos_and_flowcell='AH2LC5AFXX', machineID='NS500422', counter='0126', pos='A', runType='', flowcell='H2LC5AFXX', runName='150527_NS500422_0126_AH2LC5AFXX', date='150527')

      self.assertTrue(namehash.pos_and_flowcell == 'AH2LC5AFXX')
      self.assertTrue(namehash.machineID        == 'NS500422')
      self.assertTrue(namehash.counter          == '0126')
      self.assertTrue(namehash.flowcell         == 'H2LC5AFXX')
      self.assertTrue(namehash.runName          == '150527_NS500422_0126_AH2LC5AFXX')
      self.assertTrue(namehash.date             == '150527')

    def testParseRunInfo1(self):

       """ This is a correct RunInfo file """

       rifile1 = "./iggytools/iggyseq/test/data/H2LC5AFXX.RunInfo.xml"

       (rdict, datetext) = parseRunInfo(rifile1)

       self.assertTrue(rdict)
       self.assertTrue(datetext == "150527")


       #{'Read1': {'num_cycles': '76', 'is_index': 'N'}, 'Read2': {'num_cycles': '76', 'is_index': 'N'}}

       self.assertTrue(len(rdict) ==2)
       self.assertTrue(rdict['Read1'])
       self.assertTrue(rdict['Read2'])

       self.assertTrue(rdict['Read2']['is_index'] == 'N')

    def testParseRunInfo2(self):

       """ This is an  incorrect RunInfo file """

       rifile1 = "./iggytools/iggyseq/test/data/H2LC5AFXX.bad1.RunInfo.xml"


       try:

         (rdict, datetext) = parseRunInfo(rifile1)

       except Exception as e:
         # This obviously isn't a very informative error message.  But the test passes
         self.assertTrue(e.message == "Number")

    def testParseRunInfo3(self):

       """ This is an incorrect RunInfo file """

       rifile1 = "./iggytools/iggyseq/test/data/H2LC5AFXX.bad2.RunInfo.xml"


       try:

         (rdict, datetext) = parseRunInfo(rifile1)

       except Exception as e:
         # This obviously isn't a very informative error message.  But the test passes
         self.assertTrue(e.message == "NumCycles")


    def tearDown(self):
        pass


    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
