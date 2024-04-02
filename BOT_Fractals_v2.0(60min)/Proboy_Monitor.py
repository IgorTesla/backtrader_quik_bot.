from datetime import datetime, date
from atr import atr

class monitor:

    def __init__(self, data, HIGH_Proboy, LOW_Proboy, KOL_Candles_HIGH, ATR_Long1, KOL_Candles_LOW, ATR_Short1, DESTROY_LEWEL_HIGH, DESTROY_LEWEL_LOW, timeframe=60):
        self.data = data
        self.HIGH_Proboy = HIGH_Proboy
        self.LOW_Proboy = LOW_Proboy
        self.KOL_Candles_HIGH =KOL_Candles_HIGH
        #self.ATR_Long1 = ATR_Long1
        self.KOL_Candles_LOW = KOL_Candles_LOW
        #self.ATR_Short1 = ATR_Short1
        self.DESTROY_LEWEL_HIGH = DESTROY_LEWEL_HIGH
        self.DESTROY_LEWEL_LOW = DESTROY_LEWEL_LOW
        self.timeframe = timeframe
        self.df_up = None
        self.df_low = None
        self.atr_Long = atr(data=self.data, period=ATR_Long1).getATR().iloc[-1]
        self.atr_Short = atr(data=self.data, period=ATR_Short1).getATR().iloc[-1]
        #print(f'self.atr_Long - {self.atr_Long}, atr_Short- {self.atr_Short}')

    def is_HIGH_Level_Live(self):
        if self.HIGH_Proboy is not None:
            dt_now = datetime.fromisoformat(str(self.data['datetime'].iloc[-1]))
            #print(f"dt_now: {dt_now}, self.HIGH_Proboy:{self.HIGH_Proboy}")
            time_diff = self.HIGH_Proboy[1]
            #time_diff = int((time_diff.total_seconds()/60)/self.timeframe) +1

            self.df_up = self.data['close'].iloc[-time_diff:].to_numpy()
            #print(self.df_up, self.HIGH_Proboy[0])
            df_min = self.df_up[self.df_up < self.HIGH_Proboy[0]].shape[0] # Количество строк
            #print(f"dt_now: {dt_now}, self.HIGH_Proboy[0]:{self.HIGH_Proboy[0]}, time_diff:{time_diff}, self.timeframe:{self.timeframe}, df_min:{df_min}")
           # if (self.HIGH_Proboy[0] == 21460): print(self.df_up)
            if df_min <= self.DESTROY_LEWEL_HIGH:
                return True
            else:
                return False

    def is_LOW_Level_Live(self):
        if self.LOW_Proboy is not None:
            dt_now = datetime.fromisoformat(str(self.data['datetime'].iloc[-1]))
            time_diff = self.LOW_Proboy[1]
            #time_diff = int((time_diff.total_seconds()/60)/self.timeframe) +1
            self.df_low = self.data['close'].iloc[-time_diff:].to_numpy()

            df_min = self.df_low[self.df_low > self.LOW_Proboy[0]].shape[0] # Количество строк
            #print(f"dt_now: {dt_now}, self.LOW_Proboy[0]:{self.LOW_Proboy[0]}, time_diff:{time_diff}, self.timeframe:{self.timeframe}, df_min:{df_min}")

            if df_min <= self.DESTROY_LEWEL_LOW:
                return True
            else:
                return False

    def is_much_level_high(self):
        temp_ = self.df_up
        temp = temp_[temp_ >= self.HIGH_Proboy[0]]
        #print(f"temp: {temp}, self.HIGH_Proboy[0]: {self.HIGH_Proboy[0]}")
        if len(temp)>self.KOL_Candles_HIGH :
            #print(f"дата - {self.data['datetime'].iloc[-1]}")
            return True
        else: return False

    def is_much_level_low(self):
        temp_ = self.df_low
        #print(temp_, self.LOW_Proboy[0])
        temp = temp_[temp_ <= self.LOW_Proboy[0]]
        if len(temp)> self.KOL_Candles_LOW:
            #print(f"дата - {self.data['datetime'].iloc[-1]} shoort")
            return True
        else: return False

    def ProboyLong(self):
        if self.is_HIGH_Level_Live():
            if self.is_much_level_high():
                if (self.data['low'].iloc[-2] > self.HIGH_Proboy[0] + self.atr_Long and
                    self.data['low'].iloc[-1] <= self.HIGH_Proboy[0] + self.atr_Long and
                    self.data['low'].iloc[-1] > self.HIGH_Proboy[0]):
                    return True
                else: return False
            else: return  False
        else: return  False

    def ProboyShort(self):
        if self.LOW_Proboy is not None and self.is_LOW_Level_Live():
            if self.is_much_level_low():
                if (self.data['high'].iloc[-2] < self.LOW_Proboy[0] - self.atr_Short and
                        self.data['high'].iloc[-1] >= self.LOW_Proboy[0] - self.atr_Short and
                        self.data['high'].iloc[-1] < self.LOW_Proboy[0]):
                    #print(f"self.LOW_Proboy[0]: {self.LOW_Proboy[0]}")
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False





