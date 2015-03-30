import os.path as path
import sys, argparse, re
from iggytools.iggyref.repoClass import Repo
from iggytools.utils.util import getUserHome

def update(inputArgs):

    repoChoices = ['ebi', 'ensembl', 'ncbi', 'ucsc', 'uniprot']
    defaultPrefDir = path.join(getUserHome(), '.iggytools')

    parser = argparse.ArgumentParser(prog='iggyref_update', usage='%(prog)s [options]')
    parser.add_argument('-r', '--repos',        help='Comma-separated list of repos to update. Choices: %s, all. If no value or "all" is specified, all five repos are updated.' 
                        % ', '.join(repoChoices), default='')
    parser.add_argument('-f', '--force',        help='Force download and postprocessing of all files in repo. Default: %(default)s', action='store_true', default=False)
    parser.add_argument('-p', '--forceProcess', help='Force postprocessing only. Default: %(default)s', action='store_true', default=False)
    parser.add_argument('-d', '--prefDir',      help='Directory where iggyref preferences file is located. Default: %(default)s', default=defaultPrefDir)
    parser.add_argument('-v', '--verbose',      help='Verbose mode', action='store_true', default=False)
    args = parser.parse_args()

    if not args.repos:  #args.repos is a string
        sourceNames = repoChoices
    else:
        sourceNames = args.repos.split(',')

    if args.verbose: print '\nRepos to update: %s' % ', '.join(sourceNames)
    
    for source in sourceNames:
        if args.verbose: print '\nUpdating repo %s... ' % source
        R = Repo(source, args.prefDir)
        R.downloadCollections(args.force)
        R.postProcessCollections(args.forceProcess)

if __name__ == "__main__":
    update(sys.argv[1:])
