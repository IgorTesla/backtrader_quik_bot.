from atr import atr

class trail_stop:
    def __init__(self, data,
                 ATR,
                 kStop,
                 kStart,
                 kPorabolic):
        #Лонговые константы
        self.ATR = ATR
        self.kStop = kStop
        self.kStart = kStart
        self.kPorabolic = kPorabolic

        self.dat = data

    # подразумеваю что данные сразу обрезаны с момента входа в сделку
    # Данные должны поставляться
    # Price - цена открытия позиции
    def get_real_stop(self, price, operation, data = None):
        #price = price*self.lotsize
        stop_price = 0
        if operation == "B": #условие для шорта
                # передаю в atr только необходимое количество данных чтобы выдернуть последнее значение
                atr1 = atr(data=self.dat.iloc[-self.ATR:], period=self.ATR)
                atr_ = atr1.getATR().iloc[-1]  # Тянем последнее значение АТР

                stop_price = price + atr_*self.kStop  # Начальное условие выставляем стоп по дефолту

                if data is not None:
                    # Вычисляем удерживалось баров
                    Ubars = len(data.index)
                    # Вычисляем MFE!
                    if Ubars > 1:
                        data["minimal"] = data["low"].cummin()  # get cumulative min
                    else:
                        data["minimal"] = data["low"]
                    # Вычисляем Porabolic Stop
                    Porabolic = stop_price - Ubars * Ubars * (atr_ / self.kPorabolic)
                    #print(f'Ubars - {Ubars}, Porabolic - {Porabolic}')
                    if price - data["minimal"].iloc[-1] >= atr_*self.kStart:
                        stop_price = min(stop_price, Porabolic)


        if operation == "S": #условие для лонга
                # передаю в atr только необходимое количество данных чтобы выдернуть последнее значение
                atr1 = atr(data=self.dat.iloc[-self.ATR:], period=self.ATR)
                atr_ = atr1.getATR().iloc[-1] # Тянем последнее значение АТР

                stop_price = price - atr_*self.kStop # Начальное условие выставляем стоп по дефолту

                if data is not None:
                    #Вычисляем удерживалось баров
                    Ubars = len(data.index)
                    #Вычисляем MFE!
                    if Ubars > 1:
                        data["highest"] = data["high"].cummax()  # get cumulative max
                    else:
                        data["highest"] = data["high"]
                    #Вычисляем Porabolic Stop
                    Porabolic = Ubars*Ubars*(atr_/self.kPorabolic) + stop_price
                    #Вычисляем максимальный стоп из пораболика и стандартного стопа
                    if data["highest"].iloc[-1] - price >= atr_*self.kStart:
                        stop_price = max(Porabolic, stop_price)

                    #print(price, self.porog, stop_price)
            # Если впервые устонавливаем стоп
        return stop_price



