import matplotlib.pyplot as plt

def plotEstimates(estimates,radii,SampleMethod,GenClass,treesize,filename,cmdstr,seed):
    plt.figure(1)
    lower_ci = [estimates[i] - radii[i].real for i in range(len(estimates))]
    upper_ci = [estimates[i] + radii[i].real for i in range(len(estimates))]
    plt.plot(range(len(estimates)),estimates,SampleMethod.colour+SampleMethod.graphShape,label=SampleMethod.branchType + " " + GenClass.genMethod)
    plt.fill_between(range(len(estimates)), lower_ci, upper_ci, color = SampleMethod.colour, alpha = 0.4, label = '$99% CI$')
    plt.xlabel('$k$',fontsize=18)
    plt.ylabel('$E_k$',fontsize=18)
    plt.title("{}".format(filename.rsplit('/',1)[-1]))
    plt.axhline(y=treesize,color='k',linestyle='-')
    plt.ylim([0,treesize*2])
    plt.legend()
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
