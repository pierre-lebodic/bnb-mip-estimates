# Tree size estimates for the B&B search
#
# Tracks the current estimated progress of the search, and the
# estimated amount of resources used so far, and extrapolates the
# estimated total amount of resources that will be needed for
# the entire search
#
# Author: Daniel Anderson (dlanders@cs.cmu.edu)
# Author: Pierre Le Bodic (pierre.lebodic@monash.edu)
#

import math
from enum import Enum

# -----------------------------------------------------------------------------
#                 Methods for velocity extrapolation
# -----------------------------------------------------------------------------

# Online smoothing - Track the smoothed velocity of a sequence
class Smoothing:
  def __init__(self, method, alpha, beta):
    self.alpha = alpha
    self.beta = beta
    self.method = method
    self.s = 0
    self.b = 0
    self.n = 0

  # Returns the smoothed velocity of the resulting sequence
  def insert(self, x):
    self.n += 1
    if self.n == 1:
      self.s = x
      self.b = x
    else:
      if self.method == "Holt":
        news = self.alpha * x + (1 - self.alpha) * (self.s + self.b)
        newb = self.beta * (news - self.s) + (1 - self.beta) * self.b
      elif self.method == "Brown":
        news = self.alpha * x + (1 - self.alpha) * self.s
        newb = self.beta * (news - self.s) + (1 - self.beta) * self.b
      else:
        assert False, "Method must be 'Holt' or 'Brown'"
      self.s = news
      self.b = newb
    return self.b

# -----------------------------------------------------------------------------
#                           Progress measurement
# -----------------------------------------------------------------------------

# Base class for Progress Measures
class ProgressMeasure:

  # Insert a new estimate of the progress and resources used
  # and return the estimated amount of total resources required
  def insert(self, progress, resources):
    assert False, "Not implemented"

# Track the progress using Double Exponential Smoothing (BROWN or HOLT)
class DoubleExponentialSmoothing(ProgressMeasure):

  def __init__(self, method, alpha, beta):
    self.progress_smoother = Smoothing(method, alpha, beta)
    self.resource_smoother = Smoothing(method, alpha, beta)

  def insert(self, progress, resources):
    progress_v = self.progress_smoother.insert(progress)
    resource_v = self.resource_smoother.insert(resources)
    m = (1 - progress) / progress_v
    remresource = resource_v * m
    totalresources = remresource + resources
    return totalresources

# Track the progress using a linear estimate of the velocity of a sliding window
class RollingAverage(ProgressMeasure):

  def __init__(self, maxwindowsize, useacceleration):
    if maxwindowsize == None: maxwindowsize = math.inf
    assert maxwindowsize >= 1

    self.maxwindowsize = maxwindowsize
    self.useacceleration = useacceleration
    self.accprogressmeasures = [0]
    self.accresourcemeasures = [0]

  #we compute the accumulated progress measure in the window
  def measurevelocity(self, start, end):
      accprogress = self.accprogressmeasures[end] - self.accprogressmeasures[start]
      if math.isclose(accprogress, 1) and accprogress > 1: accprogress = 1
      assert accprogress <= 1

      accresource = self.accresourcemeasures[end] - self.accresourcemeasures[start]
      #we compute the ratio progress/resource (=velocity) in the window:
      progressresourceratio =  accprogress/accresource
      assert progressresourceratio > 0  # crashes on 69_harp2
      return progressresourceratio

  def insert(self, progress, resources):
    self.accprogressmeasures.append(progress)
    self.accresourcemeasures.append(resources)

    #we compute the size of the window:
    windowend = len(self.accprogressmeasures) - 1 #the last measure in the window
    windowstart = max(0, windowend - self.maxwindowsize) #the first measure in the window
    assert windowstart < windowend
    windowmid = (windowend - windowstart)// 2
    if windowmid == windowstart or windowmid == windowend:
        withacceleration = False
    else:
      withacceleration = self.useacceleration

    #the remaining progress:
    remprogress = max(0,1 - self.accprogressmeasures[windowend])
    assert remprogress >= 0
    assert remprogress <= 1

    totalresources = 0
    r1 = self.accresourcemeasures[windowstart]
    r2 = self.accresourcemeasures[windowmid]
    r3 = self.accresourcemeasures[windowend]
    
    p1 = self.accprogressmeasures[windowstart]
    p2 = self.accprogressmeasures[windowmid]
    p3 = self.accprogressmeasures[windowend]

    v_window = self.measurevelocity(windowstart, windowend)
    if withacceleration is True:
        v1 = self.measurevelocity(windowstart, windowmid)
        v2 = self.measurevelocity(windowmid, windowend)
        
        # the acceleration is the difference in speed between the (end of) the
        # first half window and the (end of) the second half window
        a = 2.0 * (v_window - v1)/ (r3 - r2)
        
        # Velocity given acceleration
        v = v1 - 0.5*a * (r1 + r2)
        s0 = p1 - v * r1 - 0.5 * a * r1**2
        
        #the estimated remaining resources:
        discriminant = max(0, v**2 - 2*a*(s0 - 1.0))
        rootdiscriminant = math.sqrt(discriminant)

        # only if there is at least a little bit of acceleration, we solve the
        # quadratic equation.
        if abs(a) > 1e-9:
            remresource1 = (- v + rootdiscriminant) / a
            remresource2 = (- v - rootdiscriminant) / a
            #one of the two roots is negative
            remresource = max(remresource1, remresource2)
        else:
          # no notable acceleration, we use a linear forecast
          remresource = remprogress / v
          
        # Shouldn't be negative...
        remresource = max(0, remresource)
        #assert(remresource > 0)
        
        #the estimated total resources:
        totalresources = r3 + remresource
    else:
        #the estimated remaining resources:
        remresource = remprogress / v_window
        #the estimated total resources:
        totalresources = r3 + remresource

    return totalresources
