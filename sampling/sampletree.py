import plot as p

def sampleTree(tree,samplenum,SampleMethod,filename,debug,seed):
    print("Sampling tree...")
    if SampleMethod.genMethod == "uniform":
        samplegen = SampleMethod.generator(tree,samplenum,seed)
    else:
        samplegen = SampleMethod.generator(tree,samplenum)
    sampleSet = []
    sampleEstimates = []
    if debug:
        debugEst = open("{}.{}.{}.est".format(filename,SampleMethod.branchType,SampleMethod.genMethod),'w')
        debugProbs = open("{}.{}.{}.probs".format(filename,SampleMethod.branchType,SampleMethod.genMethod),'w')
        debugTotal = open("{}.{}.{}.total".format(filename,SampleMethod.branchType,SampleMethod.genMethod),'w')
    averageAcc = 0
    probAcc = 0
    sampleCount = 0
    for sample in samplegen:
        sampleCount += 1
        sampleSet.append(sample)
        if SampleMethod.withReplacement:
            averageAcc += sample.totalSize
            sampleEstimates.append(averageAcc/sampleCount)
        else:
            averageAcc += sample.totalSize * sample.totalPhi
            probAcc += sample.totalPhi
            sampleEstimates.append(averageAcc/probAcc)
        if debug:
            debugEst.write(str(sample.totalSize)+"\n")
            debugProbs.write(str(sample.totalPhi)+"\n")
            debugTotal.write(str(sampleEstimates[-1])+"\n")
    return (sampleSet,sampleEstimates)

def sampleStats(treesize,estimates,filename,bias,SampleMethod):
    average = estimates[-1]
    print("{} - {}".format(SampleMethod.branchType,SampleMethod.genMethod))
    print("Average sample:",average,sep='\t')
    print("Actual size:",treesize,sep='\t')
    print("Err of Ave:",abs(round(100*(treesize-average)/(treesize+bias),2)),sep='\t')
