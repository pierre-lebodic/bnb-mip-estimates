import argparse
import sys

import readtree as rt
import sampletree as st
import branchclasses as bc
import samplegenerators as sg
import plot as p

parser = argparse.ArgumentParser()
source = parser.add_mutually_exclusive_group(required=True)
parser.add_argument("-r","--replacement",help="samples tree with replacement",action="store_true")
parser.add_argument("-D","--debug",help="outputs debug files",action="store_true")
parser.add_argument("-g","--graph",help="outputs graphs",action="count")
parser.add_argument("-t","--tree_based",help="finds sample based on tree traversal",action="store_true")
parser.add_argument("-o","--online",help="finds samples in the order SCIP finds them",action="store_true")
parser.add_argument("-u","--uniform",help="leaves sampled uniformly",action="store_true")
parser.add_argument("-z","--zero_phi",type=float,default=0.9,help="dictates phi value at 0 gain nodes")
parser.add_argument("-p","--test_phi",help="dumps phi/real ratio values into a file",action="store_true")
parser.add_argument("--method",type=int,choices=[0,1,2],default=0,help="0 - Biased Phi; 1 - Even; 2 - All")
parser.add_argument("--bias",type=int,default=0,help="bias the relative error values")
parser.add_argument("--seed",type=str,default=0,help="seed for shuffling of uniform leaf list")
parser.add_argument("sample_number",type=int,help="number of samples")
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
for BranchClass in branchingMethods:
    for GenClass in generators:
        SampleMethod = GenClass(BranchClass,args.replacement)
        samples, estimates = st.sampleTree(tree,args.sample_number,SampleMethod,args.filename,args.debug,args.seed)
        st.sampleStats(tree.root.subtreesize,estimates,args.filename,args.bias,SampleMethod)
        if args.graph is not None:
            p.plotEstimates(estimates,SampleMethod,tree.root.subtreesize,args.filename,sys.argv[1][1:],args.seed)
            if args.graph >= 2:
                if GenClass.genMethod == "online":
                    p.plotSeenNodes(samples,tree.root.subtreesize,args.filename,SampleMethod)
                p.plotDepths(samples,args.filename,SampleMethod)
                p.plotSingleEstimates(samples,tree.root.subtreesize,args.filename,SampleMethod)
