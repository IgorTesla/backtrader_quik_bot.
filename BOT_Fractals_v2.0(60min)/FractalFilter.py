from fractal import fractal

class fractalFilter:
    def __init__(self, data, maxRFilter, maxLFilter, minRFilter, minLFilter, fractalH=None, fractalL=None):
        self.data = data
        self.maxRFilter = maxRFilter
        self.maxLFilter = maxLFilter
        self.minRFilter = minRFilter
        self.minLFilter = minLFilter
        self.porogHigh = self.maxRFilter
        self.porogLow = self.minRFilter
        self.fractalH = fractalH
        self.fractalL = fractalL
        self.fractal_ = fractal(data=self.data, maxR=self.maxRFilter, maxL=self.maxLFilter, minR=self.minRFilter, minL=self.minLFilter, fractalH=self.fractalH, fractalL=self.fractalL)

    def minFilter(self):
        return(self.fractal_.minFractal())  # вычисляем последний максимальный фрактал

    def maxFilter(self):
        return(self.fractal_.maxFractal())

    def isLong(self): #Условие на лонг
        fMin = self.minFilter()
        if self.data['close'].iloc[-1] >= fMin:
            return True
        else:
            return False

    def isShort(self): #Условие на Шорт
        fMax = self.maxFilter()# вычисляем последний максимальный фрактал
        if self.data['close'].iloc[-1] <= fMax:
            return True
        else:
            return False






