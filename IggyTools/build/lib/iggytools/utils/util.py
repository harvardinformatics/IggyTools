import subprocess, sys, os, select 
import os.path as path
import shutil, errno, re, stat, platform
import hashlib, gzip, tarfile, glob
import distutils.dir_util

def reverseComp(seq):
    baseChars = 'ATCGNTAGCNatcgntagcn'
    seqDict = dict()
    for i in range(0,5) + range(10,15):
        seqDict[baseChars[i]]  = baseChars[i+5]
    seqDict['-'] = '-'
    return "".join([seqDict[base] for base in reversed(seq)])

def shquote(text):
    """Return the given text as a single, safe string in sh code.

    Note that this leaves literal newlines alone; sh and bash are fine with 
    that, but other tools may require special handling.
    """
    return "'%s'" % text.replace("'", r"'\''")

def runCmd(cmd):
    """Run shell code and yield stdout lines.
    
    This raises an Exception if exit status is non-zero or stderr is non-empty. 
    Be sure to fully iterate this or you will probably leave orphans.
    """
    BLOCK_SIZE = 4096
    p = subprocess.Popen(
        ['/bin/bash', '-c', cmd],
        shell=False,
        stdin=open('/dev/null', 'r'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdoutDone, stderrDone = False, False
    out = ''
    while not (stdoutDone and stderrDone):
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


def shell(command, outputFile, append=True):
    if append:
        mode = 'a'
    else:
        mode = 'w'
    parentDir = path.dirname(outputFile)
    if not path.isdir(parentDir):
        mkdir_p(parentDir)
    fh = open(outputFile, mode)
    fh.write('\n\n' + command + '\n\n') #write command to file
    for line in runCmd(command):
        line = line.strip()
        if line != '':
            fh.write(line + '\n') #write command output to file
            fh.flush()
    fh.close()

def errScan(logFile):
    errs = ''
    with open(logFile, 'r') as fh:
        for i, line in enumerate(fh):
            if re.search('error|exception|fail', line, re.IGNORECASE):
                errs += 'Error on Line %s: %s\n' % (i, line)
    if errs:
        raise Exception('Error(s) found in file %s: %s' % (logFile, errs))

def rsync(srcDir, targetDir, logFile):
    mkdir_p(targetDir)
    command = "rsync -av --exclude '.temp' --exclude '*.gz' %s/ %s/" % (srcDir, targetDir)
    shell(command, logFile, append=False)
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

def email(addresses, subject, message):
    if isinstance(addresses, basestring): addresses = addresses.split(',')
    for address in addresses:
        for error in runCmd("echo \"" + message + "\"|  mail -s \"" + subject + "\" " + address):
            raise(error)  #if there is anything written to stdout/stderr from this cmd, it will be an error

def append(text, filename, echo = False):
    if echo: print text
    fh = open(filename, 'a')
    fh.write(text + "\n") #append text to file                                                                                                              
    fh.close()

def copy(src, dst):  #copy a file or directory. Notes that dst is the target itself, not the parent directory. 
    try:
        #copy a directory
        shutil.copytree(src, dst)  #dst must not exist.
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            #copy a file
            shutil.copy(src, dst)  #dst can be a file or directory. If dst does not exist, it is treated as the new filename of src.
        else: raise

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

def md5Checksum(afile, blocksize=65536):
    hasher = hashlib.md5()
    fh = open(afile, 'rb')
    buf = fh.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fh.read(blocksize)
    return hasher.hexdigest()

def sumChecksum(afile):
    out = runCmd('sum ' + afile).next().rstrip()
    if re.search('error|exception|fail', out, re.IGNORECASE):
        raise Exception('Error occurred while runnig sum on %s: %s' % (afile, out))
    return '_'.join(out.split())

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

def getUserHome():
    if 'HOME' in os.environ.keys() and os.environ['HOME']: #determine user's preferences directory
        return os.environ['HOME']
    elif 'USERPROFILE' in os.environ.keys() and os.environ['USERPROFILE']:
        return os.environ['USERPROFILE']
    else:
        raise Exception('Unable to determine user home directory')

def get_3p_dirname():
    system = platform.system()
    if system == 'Linux':
        return 'linux-x86_64'
    elif system == 'Windows':
        return 'win64'
    elif system == 'Darwin':
        return 'macos-x86_64'
    else:
        raise Exception('Unrecognized system: %s' % system)
    
