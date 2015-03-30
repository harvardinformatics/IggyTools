import os.path as path
from iggytools.utils.util import copy
import sys, os, re
import shutil, errno

def copyRunFiles(runPath, dstDir):  #copy essential run files
    runName = path.basename(runPath)
    os.mkdir(path.join(dstDir,runName))
    for item in ["SampleSheet.csv", "RunInfo.xml", "runParameters.xml", "RunParameters.xml", "InterOp"]:
        if path.isfile(path.join(runPath, item)) or path.isdir(path.join(runPath, item)):
            copy(path.join(runPath,item), path.join(dstDir,runName,item))
