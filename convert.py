import os, re, shutil

class File:
    def __init__(self, frname, precision=r"d0", verbose=False):
        self.frname = frname
        self.fwname = frname
        self.precision = precision
        self.verbose = verbose

    def getSource(self):
        f = open(self.frname)
        self.lines = f.readlines()
        f.close()

    def sourceConverter(self):
        # If there was no end of the line character (\n) we would need to check
        # if this is the end of the line (something like ([^dq\_0-9]|$)
        self.newlines = []
        regex = re.compile(r'(\d*\.\d*)([^dq\_0-9])')
        for i, line in enumerate(self.lines):
            search = regex.findall(line)
            if search != []: 
                newline = regex.sub(r'\g<1>'+ self.precision + r'\g<2>', line)
                self.newlines.append(newline)
                if self.verbose:
                    print('Real found in line #%d: ' %i)
                    print search
                    print('The following line:\n %s' %line)
                    print('will be replace by:')
                    print('%s' %newline)
            else:
                self.newlines.append(line)

    def writeSource(self, fwname=""):
        if fwname != "": self.fwname = fwname
        f = open(self.fwname, 'w')
        f.writelines(self.newlines)
        f.close()

class FileTree:
    def __init__(self, inputDir="./", tmp=True):
        self.dir = inputDir
        self.tmp = tmp

    def listFiles(self):
        self.listDirs = []
        self.listFiles = []
        self._listIgnore = []
        for root, dirs, files in os.walk(self.dir):
            self._listFiles(root, files)
        self._cleanFiles()

    def _listFiles(self, root, files):
        if root.split('/')[-1][0] != '.' or len(root.split('/')[-1]) == 1:
            if self._listIgnore:
                for ignore in self._listIgnore:
                    if root[:len(ignore)] == ignore:
                        return
                    else:
                        if files:
                            self.listDirs.append(root)
                            self.listFiles.append(files)
            else:
                if files:
                    self.listDirs.append(root)
                    self.listFiles.append(files)
        else:
            self._listIgnore.append(root)

    def _cleanFiles(self):
        if self.listDirs:
            for i, listFiles in enumerate(self.listFiles):
                iterList = listFiles.__iter__()
                filesToRemove = []
                for file_ in iterList:
                    if not(file_[-4:] in ['.f90', '.F90'] or \
                       file_[-2:] in ['.f', '.F']):
                        filesToRemove.append(file_)
                if filesToRemove:
                    for file_ in filesToRemove:
                        self.listFiles[i].remove(file_)
            for i, listFiles in enumerate(self.listFiles):
                if not listFiles: 
                    self.listFiles.remove(self.listFiles[i])
                    self.listDirs.remove(self.listDirs[i])

    def _removeTrailingDot(self, listDirs):
        cleanDirs = []
        trailingDot = re.compile('\.\.\/')
        for dir_ in listDirs:
            cleanDirs.append(trailingDot.sub('', dir_))
        return cleanDirs

    def createTmpTree(self, tmpRoot='./'):
        self.tmpTree = self._removeTrailingDot(self.listDirs)
        workDir = os.getcwd()
        npardir = tmpRoot.count('../')
        if npardir > 0:
            workDirRoot = "/".join(workDir.split('/')[:-npardir]) + '/'
            print self._removeTrailingDot([tmpRoot])
            workDirRoot += self._removeTrailingDot([tmpRoot])[0]
        else:
            workDirRoot = workDir + '/' + tmpRoot
        for dir_ in self.tmpTree:
            try:
                os.makedirs(workDirRoot + dir_)
            except OSError:
                pass
        for i, dir_ in enumerate(self.tmpTree):
            for file_ in self.listFiles[i]:
                shutil.copy(self.listDirs[i] + '/' + file_, dir_ + '/' + file_)
        
