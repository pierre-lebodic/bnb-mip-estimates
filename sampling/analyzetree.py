import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt

import treenode as tn

class TreeAnalyzer():

    def __init__(self, tree):
        self.features = [tn.TreeNode.getLpValue, tn.TreeNode.getDepth]
        self.label = tn.TreeNode.getSubTreeSize
        self.X = None
        self.y = None
        self.analyzetree(tree, self.label, self.features, self.y, self.X)

#we do a raversal of the tree and collect labels and features in y and X
    def analyzetree(self, tree, label, features, y, X):
        nfeatures = len(self.features)
        root = tree.root
        ninnernodes = (root.subtreesize)//2
        assert(root is not None)
        #X will store the LP bound and the depth of the node
        X = np.zeros((nfeatures,ninnernodes))
        #y will store the size of the subtree at that node
        y = np.zeros(ninnernodes)

        #we traverse the tree and build X and y
        nodeindex = 0
        for node in root:
            #we do not take leaves as data points
            if node.leaf is False:
                y[nodeindex] = label(node)
                #we collect each feature
                for i, f in enumerate(features):
                    X[i][nodeindex] = f(node) 
                nodeindex += 1
        assert nodeindex == ninnernodes

    
