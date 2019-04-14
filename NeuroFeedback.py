import sys, time, json, requests
from queue import Queue

fatigue_update = {}

class FatigueBasic(object):
   """MuseDatastructure"""
   def __init__(self, fatigueWindowSize, out_q):

      self.alphas = []
      self.betas = []
      self.gammas = []
      self.deltas = []
      self.thetas = []
      self.ticks = 0
      self.timestamp = 0
      self.fatigueWindowSize = fatigueWindowSize * 10 #window length in seconds
      self.out_q = out_q

   def interval10hz(self, alpha, beta, gamma, delta, theta, timestamp):
      self.alphas.append(alpha)
      self.betas.append(beta)
      self.gammas.append(gamma)
      self.deltas.append(delta)
      self.thetas.append(theta)
      self.timestamp = timestamp
      self.ticks += 1

      print self.ticks
      print self.fatigueWindowSize
      if (float(self.ticks) % self.fatigueWindowSize == 0):
         self.__checkFatigueLevel()


   def __checkFatigueLevel(self):
      '''Checks readouts of bands over window and sends update to server'''

      alphaWindowAvg = self.__getChanelAvg(self.alphas, self.fatigueWindowSize)
      alphaGlobalAvg = self.__getChanelAvg(self.alphas, -1)
      thetaWindowAvg = self.__getChanelAvg(self.thetas, self.fatigueWindowSize)
      thetaGlobalAvg = self.__getChanelAvg(self.thetas, -1)
      betaWindowAvg = self.__getChanelAvg(self.betas, self.fatigueWindowSize)
      betaGlobalAvg = self.__getChanelAvg(self.betas, -1)

      a = alphaWindowAvg / alphaGlobalAvg
      print "a: " + str(a)

      taobWindow = (thetaWindowAvg + alphaWindowAvg) / betaWindowAvg
      taobGlobal = (thetaGlobalAvg + alphaGlobalAvg) / betaGlobalAvg
      taob = taobWindow / taobGlobal
      print "taob: " + str(taob)

      toaWindow = thetaWindowAvg / alphaWindowAvg
      toaGloabal = thetaGlobalAvg / alphaGlobalAvg
      toa = toaWindow / toaGloabal
      print "toa: " + str(toa)

      fatigueScore = float(a + taob + (2 - toa)) / 3
      print "fatigueScore:" + str(fatigueScore - 1)

      fatigue_update['timestamp'] = self.timestamp
      if fatigueScore < .5:
         fatigueScore = .8
      elif fatigueScore > 1.5:
         fatigueScore = 1.2

      fatigue_update['fatigue_score'] = fatigueScore
      self.out_q.put({'fatigue': fatigue_update})

   def __getChanelAvg(self, channel, windowSize):

      if windowSize < 0:
         windowSize = len(self.alphas)
      return float(reduce(lambda x, y: x + y, channel[-windowSize:]) / float(windowSize))
