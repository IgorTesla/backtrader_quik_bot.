import math

import numpy as np
import pandas as pd

'''Get compressed data and refactor them to atr'''
class atr:
    def __init__(self, data, period):
        self.data = data
        self.period = period
        # self.take = take
        # self.take_mlvl = take_mlvl
        # self.PE = PE

    def getATR(self):
        high_low = self.data['high'] - self.data['low']
        high_close = np.abs(self.data['high'] - self.data['close'].shift())
        low_close = np.abs(self.data['low'] - self.data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(self.period).sum() / self.period
        return atr
