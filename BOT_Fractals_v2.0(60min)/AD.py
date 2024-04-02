

class AD_Filter:
    def __init__(self, data, Persent_AD_LONG, Persent_AD_SHORT, AD=None, ):
        self.data = data
        self.Persent_AD_LONG = Persent_AD_LONG
        self.Persent_AD_SHORT = Persent_AD_SHORT
        self.AD = AD


    def get_AD(self):
        if self.data['high'].iloc[-1] - self.data['low'].iloc[-1] >0:
            AD = (self.data['close'].iloc[-1] - self.data['close'].iloc[-2])/(self.data['high'].iloc[-1] - self.data['low'].iloc[-1]) * self.data['volume'].iloc[-1] + self.AD
            return AD
        else:
            return self.AD


    def isLong(self): #Условие на лонг
        AD_Long = self.get_AD()
        if self.AD is not None:
            ret = self.AD + (abs(self.AD)/100)*self.Persent_AD_LONG
        else:
            ret = -999999999999
        if AD_Long >= ret:
            return True
        else:
            return False

    def isShort(self): #Условие на Шорт
        AD_SHORT = self.get_AD()# вычисляем последний максимальный фрактал
        if self.AD is not None:
            ret = self.AD - (abs(self.AD)/100)*self.Persent_AD_SHORT
        else:
            ret = 999999999999
        if AD_SHORT <= ret:
            return True
        else:
            return False






