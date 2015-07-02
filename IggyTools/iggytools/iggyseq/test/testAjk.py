'''
Created on Jul 2, 2015

@author: akitzmiller
'''
import unittest
import os, shutil


class Test(unittest.TestCase):


        
    def setUp(self):
        self.workingdir = os.path.join(os.getcwd(),'run')
        os.makedirs(self.workingdir)
        
        pipestr = '''
###
## iggypipe preferences
###

# Directory for analysis results and logs.
IGGYPIPE_DIR: /n/regal/rc_admin/mclamp/iggypipeout/

# Logging level.
# Choices: [info, debug]
LOGGING_LEVEL: debug

# Database type.
# Choices: [sqlite, mysql]
DB_TYPE: mysql

# If DB_TYPE is sqlite, mysql settings can be ignored.
MYSQL_HOST: db-internal

MYSQL_DB: iggypipe_mclamp

MYSQL_USER: iggy

MYSQL_PASS: 98smms76

# Debug mode.
DEBUG: False        
'''
        f = open(os.path.join(self.workingdir,'iggypipe_settings.yaml'), 'w')
        f.write(pipestr)
        f.close()
        
        refstr = '''
####
##  IggyRef preferences
####

# Directory for genomes and databases 
IGGYREF_REPOSITORY_DIR: '/n/regal/informatics_public/ref/'

# Level of logging detail (info or debug)
LOGGING_LEVEL: debug

# Database type (sqlite or mysql)
DB_TYPE: mysql

# Note, if DB_TYPE is sqlite, then the mysql settings below can be ignored:
MYSQL_USER: iggy
MYSQL_HOST: db-internal
MYSQL_DB: iggyref
MYSQL_PASS: 98smms76

# Debug mode (In debug mode, files are not copied to REPOSITORY_DIR)
DEBUG: False

# EBI collection choices are interpro, pfam
EBI_COLLECTIONS: [interpro, pfam]

# Ensembl collection choices are human, fruitfly, worm, yeast
ENSEMBL_COLLECTIONS: [human, fruitfly, worm, yeast]

# NCBI collection choices are nr, nt, refseq_genomic, refseq_protein, refseq_rna, swissprot
NCBI_COLLECTIONS: [nr, nt, refseq_genomic, refseq_protein, refseq_rna, swissprot]

# UCSC collection choices are chicken_galGal3, chicken (most recent), fruitfly, human, 
# mouse, rat, worm, yeast, zebrafinch
UCSC_COLLECTIONS: [chicken_galGal3, chicken, fruitfly, human, mouse, rat, worm, yeast, zebrafinch]

# The sole Uniprot collection choice is uniref100
UNIPROT_COLLECTIONS: [uniref100]
'''
        f = open(os.path.join(self.workingdir,'iggyref_settings.yaml'), 'w')
        f.write(refstr)
        f.close()
        
        prefs = {
            'watchersfile'    : '/n/informatics/saved/seqprep_watchers_list.txt',
            'usersfile'       : '/n/informatics/saved/iggyseq_users_list.txt',
            'primaryparent'   : '/n/informatics/git/testdata',
            'logdirparent'    : os.path.join(self.workingdir,'seqprep_log'),
            'processingparent' : os.path.join(self.workingdir,'analysis_in_progress'),
            'finishingparent' : os.path.join(self.workingdir,'analysis_finished'),
            'finalparent'     : os.path.join(self.workingdir,'ngsdata'),
            'seqstatshistdir' : os.path.join(self.workingdir,'seqstats_bkup'),
            'seqstatslogfile' : os.path.join(self.workingdir,'seqprep_log','seqstatslog.txt'),   
            'machinetype'     :"{'NS500422': 'NextSeq', 'SN343': 'HiSeq', 'D00365': 'HiSeq', 'NS500305': 'NextSeq'}"         
        }
        for d in ['logdirparent','processingparent','finishingparent','finalparent','seqstatshistdir']:
            os.makedirs(prefs[d])
            
            
        self.preffile = os.path.join(self.workingdir,'iggyseq_settings.yaml')
        preftext = """
VERBOSE: True
PRIMARY_PARENT: {primaryparent}
MACHINE_TYPE: {machinetype}
USERS_FILE: {usersfile}
WATCHERS_FILE: {watchersfile}
LOGDIR_PARENT: {logdirparent}
PROCESSING_PARENT: {processingparent}
FINISHING_PARENT: {finishingparent}
FINAL_PARENT: {finalparent}
SEQPREP_NUM_MISMATCHES: 0
SEQPREP_NUM_THREADS: 8
SEQPREP_IGNORE_MISSING_BCL: True
SEQPREP_IGNORE_MISSING_CONTROL: True
SEQPREP_WITH_FAILED_READS: False
SEQPREP_TILE_REGEX: None
SEQPREP_DB_STORE: False
NEXTSEQ_MASK_SHORT_ADAPTER_READS: None
NEXTSEQ_SUPPRESS_ADAPTER_TRIMMING: False
NEXTSEQ_MIN_TRIMMED_READ_LENGTH: 0
SLURM_TIME: '48:00:00'
SLURM_MEM: 10000
SLURM_PARTITION: general
SEQSTATS_HIST_DIR: {seqstatshistdir}
SEQSTATS_LOGFILE: {seqstatslogfile}
""".format(**prefs)
    
        f = open(self.preffile,'w')
        f.write(preftext)
        f.close()
    


    def tearDown(self):
        pass
        #shutil.rmtree(self.workingdir)


    def testRun(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()