import math

#at the moment this is quite inefficient, as we recompute the entire series for every new value
def doubleExponentialSmoothing(accprogressmeasures, accresourcemeasures, alpha, beta):
    #we use double smoothing on the progress measure, and separately on the resource measure
    #Holt-Winters version of double exponential smoothing
    def holtwinters(x, alpha, beta):
        olds, oldb, news, newb = 0, 0, 0, 0
        for i, xi in enumerate(x):
            if i == 0:
                continue
            elif i == 1:
                news = xi
                newb = xi 
            else:
                news= alpha * xi + (1 - alpha)*(olds + oldb)
                newb= beta * (news - olds)+ (1- beta) * oldb

            olds = news
            oldb = newb
        return newb

    def brown(x, alpha, beta):
        olds, oldb, news, newb = 0, 0, 0, 0
        for i, xi in enumerate(x):
            if i == 0:
                continue
            elif i == 1:
                news = xi
                newb = xi 
            else:
                news= alpha * xi + (1 - alpha)*olds
                newb= beta * (news - olds)+ (1- beta) * oldb

            olds = news
            oldb = newb
        return newb         

    #progress per data point
    progressvelocity = expsmooth(accprogressmeasures,alpha, beta) 
    #resource per data point
    resourcevelocity = expsmooth(accresourcemeasures,alpha, beta) 

    #we determine how many more data points would be needed given the progress velocity
    m = (1 - accprogressmeasures[-1]) / progressvelocity
    #we determine the amount of resources needed for these m additional data points
    remresource = resourcevelocity * m

    totalresources = remresource + accresourcemeasures[-1]

    return totalresources

#Computes an estimate of the remaining resources (e.g. nodes) required to reach 
#a progress measure of 1, given the accumulated progress and resources measures
#so far.
#This method first computes the average velocity by which we accrue progress as a 
#function of resources used in a window of given size.
#Then, supposing that this velocity remains constant, we estimate the amount of
#resources required to reach a progress measure of 1.
def rollingAverageForecasting(accprogressmeasures, accresourcemeasures, windowsize):
    assert accresourcemeasures[0] == 0

    if windowsize == None:
        windowsize = math.inf
    assert windowsize >= 1
    assert len(accresourcemeasures) == len(accprogressmeasures)
    assert accresourcemeasures[0] == 0
    assert accprogressmeasures[0] == 0

    #we compute the size of the window:
    windowend = len(accprogressmeasures) - 1 #the last measure in the window
    windowstart = max(0, windowend - windowsize) #the first measure in the window
    assert windowstart < windowend

    #we compute the accumulated progress measure in the window
    accprogress = accprogressmeasures[windowend] - accprogressmeasures[windowstart]
    if math.isclose(accprogress, 1) and accprogress > 1:
        accprogress = 1
    assert accprogress <= 1, "found accproress = {} - {} = {}".format(accprogressmeasures[windowend], accprogressmeasures[windowstart], accprogress)

    accresource = accresourcemeasures[windowend] - accresourcemeasures[windowstart]

    #we compute the ratio progress/resource (=velocity) in the window:
    progressresourceratio =  accprogress/accresource
    #print( "{} = {}/ {}".format(progressresourceratio, accprogress, accresource))
    assert progressresourceratio > 0
    #the remaining progress:
    remprogress = max(0,1 - accprogressmeasures[windowend])
    #the estimated remaining resources:
    assert remprogress >= 0
    assert remprogress <= 1
    remresource = remprogress / progressresourceratio
    #the estimated total resources:
    totalresources = accresourcemeasures[windowend] + remresource
        
    #print(totalresources)
    return totalresources
    
