class fractal:

    def __init__(self, data, maxR, maxL, minR, minL, fractalH=None, fractalL=None):
        self.data = data
        self.maxR = maxR
        self.maxL = maxL
        self.minR = minR
        self.minL = minL
        self.k = self.minL
        self.k1 = self.maxL
        self.k2 = self.minR
        self.k3 = self.maxR
        self.fractalH = fractalH
        self.fractalL = fractalL
        self.fMax = None
        self.fMin = None

    def first_maxFractals(self):
        i=1
        #data = self.data
        while (self.fractalH == 0 or self.fractalH is None) and i<=len(self.data.index)-max(2*self.maxR,2*self.maxL)-2:
            data = self.data.iloc[:-i]
            self.fractalH = self.maxFractal(data=data)
            #print(f'i - {i}, len(self.data.index): {len(data.index)} ,self.fractalH: {self.fractalH}')
            i += 1
        return self.fractalH

    def first_minFractal(self):
        i=1
        #data = self.data
        while (self.fractalL == 0 or self.fractalL is None) and i<=len(self.data.index)-max(2*self.minL,2*self.minR)-2:
            data = self.data.iloc[:-i]
            self.fractalL = self.minFractal(data=data)
            i += 1
        return self.fractalL


    def maxFractal(self, data=None): #верхние фракталы
        if data is None: data = self.data
        maxR = data['high'].iloc[-self.maxR-self.k3-1:].rolling(self.maxR).max() # Тянем последние максимальные значения чтобы не грузить проц
        maxL = data['high'].iloc[-self.maxL-self.k1-1:].rolling(self.maxL).max()
        #self.data['rolHighestML'] = maxL
        #print(f'maxL - {self.maxL}, maxH - {self.maxR}')
        #if self.maxL == 10: print(f'{self.data["datetime"].iloc[-1]} maxR[-k+1]: {maxR.iloc[-self.k+1]}, maxR - {maxR.iloc[-1]}, maxL[-k] - {maxL.iloc[-self.k]}')

        if maxR.iloc[-1] == maxR.iloc[-self.k3] and maxR.iloc[-1] > maxL.iloc[-self.k1-1]:
           #print(f'{self.data["datetime"].iloc[-1]} new Fractal!!!!!!!!!!!!!!!!!!: {maxR.iloc[-1]}')
            return maxR.iloc[-1]
        elif self.fractalH:
            return self.fractalH
        else:
            return 0

    def minFractal(self, data = None): #нижние фракталы
        if data is None: data = self.data
        minR = data['low'].iloc[-self.minR - self.k2-1:].rolling(self.minR).min()
        minL = data['low'].iloc[-self.k-self.minL-1:].rolling(self.minL).min()
        #print(f'minL - {self.minL}, minR - {self.minR}')
        #print(f'{self.data["datetime"].iloc[-1]} minR[-k2]: {minR.iloc[-self.k2]}, minR - {minR.iloc[-1]}, minL[-k-1] - {minL.iloc[-self.k-1]}')

        if minR.iloc[-1] == minR.iloc[-self.k2] and minR.iloc[-1] < minL.iloc[-self.k-1]:
            #print(f'{self.data["datetime"].iloc[-1]} new Fractal!!!!!!!!!!!!!!!!!!: {minR.iloc[-1]}')
            return minR.iloc[-1]
        elif self.fractalL:
            return self.fractalL
        else:
            return 0

    # Условие Main на вход в лонг
    def isLong(self):
        self.fMax = self.maxFractal()
        if (self.data['close'].iloc[-2] <= self.fMax and self.data['close'].iloc[-1] > self.fMax):
            return True
        else:
            return False

    # Условие Main на вход в шорт
    def isShort(self):
        self.fMin = self.minFractal()
        if (self.data['close'].iloc[-2] >= self.fMin and self.data['close'].iloc[-1] < self.fMin):
            return True
        else:
            return False


