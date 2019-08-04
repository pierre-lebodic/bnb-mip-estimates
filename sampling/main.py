#!/usr/bin/env python3

import argparse
import sys
import copy

import readtree as rt
import sampletree as st
import branchclasses as bc
import samplegenerators as sg
import progressmeasure as pm
import plot as p
import textwrap
import logging

logging.basicConfig(format='[%(filename)s on %(asctime)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S', stream=sys.stdout)

epilog="""
Usage Examples
==============

## 1.

Process the leaves in the order in which SCIP finds them ('-o' option). Then use --debug to also write out additional files
such as a probs file that contains the leaf counts.

./main.py -f ../trees/abc/small/blend2.abc 1000000 --debug -o --method 1 -w

NOTE: It is necessary to specify -w because otherwise, the tree is not processed (sampled).
"""

parser = argparse.ArgumentParser(
    epilog=textwrap.dedent(epilog),
    formatter_class = argparse.RawDescriptionHelpFormatter
    )
source = parser.add_mutually_exclusive_group(required=True)
parser.add_argument("-r","--replacement",help="samples tree with replacement",action="store_true")
parser.add_argument("-D","--debug",help="outputs debug files",action="store_true")
parser.add_argument("-e","--expsmoothing",help="use doubly exponential smoothing",action="store_true")
parser.add_argument("-g","--graph",help="outputs graphs",action="count")
parser.add_argument("-t","--tree_based",help="finds sample based on tree traversal",action="store_true")
parser.add_argument("-o","--online",help="finds samples in the order SCIP finds them",action="store_true")
parser.add_argument("-u","--uniform",help="leaves sampled uniformly",action="store_true")
parser.add_argument("-w","--window",help="use a rolling window",action="store_true")
parser.add_argument("-z","--zero_phi",type=float,default=0.9,help="dictates phi value at 0 gain nodes")
parser.add_argument("-p","--test_phi",help="dumps phi/real ratio values into a file",action="store_true")
parser.add_argument("--method",type=int,choices=[0,1,2],default=0,help="0 - Biased Phi; 1 - Even; 2 - All")
parser.add_argument("--bias",type=int,default=0,help="bias the relative error values")
parser.add_argument("--seed",type=int,default=0,help="seed for shuffling of uniform/tree based leaf list")
parser.add_argument("-m","--modeltree-num",dest="modeltree_num",type=int,default=-1,
                    help="number of samples to build model tree (can be smaller than sample number)")
parser.add_argument("--windowsize",type=int,default=None,help="the size of the rolling window")
parser.add_argument("--windowacc", help="compute acceleration in the window", action = "store_true")
parser.add_argument("--alpha",type=float,default=0.1,help="the smoothing coefficient for (doubly) exp smoothing")
parser.add_argument("--beta",type=float,default=0.1,help="the trend smoothing coefficient for doubly exp smoothing")
parser.add_argument("sample_number",type=int,help="number of samples")
parser.add_argument("--confidence-level",type=float,dest="confidence_level",default=0.90,help="How strong should the confidence level of the confidence interval be? Values between 0 and 1")
parser.add_argument("--confidence-noplot",dest="confidence_noplot",help="Should the confidence interval be hidden in the plot?",action="store_true")
parser.add_argument("--stds-not-weighted",dest="stds_not_weighted",help="Should the confidence interval not be weighted by progress of tree exploration?",action="store_true")
parser.add_argument("--progress",dest="progress_measure",help="Plot the progress measure",action="store_true")
parser.add_argument("--avg-error",dest="avg_error",help="Compute the average error")
parser.add_argument("--mape",dest="mape",help="File to store mean errors for tree size estimates")
source.add_argument("-f","--filename",help="abc file to process")
source.add_argument("--svb",nargs=3,type=int,help="Generate an SVB tree with values [left] [right] [gap]")
source.add_argument("--mvb",nargs=2,help="Generate an MVB tree with vars from [file] [gap]")
source.add_argument("--gvb",nargs=2,help="Generate an GVB tree with vars from [file] [gap]")
args = parser.parse_args()

if not args.svb is None:
    tree = rt.readSVBTree(args.svb[0],args.svb[1],args.svb[2])
    args.filename = "svb_{}_{}_{}".format(args.svb[0],args.svb[1],args.svb[2])

elif not args.mvb is None:
    gap = int(args.mvb[1])
    f = open(args.mvb[0])
    variables = []
    for line in f:
        l,r,*_ = map(int,line.split()) # mvb can take gvb inputs: the lim value is discarded into *_
        variables.append((l,r))
    args.filename = "mvb_{}_{}".format(args.mvb[0].rsplit('/',1)[-1],gap)
    tree = rt.readMVBTree(gap,variables)

elif not args.gvb is None:
    gap = int(args.gvb[1])
    f = open(args.gvb[0])
    variables = []
    for line in f:
        l,r,lim = map(int,line.split()) # gvb CANNOT take mvb input
        variables.append(((l,r),lim))
    args.filename = "gvb_{}_{}".format(args.gvb[0].rsplit('/',1)[-1],gap)
    tree = rt.readGVBTree(gap,variables)

else:
    tree = rt.readTree(args.filename,args.zero_phi)
    # Checking tree
    print("Checking tree: {}".format(tree.check()))
    args.filename = args.filename.rsplit('.',1)[0] # strip .abc

if args.test_phi:
    z = open("{}.phitest".format(args.filename),'w')
    nodecount = 0
    phierroracc = 0
    evenerroracc = 0
    simpleperr = 0
    simpleeerr = 0
    numleavesacc = 0
    #sumweights = 0
    for node in tree.root:
        if node.gains[0] is not None:
            nodecount += 1
            leavesfromnode = (node.subtreesize + 1)/2
            numleavesacc += leavesfromnode
            phierroracc += abs(node.phi[0]-node.realRatio[0]) * leavesfromnode
            evenerroracc += abs(0.5-node.realRatio[0]) * leavesfromnode
            simpleperr += abs(node.phi[0]-node.realRatio[0])
            simpleeerr += abs(0.5-node.realRatio[0])
            #phierroracc += abs(node.phi[0]-node.realRatio[0])/2**node.depth
            #evenerroracc += abs(0.5-node.realRatio[0])/2**node.depth
            #sumweights += 1/2**node.depth
            z.write("{} {} {} {} {}\n".format(node.num,node.parent.num,node.phi,node.realRatio,node.gains))
    phierroracc /= numleavesacc
    evenerroracc /= numleavesacc
    simpleperr /= nodecount
    simpleeerr /= nodecount
    #phierroracc /= sumweights
    #evenerroracc /= sumweights
    print("wphi error: {}\nwevn error: {}\nsphi error: {}\nsevn error: {}\n".format(phierroracc,evenerroracc,simpleperr,simpleeerr))

branchingMethods = [bc.BiasedPhi,bc.Evenly]
if not args.method == 2:
    branchingMethods = [branchingMethods[args.method]]

generators = []
if args.tree_based:
    generators.append(sg.TreeBasedSG)
if args.online:
    generators.append(sg.OnlineBasedSG)
if args.uniform:
    generators.append(sg.UniformSG)

#we generate the set of methods to use:
methods = []
for BranchClass in branchingMethods:
    for GenClass in generators:
        methods.append(GenClass(BranchClass,args.replacement))
#we generate possible modifiers to these methods:
addmethods = []
if args.window:
    for oldmethod in methods:
        newmethod = copy.copy(oldmethod)
        newmethod.forecast = "window"
        newmethod.progressmeasure = "totalphi"
        newmethod.windowsize = args.windowsize
        newmethod.withacceleration = args.windowacc
        newmethod.colour = 'k'
        addmethods.append(newmethod)
if args.expsmoothing:
    for oldmethod in methods:
        newmethod = copy.copy(oldmethod)
        newmethod.forecast = "expsmoothing"
        newmethod.progressmeasure = "totalphi"
        newmethod.alpha = args.alpha
        newmethod.beta = args.beta
        newmethod.colour = 'y'
        addmethods.append(newmethod)

#methods.extend(addmethods)
methods = addmethods

for method in generators:
    print(method)

for method in methods:
        samples, estimates, stds = st.sampleTree(tree,args.sample_number,method,args.filename,args.debug,args.seed,args.stds_not_weighted)

        # Plots a graph of the progress measures over time
        if args.progress_measure is True:
          progress = [0]
          for sample in samples:
            progress.append(progress[-1] + sample.totalPhi)
          p.plotProgress(progress, str(method))

        # Outputs information about the mean errors in the tree size estimations
        # compared to the true number of nodes in the tree
        if args.mape is not None and tree.numNodes:
          error = 0.0
          error_over = 0.0
          error_under = 0.0
          for i in range(100, len(estimates)):
            error += 1.0 / (len(estimates) - 100) * abs(estimates[i] - tree.numNodes)
            error_over += 1.0 / (len(estimates) - 100) * max(0, estimates[i] - tree.numNodes)
            error_under += 1.0 / (len(estimates) - 100) * max(0, tree.numNodes - estimates[i])
          print('Printing error results into {}'.format(args.mape))
          with open(args.mape, 'a') as outfile:
            print('{} {} {} {}'.format(tree.numNodes, error / tree.numNodes, error_over / tree.numNodes, error_under / tree.numNodes), file=outfile)

        # Outputs information about the accuracy of the progress measurements
        if args.avg_error is not None:
          error = 0.0
          error_over = 0.0
          error_under = 0.0
          progress = 0.0
          for sample in samples:
            progress += sample.totalPhi
            actualProgress = min(1.0, sample.nodesVisited / tree.numNodes)
            #print("progress: {}, actual: {}. vis = {}, total = {}".format(progress, actualProgress, sample.nodesVisited, tree.numNodes))
            error += abs(progress - actualProgress)
            if progress > actualProgress: error_over += progress - actualProgress
            else: error_under += actualProgress - progress
          error /= len(samples)
          print("Method: {}, Average Error: {}".format(str(method), error))
          with open(args.avg_error, 'a') as outfile:
            print("{:d} {:f}".format(tree.numNodes, error), file=outfile)

        st.sampleStats(tree.root.subtreesize,estimates,stds,args.filename,args.bias,method)
        if args.graph is not None:
            p.plotEstimates(estimates,stds,method,GenClass,tree.root.subtreesize,args.filename,sys.argv[1][1:],args.seed,args.confidence_level,args.confidence_noplot)
            if args.graph >= 2:
                if method.genMethod == "online":
                    p.plotSeenNodes(samples,tree.root.subtreesize,args.filename,method)
                p.plotDepths(samples,args.filename,method)
                p.plotSingleEstimates(samples,tree.root.subtreesize,args.filename,method)
                p.plotTreeProfile(samples, args.filename, method, args.modeltree_num)

# Plot additional progress measures
if args.progress_measure is True:

  # Plot the true / actual progress and the dual gap
  tree.genLeafList()
  tree.leafList.sort(key=(lambda x: x.nodesVisited))
  actualSizes = [0]
  for i, leaf in enumerate(tree.leafList):
    actualSizes.append(min(1.0, leaf.nodesVisited / tree.numNodes))
  p.plotProgress(actualSizes, "actual")


# if args.graph is not None or args.progress_measure is not None:
#   p.reveal()
