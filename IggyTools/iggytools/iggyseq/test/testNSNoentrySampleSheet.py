'''
Created on Jul 2, 2015

@author: gmarnellos

Test to check whether seqprep can process NextSeq sample sheet with no library entries.
'''
import unittest, shutil
import os, subprocess, re


class NSNoentrySampleSheet(unittest.TestCase):


    def setUp(self):
	# Indicate paths to code, settings, and output directories 
	self.iggyprefdir = "/n/informatics/git/test_settings/george_settings"
	#self.codedir = "/n/home_rc/gmarnellos/test/iggy/IggyTools/IggyTools"
	self.codedir = "../../../../../IggyTools/IggyTools"
	self.pathfinished = "/tmp/analysis_finished"
	self.pathinprogress = "/tmp/analysis_in_progress"
	self.iggylog = "/tmp/seqprep_log"
	# Command to set up iggy environment 
	self.setupcmd = "source %s/setup.sh %s" % (self.iggyprefdir, self.codedir)
	# Command needed for the main body of the test
	self.jobcmd1 = "seqprep --suffix '_test_noentry' --verbose  150529_NS500305_0015_AHFCWWBGXX"
        #pass

  
    def tearDown(self):
	# Remove test output folders
	pathtoremove = self.pathfinished
	if os.path.exists(pathtoremove):
		shutil.rmtree(pathtoremove)
	pathtoremove = self.pathinprogress
	if os.path.exists(pathtoremove):
		shutil.rmtree(pathtoremove)
	pathtoremove = self.iggylog
	if os.path.exists(pathtoremove):
		shutil.rmtree(pathtoremove)


    def testNoentry(self):
        # Run command, get its output 
	cmd = "%s && IGGYPREFDIR=%s %s" % (self.setupcmd, self.iggyprefdir, self.jobcmd1)
	print cmd
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	out,err = p.communicate()
	output = 0
	# Look at SampleSheet written out in the output to see if test succeeded or not.
	samplesheet_path = "%s/150529_NS500305_0015_AHFCWWBGXX_test_noentry/SampleSheet.csv" % (self.pathfinished)
	test_ss = "ls -l %s | awk '{print $5}' " % (samplesheet_path)
	if os.path.exists(samplesheet_path):
		p = subprocess.Popen(test_ss, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        	out,err = p.communicate()
		output = int(out)
		#print output
	if output > 0:
		print("\nSampleSheet Noentry Test succeeded. Wrote out SampleSheet of size: %s" % (output))
	else:
		print("\nSampleSheet Noentry Test failed")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

