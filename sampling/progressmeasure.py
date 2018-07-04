import math

def measureProgress(tree,samplenum,SampleMethod,seed):
    assert SampleMethod.withReplacement == False

    print("Computing progress measure on the tree...")
    if SampleMethod.genMethod == "uniform":
        samplegen = SampleMethod.generator(tree,samplenum,seed)
    else:
        samplegen = SampleMethod.generator(tree,samplenum)
    sampleSet = []
    leafphis = []

    sampleCount = 0
    for sample in samplegen:
        sampleCount += 1
        sampleSet.append(sample)
        leafphis.append(sample.totalPhi)

    return (sampleSet, leafphis)

def rollingAverageForecasting(sampleSet, progressmeasures, accresourcemeasures, windowsize = None):
    if windowsize == None:
        windowsize = math.inf
    assert windowsize == None or windowsize >= 1
    assert len(sampleSet) == len(progressmeasures)
    #we compute the accumulated progress measure
    accprogressmeasures = []
    currentprogress = 0
    for progress in progressmeasures:
        currentprogress += progress
        accprogressmeasures.append(currentprogress)

    estimates = []

    #for convenience we add dummy data at index 0:
    progressmeasures.insert(0, 0)
    accprogressmeasures.insert(0, 0)
    accresourcemeasures.insert(0, 0)

    #we compute the average progress measure of all samples so far
    for i, (progress, accprogress, accresource) in enumerate(zip(progressmeasures, accprogressmeasures, accresourcemeasures)):
       if i == 0:
           continue
       assert progress > 0
       assert progress <= 1
       assert accprogress > 0
       assert accresource > 0
       if math.isclose(accprogress, 1) and accprogress > 1:
           accprogress = 1
       assert accprogress <= 1, "found accproress = {}".format(accprogress)
       #we compute the ratio progress/resource in the window:
       windowstart = max(0, i - windowsize)
       assert windowstart < i
       progressresourceratio =  (accprogressmeasures[i] - accprogressmeasures[windowstart])/(accresourcemeasures[i] - accresourcemeasures[windowstart])
       assert progressresourceratio > 0
       #the remaining progress:
       remprogress = 1 - accprogress
       #the estimated remaining resources:
       assert remprogress >= 0
       assert remprogress <= 1
       remresource = remprogress / progressresourceratio
       #the estimated total resources:
       totalresources = accresource + remresource
       estimates.append(totalresources)
        
    return estimates
    
