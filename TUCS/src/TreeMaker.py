from array import array

# typecodes in ROOT trees and Python arrays
_tcode = {'char':1,'short':2,'unsigned short':3,'int':4,'unsigned int':5,'float':6,'double':7, 'object': 8}
_tcode.update({'C':1,'S':2,'s':3,'I':4,'i':5,'F':6,'D':7,'J':8})
_tcodeToPython = {1:'c',2:'h',3:'H',4:'i',5:'I',6:'f',7:'d',8:'j'}
_tcodeToRoot = {1:'C',2:'S',3:'s',4:'I',5:'i',6:'F',7:'D',8:'J'}

# enable strict validation of passed types? For example, if a branch is declared as int
# but the user passes a float, validation code will raise an exception
_STRICT_VALIDATION=False

class TreeMaker(object):
    def __init__(self, name, title='', compression=-1):
        self.__dict__['leaflist'] = {}
        self.__dict__['leaforder'] = []
        self.__dict__['tree'] = None
        self.__dict__['nametitle'] = (name, title)
        self.__dict__['buffers'] = {}
        self.__dict__['userattrs'] = {}
        self.__dict__['compression'] = compression

    # type should be passed as ROOT type
    def addLeaf(self, lname, ltype, indexvar=None):
        self.leaforder.append(lname)
        if lname not in self.leaflist:
            self.leaflist[lname] = (_tcode[ltype], indexvar)
        else:
            assert False,'VALIDATION ERROR: branch %s is being added multiple times'%lname
        if indexvar != None:
            self.userattrs[lname] = []
        else:
            self.userattrs[lname] = 0

    def createbuffers(self):
        from array import array
        for leaf in self.leaforder:
            #print leaf, self.leaflist[leaf][0]
            ltype = _tcodeToPython[self.leaflist[leaf][0]]
            if ltype != 'j':
                self.buffers[leaf] = array(ltype, [0])

    def create(self):
        from ROOT import TTree
        self.createbuffers()
        self.tree = TTree(*self.nametitle)
        for leaf in self.leaforder:
            ltype = _tcodeToRoot[self.leaflist[leaf][0]]
            if ltype == 'J':
                br = self.tree.Branch(leaf, self.buffers[leaf])
            elif self.leaflist[leaf][1]:
                br = self.tree.Branch(leaf, self.buffers[leaf], '%s[%s]/%s' % (leaf, self.leaflist[leaf][1], ltype))
            else:
                br = self.tree.Branch(leaf, self.buffers[leaf], '%s/%s' % (leaf, ltype))
            br.SetCompressionLevel(self.compression)
        return self.tree

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except:
            try:
                return self.__dict__['userattrs'][name]
            except KeyError:
                raise AttributeError('%s not a variable of %s' % (name, self.nametitle[0]))

    def __setattr__(self, name, val):
        if name in self.__dict__:
            self.__dict__[name] = val; return
        obj = self.userattrs.get(name)
        if obj == None:
            raise AttributeError('need to create leaf %s first with addLeaf()' % name)
        #print 'setting', name, val
        self.userattrs[name] = val
        if self.leaflist[name][0] == 8:
            self.buffers[name] = val
            if self.tree is not None:
                self.tree.GetBranch(leaf).SetAddress(val)

    def _syncvals(self):
        for leaf, val in list(self.userattrs.items()):
            #print 'top', leaf, val
            ltype = _tcodeToPython[self.leaflist[leaf][0]]
            if ltype == 'j':
                #object
                self.buffers[leaf] = val
            elif self.leaflist[leaf][1]:
                #array
                #if len(val) == 0:
                #    val = [0]
                if _STRICT_VALIDATION:
                    if len(val)>0 and val[0].__class__.__name__=='float' and ltype in ('h','H','i','I'):
                        print(('VALIDATION ERROR: integer branch',leaf,'is being filled with float point:', val))
                        assert False, 'ERROR: wrong branch type specified in FlatNtupler: a float value was passed to an integer branch'
                    nexpected = self.userattrs[self.leaflist[leaf][1]]
                    assert nexpected==len(val),'ARRAY ERROR: branch %s should be of size %s=%d, but has %d elements'%(leaf,self.leaflist[leaf][1],nexpected,len(val))
                self.buffers[leaf] = array(ltype, val)
                self.tree.GetBranch(leaf).SetAddress(self.buffers[leaf])
                #print 'was iterable', val
            else:
                # scalar
                self.buffers[leaf][0] = val
                #print self.buffers[leaf]
            #print leaf, self.buffers[leaf], val

    def clearall(self):
        for leaf, info in list(self.leaflist.items()):
            ltype = _tcodeToRoot[info[0]]
            if ltype == 'J':
                continue
            isarr = (info[1] != None)
            if isarr:
                self.__setattr__(leaf, [])
            else:
                self.__setattr__(leaf, 0)

    def fill(self):
        self._syncvals()
        self.tree.Fill()



class TreeMakerVec(object):
    def __init__(self, name, title=''):
        self.__dict__['leaflist'] = {}
        self.__dict__['leaforder'] = []
        self.__dict__['tree'] = None
        self.__dict__['nametitle'] = (name, title)
        self.__dict__['buffers'] = {}
        self.__dict__['userattrs'] = {}
##         self.__getattr__ = self.__getattr_h__
##         self.__setattr__ = self.__setattr_h__
        pass

    # type should be passed as ROOT type
    _typedict = { 'S': 'short',
                  's': 'unsigned short',
                  'I': 'int',
                  'i': 'unsigned int',
                  'F': 'float',
                  'D': 'double',
                  'L': 'long',
                  'l': 'unsigned long',
                  'C': 'string'
                  }
                  
    def addLeaf(self, lname, ltype, indexvar=None):
        import ROOT
        self.leaforder.append(lname)
        lltype = ltype.swapcase()
#        if lltype == 'S': lltype = 'H'
#        if lltype == 's': lltype = 'h'
        self.leaflist[lname] = (lltype, indexvar)
        if indexvar != None:
            self.userattrs[lname] = ROOT.std.vector(self._typedict[ltype])()
        else:
            self.userattrs[lname] = 0

    def createbuffers(self):
        from array import array
        for leaf in self.leaforder:
            #print leaf, self.leaflist[leaf][0]
            if self.leaflist[leaf][1] is None:
                ltype = self.leaflist[leaf][0]
##             ltype = self.leaflist[leaf][0].swapcase()
##             indexvar = self.leaflist[leaf][1]
                self.buffers[leaf] = array(ltype, [0])

    def create(self):
        from ROOT import TTree, AddressOf
        self.createbuffers()
        self.tree = TTree(*self.nametitle)
        for leaf in self.leaforder:
            ltype = self.leaflist[leaf][0].swapcase()
#            if ltype == 'H': ltype = 'S'
#            if ltype == 'h': ltype = 's'
            if self.leaflist[leaf][1] is not None:
                self.tree.Branch(leaf, self.userattrs[leaf])
            else:
                self.tree.Branch(leaf, self.buffers[leaf], '%s/%s' % (leaf, ltype))
        return self.tree

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except:
            try:
                return self.__dict__['userattrs'][name]
            except KeyError:
                raise AttributeError('%s not a variable of %s' % (name, self.nametitle[0]))

    def __setattr__(self, name, val):
        if name in self.__dict__:
            self.__dict__[name] = val; return
        obj = self.userattrs.get(name)
        if obj == None:
            raise AttributeError('need to create leaf %s first with addLeaf()' % name)
        self.userattrs[name] = val

    def _syncvals(self):
        for leaf, val in list(self.userattrs.items()):
            #print 'top', leaf, val
##             ltype = self.leaflist[leaf][0].swapcase()
            try:
                ltype = _tcodeToPython[self.leaflist[leaf][0]]
                if len(val) == 0:
                    pass
    ##                  val = [0]                    
    ##             self.buffers[leaf] = array(ltype, val)
    ##             print 'was iterable', val
    ##             self.tree.GetBranch(leaf).SetAddress(val)
            except TypeError:
                # scalar
                #self.buffers[leaf] = array(ltype, [val])
                self.buffers[leaf][0] = val
    ##         print self.buffers[leaf]
                #self.tree.GetBranch(leaf).SetAddress(self.buffers[leaf])
            #print leaf, self.buffers[leaf], val

    def clearall(self):
        for leaf, info in list(self.leaflist.items()):
##             ltype = info[0].swapcase()
            isarr = (info[1] is not None)
            if isarr:
                #self.setval(leaf, [0])
                #self.__setattr__(leaf, [])
                self.__getattr__(leaf).clear()
            else:
                #self.setval(leaf, 0)
                self.__setattr__(leaf, 0)

    def fill(self):
        self._syncvals()
        self.tree.Fill()
