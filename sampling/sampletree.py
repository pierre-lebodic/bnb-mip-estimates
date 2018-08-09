import plot as p
import math

import progressmeasure as pm

def sampleTree(tree,samplenum,SampleMethod,filename,debug,seed,notWeighted):
    print("Sampling tree...")
    if SampleMethod.genMethod in ["uniform", "treebased"]:
        samplegen = SampleMethod.generator(tree,samplenum,seed)
    else:
        samplegen = SampleMethod.generator(tree,samplenum)
    sampleSet = []
    sampleEstimates = []
    progressmeasures = []
    resourcemeasures = []
    accprogressmeasures = [0]
    accresourcemeasures = [0]
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
        if SampleMethod.progressmeasure == "totalphi":
            progressmeasures.append(sample.totalPhi)
            accprogressmeasures.append(min(1,accprogressmeasures[-1] + sample.totalPhi))
            accresourcemeasures.append(2*sampleCount - 1)
            resourcemeasures.append(accresourcemeasures[-2] - accresourcemeasures[-1])
            #accresourcemeasures.append(sample.num)
            if SampleMethod.forecast == "window":
                sampleEstimates.append(pm.rollingAverageForecasting(accprogressmeasures, accresourcemeasures, SampleMethod.windowsize, SampleMethod.withacceleration))
            if SampleMethod.forecast == "expsmoothing":
               sampleEstimates.append(pm.doubleExponentialSmoothing(accprogressmeasures, accresourcemeasures, SampleMethod.alpha, SampleMethod.beta))

        elif SampleMethod.withReplacement:
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
    stds = calculateStds(sampleSet,notWeighted)
    writeTotal(sampleEstimates,filename,SampleMethod)
    return (sampleSet,sampleEstimates,stds)

def writeTotal(estimates,filename,SampleMethod):
    with open("%s.%s.%s.total" % (filename,SampleMethod.branchType,SampleMethod.genMethod), "w") as currfile:
        for estimate in estimates:
            currfile.write("{}\n".format(estimate))

def sampleStats(treesize,estimates,stds,filename,bias,SampleMethod):
    average = estimates[-1]
    print(SampleMethod)
    print("Average sample:",average,sep='\t\t')
    print("Confidence margin:",stds[-1].real,sep='\t')
    print("Actual size:",treesize,sep='\t\t')
    print("Err of Ave:",abs(round(100*(treesize-average)/(treesize+bias),2)),sep='\t\t')

def calculateStds(sampleSet,notWeighted):
    stds = []
    weightSum = 0
    mean = 0
    prevmean = 0
    Sn = 0
    for sample in sampleSet:
        weightSum += sample.totalPhi
        prevmean = mean
        mean = prevmean + (sample.totalPhi / weightSum) * (sample.totalSize - prevmean)
        Sn += sample.totalPhi * (sample.totalSize - prevmean) * (sample.totalSize - mean)
        if( notWeighted ):
            stds.append( math.sqrt(Sn/weightSum) )
        else:
            stds.append( (1-weightSum) * math.sqrt(Sn/weightSum) )
    return stds
