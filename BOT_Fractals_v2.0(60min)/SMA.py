class SMA:
    def __init__(self, datas, num_datas):
        self.datas = datas
        self.num_datas = num_datas

    def calculate(self):
        # finding EMA
        # use any constant value that results in
        # good smoothened curve
        stockValues = self.datas # N-последних строк
        sma = stockValues.rolling(window = self.num_datas).mean()
        return sma

    def isLong(self):
        sma_ = self.calculate()
        if (self.datas.iloc[-1] > sma_.iloc[-1]):
            return True
        else:
            return False

    def isShort(self):
        sma_ = self.calculate()
        if (self.datas.iloc[-1] < sma_.iloc[-1]):
            return True
        else:
            return False