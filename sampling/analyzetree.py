import math
import numpy as np

from sklearn import linear_model
from sklearn import svm
from sklearn import neural_network
from sklearn import neighbors
from sklearn import model_selection
from sklearn.metrics import mean_squared_error, r2_score

from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

import treenode as tn

class TreeAnalyzer():

    def __init__(self, tree):
        self.features = []
        self.features.append(tn.TreeNode.getLpValue)
        self.features.append (tn.TreeNode.getDepth)
        self.nfeatures = len(self.features)

        self.labels = []
        #self.labels.append(tn.TreeNode.getSubTreeSize)
        self.labels.append(loglabel(tn.TreeNode.getSubTreeSize))
        self.nlabels = len(self.labels)

        self.regressions = []
        self.regressions.append(linear_model.LinearRegression)
        self.regressions.append(svm.SVR)
#        self.regressions.append(neural_network.MLPRegressor)
#        self.regressions.append(neighbors.KNeighborsRegressor)
#        self.regressions.append(neighbors.RadiusNeighborsRegressor)

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

    def regression(self, trainingratio = 1, trainingsamples = math.inf):
        assert trainingratio <= 1
        assert trainingratio > 0
        assert trainingsamples > 0

        train_size = self.ninnernodes * trainingratio
        train_size = int(min(train_size, trainingsamples))

        test_size = self.ninnernodes - train_size
        print("Using {}/{} training samples".format(train_size, self.ninnernodes))

        for yi, label in enumerate(self.labels):
            print(label.__name__)
            if trainingratio == 1:
                X_train = self.X
                X_test = self.X
                y_train = self.y
                y_test = self.y
            else:
                X_train, X_test, y_train, y_test = model_selection.train_test_split(self.X, self.y, test_size = test_size, train_size=train_size, shuffle = True, random_state=0)
            for regression in self.regressions:
                print(regression.__name__)
                regr = regression()
                regr.fit(X_train, y_train[:, yi])
                # Make predictions using the testing set
                y_pred = regr.predict(X_test)
                # The coefficients
#               print('Coefficients: \n', regr.coef_)
                # The mean squared error
                print("Mean squared error: %.2f"
                % mean_squared_error(y_test[:, yi], y_pred))
                # Explained variance score: 1 is perfect prediction
                print('Variance score: %.2f' % r2_score(y_test[:, yi], y_pred))

def loglabel(label):
    return lambda x: math.log(label(x))
