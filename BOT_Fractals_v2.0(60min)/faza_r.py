class faza_r:
    def __init__(self, data, MaxFAZA, MinFAZA):
        self.data = data
        self.MaxFAZA = MaxFAZA
        self.MinFAZA = MinFAZA

    def isLong(self): #Условие на лонг
        min_ = self.data['low'].iloc[-self.MinFAZA - 2:].rolling(self.MinFAZA).min() # Тащим скользящий минимум
        if min_.iloc[-1] >= min_.iloc[-2]: # Если минимумы не обновляются то считаем что хотя бы не падающий тренд
            return True
        else:
            return False

    def isShort(self): #Условие на Шорт
        max_ = self.data['high'].iloc[-self.MaxFAZA - 2:].rolling(self.MaxFAZA).max()
        if max_.iloc[-1] <= max_.iloc[-2]: #Если максимумы не обновляются то считаем что тренд не восходящий
            return True
        else:
            return False

    def isFlat(self): #Условие на Шорт
       pass






