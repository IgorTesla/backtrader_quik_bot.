from atr import atr

class take_profit:
    def __init__(self, period_atr = None, take_atr = None, take_mlvl_atr=None, lotsize=1):
        self.lotsize = lotsize
        self.period_atr = period_atr
        self.take_atr = take_atr
        self.take_mlvl_atr = take_mlvl_atr/self.lotsize

    def get_atr_take_profit(self, data, operation, price):
        if self.period_atr != None:  # Если Это RSI стратегия то
            #price *= self.lotsize
            atr_ = atr(data=data, period=self.period_atr, take=self.take_atr, take_mlvl=self.take_mlvl_atr,
                       PE=price)
            tprofit=None
            if operation == 'S':  # Должен быть BUY
                tprofit = atr_.tpforLong()
            elif operation == 'B':
                tprofit = atr_.tpforShort()

        return tprofit
