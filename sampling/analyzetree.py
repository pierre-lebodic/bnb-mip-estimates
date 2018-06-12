import numpy as np
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

import treenode as tn

class TreeAnalyzer():

    def __init__(self, tree):
        self.features = [tn.TreeNode.getLpValue, tn.TreeNode.getDepth]
        self.label = tn.TreeNode.getSubTreeSize
        self.nfeatures = len(self.features)
        self.root = tree.root
        assert(self.root is not None)
        self.ninnernodes = (self.root.subtreesize)//2
        #X will store the features
        self.X = np.zeros((self.ninnernodes, self.nfeatures))
        #y will store the size of the subtree at that node
        self.y = np.zeros(self.ninnernodes)
        self.analyzetree()

    #we do a raversal of the tree and collect labels and features in y and X
    def analyzetree(self):
        #we traverse the tree and build X and y
        nodeindex = 0
        for node in self.root:
            #we do not take leaves as data points
            if node.isLeaf() is False:
                self.y[nodeindex] = self.label(node)
                #we collect each feature
                for i, f in enumerate(self.features):
                    self.X[nodeindex][i]= f(node) 
                nodeindex += 1
        assert nodeindex == self.ninnernodes, "nodeindex = {}, self.ninnernodes = {}"\
            .format(nodeindex, self.ninnernodes)

    def linearregression(self):
        regr = linear_model.LinearRegression()
        regr.fit(self.X, self.y)
        # Make predictions using the testing set
        ypred = regr.predict(self.X)
        # The coefficients
        print('Coefficients: \n', regr.coef_)
        # The mean squared error
        print("Mean squared error: %.2f"
        % mean_squared_error(self.y, ypred))
        # Explained variance score: 1 is perfect prediction
        print('Variance score: %.2f' % r2_score(self.y, ypred))

