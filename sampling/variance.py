from cmath import sqrt



def calculateVariances(sampleSet):
    print("Calculating Variance...")
    variances = []
    weightSum = 0
    mean = 0
    prevmean = 0
    Sn = 0
    for sample in sampleSet:
        weightSum += sample.totalPhi
        prevmean = mean
        mean = prevmean + (sample.totalPhi / weightSum) * (sample.totalSize - prevmean)
        Sn += sample.totalPhi * (sample.totalSize - prevmean) * (sample.totalSize - mean)
        variances.append(sqrt(Sn/weightSum))
    return variances