from random import random

class GenericBranch:

    def branch(node,num):
        raise NotImplementedError

    def getPhi(node,child):
        raise NotImplementedError

    def processLeaf(withReplacement,node):
        """
        Adjusts branching probabilities during tree-based sampling with replacement
        """
        if withReplacement == False:
            cnode = node
            while cnode.num > 0:
                cnode.probsum -= node.totalPhi
                cnode = cnode.parent


class BiasedPhi(GenericBranch):

    btype = "p_k"
    graphShape = "--"
    phiBased = True

    def branch(node,num):
        return True if num > node.children[0].probsum else False

    def getPhi(node,child):
        return node.phi[child]


class Evenly(GenericBranch):

    btype = "p_u"
    graphShape = "-"
    phiBased = False

    def branch(node,num):
        return True if num > node.children[0].probsum else False

    def getPhi(node,child):
        return 0.5
