import numpy as np
from sklearn import linear_model

import treenode as tn

#we do a post-order DFS traversal of the tree
def analyzetree(tree):
    features = [tn.TreeNode.getLpValue, tn.TreeNode.getDepth]
    nfeatures = len(features)
    label = tn.TreeNode.getSubTreeSize
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
    print(y) 
    print(X) 
