#!/usr/bin/env python 
from seqprep import settings
from seqprep import options as opts
from seqhub import hUtil
import sys, re
import os.path as path

## NOTE: slurm processing is currently unused in seqprep. This function has not been tested.

def slurmProcess(argv): #create slurm script that calls processRun.py with commandline arguments
    options, runName = opts.parseOptions(argv)
    if options.suffix:
        runOutName = runName + options.suffix
    else:
        runOutName = runName

    runOutDir = path.join(settings.SLURM_SCRIPT_DIR, runOutName)
    util.mkdir_p(runOutdir)

    scriptFile = path.join(settings.SLURM_SCRIPT_DIR, runOutName, "script.sh")
    f = open(scriptFile, 'w')
    f.write("#!/bin/bash\n")
    f.write("#SLURM --nodes=1\n")
    f.write("#SLURM --output="    + path.join(runOutDir,"out.txt") + "\n")
    f.write("#SLURM --ntasks="    + options.numThreads  + "\n")
    f.write("#SLURM --time="      + options.time        + "\n")
    f.write("#SLURM --mem="       + options.mem         + "\n")
    f.write("#SLURM --partition=" + options.partition   + "\n")
    f.write("#SLURM --job-name="  + options.jobName     + "\n")
    f.write("#SLURM --mail-user=" + options.usersString + "\n")
    f.write("#SLURM --mail-type=END\n")
    f.write("#SLURM --mail-type=FAIL\n\n")

    f.write("set -eu\n")
    f.write("module load centos6/seqve_2.6.6\n") # the seq virutal env; modfile also sets pythonpath for seqstats and seqprep, and path for bin directory
    f.write(". activate\n")  #activate virutal env
    f.write("processRun.py " + " ".join(argv) + "\n\n")

    f.write("#This script was generated by slurmProcessRun.py\n")
    f.close()

    hUtil.runCmd("sbatch " + scriptFile)
