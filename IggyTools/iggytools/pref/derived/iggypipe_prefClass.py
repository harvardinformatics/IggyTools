import os.path as path
import sys, os, yaml, imp, re, logging
from collections import namedtuple
from iggytools.utils.util import mkdir_p, getUserHome, dict2namedtuple
from iggytools.pref.toolClass import BaseToolPref
from iggytools.pref.derived.iggypipe_fileClass import Iggypipe_PrefFile
from iggytools.pref.derived.fastqc_fileClass import Fastqc_PrefFile
from iggytools.pref.derived.trimmomatic_fileClass import Trimmomatic_PrefFile
from iggytools.pref.derived.bowtie2_fileClass import Bowtie2_PrefFile


class Iggypipe_Preferences(BaseToolPref):


    def __init__(self, iggytools_prefDir):  # Set prefdir location

        BaseToolPref.__init__(self, iggytools_prefDir)


    def getPreferences(self):  # Load tool preferences
        
        p = dict()

        self.prefFiles = [ Iggypipe_PrefFile(self.iggytools_prefDir),
                           Fastqc_PrefFile(self.iggytools_prefDir),
                           Trimmomatic_PrefFile(self.iggytools_prefDir),
                           Bowtie2_PrefFile(self.iggytools_prefDir)]


        for pfile in self.prefFiles:
            p[pfile.id] = pfile.getVars()
            
        return p


