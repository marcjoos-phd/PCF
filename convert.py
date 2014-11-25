import re

fname = './prec.f90'
f = open(fname)
lines = f.readlines()
f.close()
# If there was no end of the line character (\n) we would need to check if 
# this is the end of the line (something like ([^dq\_0-9]|$)
regex = re.compile(r'(\d*\.\d*)([^dq\_0-9])')
for i, line in enumerate(lines):
    search = regex.findall(line)
    if search != []: 
        print('Real found in line #%d: ' %i)
        print search
        print('The following line:\n %s' %line)
        print('will be replace by:')
        newline = regex.sub(r'\g<1>d0\g<2>', line)
        print('%s' %newline)
        lines[i] = newline
nname = './new.f90'
fn = open(nname, 'w')
fn.writelines(lines)
fn.close()
