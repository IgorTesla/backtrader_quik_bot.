'''Индекс относительной силы на вход подается датафрейм один столбец 'close' или 'max' или 'low' и период индикатора'''
from atr import atr
from EMA import EMA


class adx:
    def __init__(self, data, periods, kADX_Long, kADX_Short):
        self.periods = periods
        self.data = data
        self.kADX_Long = kADX_Long
        self.kADX_Short = kADX_Short

    def cycle(self, df1, df2): # Проходим по элементам и обнуляем по условию
        for i in range(len(df1.index)):
            # print(f"Index: {i}")
            # print(f"{row}\n")
            if df1.iloc[i] <0 or df1.iloc[i]<df2.iloc[i]:
                df1.iloc[i] = 0
        return df1

    def get_adx(self):
        plus_dm = self.data['high'].diff() #p
        minus_dm = self.data['low'].diff()*-1 #n подгоняем под формулу

        plus_dm1 = self.cycle(df1=plus_dm, df2=minus_dm)
        minus_dm1 = self.cycle(df1=minus_dm, df2=plus_dm)
        #plus_dm[plus_dm < 0 | plus_dm < minus_dm] = 0
        #minus_dm[minus_dm < 0 | minus_dm < plus_dm] = 0

        # tr1 = pd.DataFrame(high - low)
        # tr2 = pd.DataFrame(abs(high - close.shift(1)))
        # tr3 = pd.DataFrame(abs(low - close.shift(1)))
        # frames = [tr1, tr2, tr3]
        # tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
        atr_ = atr(data = self.data, period=self.periods)
        atr1 = atr_.getATR()

        ema_ = EMA(datas=plus_dm1, num_datas=self.periods)
        plus_di = (ema_.calculate() / atr1)
        ema_ = EMA(datas=minus_dm1, num_datas=self.periods)
        minus_di = (ema_.calculate() / atr1)

        dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
        adx = ((dx.shift(1) * (self.periods - 1)) + dx) / self.periods

        ema_ = EMA(datas=adx, num_datas=self.periods)
        adx_smooth = ema_.calculate()
        return plus_di, minus_di, adx_smooth

    def isLong(self):
        adx_ = self.get_adx()[2]
        if adx_.iloc[-1] > self.kADX_Long:
            return True
        else:
            return False

    def isShort(self):
        adx_ = self.get_adx()[2]
        if adx_.iloc[-1] > self.kADX_Short:
            return True
        else:
            return False