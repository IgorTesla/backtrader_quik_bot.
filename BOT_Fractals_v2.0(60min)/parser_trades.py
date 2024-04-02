from QuikPy import QuikPy
from datetime import datetime

class parser_Trades:
    def __init__(self, classcode, seccode):
        self.classcode = classcode
        self.seccode = seccode
        self.table = self.getallTrades() # тянем все сделки по выбранному инструменту

    def getallTrades(self):
        qpProvider = QuikPy()
        table = qpProvider.GetTrade(ClassCode=self.classcode, SecCode=self.seccode)[
            'data']  # Массив с элементами словарями
        return table

    def parseInterstByTime(self, dt):
        summ_OI = 0
        for i in range(len(self.table)-1, 0, -1):# идем в обратн7ом порядке
            #dt.year, dt.month, dt.day, dt.hour, dt.minute,
            dta = self.table[i]['datetime']

            if dt.year == dta['year'] and dt.month == dta['month'] and dt.day == dta['day'] and dt.hour == dta['hour'] and dt.minute == dta['min']: # если совпадают даты то
                #print(dta)
                temp = self.table[i]
                #print(temp)
                if temp['flags'] == 1026: # Если купля
                    summ_OI+=temp['qty']*temp['price']
                elif temp['flags'] == 1025: # Если продажа
                    summ_OI-=temp['qty']*temp['price']
        return summ_OI


