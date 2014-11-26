#!/usr/bin/env python
#===============================================================================
## \file convert.py
# \brief
# \b Precision Converter
# This is a converter for precision consistency in Fortran
# \author
# Marc Joos <marc.joos@cea.fr>
# \copyright
# Copyrights 2014, CEA.
# This file is distributed under the CeCILL-A & GNU/GPL licenses, see
# <http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html> and
# <http://www.gnu.org/licenses/>
# \date
# \b created:          11-25-2014
# \b last \b modified: 11-26-2014
#===============================================================================
import os, re, sys, shutil, argparse

bold  = "\033[1m"
reset = "\033[0;0m"

class File:
    def __init__(self, frname, precision=r"d0", verbose=False):
        self.frname = frname
        self.fwname = frname
        self.precision = precision
        self.verbose = verbose

    def _getSource(self):
        f = open(self.frname)
        self.lines = f.readlines()
        f.close()

    def _writeSource(self, fwname=""):
        if fwname != "": self.fwname = fwname
        f = open(self.fwname, 'w')
        f.writelines(self.newlines)
        f.close()

    def _checkPrecision(self):
        listPrec = ['d0', 'q0', '_sp', '_dp', '_qp']
        try:
            assert self.precision in listPrec
        except AssertionError:
            print(bold + "Error:" + reset + \
            "The given precision has to be in [" + ", ".join(listPrec) + "]")
            sys.exit(0)

    def sourceConverter(self, fwname=""):
        # If there was no end of the line character (\n) we would need to check
        # if this is the end of the line (something like ([^dq\_0-9]|$)
        self._checkPrecision()
        self._getSource()
        self.newlines = []
        edit = False
        regex = re.compile(r'(\d*\.\d*)([^dq\_0-9])')
        for i, line in enumerate(self.lines):
            search = regex.findall(line)
            if search != []: 
                edit = True
                newline = regex.sub(r'\g<1>'+ self.precision + r'\g<2>', line)
                self.newlines.append(newline)
                if self.verbose:
                    print(bold + 'The line #%d:' + reset + '\n %s' \
                              %(i,line[:-1]))
                    print(bold + 'will be replace by:'+ reset)
                    print('%s' %newline[:-1])
            else:
                self.newlines.append(line)
        if not edit and self.verbose: print('Nothing to be done')
        self._writeSource(fwname)

class FileTree:
    def __init__(self, inputDir="./", tmpRoot=None):
        self.dir = inputDir
        self.tmpRoot = tmpRoot
        if self.tmpRoot:
            self.tmp = True
        else:
            self.tmp = False

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

    def createTmpTree(self):
        self.tmpTree = self._removeTrailingDot(self.listDirs)
        workDir = os.getcwd()
        npardir = self.tmpRoot.count('../')
        if npardir > 0:
            workDirRoot = "/".join(workDir.split('/')[:-npardir]) + '/'
            print self._removeTrailingDot([self.tmpRoot])
            workDirRoot += self._removeTrailingDot([self.tmpRoot])[0]
        else:
            workDirRoot = workDir + '/' + self.tmpRoot
        for dir_ in self.tmpTree:
            try:
                os.makedirs(workDirRoot + dir_)
            except OSError:
                pass
        for i, dir_ in enumerate(self.tmpTree):
            for file_ in self.listFiles[i]:
                shutil.copy(self.listDirs[i] + '/' + file_, dir_ + '/' + file_)
        
    def convertAllFiles(self, tmpFile=False, precision="d0", verbose=False):
        tree = (self.tmpTree if self.tmp else self.listDirs)
        for i, dir_ in enumerate(tree):
            for file_ in self.listFiles[i]:
                ftc = File(dir_ + '/' + file_, precision=precision \
                               , verbose=verbose)
                fwrite = ('tmp_' if tmpFile else '') + file_
                if verbose: print("In file: " + file_)
                ftc.sourceConverter(dir_ + '/'  + fwrite)
        

def main():
    parser = argparse.ArgumentParser(description="Precision Converter: a converter for precision consistency in Fortran")
    parser.add_argument("--path=", "-p", dest="path", type=str, default="./" \
                            , help="source directory")
    parser.add_argument("--precision=", "-P", dest="precision", type=str \
                            , default="d0", help="precision suffix; must be in ['d0', 'q0', '_sp', '_dp', '_qp']")
    parser.add_argument("--tmpdir=", "-t", dest="tmpdir", type=str \
                            , default="./", help="If set, use the given path as a temporary directory to store and convert the source files")
    parser.add_argument("--tmpfile", "-T", dest="tmpfile", action="store_true" \
                            , help="If set, write converted files in temporary files (starting with the prefix 'tmp_')")
    parser.add_argument("--verbose", "-v", dest="verbose", action="store_true" \
                            , help="verbose mode")
    args = parser.parse_args()
    path, precision = args.path, args.precision
    tmpdir, tmpfile = args.tmpdir, args.tmpfile
    verbose         = args.verbose

    listPrec = ['d0', 'q0', '_sp', '_dp', '_qp']
    try:
        assert precision in listPrec
    except AssertionError:
        print(bold + "Error:" + reset + \
        "The given precision has to be in [" + ", ".join(listPrec) + "]")
        sys.exit(0)

    tree = FileTree(path, tmpRoot=tmpdir)
    tree.listFiles()
    if verbose:
        print(bold + 'The following files will be converted:' + reset)
        for i, dir_ in enumerate(tree.listDirs):
            for file_ in tree.listFiles[i]:
                print(dir_ + '/' + file_)
    if tmpdir:
        tree.createTmpTree()
    tree.convertAllFiles(tmpFile=tmpfile, precision=precision, verbose=verbose)

if __name__ == "__main__":
    main()
