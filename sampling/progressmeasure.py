import math

def rollingAverageForecasting(accprogressmeasures, accresourcemeasures, windowsize = None):
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

    #we compute the ratio progress/resource in the window:
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
    
