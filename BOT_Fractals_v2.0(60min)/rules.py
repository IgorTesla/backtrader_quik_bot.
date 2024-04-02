import math
import json

class rules:
    def __init__(self, ticker,  year, month, day, hour, min, exp_forward, exp_back, exp_day, exp_month, timedo=0, timeposle=0, maxprosac = 0):
        self.ticker = ticker
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.min = min
        self.exp_forward = exp_forward
        self.exp_back = exp_back
        self.exp_day = exp_day
        self.exp_month = exp_month
        self.timedo = timedo
        self.timeposle = timeposle
        self.maxprosac = maxprosac

    def canTrade(self):
        month =  self.month
        dm = self.day
        temp = (int)(f"{self.hour}{self.min}")
        if (month % self.exp_month == 0) and (dm<=self.exp_day + self.exp_forward) and (dm>=self.exp_day-self.exp_back):
            return False
        # temp = ""
        # if self.hour/10 < 1 : self.hour = "0"+self.hour
        # if self.min / 10 < 1: self.min = "0" + self.min

        elif (temp < 2340):
            return True
        else: return False

    def expiration(self):
        month = self.month
        dm = self.day
        if (month % self.exp_month == 0) and (dm <= self.exp_day + self.exp_forward) and (dm >= self.exp_day - self.exp_back):
            return True
        else: return False

    # Исключаем неторгуемое время в нашем случае с 12:00 до 15:00
    def timeExcept(self):
        hour_ = self.hour
        min_ = self.min
        if hour_/10 < 1 : hour_ = "0"+str(self.hour)
        if min_/10 < 1: min_ = "0" + str(self.min)
        temp = (int)(f"{hour_}{min_}")
        if temp <= self.timedo or temp >= self.timeposle:
            return True
        else: return False

    def isLimitDown(self):
        #print("sdfsdfsdfsdfsdfsdf")
        with open(f"{os.getcwd()}\stats.json") as file:
            data = file.read()
            stat = json.loads(data)
        if self.ticker in stat and self.maxprosac != 0:

            Limit = 0
            Limit = stat[self.ticker][0] - stat[self.ticker][1]

            if Limit >= abs(self.maxprosac):
                print(f"{self.ticker} - превышение максимально допустимой просадки!\nмаксимальная просадка - {self.maxprosac}, текущая просадка - {Limit}\nНеобходима оптимизация, перед новым запуском НЕ ЗАБУДЬ ПОЧИСТИТЬ stats.json!!!")
                return False
            else:
                return True
        else: return True

