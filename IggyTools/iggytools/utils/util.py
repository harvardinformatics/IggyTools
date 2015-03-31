import subprocess, sys, os, select, filecmp, traceback
import os.path as path
import shutil, errno, re, stat, platform
import hashlib, gzip, tarfile, glob
import distutils.dir_util
from collections import namedtuple
from contextlib import contextmanager


class Command(object):  # Run command and yield stdout lines.


    def __init__(self, cmd):
        self.p = subprocess.Popen( ['/bin/bash', '-c', cmd],
                                   shell=False,
                                   stdin=open('/dev/null', 'r'),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE )
        self.command = cmd
        self.pid = self.p.pid


    def run(self):

        p = self.p

        BLOCK_SIZE = 4096

        stdoutDone, stderrDone = False, False
        out = ''
        while not (stdoutDone and stderrDone):  # Be sure to fully iterate this or you will probably leave orphans.
            rfds, ignored, ignored2 = select.select([p.stdout.fileno(), p.stderr.fileno()], [], [])
            if p.stdout.fileno() in rfds:
                s = os.read(p.stdout.fileno(), BLOCK_SIZE)
                if s=='': stdoutDone = True
                if s:
                    i = 0
                    j = s.find('\n')
                    while j!=-1:
                        yield out + s[i:j+1]
                        out = ''
                        i = j+1
                        j = s.find('\n',i)
                    out += s[i:]
            if p.stderr.fileno() in rfds:
                s = os.read(p.stderr.fileno(), BLOCK_SIZE)
                if s=='': stderrDone = True
                if s:
                    i = 0
                    j = s.find('\n')
                    while j!=-1:
                        yield out + s[i:j+1]
                        out = ''
                        i = j+1
                        j = s.find('\n',i)
                    out += s[i:]
        if out!='':
            yield out 
        p.wait()


class Command_toFile(object):  #run command obj, exposing pid and logging both command and output to file

    def __init__(self, command, outputFile, append=True, echo=True):

        if append:
            self.mode = 'a'
        else:
            self.mode = 'w'

        parentDir = path.dirname(outputFile)
        if not path.isdir(parentDir):
            mkdir_p(parentDir)

        self.outputFile = outputFile
        self.echo = echo

        self.cmd = Command(command)
        self.pid = self.cmd.pid


    def run(self):
        fh = open(self.outputFile, self.mode)
        fh.write('\n\n' + self.cmd.command + '\n\n') #write command to file

        for line in self.cmd.run():
            line = line.strip()
            if line != '':
                fh.write(line + '\n') #write command output to file
                fh.flush()
            if self.echo: print line

        fh.close()


class Command_toStdout(object):  #run command obj, exposing pid and printing output

    def __init__(self, command):

        self.cmd = Command(command)
        self.pid = self.cmd.pid

    def run(self):
        for line in self.cmd.run():
            print line


def shquote(text):
    """Return the given text as a single, safe string in sh code.

    Note that this leaves literal newlines alone; sh and bash are fine with 
    that, but other tools may require special handling.
    """
    return "'%s'" % text.replace("'", r"'\''")


def sbatch(scriptFile):  #submit a job to slurm

    p = subprocess.Popen(
        ['/bin/bash', '-c', 'sbatch %s' % scriptFile],
        shell=False,
        stdin=open('/dev/null', 'r'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out = '\n'.join(p.communicate())  #concat stdout, stderr

    match = re.match('Submitted batch job ([0-9]+)\s*$', out)
    if match:
        return int(match.group(1))
    else:
        raise Exception('Unable to submit slurm script %s:\n  %s' % (scriptFile, out))


def printJobStatus(jobID):  

    p = subprocess.Popen(
        ['/bin/bash', '-c', 'squeue -j %s' % jobID],
        shell=False,
        stdin=open('/dev/null', 'r'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, errors = p.communicate() 

    if errors and output:
        print output
        return

    p = subprocess.Popen(
        ['/bin/bash', '-c', 'sacct -j %s' % jobID],
        shell=False,
        stdin=open('/dev/null', 'r'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )
    output, errors = p.communicate()  

    if errors:
        raise Exception('Unable to get job status for %s:\n%s' % (jobID, errors))

    print output


def errScan(logFile):  #scan a log file for error messages
    errs = ''

    with open(logFile, 'r') as fh:
        for i, line in enumerate(fh):
            if re.search('error|exception|fail', line, re.IGNORECASE):
                errs += 'Error on Line %s: %s\n' % (i, line)

    if errs:
        raise Exception('Error(s) found in file %s: %s' % (logFile, errs))


def rsync(srcDir, targetDir, logFile):
    mkdir_p(targetDir)
    command = "rsync -av --exclude '*.gz' %s/ %s/" % (srcDir, targetDir)

    s = Shell(command, logFile, append=False)
    s.run()

    errScan(logFile)


def recursiveChmod(item, filePermissions, dirPermissions):
    for root,dirs,files in os.walk(item):

        for d in dirs:
            os.chmod(path.join(root,d), dirPermissions)

        for f in files:
            os.chmod(path.join(root,f), filePermissions)


def mkdir_p(myDir):  #implements bash's mkdir -p
    if not path.isdir(myDir):
        os.makedirs(myDir)


def email(users, subject, message):  #users can be mix of email addresses and local usernames, in a list or comma-separated str

    if type(users) == str:
        users = users.split(',')

    for user in users:
        cmd = Command("echo \"" + message + "\"|  mail -s \"" + subject + "\" " + user)
        for error in cmd.run():
            raise Exception(error)  #if anything is written to stdout/stderr from this cmd, it is an error


def append(text, filename, echo = False):
    if echo: 
        print text

    fh = open(filename, 'a')
    fh.write(text + "\n") #append text to file                                                                                                              

    fh.close()


def copy(src, dst):  #copy a file or directory. Note that dst is the target itself, not the parent directory 
    mkdir_p( path.dirname(dst) )

    try:
        #copy a directory
        shutil.copytree(src, dst)  #note: dst must not exist

    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            #copy a file
            shutil.copy2(src, dst)  #dst can be a file or directory 
        else: raise


def pysync(src, dest):  #update dest with contents of src
    mkdir_p(dest)
    dcmp = filecmp.dircmp(src, dest)

    toCopy = find_missingAndDiffFiles(dcmp)

    for s, d in toCopy:
        copy(s,d)


def find_missingAndDiffFiles(dcmp, toCopy = None):
    if not toCopy:
        toCopy = list()

    print 'Examining left and right dirs: %s, %s' % (dcmp.left, dcmp.right)

    for src_itemName in dcmp.left_only:  #files and dirs that exist only in left
        srcItem_absPath = path.join(dcmp.left, src_itemName)

        if ( not re.match('^\.|.*~|.*\.gz', src_itemName) #skip dot files, emacs backup files, zip files
             and path.isfile( srcItem_absPath ) ): #item is a file, not a directory
            destItem_absPath = path.join(dcmp.right, src_itemName)
            toCopy.append( (srcItem_absPath, destItem_absPath) ) #append non-ignored files that exist only in left

    for src_itemName in dcmp.diff_files:  #files that differ in left and right
        srcItem_absPath = path.join(dcmp.left, src_itemName)
        destItem_absPath = path.join(dcmp.right, src_itemName)
        toCopy.append( (srcItem_absPath, destItem_absPath) ) #append files that differ

    for sub_dcmp in dcmp.subdirs.values():
        find_missingAndDiffFiles(sub_dcmp, toCopy)

    return toCopy


def copy_preserve_nonoverlapping(src, dst):  #Recursively copy contents of src into dst, while preserving existing dst-only files.
    distutils.dir_util.copy_tree(src, dst)


def insert(src, dst, action = 'copy', symlinks = False, ignore = None):    # Recursively move or copy files to destination, while preserving existing dst-only files.
    if action not in ['copy', 'move']:                                     # See shutil.copytree doc for info on ignore parameter
        raise Exception('Unrecognized action %s' % action)

    if not os.path.exists(dst):
        os.makedirs(dst)
        #shutil.copystat(src, dst)

    dirContents = os.listdir(src)

    if ignore:
        excluded = ignore(src, dirContents)
        dirContents = [x for x in dirContents if x not in excluded]

    for item in dirContents:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)

        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)

            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)

            except:
                pass # lchmod not available

        elif os.path.isdir(s):
            insert(s, d, action, symlinks, ignore)

        else:
            if action == 'copy':
                shutil.copy2(s, d)
            else:
                os.remove(d)
                shutil.move(s, d)


def intersect(a, b):
     return list(set(a) & set(b))


def unique(a):
     return list(set(a))


def touch(fname):
    open(fname, 'a').close()


def filestem(fname):
    return path.basename(path.splitext(fname)[0])


def md5Checksum(afile, blocksize=65536):
    hasher = hashlib.md5()

    fh = open(afile, 'rb')
    buf = fh.read(blocksize)

    while len(buf) > 0:
        hasher.update(buf)
        buf = fh.read(blocksize)

    return hasher.hexdigest()


def sumChecksum(afile):
    cmdObj = Command('sum ' + afile)
    cmd = cmdObj.run()
    out = cmd.next().rstrip()
    if re.search('error|exception|fail', out, re.IGNORECASE):
        raise Exception('Error occurred while runnig sum on %s: %s' % (afile, out))
    return '_'.join(out.split())


def reverseComp(seq):
    baseChars = 'ATCGNTAGCNatcgntagcn'
    seqDict = dict()

    for i in range(0,5) + range(10,15):
        seqDict[baseChars[i]]  = baseChars[i+5]

    seqDict['-'] = '-'

    return "".join([seqDict[base] for base in reversed(seq)])


def deleteItem(item):
    if path.isdir(item):
        shutil.rmtree(item, ignore_errors=True)

    elif path.isfile(item):
        os.remove(item)


def flatten(x):
    result = []

    for elem in x:

        if hasattr(elem, "__iter__") and not isinstance(elem, basestring):
            result.extend(flatten(elem))

        else:
            result.append(elem)

    return result


def flatlist(x): #ensure a list is passed to flatten()
    return flatten([x])


def dict2namedtuple(dictionary):
    return namedtuple('NamedTuple', dictionary.keys())(**dictionary)


def gzNotEmpty(f):

    if not path.isfile(f):
        raise Exception('File %s not found.' % f)

    if not re.search('.gz$', f, flags=re.IGNORECASE):
        raise Exception('Attempt to decompress file not ending in .gz: %s' % f)

    fh = gzip.open(f, 'rb')
    data = fh.read(100)
    fh.close()

    if data:
        return True #gz file contains data
    else:
        return False


def isGZippedFile(filename):
    if re.search(r'(?<!\.tar)\.gz$', filename, re.IGNORECASE):
        return True
    else:
        return False


def getUserHome():
    if 'HOME' in os.environ.keys() and os.environ['HOME']: #determine user's home directory
        return os.environ['HOME']

    elif 'USERPROFILE' in os.environ.keys() and os.environ['USERPROFILE']:
        return os.environ['USERPROFILE']

    else:
        raise Exception('Unable to determine user home directory')


def get_3p_dirname():
    system = platform.system()

    if re.match('linux', system, re.IGNORECASE): #matches from beg. 
        return 'linux-x86_64'

    elif re.match('windows|cygwin', system, re.IGNORECASE):
        return 'win64'

    elif re.match('darwin', system, re.IGNORECASE):
        return 'macos-x86_64'

    else:
        raise Exception('Unrecognized system: %s' % system)
    

def upperFirst(a):  #capitalize first letter of string
    return a[0].upper() + a[1:].lower()


def str2list_byComma(a):
    if type(a) == list:
        return a
    else:
        return a.split(',')

@contextmanager
def suppress_stdout():

    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull

        try:  
            yield

        finally:
            sys.stdout = old_stdout
