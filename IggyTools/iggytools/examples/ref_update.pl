
# Update iggyref repos from within python

# Update ucsc repository
from iggytools.iggyref.repoClass import Repo
b = Repo('ucsc')
b.downloadCollections()
b.postProcessCollections()

#Update ebi, force postprocessing of all files
from iggytools.iggyref.repoClass import Repo
b = Repo('ensembl')
b.downloadCollections()
b.postProcessCollections(force=True)

