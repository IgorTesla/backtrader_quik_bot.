'''Индекс относительной силы на вход подается датафрейм один столбец 'close' или 'max' или 'low' и период индикатора'''
import pandas as pd


class rsi:
    def __init__(self, data, periods, LRSI=70, SRSI=30):
        self.periods = periods
        self.data = data
        self.LRSI = LRSI
        self.SRSI = SRSI

    def rsi(self, ema=True):
        """
        Returns a pd.Series with the relative strength index.
        """
        close_delta = self.data.diff()

        # Make two series: one for lower closes and one for higher closes
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)

        if ema == True:
                # Use exponential moving average
                ma_up = up.ewm(span=self.periods, min_periods=self.periods).mean()
                ma_down = down.ewm(span=self.periods, min_periods=self.periods).mean()
        else:
                # Use simple moving average
                ma_up = up.rolling(window=self.periods).mean()
                ma_down = down.rolling(window=self.periods).mean()

        rsi = ma_up / ma_down
        rsi = 100 - (100 / (1 + rsi))
        return rsi

    def isLong(self):
        rsi_ = self.rsi()
        if (rsi_.iloc[-1] > self.LRSI - 0.2*self.LRSI) and (rsi_.iloc[-1] < self.LRSI + 0.2*self.LRSI):
            return True
        else:
            return False

    def isShort(self):
        rsi_ = self.rsi()
        if (rsi_.iloc[-1] > self.SRSI - 0.21*self.SRSI) and (rsi_.iloc[-1] < self.SRSI + 0.21*self.SRSI):
            return True
        else:
            return False