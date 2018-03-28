import plot as p
from cmath import sqrt

def sampleTree(tree,samplenum,SampleMethod,filename,debug,seed):
    print("Sampling tree...")
    if SampleMethod.genMethod == "$uniform$":
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
    confidenceRadii = calculateConfidenceRadii(sampleSet)
    return (sampleSet,sampleEstimates,confidenceRadii)

def sampleStats(treesize,estimates,radii,filename,bias,SampleMethod):
    average = estimates[-1]
    print("{} - {}".format(SampleMethod.branchType,SampleMethod.genMethod))
    print("Average sample:",average,sep='\t\t')
    print("Confidence radius:",radii[-1].real,sep='\t')
    print("Actual size:",treesize,sep='\t\t')
    print("Err of Ave:",abs(round(100*(treesize-average)/(treesize+bias),2)),sep='\t\t')

def calculateConfidenceRadii(sampleSet):
    print("Calculating Confidence Radii...")
    
    confidenceRadii = []
    weightSum = 0
    mean = 0
    prevmean = 0
    Sn = 0
    for sample in sampleSet:
        weightSum += sample.totalPhi
        prevmean = mean
        mean = prevmean + (sample.totalPhi / weightSum) * (sample.totalSize - prevmean)
        Sn += sample.totalPhi * (sample.totalSize - prevmean) * (sample.totalSize - mean)
        variance = sqrt(Sn/weightSum)
        confidenceRadii.append( abs(1 - weightSum) * (variance / sqrt(0.01)) )
    return confidenceRadii
