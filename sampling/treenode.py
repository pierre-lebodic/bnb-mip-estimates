from math import sqrt

class TreeNode:

    def __init__(self, num, parent):
        self.num = num #number in which the node appears in vbc file (root -> 0)
        self.parent = parent
        self.subtreesize = None
        self.leftorright = None # Is this node the left or right child of its parent? 0 for left, 1 for right
        self.children = []
        self.lpValue = None
        self.firstlpValue = None
        self.gains = [None, None]
        self.depth = None
        self.phi = [None, None] # stores [phi^-l, phi^-r]
        self.realRatio = [None, None]
        self.totalPhi = 1 # the probability/weight of a leaf
        self.totalSize = 1 # the size estimated by this leaf
        self.probsum = 1 # used for sampling without replacement
        self.ready = False # used in  "online" sampling
        self.online = 1e+20 # Stores the tree size at the time this node was ready
        self.leaf = False
        self.curGap = 0
        self.nodesVisited = 1e+20 # The number of nodes visited up to (including) this one
        self.ssg = -1 # The Subtree Sum Gap when this node was processed
        self.step = -1 # the last step at which this node has been updated

    def __iter__(self):
        yield self
        for child in self.children:
            for node in child:
                yield node

    def addChild(self, child):
        self.children.append(child)
        self.children[-1].leftorright = len(self.children)-1

    def addlpValue(self,value):
        if self.lpValue is None:
            self.firstlpValue = value
        self.lpValue = value

    def addGains(self):
        """
        Sets the half of the gains of the node's PARENT
        """
        if self.lpValue is None or self.parent.lpValue is None:
            return
        self.parent.gains[self.leftorright] = self.lpValue - self.parent.lpValue

    def addDepth(self, depth):
        self.depth = depth

    def calcRealRatio(self):
        """
        Calculates the balance of left and right subtrees,
        i.e. what phi attempts to approximate
        """
        if self.children == []:
            return
        left  = self.children[0].subtreesize/(self.subtreesize-1)
        right = self.children[1].subtreesize/(self.subtreesize-1)
        self.realRatio = [left,right]

    def calcSubTreeSize(self):
        if self.children == []:
            self.subtreesize = 1
            return 1
        else:
            size = 1 + self.children[0].calcSubTreeSize() + self.children[1].calcSubTreeSize()
            self.subtreesize = size
            self.calcRealRatio()
            return size

    def addPhi(self,zeroPhi):
        for i in range(2):
            if self.gains[i] is None or self.gains[i] < 0:
                return # if the gains are not ready, return; they will be ready later
        if self.gains[0] > self.gains[1]: # maintain left gain <= right gain
            self.gains[0], self.gains[1] = self.gains[1], self.gains[0]
            self.children[0], self.children[1] = self.children[1], self.children[0]
            self.children[0].leftorright = 0
            self.children[1].leftorright = 1
        l = self.gains[0]
        r = self.gains[1]
        if l < 1e+20 and r > 1e+19:
            self.phi = [zeroPhi,1-zeroPhi]
            return
        if l == r:
            self.phi = [0.5,0.5]
            return
        elif l == 0 or r == 0:
            self.phi = [zeroPhi,1-zeroPhi]
            return
        lr = l/r
        itr = 164
        x = 2
        for j in range(itr):
            x = 1 + 1/(x**lr - 1)
        self.phi = [1-1/x, 1/x]

    def markReady(self,numNodes, upperBound=0, lowerBound=0):
        """
        Used to determine online order of leaves
        """
        if self.phi != [None,None] and (self.parent.ready == True):
            self.ready = True
            for child in self.children:
                child.markReady(numNodes, upperBound, lowerBound)
        elif self.leaf == True:
            self.online = numNodes

    def killNode(self):
        """
        Used to adjust the tree so that a leaf is not sampled twice when
        sampling using the tree-based sampling without replacement
        """
        self.dead = True
        if self.num == 1:
            return
        if self.parent.children[self.leftorright-1].dead == True:
            self.parent.killNode()
        return

    def unKillAll(self):
        self.dead = False
        if self.children != []:
            self.children[0].unKillAll()
            self.children[1].unKillAll()

    def cascadePhi(self,phiBased):
        """
        Propogates phi values down the tree
        For leaves, totalSize is their individual estimate of the tree size
        and totalPhi is their probability/weight
        """
        if self.num == 1:
            self.probsum = 1
        if self.children != []:
            if phiBased:
                phi = self.phi
            else:
                phi = [0.5,0.5]
            for i in range(2):
                self.children[i].totalPhi = self.totalPhi * phi[i]
                self.children[i].probsum = self.children[i].totalPhi # used in tree-based sampling
                self.children[i].totalSize = self.totalSize + 1/self.children[i].totalPhi
                self.children[i].cascadePhi(phiBased)

    def genLeaves(self,leafList):
        if self.children == []:
            if self.lpValue is None:
                self.lpValue = 1e+20
            leafList.append(self)
            #print('Found leaf -- node {} is a leaf. self.leaf = {}, self.online = {}. self.nodesVisited = {}'.format(self.num, self.leaf, self.online, self.nodesVisited))
            #assert self.leaf == True
        else:
            self.children[0].genLeaves(leafList)
            self.children[1].genLeaves(leafList)

    def checkNode(self):
        if self.depth > 0:
            # every non root node must have a parent
            if self.parent is None:
                return False
            if self.parent.children == []:
                return False

            if self.parent.children[self.leftorright] != self:
                return False

        if self.children == []:
            return True
        else:
            return self.children[0].checkNode() and self.children[1].checkNode()


class Tree:

    def __init__(self,root):
        self.root = root
        self.leafList = []

    def genLeafList(self):
        self.leafList = []
        self.root.genLeaves(self.leafList)

    def check(self):
        return self.root.checkNode()
