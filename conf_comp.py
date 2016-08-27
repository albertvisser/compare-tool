import sys
import os
# vergelijk entries in config file

# 1. toon schermpje waarin je de twee files kunt kiezen
# lees alle entries onder alle headers
# per header: sorteer de entries en zet ze daarna naast elkaar

# subroutine: lees ini file
from ConfigParser import SafeConfigParser, MissingSectionHeaderError

class MyNewConfigParser:
    def __init__(self):
        self.sections = {}
        self.garbage = []
        self.inSection = False
        self.inOption = False

    def read(self,fn):
        section = {}
        garb = []
        for x in file(fn,"r"):
            h = x[:-1]
            if h == "":
                continue
            if h.startswith("[") and h.endswith("]"):
                if len(section) > 0:
                    self.sections[secname] = section
                    section = {}
                if len(garb) > 0:
                    self.garbage.append(garb)
                    garb = []
                secname = h[1:-1]
                self.inSection = True
                continue
            elif h.startswith("#") or h.startswith(";"):
                garb.append(h)
            elif not self.inSection:
                garb.append(h)
            else:
                s = h.split("=",1)
                if len(s) == 1:
                    s.append("")
                section[s[0]] = s[1]
        if len(section) > 0:
            self.sections[secname] = section
        if len(garb) > 0:
            self.garbage.append(garb)


class MyConfigParser:
    def __init__(self):
        self.volgorde = [] # sections en begin- en eindflauwekul
        self.options = {}
        self.thisSection = None

    def read(self,fn):
        f = file(fn,"r")
        self.inSection = False
        self.inOption = False
        self.endOption = False
        self.thisOption = []
        for x in f.readlines():
            if x[0] == "#" or x[0] == ";":
                if self.inOption:
                    self.thisOption.append(x[:-1])
                elif self.inSection:
                    self.thisSection.append(x[:-1])
            elif not self.inSection:
                self.volgorde.append(x[:-1])
            elif x[0] == "[":
                self.newSection(x)
            else:
                h = x[:-1].split("=")
                if len(h) == 1:
                    h = x[:-1].split(": ")
                if len(h) == 1:
                    self.thisOption.append(x)
                else:
                    naam = h[0]
                    j = h[1].split("#")
                    if len(j) == 1:
                        j = h[1].split(";")
                    if len(j) == 1:
                        waarde = j
                        cmt = ''
                    else:
                        waarde = j[0]
                        cmt = j[0]
                    self.thisSection["volgorde"].append(naam)
                    self.thisSection[naam] = (self.thisOption,waarde,cmt)
                    self.inOption = False
            if self.thisSection != None:
                self.addSection()

    def newSection(self,x):
        if self.thisSection != None:
            self.addSection()
        self.inSection = True
        self.inOption = True
        i = x.find("]")
        h = x[1:i]
        self.thisSection = {"naam": h,"volgorde": []}
        h = x[i+1:]
        self.thisSection["regelrest"] = h

    def addSection(self):
        d = {}
        for x in self.thisSection["volgorde"]:
            d[x] = self.thisSection[x]
        self.options[self.thisSection["naam"]]= (self.thisSection["volgorde"],d)
        self.volgorde.append(self.thisSection["naam"])



class iniobj(SafeConfigParser):
    def __init__(self,fn):
        self.dlm = "#$#"
        self.fn = fn
        SafeConfigParser.init()

    def read():
        SafeConfigParser.read(self.fn)

    def list(self):
        print self.fnaam

    def write(self):
        f = file(self.fn,"W")
        SafeConfigParser.write(f)

class readini:
    def __init__(self,fn):
        self.dlm = "#$#"
        self.mld = None
        self.sections = {}
        # inlezen mru-gegevens
        s = MyNewConfigParser() # was SafeConfigParser()
        try:
            s.read(fn)
        except MissingSectionHeaderError, mld:
            self.mld = mld
            return
        else:
            pass
        sc = s.sections.keys() # was s.sections()
        sc.sort()
        for x in sc:
            op = s.sections[x].keys() # was s.options(x)
            op.sort()
            opval = {}
            for y in op:
                v = s.sections[x][y] # was s.get(x,y)
                opval[y] = v
            self.sections[x] = opval

    def listkeys(self):
        self.options = []
        h = self.sections.keys()
        h.sort()
        for x in h:
            self.options.append("%ssection%s%s" % (self.dlm,self.dlm,x))
            hh = self.sections[x].keys()
            hh.sort()
            for y in hh:
                self.options.append("%soption%s%s%s%s" % (self.dlm,self.dlm,y,self.dlm,self.sections[x][y]))

class inicomp:
    def __init__(self,f1,f2):
        self.ft = ''
        self.olist = []
        self.rlist = []
        self.llist = []
        h1 = readini(f1)
        if h1.mld is not None:
            self.ft = ('bestand "%s" is geen leesbaar ini file voor deze procedure' % f1)
            return
        h1.listkeys()
        #~ print h1.dlm,f1,h1.dlm
        #~ for x in h1.options:
            #~ print x
        h2 = readini(f2)
        if h2.mld is not None:
            self.ft =  ('bestand "%s" is geen leesbaar ini file voor deze procedure' %  f2)
            return
        h2.listkeys()
        #~ print h2.dlm,f2,h2.dlm
        #~ for x in h2.options:
            #~ print x
        i1 = 0
        i2 = 0
        while i1 < len(h1.options) and i2 < len(h2.options):
            s1 = h1.options[i1].split(h1.dlm)
            x1 = ":".join(s1[1:3])
            s2 = h2.options[i2].split(h2.dlm)
            x2 = ":".join(s2[1:3])
            if x1 < x2:
                if len(s1) < 4:
                    self.olist.append('[%s]' % s1[2])
                    self.llist.append('')
                    self.rlist.append('')
                    #~ r = ("%s: %s" % (s1[1],s1[2]))
                else:
                    self.olist.append(s1[2])
                    self.llist.append(s1[3])
                    self.rlist.append('')
                    #~ r = ("  %s %s: %s" % (s1[1],s1[2],s1[3]))
                i1 += 1
            elif x1 > x2:
                if len(s2) < 4:
                    self.olist.append('[%s]' % s2[2])
                    self.llist.append('')
                    self.rlist.append('')
                    #~ r = ("%s:                                               %s" % (s2[1],s2[2]))
                else:
                    self.olist.append(s2[2])
                    self.llist.append('')
                    self.rlist.append(s2[3])
                    r = ("  %s                                              %s: %s" % (s2[1],s2[2],s2[3]))
                i2 += 1
            if x1 == x2:
                if len(s1) < 4:
                    self.olist.append('[%s]' % s1[2])
                    self.llist.append('')
                    self.rlist.append('')
                    #~ r = ("%s: %s                  %s" % (s1[1],s1[2],s2[2]))
                else:
                    self.olist.append(s1[2])
                    self.llist.append(s1[3])
                    self.rlist.append(s2[3])
                    #~ r = ("  %s %s: %s             %s: %s" % (s1[1],s1[2],s1[3],s2[2],s2[3]))
                i1 += 1
                i2 += 1

def test_afrift():
    f1 = "afrift.ini"
    f2 = "afriftftc.ini"
    c = inicomp(f1,f2)
    for x in range(len(c.olist)):
        i = x # - 1
        print ('%20s %40s %40s' % (c.olist[i],c.llist[i],c.rlist[i]))

def test_myCP(fn):
    my = MyConfigParser()
    my.read(fn)
##    print "volgorde:"
##    for x in my.volgorde:
##        print "\t",x
##    print "options: "
##    for x in my.options.keys():
##        print "\t",x,my.options[x]
    return my

def test_myNCP(fn):
    my = MyNewConfigParser()
    my.read(fn)
    return my

def test_readini(fn):
    my = readini(fn)
    ## if my.mld is not None:
        ## print my.mld
##        self.ft = ('bestand "%s" is geen leesbaar ini file voor deze procedure' % f1)
        ## return
##    my.listkeys()
    return my

def schrijf_test(my,out):
    o = open(out,"w")
    for x in my.__dict__.keys():
        o.write(x + "\n")
        h = my.__dict__[x]
        if type(h) is list:
            for y in h:
                o.write(str(y).join(("\t","\n")))
        elif type(h) is dict:
            for y in h.keys():
                o.write(str(y).join(('\t',"\n")))
                if type(h[y]) is dict:
                    for z in h[y].keys():
                        o.write(str(z).join(('\t\t',"\n")))
                        o.write(str(h[y][z]).join(("\t\t\t","\n")))
                else:
                    o.write(str(h[y]).join(("\t\t","\n")))
        else:
            o.write(str(my.__dict__[x]).join(("\t","\n")))
    o.close()

if __name__ == "__main__":
    fn = "wincmd.ini"
    out = os.path.split(fn)[1] + "_myNCP.txt"
    my = test_myNCP(fn)
    schrijf_test(my,out)
    out = os.path.split(fn)[1]  + "_myCP.txt"
    my = test_myCP(fn)
    schrijf_test(my,out)
    sys.exit()
    for fn in ("opera6_V76.ini","testing.ini","afrift.ini"):
        ## out = fn + "_readini.txt"
        ## my = test_readini(fn)
        ## schrijf_test(my,out)
        out = fn + "_myNCP.txt"
        my = test_myNCP(fn)
        schrijf_test(my,out)
        out = fn + "_myCP.txt"
        my = test_myCP(fn)
        schrijf_test(my,out)
##    test_afrift()
