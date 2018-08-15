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
    progressvelocity = brown(accprogressmeasures,alpha, beta)
    #resource per data point
    resourcevelocity = brown(accresourcemeasures,alpha, beta)

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
def rollingAverageForecasting(accprogressmeasures, accresourcemeasures, maxwindowsize, withacceleration = True):
    assert accresourcemeasures[0] == 0

    if maxwindowsize == None:
        maxwindowsize = math.inf
    assert maxwindowsize >= 1
    assert len(accresourcemeasures) == len(accprogressmeasures)
    assert accresourcemeasures[0] == 0
    assert accprogressmeasures[0] == 0

    #we compute the size of the window:
    windowend = len(accprogressmeasures) - 1 #the last measure in the window
    windowstart = max(0, windowend - maxwindowsize) #the first measure in the window
    assert windowstart < windowend
    windowmid = (windowend - windowstart)// 2
    if windowmid == windowstart or windowmid == windowend:
        withacceleration = False

    #we compute the accumulated progress measure in the window
    def measurevelocity(accprogressmeasures, accresourcemeasures, start, end):
        accprogress = accprogressmeasures[end] - accprogressmeasures[start]
        if math.isclose(accprogress, 1) and accprogress > 1:
            accprogress = 1
        assert accprogress <= 1, "found accproress = {} - {} = {}".format(accprogressmeasures[end], accprogressmeasures[start], accprogress)

        accresource = accresourcemeasures[end] - accresourcemeasures[start]
        #we compute the ratio progress/resource (=velocity) in the window:
        progressresourceratio =  accprogress/accresource
        #print( "{} = {}/ {}".format(progressresourceratio, accprogress, accresource))
        assert progressresourceratio > 0
        return progressresourceratio

    #the remaining progress:
    remprogress = max(0,1 - accprogressmeasures[windowend])
    assert remprogress >= 0
    assert remprogress <= 1

    totalresources = 0

    if withacceleration is True:
        velocityfirsthalf = measurevelocity(accprogressmeasures, accresourcemeasures, windowstart, windowmid)
        velocitysecondhalf = measurevelocity(accprogressmeasures, accresourcemeasures, windowmid, windowend)
        velocitywindow = measurevelocity(accprogressmeasures, accresourcemeasures, windowstart, windowend)
        #the acceleration is the difference in speed between the total window and the (end of) the second half window
        acceleration = (velocitywindow - velocityfirsthalf)/(accresourcemeasures[windowend]-accresourcemeasures[windowmid])
        #the estimated remaining resources:
        #
        # TODO use total velocity instead? use y-intercept different from 0.0 that captures quadratic function better?
        #
        # the total velocity is
        # velocitytotal = velocityfirsthalf - .5 * acceleration (accresourcemeasures[windowmid] + accresourcemeasures[windowstart])
        #
        # the y intercept can be computed as
        # yintercept = accprogressmeasures[windowstart] - velocitytotal * accresourcemeasures[windowstart] - .5 * acceleration * (accresourcemeasures[windowstart] ** 2)
        #
        discriminant = velocitysecondhalf**2 + 2*acceleration*(remprogress)
        #if the search is really slowing down, it's possible that acceleration is so negative that
        #the discriminant is negative. Then we set it to 0.
        discriminant = max(0, discriminant)
        rootdiscriminant = math.sqrt(discriminant)
        remresource1 =  2.0 * (- velocitysecondhalf + rootdiscriminant) / acceleration
        remresource2 =  2.0 * (- velocitysecondhalf - rootdiscriminant) / acceleration
        #one of the two roots is negative
        remresource = max(remresource1, remresource2)
        assert(remresource > 0)
        #the estimated total resources:
        totalresources = accresourcemeasures[windowend] + remresource
    else:
        velocitywindow = measurevelocity(accprogressmeasures, accresourcemeasures, windowstart, windowend)
        #the estimated remaining resources:
        remresource = remprogress / velocitywindow
        #the estimated total resources:
        totalresources = accresourcemeasures[windowend] + remresource

    return totalresources
