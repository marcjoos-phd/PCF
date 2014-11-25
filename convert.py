import re

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
