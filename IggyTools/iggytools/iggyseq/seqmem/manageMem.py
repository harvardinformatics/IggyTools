from seqmem.util import diskPercentUsage, ageInDays, runNameMatch
from seqhub import hUtil, hSettings 
import os, re, shutil, operator
import os.path as path

def capDirUsage(myDir, capPerc, ageLimitDays, copyInSEQCFS = True, verbose = False):
    perc = diskPercentUsage(myDir)
    if verbose: print '\n(capDirUsage):  Disk usage for %s: %.2f %% (cap: %.2f)' % (myDir, perc, capPerc)
    if perc > float(capPerc):
        while perc > float(capPerc):
            deleteOldestRun(myDir, ageLimitDays, copyInSEQCFS, verbose)
            perc = diskPercentUsage(myDir)
        if verbose: print '(capDirUsage):  Disk usage for %s after deletions: %.2f %%' % (myDir, perc)        

def deleteOldestRun(myDir, minimumAgeDays, copyInSEQCFS = True, verbose = False):
    ageDict = dict()
    for item in os.listdir(myDir):
        if path.isdir(path.join(myDir,item)) and runNameMatch(item):
            runName = item
            ageDict[runName] = ageInDays(path.join(myDir,runName))
    if not ageDict:
        raise Exception('No run folders found in %s' % (myDir))

    ageSorted = sorted(ageDict.items(), key=operator.itemgetter(1), reverse=True)  #sort dict by value, descending
    oldestRunName = ageSorted[0][0]
    oldestRunAge = ageSorted[0][1]
    if oldestRunAge <= minimumAgeDays:
        raise Exception('Cannot delete oldest run from %s due to required minimum age of %s days. (Oldest run, age: %s, %s days)' 
                        % (myDir, minimumAgeDays, oldestRunName, oldestRunAge))
    if copyInSEQCFS and not path.isdir(path.join('/n/seqcfs/sequencing/analysis_finished/',oldestRunName)):
        raise Exception('Attempt to delete run in %s which has no copy in /n/seqcfs/sequencing/analysis_finished: %s (age: %s days)' 
                        % (myDir, oldestRunName, oldestRunAge))
    if verbose: print 'Deleting oldest run (%s, age %s days) from %s ...' % (oldestRunName, oldestRunAge, myDir)
    shutil.rmtree(path.join(myDir, oldestRunName), ignore_errors=True)

def deleteOldRuns(myDir, maxDays, copyInSEQCFS = True, verbose = False):
    if verbose: print '\n(deleteOldRuns):  Looking for runs older than %s days in %s to delete ...' % (maxDays, myDir)

    if (maxDays < 40 and re.search('ngsdata', myDir)) \
            or (maxDays < 120 and re.search('analysis_in_progress', myDir)):
        raise Exception('Unexpected maxDays, myDir parameters: "%s", "%s"' % (maxDays, myDir))
    elif re.search('analysis_finished', myDir):
        raise Exception('Runs in /n/seqcfs/sequencing/analysis_finished should be deleted manually after retention of >= 2 years')

    numDeleted = 0
    for item in os.listdir(myDir):
        if runNameMatch(item):
            runName = item
            runPath = path.join(myDir,runName)
            elapsedDays = ageInDays(runPath)
            if elapsedDays > maxDays:  #mark run for deletion  (after debugging, change this to an actual delete)
                if copyInSEQCFS and not path.isdir(path.join('/n/seqcfs/sequencing/analysis_finished/',runName)):
                    raise Exception('Attempt to delete run in %s which has no copy in /n/seqcfs/sequencing/analysis_finished: %s (age: %s days)' 
                        % (myDir, runName, elapsedDays))
                #newRunPath = path.join(myDir,runName + '_ToDelete')
                #if verbose: print '  Renaming %s to %s (elapsed: %s days)' % (runPath, newRunPath, elapsedDays)
                #os.rename(runPath, newRunPath)
                if verbose:
                    print '  Deleting ' + runPath
                shutil.rmtree(runPath, ignore_errors=True)
                numDeleted += 1
    if verbose:
        if numDeleted == 0:
            print '  Found none.'
        else:
            print '  Deleted %s folders in %s' % (numDeleted, myDir)

def moveOldPrimaryToArchive(maxDaysInPrimary=20, verbose=False):
    primaryDir = '/n/illumina01/primary_data'
    archiveDir = '/n/illumina01/archive/primary_data'

    if verbose: print '\n(moveOldPrimaryToArchive):  Looking for primary_data runs older than %s days to move to archive folder ...' % maxDaysInPrimary

    numMoved = 0
    for item in os.listdir(primaryDir):
        if runNameMatch(item):
            runName = item
            runPath = path.join(primaryDir,runName)
            elapsedDays = ageInDays(runPath)
            if elapsedDays > maxDaysInPrimary:  #move run to archive folder
                newRunPath = path.join(archiveDir,runName)
                if verbose: print '  Moving %s to %s (elapsed: %s days)' % (runPath, newRunPath, elapsedDays)
                shutil.move(runPath, newRunPath)
                numMoved += 1
    if verbose:
        if numMoved == 0:
            print '  Found none.'
        else:
            print '  Moved %s run folders in %s to %s' % (numMoved, primaryDir, archiveDir)

def reportDiskUsage(dirList):
    message = ''
    for myDir in dirList:
        perc = diskPercentUsage(myDir)
        print '\n(reportDiskUsage):  Disk usage for %s: %.2f %%' % (myDir, perc)
        if perc > 90.0:
            message += 'Disk usage for %s: %.2f %%\n' % (myDir, perc)

    if message:
        hUtil.email(hSettings.NOTIFY_EMAILS, 'SeqMem Warning: disk usage > 90%', message)
    
