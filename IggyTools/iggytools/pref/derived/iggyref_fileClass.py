import os.path as path
from iggytools.utils.util import getUserHome, dict2namedtuple
from iggytools.pref.fileClass import BasePrefFile
from iggytools.pref.varClass import PrefVar

class Iggyref_PrefFile(BasePrefFile):


    def __init__(self, prefDir):

        BasePrefFile.__init__(self, 
                              ID = 'iggyref', 
                              filePath = path.join(prefDir, 'iggyref_settings.yaml'), 
                              iggytool = 'iggyref')

        self.vars = [ PrefVar( name = 'IGGYREF_REPOSITORY_DIR',
                               default = path.join(getUserHome(), 'iggyref'),
                               comment = 'Directory for genomes and databases',
                               varType = str ),

                      PrefVar( name = 'LOGGING_LEVEL',
                               default = 'info',
                               choices = ['info', 'debug'],
                               comment = 'Level of logging detail',
                               varType = str ),

                      PrefVar( name = 'DB_TYPE',
                               default = 'sqlite',
                               choices = ['sqlite', 'mysql'],
                               comment = 'Database type',
                               varType = str ),

                      PrefVar( name = 'MYSQL_HOST',
                               default = 'localhost',
                               comment = 'If DB_TYPE is sqlite, mysql settings can be ignored',
                               varType = str ),

                      PrefVar( name = 'MYSQL_DB',
                               default = 'iggypipe_db',
                               varType = str ),

                      PrefVar( name = 'MYSQL_USER',
                               default = 'iggypipe',
                               varType = str ),

                      PrefVar( name = 'MYSQL_PASS',
                               default = 'iggypipe',
                               varType = str ),

                      PrefVar( name = 'DEBUG',
                               default = False,
                               comment = 'Debug mode (In debug mode, files are not copied to IGGYREF_REPOSITORY_DIR',
                               varType = bool ),

                      PrefVar( name = 'EBI_COLLECTIONS',
                               default = ['interpro', 'pfam'],
                               choices = ['interpro', 'pfam'],
                               comment = 'EBI collections',
                               varType = list ),

                      PrefVar( name = 'ENSEMBL_COLLECTIONS',
                               default = ['human', 'fruitfly', 'worm', 'yeast'],
                               choices = ['human', 'fruitfly', 'worm', 'yeast'],
                               comment = 'Ensembl collections',
                               varType = list ),

                      PrefVar( name = 'NCBI_COLLECTIONS',
                               default = ['nr', 'nt', 'refseq_genomic', 'refseq_protein', 'refseq_rna', 'swissprot'],
                               choices = ['nr', 'nt', 'refseq_genomic', 'refseq_protein', 'refseq_rna', 'swissprot'],
                               comment = 'NCBI collections',
                               varType = list ),

                      PrefVar( name = 'UCSC_COLLECTIONS',
                               default = ['chicken_galGal3', 'chicken', 'fruitfly', 'human', 'mouse', 'rat', 'worm', 'yeast', 'zebrafinch'],
                               choices = ['chicken_galGal3', 'chicken', 'fruitfly', 'human', 'mouse', 'rat', 'worm', 'yeast', 'zebrafinch'],
                               comment = 'UCSC collections',
                               varType = list ),

                      PrefVar( name = 'UNIPROT_COLLECTIONS',
                               default = ['uniref100'],
                               choices = ['uniref100'],
                               comment = 'Uniprot collections',
                               varType = list ) ]

    def getVars(self):

        self.fileSetup()  #ensure pref file exists

        self.load()  #read and process preferences 

        vDict = dict( [(x.name, x.value) for x in self.vars] )

        vDict['REPO_DIR']      = vDict.pop('IGGYREF_REPOSITORY_DIR')   #rename key

        vDict['WORK_DIR']      = path.join( vDict['REPO_DIR'], '.work' )

        vDict['LOG_DIR']       = path.join( vDict['WORK_DIR'], 'log' )
        vDict['DOWNLOAD_DIR']  = path.join( vDict['WORK_DIR'], 'download' )
        vDict['INTERMED_DIR']  = path.join( vDict['WORK_DIR'], 'intermed' )
        vDict['TEMP_DIR']      = path.join( vDict['WORK_DIR'], 'temp' )

        return dict2namedtuple( dict( [(name, value) for name,value in vDict.iteritems()] ) )


