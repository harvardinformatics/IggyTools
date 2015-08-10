'''
Created on Jul 1, 2015

@author: afreedman

sundry tests of iggyseq run classes

'''

### importing stuff specific to testing framework execution (minus os) ###
import unittest
import shutil 
import sys
import os
from subprocess import Popen,PIPE

### update python path to look for iggytools--UPDATE if move test directory ###

scriptdir=os.path.dirname(os.path.realpath(__file__))
#print 'scriptdir is', scriptdir
#testdir=sys.path.append("/".join(scriptdir.split("/"))[:-2])


sys.path.append(scriptdir+"/../../../")
#print os.path

### stuff required by RunClasses.py ###
import re, traceback, imp
from os import path
from abc import ABCMeta, abstractmethod
from iggytools.iggyseq.sampleSheetClasses import BaseSampleSheet
from iggytools.iggyseq.seqUtil import setPermissions
from iggytools.utils.util import touch, mkdir_p, intersect, deleteItem, copy, Command, unique, str2list_byComma
from iggytools.iggyseq.getSeqPref import getSeqPref
from iggytools.iggyseq.seqUtil import parseRunName

### accessing run class methods ###
from iggytools.iggyseq.runClasses import IlluminaNextGen,HiSeq,NextSeq

#data_dir="/n/informatics/git/testdata/150605_D00365_0511_BC6FHCANXX"

class Test(unittest.TestCase):
		
	def setUp(self):
		self.workingdir=os.path.join(os.getcwd(),"tempdir")
		os.system("mkdir %s" % self.workingdir)
		self.prefdir=os.path.join(self.workingdir,"pref")
		paths={
		"LOGDIR_PARENT":os.path.join(self.workingdir,"seqprep_log"),
		"PROCESSING_PARENT":os.path.join(self.workingdir,"analysis_in_progress"),
		"FINISHING_PARENT":os.path.join(self.workingdir,"analysis_finished"),
		"FINAL_PARENT":os.path.join(self.workingdir,"ngsdata"),
		"SEQSTATS_HIST_DIR":os.path.join(self.workingdir,"seqstats_bkup"),
		"SEQSTATS_LOG_DIR":os.path.join(self.workingdir,"seqstats_log")}
	
		for name,path in paths.iteritems():
			os.system("mkdir %s" % path)
			print path	
		paths["TILE_REGEX"]="s_1_1205"
		paths["MACHINE_TYPE"]="{'NS500422': 'NextSeq', 'SN343': 'HiSeq', 'D00365': 'HiSeq', 'NS500305': 'NextSeq'}"
		
		self.preffile=os.path.join(self.prefdir,"iggyseq_settings.yaml")
		os.system("mkdir %s" % self.prefdir)	
		self.prefdata="""
###
## iggyseq preferences
###

# Iggyseq verbose mode.
VERBOSE: False

# Directory where run directories with BCL files are located.
PRIMARY_PARENT: /n/informatics/git/testdata

# Dictionary mapping machine name to machine type. (Keys are machine names, values are type.
MACHINE_TYPE: {MACHINE_TYPE}

# File containing comma-separated email addresses to be sent all iggyseq notifications and demultiplex summaries.
USERS_FILE: /n/informatics/saved/iggyseq_users_list.txt

# File containing comma-separated email addresses to be sent demultiplex summaries only.
WATCHERS_FILE: /n/informatics/saved/seqprep_watchers_list.txt

# Directory where run log directories are written.
LOGDIR_PARENT: {LOGDIR_PARENT}

# Directory where run processing directories are written.
PROCESSING_PARENT: {PROCESSING_PARENT}

# Directory where run finishing directories are written.
FINISHING_PARENT: {FINISHING_PARENT}

# Directory where demultiplexed runs are written for download by users.
FINAL_PARENT: {FINAL_PARENT}

# Number of mismatches allowed in barcodes when demultiplexing.
SEQPREP_NUM_MISMATCHES: 0

# Number of threads for demultiplexing.
SEQPREP_NUM_THREADS: 8

# Ignore missing BCL files.
SEQPREP_IGNORE_MISSING_BCL: True

# Ignore missing CONTROL files.
SEQPREP_IGNORE_MISSING_CONTROL: True

# Include failed reads in demultiplex results.
SEQPREP_WITH_FAILED_READS: False

# Regex for tile selection.
SEQPREP_TILE_REGEX: {TILE_REGEX}

# Update minilims upon completion of demultiplexing.
SEQPREP_DB_STORE: True

# For NextSeq, mask short adapter reads.
NEXTSEQ_MASK_SHORT_ADAPTER_READS: None

# For NextSeq, suppress adater trimming.
NEXTSEQ_SUPPRESS_ADAPTER_TRIMMING: False

# For NextSeq, minimum trimmed read length.
NEXTSEQ_MIN_TRIMMED_READ_LENGTH: 0

# Slurm time reservation in format HH:MM:SS.
SLURM_TIME: '48:00:00'

# Slurm memory reservation in MB.
SLURM_MEM: 10000

# SLURM PARTITION.
SLURM_PARTITION: general

# Where Illumina run statistics files are kept.
SEQSTATS_HIST_DIR: {SEQSTATS_HIST_DIR}

# Seqtats log file.
SEQSTATS_LOGFILE: {SEQSTATS_LOG_DIR}log.txt
""".format(**paths)
	
		preffile=open(self.preffile,"w")
		preffile.write(self.prefdata)
		preffile.close()


	def tearDown(self):
		shutil.rmtree(self.workingdir)
		pass

	def testGetIlluminaNextGenInstance(self):
		 
		pref = getSeqPref(self.prefdir)
		#args = parseArgs(argv, pref = pref)
		runName = "150605_D00365_0511_BC6FHCANXX"
		r = IlluminaNextGen.getInstance(runName, pref = pref, verbose=True)
		#print "r type is....", type(r)
		#if r.runType=="HiSeq":
		self.assertTrue(r.runType in ("HiSeq","NextSeq"), "incorrect runType for IlluminaNextGen class instance")
		self.assertTrue(r.optionsStr not in (None,""), "empty options string for Hi/Next-Seq sublcass of IlluminaNextGen")
		self.assertTrue(r.runparametersFile not in (None,""),"empty or null runparametersFile of Hi/Next-Seq sublcass of IlluminaNextGen") 	

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
