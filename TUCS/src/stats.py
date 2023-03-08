############################################################
#
# stats.py
#
############################################################
#
# Author: Henric
# Date: summer solstice 2013
# Aim: standardised statistics 
#
# Input parameters are:
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8 
#2345678901234567890123456789012345678901234567890123456789012345678901234567890
#
###########################################################

import math

class stats:

    def __init__(self):
        self.entries = 0
        self.sum     = float(0.)
        self.sum2    = float(0.)
        self.sumweight = float(0.)
        self.sumweight2 = float(0.)
        self.simple = True


    def fill(self, value, weight=1.):
        self.entries += 1 
        self.sum     += value*weight
        self.sum2    += value*value*weight
        self.sumweight += weight
        self.sumweight2 += weight*weight
        if weight!=1.:
            self.simple = False


    def reset(self):
        self.entries = 0
        self.sum     = float(0.)
        self.sum2    = float(0.)
        self.sumweight = float(0.)
        self.sumweight2 = float(0.)
        self.simple = True

 
    def mean(self):
        if self.sumweight>0:
            return self.sum/self.sumweight

    def neff(self):
        return self.sumweight*self.sumweight/self.sumweight2

    def variance(self):
        m = self.mean()
        if self.simple:
            if self.entries>1:
                return (self.sum2-m*self.sum)/(self.entries-1)
        else:            # weighted sample average
            if self.sumweight*self.sumweight!=self.sumweight2:
                neff = self.neff()
                # return self.sumweight/(self.sumweight*self.sumweight-self.sumweight2)*(self.sum2-2*m*self.sum+m*m*self.sumweight)
                # print 'toto',(self.sum2/self.sumweight-m*m) * neff/(neff-1), (self.sum2-self.sum*self.sum/self.sumweight) * self.sumweight/(self.sumweight*self.sumweight-self.sumweight2)
                #return (self.sum2-self.sum*self.sum/self.sumweight) * self.sumweight/(self.sumweight*self.sumweight-self.sumweight2)
                return  max((self.sum2/self.sumweight-m*m) * neff/(neff-1), 0.) # sometime numerical precision...

    def error(self):    
        if self.simple:
            if self.entries>0:
                return math.sqrt(self.variance()/self.entries)
        else:
            if self.entries>1 and self.sumweight!=0.:  # root variance of means, corrected fro under/over dispersion
                #m = self.mean()  
                #return math.sqrt((1./self.sumweight)*(1./(self.entries-1))*(self.sum2-2*m*self.sum+m*m*self.sumweight))
                x = 0.
                try:
                    x = math.sqrt(self.variance()/self.neff())
                except:
                    print((self.variance(), self.neff()))

                return x
    #added 10/06/2014 by Cora		
    def weighterr(self):
        if not self.simple:
            return math.sqrt(1./self.sumweight)

    def dump(self):
        print((self.entries, self.sum, self.sum2, self.sumweight, self.sumweight2, self.simple))

    def n(self):
        return self.entries

    def rms(self):
        if self.entries>0:
            return math.sqrt(self.variance())
