from SMA import SMA

class g_faza:
    def __init__(self, data, SMA_10, SMA_20, SMA_50):
        self.data = data
        self.SMA_10 = SMA_10
        self.SMA_20 = SMA_20
        self.SMA_50 = SMA_50
        self.sma_10 = None
        self.sma_20 = None
        self.sma_50 = None

    def isLong(self): #Условие на лонг
        self.sma_10 = self.sma(self.SMA_10)
        self.sma_20 = self.sma(self.SMA_20)
        self.sma_50 = self.sma(self.SMA_50)
        if self.sma_20.iloc[-1] > self.sma_50.iloc[-1] and self.sma_10.iloc[-1] > self.sma_20.iloc[-1]:
            return True
        else:
            return False

    def isShort(self): #Условие на лонг
        if self.sma_10 is None: self.sma_10 = self.sma(self.SMA_10)
        if self.sma_20 is None: self.sma_20 = self.sma(self.SMA_20)
        if self.sma_50 is None: self.sma_50 = self.sma(self.SMA_50)
        if self.sma_20.iloc[-1] < self.sma_50.iloc[-1] and self.sma_10.iloc[-1] < self.sma_20.iloc[-1]:
            return True
        else:
            return False


    def sma(self, count):
        sma = SMA(self.data['close'], count).calculate()
        return sma