import pandas as pd
class EMA:
    def __init__(self, datas, num_datas):
        self.datas = datas
        self.num_datas = num_datas

    def calculate(self):
        # finding EMA
        # use any constant value that results in
        # good smoothened curve
        stockValues = self.datas # N-последних строк
        ema = stockValues.ewm(com=1/self.num_datas, adjust=False, min_periods=self.num_datas).mean() #com=periods - 1, adjust=True, min_periods=periods
        return ema


