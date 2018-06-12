import math
import numpy as np

from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

import treenode as tn

class TreeAnalyzer():

    def __init__(self, tree):
        self.features = [tn.TreeNode.getLpValue, tn.TreeNode.getDepth]
        #self.features = [tn.TreeNode.getLpValue]
        self.nfeatures = len(self.features)
        #self.labels = [tn.TreeNode.getSubTreeSize, loglabel(tn.TreeNode.getSubTreeSize)]  
        #self.labels = [tn.TreeNode.getSubTreeSize]  
        self.labels = [loglabel(tn.TreeNode.getSubTreeSize)]  
        self.nlabels = len(self.labels)
        self.root = tree.root
        assert(self.root is not None)
        self.ninnernodes = (self.root.subtreesize)//2
        #X will store the features
        self.X = np.zeros((self.ninnernodes, self.nfeatures))
        #y will store the size of the subtree at that node
        self.y = np.zeros((self.ninnernodes, self.nlabels))
        self.analyzetree()

    #we do a raversal of the tree and collect labels and features in y and X
    def analyzetree(self):
        #we traverse the tree and build X and y
        nodeindex = 0
        for node in self.root:
            #we do not take leaves as data points
            if node.isLeaf() is False:
                #we collect all labels
                for i, l in enumerate(self.labels):
                    self.y[nodeindex][i] = l(node)
                #we collect each feature
                for i, f in enumerate(self.features):
                    self.X[nodeindex][i]= f(node) 
                nodeindex += 1
        assert nodeindex == self.ninnernodes, "nodeindex = {}, self.ninnernodes = {}"\
            .format(nodeindex, self.ninnernodes)

    def plotdata(self):
        if self.nfeatures == 1:
            plt.scatter(self.X[:, 0], self.y[:,0], cmap='Greens')
        else: 
            ax = plt.axes(projection='3d')
            ax.scatter3D(self.X[:, 0], self.X[:, 1], self.y[:,0], cmap='Greens')
            #plt.scatter(self.X[:, 0], self.y[:,0], c = self.X[:, 1])
        plt.show()

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

def loglabel(label):
    return lambda x: math.log(label(x))
