from datetime import datetime
from faza_r import faza_r
import pandas as pd
from FractalFilter import fractalFilter
from rules import rules
from voliume import voliume
from fractal import fractal
from SMA import SMA
from ADX import adx
import SPBFUT_Params
from Proboy_Monitor import monitor
from AD import AD_Filter

class fractals:
    def __init__(self, name):
        # Quik connection parameters
        self.name=name
        self.check = True
        # Значения для рекурсии
        self.fractalH = 0
        self.fractalL = 0
        self.AD = 0
        self.HIGH_Proboy = None
        self.LOW_Proboy = None
        self.counter_H = 0
        self.counter_L = 0
        self.firstStep = True

        self.Attention = True # Флаг ЗАПУСКА АКТИВНЫХ ТОРГОВ
        self.datas = pd.DataFrame()  # Создали датафрэйм в который будут грузиться свечи
        if name in SPBFUT_Params.optimized: self.params = SPBFUT_Params.optimized[name]
        else: self.params={}

    def stFractal(self, istk):

        SMA_ = SMA(datas=istk['close'].iloc[-self.params['SMA']-1:], num_datas=self.params['SMA'])
        factal_s = fractal(data=istk, maxR=self.params['MaxR'], maxL=self.params['MaxL'], minR=self.params['MinR'], minL=self.params['MinL'], fractalL=self.fractalL, fractalH=self.fractalH)
        self.AD_Filter = AD_Filter(data=istk, Persent_AD_LONG=self.params['Persent_AD_LONG'], Persent_AD_SHORT=self.params['Persent_AD_SHORT'], AD=self.AD)

        # обновляем значения для рекурсии!!
        if self.firstStep:
            self.fractalH = factal_s.first_maxFractals()
            self.fractalL = factal_s.first_minFractal()
        else:
            self.fractalH = factal_s.maxFractal()
            self.fractalL = factal_s.minFractal()
        self.AD = self.AD_Filter.get_AD()


        dt = datetime.fromisoformat(str(istk['datetime'].iloc[-1]))
        rule = rules(ticker=self.name,
                     year=dt.year,
                     month=dt.month,
                     day=dt.day,
                     hour=dt.hour,
                     min=dt.minute,
                     exp_forward=self.params['exp_forward'],
                     exp_back=self.params['exp_back'],
                     exp_day=self.params['exp_day'],
                     exp_month=self.params['exp_month'],
                     maxprosac=self.params['MaxDrowDown']
                     )

        # ЕСЛИ УРОВЕНЬ ПРОБИТ ЗАПОМИНАЕМ
        if (factal_s.isLong() and self.AD_Filter.isLong()):
            self.counter_H = 0
            self.HIGH_Proboy = [self.fractalH, self.counter_H]
        if (factal_s.isShort() and self.AD_Filter.isShort()):
            self.counter_L = 0
            self.LOW_Proboy = [self.fractalL, self.counter_L]


        monitor_ = None
        if self.HIGH_Proboy is not None or self.LOW_Proboy is not None:
            #print(f"self.HIGH_Proboy:{self.HIGH_Proboy}, dt:{dt}")
            if self.HIGH_Proboy is not None: self.HIGH_Proboy[1] = self.counter_H  # Тиков с момента пробоя
            if self.LOW_Proboy is not None: self.LOW_Proboy[1] = self.counter_L
            monitor_ = monitor(data=istk, HIGH_Proboy=self.HIGH_Proboy, LOW_Proboy=self.LOW_Proboy, KOL_Candles_HIGH=self.params['KOL_Candles_HIGH'], ATR_Long1=self.params['ATR_Long1'], KOL_Candles_LOW=self.params['KOL_Candles_LOW'], ATR_Short1=self.params['ATR_Short1'], DESTROY_LEWEL_HIGH=self.params['DESTROY_LEWEL_HIGH'], DESTROY_LEWEL_LOW=self.params['DESTROY_LEWEL_LOW'], timeframe = self.params['SMA'])
            #if self.HIGH_Proboy is not None and not monitor_.is_HIGH_Level_Live(): self.HIGH_Proboy = None
            #if self.LOW_Proboy is not None and not monitor_.is_LOW_Level_Live(): self.LOW_Proboy = None

        Answer_dict = {'Long': False, 'Short': False, 'closeLong': False, 'closeShort': False}
        print(f"{self.name}: fractH: {self.fractalH}, fractL:{self.fractalL}, {istk['datetime'].iloc[-1]}, factal_s_Long {factal_s.isLong()}, factal_s_Short {factal_s.isShort()}")
        #print(f'{self.name}: {istk["datetime"].iloc[-1]}, fractalLong - {factal_s.isLong()}, fractalShort - {factal_s.isShort()}')
        if (monitor_ is not None and
            monitor_.ProboyLong() and
            SMA_.isLong() and
            rule.isLimitDown() and
            not rule.expiration() and
            rule.canTrade()):
            print(f"{self.name}: FRACTAL - LONG дата:{istk['datetime'].iloc[-1]}")
            if self.Attention:
                self.HIGH_Proboy = None
                #открыли сделку в лонг
                Answer_dict['Long'] = True
                Answer_dict['stopLossParams'] = {'ATR':self.params['ATR_Long1'], 'kStop':self.params['kStop_Long1'], 'kStart':self.params['kStart_Long1'], 'kPorabolic':self.params['kPorabolic_Long']}
                #Answer_dict['atrParams'] = { 'period_atr':self.period_atr_long, 'take_atr': self.take_atr_long, 'take_mlvl_atr':self.take_mlvl_atr_long}

        if (monitor_ is not None and
            monitor_.ProboyShort() and
            SMA_.isShort() and
            rule.isLimitDown() and
            not rule.expiration() and
            rule.canTrade()):
            print(f"{self.name}: FRACTAL - SHORT дата:{istk['datetime'].iloc[-1]}")
            if self.Attention:
                # открыли сделку в ШОРТ
                self.LOW_Proboy = None
                Answer_dict['Short'] = True
                Answer_dict['stopLossParams'] = {'ATR':self.params['ATR_Short1'], 'kStop':self.params['kStop_Short1'], 'kStart':self.params['kStart_Short1'], 'kPorabolic':self.params['kPorabolic_Short']}
                #Answer_dict['atrParams'] = {'period_atr':self.period_atr_short, 'take_atr':self.take_atr_short, 'take_mlvl_atr':self.take_mlvl_atr_short}
       # self.check = not self.check
        self.firstStep = False
        self.counter_H += 1
        self.counter_L += 1
        return Answer_dict

