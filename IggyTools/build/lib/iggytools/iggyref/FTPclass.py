import os, re, logging
import os.path as path
from iggytools.utils import util, socks
import ftplib, time, posixpath

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, 'iliadsocks', 9823)
socks.wrapmodule(ftplib)
log = logging.getLogger('iggyref')

class iggyrefFTP():
    def __init__(self, site, tempDir):
        ftp = ftplib.FTP(site, user = '', passwd = '', acct = '', timeout = 30)  #timeout in seconds
        ftp.set_debuglevel(0)
        ftp.set_pasv(True)
        ftp.login() 
        self.topDir = ftp.pwd()
        self.ftp = ftp

        util.mkdir_p(tempDir)
        self.tempDir = tempDir

    def nlst(self):
        attempts = 0
        while True:
            attempts += 1
            try:
                return self.ftp.nlst()
            except:
                if attempts > 2:
                    raise
                else:
                    time.sleep(60)

    def copyFile(self, srcFile, destFile, overwrite = True):
        srcFile = posixpath.join('/', srcFile)

        if overwrite == False and path.isfile(destFile):
            raise Exception('Request to copy to existing file with overwrite==False: ' + destFile)

        self.ftp.cwd(path.dirname(srcFile))
        files = self.nlst()
        if path.basename(srcFile) not in files:
            raise Exception('Remote file ' + srcFile + ' not found. Found files:\n'+'\n'.join(files))

        ext = path.splitext(srcFile)[1]
        if ext in ['.gz', '.2bit']:
            ascii = False
            mode = 'b'
        elif ext in ['.txt', '.fasta', '.fa', '.md5', '.list', '.dat', '.release_note', '']:
            ascii = True
            mode = ''
        else:
            raise Exception("Unrecognized file extension: '%s' in '%s'" % (ext, srcFile))

        if not path.isdir(path.dirname(destFile)): 
            util.mkdir_p(path.dirname(destFile))

        fh = open(destFile, 'w'+mode)

        def writeline(line):
            fh.write(line + '\n')

        attempts = 0
        while True:
            attempts += 1
            fh.seek(0,0) # at each attempt start writing to beginning of file
            try:
                log.info("Copying %s to %s.  Attempt: %d" % (srcFile, destFile, attempts))
                if ascii:
                    self.ftp.retrlines('RETR ' + srcFile, writeline)
                else:
                    self.ftp.retrbinary('RETR ' + srcFile, fh.write)
                break
            except:
                if attempts > 2:
                    raise
                else:
                    time.sleep(60)

        fh.close()

        self.ftp.cwd(self.topDir)

    def getDirContents(self, ftpPath, pattern = None):
        self.ftp.cwd(posixpath.join('/',ftpPath))  #move to dir, so as to get filenames without full paths
        files = self.nlst()
        self.ftp.cwd(self.topDir)
        if pattern:
            return [x for x in files if re.search(pattern,x)]
        return files

    def getTimeString(self, remoteFile):
        attempts = 0
        while True:
            attempts += 1
            try:
                res = self.ftp.sendcmd('MDTM ' + remoteFile)  #asdf
                break
            except:
                if attempts > 2:
                    raise
                else:
                    time.sleep(60)
        return res.split(' ')[1]

    def getChecksum(self, File):
        if not File.checksumFtpPath:
            return ''
        if not File.name:
            raise Exception('File.name must be set')

        tempFile = path.join(self.tempDir, File.name + '.temp')
        if path.isfile(tempFile):
            os.remove(tempFile)

        self.copyFile(posixpath.join('/',File.checksumFtpPath), tempFile)

        found = False
        fh = open(tempFile, 'r')
        for line in fh:
            if not File.checksumType or File.checksumType == 'md5' or File.checksumType == 'md5sum':
                checksum, fnameString  = line.split()
            elif File.checksumType == 'sum':
                checksum1, checksum2, fnameString = line.split()
                checksum = '_'.join([checksum1, checksum2])
            else:
                raise Exception('Unrecognized checksum type: %s (filename: %s)' % (File.checksumType, File.name))

            if re.match(r'(.*/)?' + re.escape(File.name) + r'$', fnameString):  #allow fnameString to be a path ending in File.name
                found = True
                break
        fh.close()

        if found:
            return checksum
        else:
            raise Exception('No checksum for %s found in %s' % (File.name, File.checksumFtpPath))
        
    def closeFtp(self):
        self.ftp.quit()
