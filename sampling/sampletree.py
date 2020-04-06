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

    # Use online tree size predictions
    if SampleMethod.forecast == "window":
      measurer = pm.RollingAverage(SampleMethod.windowsize, SampleMethod.withacceleration)
    elif SampleMethod.forecast == "expsmoothing":
      measurer = pm.DoubleExponentialSmoothing("Brown", SampleMethod.alpha, SampleMethod.beta)
    else:
      measurer = None

    if debug:
        debugEst = open("{}.{}.{}.est".format(filename,SampleMethod.branchType,SampleMethod.genMethod),'w')
        debugProbs = open("{}.{}.{}.probs".format(filename,SampleMethod.branchType,SampleMethod.genMethod),'w')
        debugTotal = open("{}.{}.{}.total".format(filename,SampleMethod.branchType,SampleMethod.genMethod),'w')

    averageAcc = 0
    probAcc = 0
    sampleCount = 0
    prev_accprogressmeasure = 0
    prev_accresourcemeasure = 0

    for sample in samplegen:
        sampleCount += 1
        sampleSet.append(sample)
        if SampleMethod.progressmeasure == "totalphi":
            # Compute new measurements
            progressmeasures.append(sample.totalPhi)
            next_accprogressmeasure = min(1, prev_accprogressmeasure + sample.totalPhi)
            next_accresourcemeasure = 2*sampleCount - 1
            resourcemeasures.append(prev_accresourcemeasure - next_accresourcemeasure)

            # Compute tree size based on new measurements
            if measurer is not None:
              sampleEstimates.append(measurer.insert(next_accprogressmeasure, next_accresourcemeasure))

            # Remember previous measurements
            prev_accprogressmeasure = next_accprogressmeasure
            prev_accresourcemeasure = next_accresourcemeasure

        elif SampleMethod.withReplacement:
            averageAcc += sample.totalSize
            sampleEstimates.append(averageAcc/sampleCount)
        else:
            averageAcc += sample.totalSize * sample.totalPhi
            probAcc += sample.totalPhi
            sampleEstimates.append(averageAcc/probAcc)
        if debug:
            debugEst.write(str(sample.totalSize)+"\n")
            debugProbs.write("{} {} {}\n".format(str(sample.totalPhi), sample.nodesVisited, sample.ssg)+"\n")
            debugTotal.write(str(sampleEstimates[-1])+"\n")

    #sampleEstimates = smooth(sampleEstimates)

    stds = calculateStds(sampleSet,notWeighted)
    writeTotal(sampleEstimates,filename,SampleMethod)
    return (sampleSet,sampleEstimates,stds)

def smooth(sampleEstimates):
  newEstimates = []
  for i in range(len(sampleEstimates)):
    newEstimates.append(min(sampleEstimates[max(0,i-49):i+1]))
  return newEstimates

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
