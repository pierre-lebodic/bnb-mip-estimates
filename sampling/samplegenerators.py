import random as rand

class GenericSG:

    def __init__(self,BranchClass,withReplacement,progressmeasure=None,forecast=None):
        self.withReplacement = withReplacement
        self.branch = BranchClass
        self.graphShape = self.branch.graphShape
        self.phiBased = self.branch.phiBased
        self.branchType = self.branch.btype
        self.progressmeasure = progressmeasure #if/how to build a progress measure
        self.forecast = forecast #whether to add a time-series forecasting technique

    def __str__(self):
        name = "{} {}".format(self.branchType,self.genMethod)
        for info in [self.forecast, self.progressmeasure]:
            if info is not None:
                name+=" {}".format(info)
        return self.branchType        
        #return name
        #if self.forecast == "window": return "Moving window"
        #else: return "Smoothing"

class OnlineBasedSG(GenericSG):

    colour = "r"
    genMethod = "online"

    def generator(self,tree,samplenum):
        tree.genLeafList()
        tree.root.cascadePhi(self.phiBased)
        tree.leafList.sort(key=(lambda x: x.nodesVisited))  # nodesVisited should be the 'true' online order
        for z in range(samplenum):
            if len(tree.leafList) == z or tree.leafList[z].nodesVisited > 1e+19:
                print(">Entire tree has been sampled: halting after",z,"samples.")
                break
            sample = tree.leafList[z]
            yield sample

class UniformSG(GenericSG):

    colour = "g"
    genMethod = "uniform"

    def generator(self,tree,samplenum,seed):
        tree.genLeafList()
        tree.root.cascadePhi(self.phiBased)
        rand.seed(seed)
        rand.shuffle(tree.leafList)
        for z in range(samplenum):
            if len(tree.leafList) == z and self.withReplacement == False:
                print(">Entire tree has been sampled: halting after",z,"samples.")
                break
            if self.withReplacement:
                sample = rand.choice(tree.leafList)
            else:
                sample = tree.leafList[z]
            yield sample


class TreeBasedSG(GenericSG):

    colour = "b"
    genMethod = "treebased"

    def generator(self,tree,samplenum,seed):
        rand.seed(seed)
        tree.root.cascadePhi(self.phiBased)
        tree.root.unKillAll()

        for z in range(samplenum):
            if tree.root.dead:
                print(">Entire tree has been sampled: halting after",z,"samples.")
                break
            currentnode = tree.root
            num = tree.root.probsum * rand.random()
            while currentnode.children != []:
                # there must be at least one path not yet taken
                assert not (currentnode.children[0].dead and currentnode.children[1].dead)

                # right branch
                if currentnode.children[0].dead or self.branch.branch(currentnode,num):
                    nextchild = 1
                    num -= currentnode.children[0].probsum
                # left branch
                else:
                    nextchild = 0
                currentnode = currentnode.children[nextchild]
            self.branch.processLeaf(self.withReplacement,currentnode)

            # kill the node (and probably its parents and ancestors) if we do not draw with replacement
            if not self.withReplacement:
                currentnode.killNode()
            yield currentnode
