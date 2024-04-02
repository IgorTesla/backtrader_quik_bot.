from rsi import rsi
import pandas as pd

class rsi_filter:
    def __init__(self, data, periods, step=0):
        self.data = data
        self.periods = periods
        self.step = step

    def isLong(self):
        compressed_data = self.compress()
        rsi_ = rsi(compressed_data['close'], self.periods).rsi()
        #print(rsi_[-1:])
        if ((rsi_[-1:]>30).bool() and (rsi_[-1:]<70).bool()): return True
        else: return False

    def compress(self):
        frame = {}
        frame['close'] = []
        frame['high'] = []
        frame['low'] = []
        frame['open'] = []
        frame['datetime'] = []
        frame['date'] = []
        if self.step<=0 : return self.data
        else:
            for i in range(self.step-1,len(self.data),self.step):
                    frame['close'].append(self.data['close'].iloc[i])
                    frame['high'].append(self.data['high'][i-self.step+1:i].max())
                    frame['low'] .append(self.data['low'][i-self.step+1:i].min())
                    frame['open'].append(self.data['open'].iloc[i-self.step+1])
                    frame['datetime'].append(self.data['datetime'].iloc[i-self.step+1])
                    frame['date'].append(self.data['date'].iloc[i-self.step+1])
            # костыль для подбора последних свечек чтоб отработать оставшиеся
            temp = len(self.data)%self.step
            if (temp > 0):
                frame['close'].append(self.data['close'].iloc[-1])
                frame['high'].append(self.data['high'][-temp:].max())
                frame['low'].append(self.data['low'][-temp:].min())
                frame['open'].append(self.data['open'].iloc[-temp])
                frame['datetime'].append(self.data['datetime'].iloc[-temp])
                frame['date'].append(self.data['date'].iloc[-temp])
            #print(frame)
            frame = pd.DataFrame.from_dict(frame, orient='columns')
            return frame