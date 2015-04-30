import os.path as path
import sys, os, yaml, imp, re, logging
from collections import namedtuple
from iggytools.utils.util import mkdir_p, getUserHome, dict2namedtuple
from iggytools.pref.toolClass import BaseToolPref
from iggytools.pref.derived.iggypipe_fileClass import Iggypipe_PrefFile
from iggytools.pref.derived.fastqc_fileClass import Fastqc_PrefFile
from iggytools.pref.derived.trimmomatic_fileClass import Trimmomatic_PrefFile
from iggytools.pref.derived.bowtie2_fileClass import Bowtie2_PrefFile
from iggytools.pref.derived.cufflinks_fileClass import Cufflinks_PrefFile
from iggytools.pref.derived.sortsam_fileClass import SortSam_PrefFile


class Iggypipe_Preferences(BaseToolPref):


    def __init__(self, iggytools_prefDir):  # Set prefdir location

        BaseToolPref.__init__(self, iggytools_prefDir)


    def getPreferences(self):  # Load iggypipe preferences
        
        pref = dict()

        for prefFileClass in [Iggypipe_PrefFile, Fastqc_PrefFile, Trimmomatic_PrefFile, Bowtie2_PrefFile, SortSam_PrefFile, Cufflinks_PrefFile]:

            pFile = prefFileClass( self.iggytools_prefDir ) 

            pref[pFile.id] = pFile.getVars()

        return pref


