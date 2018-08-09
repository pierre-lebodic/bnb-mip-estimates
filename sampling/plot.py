import matplotlib.pyplot as plt
import math
from operator import itemgetter

def plotEstimates(estimates,stds,SampleMethod,GenClass,treesize,filename,cmdstr,seed,confidenceLevel,noplot):
    assert(confidenceLevel < 1)
    plt.figure(1)
    lower_ci = [estimates[i] - math.sqrt(1/(1 - confidenceLevel)) * stds[i] for i in range(len(estimates))]
    upper_ci = [estimates[i] + math.sqrt(1/(1 - confidenceLevel)) * stds[i] for i in range(len(estimates))]
    plt.plot(range(len(estimates)),estimates,SampleMethod.colour+SampleMethod.graphShape,label=str(SampleMethod))
    if( noplot == 0 ):
        plt.fill_between(range(len(estimates)), lower_ci, upper_ci, color = SampleMethod.colour, alpha = 0.4, label = "$Conf. %2.2f $"% (confidenceLevel) )
    plt.xlabel('$k$',fontsize=18)
    plt.ylabel('$E_k$',fontsize=18)
    plt.title("{}".format(filename.rsplit('/',1)[-1]))
    plt.axhline(y=treesize,color='k',linestyle='-')
    plt.ylim([0,treesize*2])
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.rc('legend',fontsize=20)
    plt.tight_layout()
    plt.savefig("{}.{}.png".format(filename,cmdstr))

def plotDepths(samples,filename,SampleMethod):
    plt.figure(2)
    depths = [sample.depth for sample in samples]
    plt.scatter(range(len(depths)),depths,s=1,alpha=0.05)
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    plt.xlabel('n')
    plt.ylabel('depth of sample n')
    plt.title('Depth of leaves')
    plt.savefig("{}.{}.{}.d.png".format(filename,SampleMethod.branchType,SampleMethod.genMethod))
    plt.close()


def getModelTreeDataFromProfile(depth2count : dict) -> dict:
    """computes relevant model tree data from a depth count map.
    """
    depthProfiles = sorted(depth2count.items(), key = itemgetter(0))
    lastfulldepth = minwaistdepth = maxwaistdepth = 0
    maxdepth = depthProfiles[-1][0]

    maxcount = 0
    for depth, count in depthProfiles:
        if count == 2 ** depth:
            lastfulldepth = depth

        if count > maxcount:
             minwaistdepth = maxwaistdepth = depth
             maxcount = count
        elif count == maxcount:
            maxwaistdepth = depth

    avgwaist = (minwaistdepth + maxwaistdepth) / 2.0
    gamma_prod = 2

    modelTreeWidths = []
    modelTreeWidths.append(1)
    estimation = 1
    for i in range(1, maxdepth + 1):
        estimation += gamma_prod
        modelTreeWidths.append(gamma_prod)
        if i < lastfulldepth:
            gamma = 2
        elif i < avgwaist:
            gamma = 2.0 - (i - lastfulldepth + 1.0)/(avgwaist - lastfulldepth + 1.0)
        else:
            gamma = 1.0 - (i - avgwaist + 1.0)/(maxdepth - avgwaist + 1.0)

        gamma_prod *= gamma

    return {
        "widths" : modelTreeWidths,
        "lastfulldepth" : lastfulldepth,
        "minwaistdepth" : minwaistdepth,
        "maxwaistdepth" : maxwaistdepth,
        "maxdepth"      : maxdepth,
        "estimation"    : estimation
    }

def plotTreeProfile(samples, filename, SampleMethod,sampleNumModelTree=-1):
    """plots a tree profile based on the samples, i.e., a histogram per depth.
    """
    nodeseen = set()
    depth2count = {}
    # collect nodes by assuming that node selection goes immediately down to a leaf/sample
    sampleNumModelTree = min(len(samples), sampleNumModelTree)
    if sampleNumModelTree == -1:
        modelTreeData = None

    for idx,s in enumerate(samples):
        assert s.children == []
        assert s not in nodeseen, "s has the number {}".format(s.num)
        parent = s
        while parent.depth is not None and parent not in nodeseen:
            nodeseen.add(parent)
            depth2count[parent.depth] = depth2count.get(parent.depth, 0) + 1
            parent = parent.parent

        if sampleNumModelTree == idx + 1:
            modelTreeData = getModelTreeDataFromProfile(depth2count)

    depths, counts = zip(*sorted(depth2count.items(), key=itemgetter(0)))
    plt.figure(2, figsize=(10,7))
    plt.plot(depths, counts, label = "samples")
    plt.title("Tree profile")
    plt.xlabel('Depth')
    plt.ylabel('Width of Tree')
    if modelTreeData is not None:
        widths =  modelTreeData["widths"]
        plt.plot(range(len(widths)), widths, label = "model tree({} samples)".format(sampleNumModelTree), linestyle='dashed')
        print("Tree Profile estimation ({} samples):".format(sampleNumModelTree))
        print("%-23s %g" %("Estimation:", modelTreeData["estimation"]))

    plt.legend(loc=2)
    plt.savefig("{}.profile.png".format(filename))
    plt.close()




def plotSingleEstimates(samples,treesize,filename,SampleMethod):
    plt.figure(2)
    estimates = [sample.totalSize for sample in samples]
    plt.scatter(range(len(estimates)),estimates,s=1,alpha=0.05)
    plt.xlim(xmin=0)
    plt.yscale('log')
    plt.xlabel('n')
    plt.ylabel('estimate of sample n')
    plt.title('Estimates of leaves')
    plt.axhline(y=treesize,color='r',linestyle='-')
    plt.savefig("{}.{}.{}.e.png".format(filename,SampleMethod.branchType,SampleMethod.genMethod))
    plt.close()

def plotSeenNodes(samples,treesize,filename,SampleMethod):
    plt.figure(2)
    seen = [sample.online if sample.online <= treesize else treesize for sample in samples]
    plt.scatter(range(len(seen)),seen,s=1)
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    plt.xlabel('n')
    plt.ylabel('nodes seen at taking of sample n')
    plt.title('Seen nodes')
    plt.axhline(y=treesize,color='r',linestyle='-')
    plt.savefig("{}.s.png".format(filename))
    plt.close()
