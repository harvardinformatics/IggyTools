import unittest
from iggytools.iggyref.repoClass import Repo
from iggytools.iggyref.FTPclass import iggyrefFTP
from iggytools.iggyref.baseCollectionClass import baseCollection
import os.path as path

class RepoCollectionTest(unittest.TestCase):
    """Test instationation of Repo and Collection classes"""

    def testRepoCollection(self):
        for source in 'ebi ncbi ucsc uniprot'.split():
            R = Repo(source)

            repoPropertiesMod = __import__('iggytools.iggyref.sources.%s.properties'%source, fromlist=['properties'])
            repoProperties = getattr(repoPropertiesMod,'repoProperties')
            for collName in repoProperties['selectedCollections']:
                C = baseCollection.getInstance(collName, R)
                self.assertIsNotNone(C)





