import json
import os


from backtrader import TimeFrame, order
from QuikPy import QuikPy
from BackTraderQuik.QKStore import QKStore
from BackTraderQuik.QKBroker import QKBroker
from backtrader_plotly.plotter import BacktraderPlotly
from backtrader_plotly.scheme import PlotScheme
import plotly.io
import time
import threading
from txt_parser import txt_parser

from datetime import datetime, timedelta, date
from datetime import time as time_
import backtrader as bt
from Fractals import fractals as strategy
from trail_stop import trail_stop
from take_profit import take_profit
import pandas as pd
from telegram_bot import telegram_bot

class Fractal_Strategy(bt.Strategy):    
    params = (  # Параметры торговой системы
        ('all_trades', None),  
        ('clientCode', None),  
        ('firmId', None),  
        ('symbols', None),  
        ('trade_account', None)
    )

    def log(self, txt, dt=None):
        """Вывод строки с датой на консоль"""
        if len(self.datas[0].datetime)>=1: dt = bt.num2date(self.datas[0].datetime[0]) if dt is None else dt  # Заданная дата или дата текущего бара
        else: dt = datetime.now()
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')  # Выводим дату и время с заданным текстом на консоль
        if self.tb.Message is not None: self.tb.Bot.send_message(self.tb.Message.from_user.id, f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')

    def __init__(self):
        """ Инициализация торговой системы """
        self.order = {}
        self.lowside = {}
        self.highside = {}
        self.trs = {}
        self.tps = {}
        self.strategy = {}
        self.dat = {}
        self.TrailingStopData = {}
        self.store = QKStore()  # Хранилище QUIK
        self.broker_ = QKBroker()  # создали экземпляр брокера
        self.isLive = {}
        self.crossed = {}
        self.Disconnected = False
        self.tb = telegram_bot()  # Инициируем нашего бота
        self.info = {} #Словарь информации по тикерам
        self.stat = None

        for data in self.datas:
            self.tb.tickers[data._name] = None #Добавляем названия тикеров в Телеграм бота для удобства
            self.isLive[data._name] = False
            self.crossed[data._name] = False
            self.order[data._name] = None  # Заявка
            self.lowside[data._name] = None # Стоп-ордер
            self.highside[data._name] = None # Тэйк профит
            self.trs[data._name] = None
            self.tps[data._name] = None
            self.strategy[data._name] = strategy(data._name) #Думаю есть необходимость брать один экземпляр системы на один тикер
            self.dat[data._name] = None #Закачиваем панды
            self.TrailingStopData[data._name] = None # Панда для подсчета трейлинг стопа

        #self.txt_parser = txt_parser()

    def start_tele_bot(self):
        self.tb.run()

    def start(self):
        #Тащим данные по статистике считаем макс убытки подряд.
        with open(f"{os.getcwd()}\stats.json") as file:
            data = file.read()
            self.stat=json.loads(data)
        if self.stat is None: self.stat = {}

        for data in self.datas:
            class_code = data._name.split('.')[0]
            sec_code = data._name.split('.')[1]
            self.info[data._name] = self.store.get_symbol_info(class_code, sec_code)  # тянем информацию о тикере            
            if data._name not in self.stat: self.stat[data._name] = [0, 0]

        self.store.provider.OnConnected = self.on_connected
        # self.store.provider.OnOrder = self.on_order
        self.store.provider.OnDisconnected = self.on_disconnected
        #self.start_monitor() # обработка позиции при запуске
       # x = threading.Thread(target=self.start_tele_bot)
       # x.start()

     
    def on_connected(self, data):
        self.log('QUIK Подключен')

    def on_disconnected(self, data):
        self.log('QUIK Отключен')

    def notify_data(self, data, status, *args, **kwargs):
        """Изменение статуса приходящих баров"""
        data_status = data._getstatusname(status)  # Получаем статус (только при LiveBars=True)
        self.tb.status = data_status # отдаем боту инфу о статусе
        self.log(data_status)  # Не можем вывести в лог, т.к. первый статус DELAYED получаем до первого бара (и его даты)
        self.isLive[data._name] = data_status == 'LIVE'  # Режим реальной торговли
        if data_status == 'DISCONNECTED': # прорабатываем включение выключение соединения
            self.Disconnected=True

    def notify_order(self, order):
        """Изменение статуса заявки"""
        if order.status in [order.Submitted, order.Accepted]:  # Если заявка не исполнена (отправлена брокеру или принята брокером)
            return  # то статус заявки не изменился, выходим, дальше не продолжаем
        if order.status in [order.Completed]:  # Если заявка исполнена
            if order.isbuy():  # Заявка на покупку
                self.log(f'Bought @{order.executed.price:.2f}, Cost={order.executed.value:.2f}, Comm={order.executed.comm:.2f}')
            elif order.issell():  # Заявка на продажу
                self.log(f'Sold @{order.executed.price:.2f}, Cost={order.executed.value:.2f}, Comm={order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:  # Заявка отменена, нет средств, отклонена брокером
            #self.log('Canceled/Margin/Rejected')
            pass
        ticker = order.info['ClassCode']+'.'+order.info['SecCode']
        if ticker in self.order.keys(): self.order[ticker] = None  # Этой заявки больше нет

    def notify_trade(self, trade):
        ticker = trade.data.classCode+'.'+trade.data.secCode #делаем название ключа из кода класса и тикера
        """Изменение статуса позиции"""
        if trade.justopened: # Если позиция только что открыта
            # trd = {}
            # #print(trade)
            # trd['price'] = self.position.price
            # # trd['dtopen'] = trade['dtopen']
            # trd['ticker'] = self.datas[0].p.dataname
            # self.txt_parser.rewrite_file(trd, trd['ticker'], 'position.dat') #Отправляем в txt парсер нашу последнюю позицию
            if (ticker in self.TrailingStopData.keys()) and (self.TrailingStopData[ticker] is None): self.TrailingStopData[ticker]=pd.DataFrame(columns= ['datetime', 'open', 'high', 'low', 'close', 'volume'])
        if not trade.isclosed:  # Если позиция не закрыта
            return  # то статус позиции не изменился, выходим, дальше не продолжаем
        if trade.isclosed:# Если позиция закрыта
            if ticker in self.TrailingStopData.keys(): self.TrailingStopData[ticker] = None  #Обнуляем панду для
            if self.crossed[ticker]:  #Если прошла перекрестная сделка выходим
                self.crossed[ticker] = False
                return
            if ticker in self.lowside.keys() and self.lowside[ticker]: self.cancel(self.lowside[ticker])
            if ticker in self.highside.keys() and self.highside[ticker]: self.cancel(self.highside[ticker])

            #self.position_ = None #Обнуляем стартовую позицию если она была
            # self.txt_parser.delete_dump_file(self.datas[0].p.dataname)# удаляем файлпосле закрытия сделки
        #Грузим стату в файл
        if ticker in self.stat:
            self.stat[ticker][1] += trade.pnlcomm
        else:
            self.stat[ticker][1] = trade.pnlcomm
        if self.stat[ticker][0] < self.stat[ticker][1]: self.stat[ticker][0] = self.stat[ticker][1]
        #else: self.stat[ticker] = trade.pnlcomm
        with open(f"{os.getcwd()}\stats.json", 'w') as outfile:
            json.dump(self.stat, outfile)

        self.log(f'Trade Profit, Gross={trade.pnl:.2f}, NET={trade.pnlcomm:.2f}')

    def generatePanda(self, data):
        df=pd.DataFrame(columns= ['datetime', 'open', 'high', 'low', 'close', 'volume'])
        dt = bt.num2date(data.datetime[0])
        tm = data.datetime.time()
        time_string = tm.strftime("%H:%M:%S")
        hour = int(time_string[0:2])
        minute = int(time_string[3:5])
        # print(hour, minute)
        dt = datetime(dt.year, dt.month, dt.day, hour, minute)
        temp = {'datetime': dt, 'open': data.open[0], 'high': data.high[0],
                'low': data.low[0], 'close': data.close[0], 'volume': data.volume[0]}
        df.loc[len(df.index)] = temp
        return df

    def if_crossShortPosition(self, answer, data):
        #Пишу условие на переворот для стратегии RSI если имеется шортовая позиция и лонговый сигнал и Это стратегия RSI то
        if self.getposition(data=data) and self.getposition(data=data).size<0 and answer['Long'] and answer['atrParams'] is not None:
            self.log("Фиксирую перекрестную Шортовую сделку инициирую переворот по рынку")
            self.order[data._name] = self.close(data=data)  # Заявка на продажу по рыночной цене

            if data._name in self.highside and self.highside[data._name] and self.highside[data._name].status == bt.Order.Accepted:  # Если заявка не исполнена принята брокером удаляем
                self.cancel(self.highside[data._name])

            if data._name in self.lowside and self.lowside[data._name] and self.lowside[data._name].status == bt.Order.Accepted:  # Если заявка не исполнена принята брокером удаляем
                self.cancel(self.lowside[data._name])
            self.crossed[data._name] = True
            time.sleep(6)

    def get_count(self, number):
        s = str(number)
        if '.' in s:
            return abs(s.find('.') - len(s)) - 1
        else:
            return 0

    def get_price_ceil(self, price, datas): #функция для подгона цены под текущие шаг цены и размер лота
        #kol = len(str(self.info[datas._name]['lot_size']))
        #print(datas._name, self.info[datas._name]['lot_size'], self.info[datas._name]['min_price_step'])
        delta = (price *self.info[datas._name]['lot_size'] % self.info[datas._name]['min_price_step'])/self.info[datas._name]['lot_size']
        #Вытаскиваем количество знаков после запятой для
        count_dec = self.get_count(self.info[datas._name]['min_price_step'])
        #print(round(price - delta, count_dec))
        return round(price - delta, count_dec)

    def chosedeal(self, answer, data):
        cash = self.broker.getcash()
        try:
            if not self.getposition(data=data) :  # Если позиции нет и свободный КЭШ имеется

                if answer['Long']:  # Если пришла заявка на покупку
                    self.log(f'Свободные средства: {cash}, Баланс: {self.broker.getvalue()}')
                    self.log(f'Buy Market {data._name}')
                    #self.order = self.buy()  # Заявка на покупку по рыночной цене

                    if 'stopLossParams' in answer:
                        self.trs[data._name] = trail_stop(data=self.dat[data._name],
                                                          ATR=answer['stopLossParams']['ATR'],
                                                          kStop=answer['stopLossParams']['kStop'],
                                                          kStart=answer['stopLossParams']['kStart'],
                                                          kPorabolic=answer['stopLossParams']['kPorabolic']
                                                          )
                    lastPrice = data.close[0]
                    self.order[data._name] = self.buy(data=data, size=self.strategy[data._name].params['quant'] * self.info[data._name]['lot_size'])
                    #Проверяем прошла ли наша сделка!
                    #self.order[data._name] = self.check_order(data=data, order_=self.order[data._name], operation="B", size=self.strategy[data._name].quant * self.info[data._name]['lot_size'])
                    time.sleep(2)
                    if self.trs[data._name] is not None:
                         tmp = self.trs[data._name].get_real_stop(price=lastPrice, operation="S")
                         stopPrice = self.get_price_ceil(tmp, datas=data)
                         self.lowside[data._name] = self.sell(data=data, price=stopPrice, exectype=bt.Order.Stop, size=self.order[data._name].size,
                                          transmit=True)
                         #print(f"{data._name}, temp: {tmp}, stopPr: {stopPrice}")
                         # Проверяем заявку если не выставлена то повторяем отправку
                         # self.lowside[data._name] = self.check_order(order_=self.lowside[data._name], data=data, price=stopPrice, type=bt.Order.Stop,
                         #                           size=self.order[data._name].size,
                         #                           operation="S")
                         time.sleep(2)
                    #print(stopPrice, tprofit)
                    #input()
                if answer['Short']:  # Если пришла заявка на продажу
                    self.log(f'Свободные средства: {cash}, Баланс: {self.broker.getvalue()}')
                    self.log(f'Sell Market {data._name}')
                    if 'stopLossParams' in answer: self.trs[data._name] = trail_stop(data=self.dat[data._name],
                                                          ATR=answer['stopLossParams']['ATR'],
                                                          kStop=answer['stopLossParams']['kStop'],
                                                          kStart=answer['stopLossParams']['kStart'],
                                                          kPorabolic=answer['stopLossParams']['kPorabolic']
                                                          )

                    lastPrice = data.close[0]
                    self.order[data._name] = self.sell(data=data, size=self.strategy[data._name].params['quant'] * self.info[data._name]['lot_size'])  # Заявка на продажу по рыночной цене
                    # Проверяем прошла ли наша сделка!
                    #self.order[data._name] = self.check_order(data=data, order_=self.order[data._name], operation="S",
                    #                                         size=self.strategy[data._name].quant * self.info[data._name]['lot_size'])
                    time.sleep(2)
                    if self.trs[data._name] is not None:
                        tmp = self.trs[data._name].get_real_stop(price=lastPrice, operation="B")
                        stopPrice =self.get_price_ceil(tmp, datas=data)
                        self.lowside[data._name] = self.buy(data=data, price=stopPrice, exectype = bt.Order.Stop, size=self.order[data._name].size,
                                                transmit = True)
                        time.sleep(2)
                        #print(f"{data._name}, temp: {tmp}, stopPr: {stopPrice}")
                        # Проверяем заявку если не выставлена то повторяем отправку
                        # self.lowside[data._name] = self.check_order(order_= self.lowside[data._name], data=data, price=stopPrice,
                        #                  type=bt.Order.Stop,
                        #                  size=self.order[data._name].size,
                        #                  operation="B")

        except Exception as e:
            print(e)
            #self.log("Ошибка при выставлении первичной заявки, error: ", e)

    def next(self):
        for data in self.datas:

            """Получение следующего бара"""
            if self.dat[data._name] is None: self.dat[data._name] = self.generatePanda(data)
            # for data in self.datas:  # Пробегаемся по всем запрошенным барам
            #      self.log(
            #          f'{data.p.dataname} Open={data.open[0]:.2f}, High={data.high[0]:.2f}, Low={data.low[0]:.2f}, Close={data.close[0]:.2f}, Volume={data.volume[0]:.0f}')
            dt = bt.num2date(data.datetime[0])
            tm = data.datetime.time()
            time_string = tm.strftime("%H:%M:%S")
            hour = int(time_string[0:2])
            minute = int(time_string[3:5])

            dt = datetime(dt.year, dt.month, dt.day, hour, minute)
            temp = {'datetime': dt, 'open': data.open[0], 'high': data.high[0],
                    'low': data.low[0], 'close': data.close[0], 'volume': data.volume[0]}
            self.dat[data._name].loc[len(self.dat[data._name].index)] = temp
            #print(f"{data._name}, is_Live: {self.isLive[data._name]}")
            if self.isLive[data._name]: # Торгуем после того как загрузится dataframe и наступит лайв режим
                #print(f"Точка останова {data._name}")
                if data._name in self.order.keys() and self.order[data._name]:  # Если есть неисполненная заявка
                    return  # то выходим, дальше не продолжаем
                # print(f"{datetime.now()} {answer}")
                answer = self.strategy[data._name].stFractal(istk=self.dat[data._name])
                # Если по задан параметр переворота из шорта в лонг!
                if self.strategy[data._name].params['iscross_short']: self.if_crossShortPosition(answer=answer, data=data)  # Условие на перекрестные сделки переворачиваемся

                if not self.getposition(data=data) and self.isLive[data._name]: #Если мы вне позиции и лайв режим
                    self.chosedeal(answer=answer, data=data)  # Использую выбор сделки и лог по ответу от стратегии
                    #pass
                else:

                   self.TrailingStopData[data._name].loc[len(self.dat[data._name].index)] = temp

                   #self.txt_parser.rewrite_file(self.TrailingStopData, self.datas[0].p.dataname, 'TrailingStopData.dat') #Сериализация данных Трейлинг стопа

                   operation = "S" if (self.getposition(data=data).size>0) else "B"
                   price = self.getposition(data=data).price

                   if data._name in self.trs and self.trs[data._name] is not None and self.isLive[data._name]:
                        temp = self.trs[data._name].get_real_stop(price=price, operation=operation, data=self.TrailingStopData[data._name])
                        stopPrice = self.get_price_ceil(temp, datas=data)
                        #print(f"{data._name} stopPr vs order: {temp} vs  {stopPrice} vs {self.lowside.price}, lastprice: {lastPrice}, openDeal {self.position.price}, stopStatus: {self.lowside.status}")
                        self.lowside[data._name] = self.move_orders(newPrice=stopPrice, oldPrice=self.lowside[data._name].price, operation=operation,
                                                   order=self.lowside[data._name], isStop=True, data=data, size = self.getposition(data=data).size)  #
                        #self.txt_parser.rewrite_file(self.lowside, self.datas[0].p.dataname, 'lowside.dat') #Сериализация стоп лоса

                   if data._name in self.tps and self.tps[data._name] is not None and self.isLive[data._name]:
                        temp = self.tps[data._name].get_atr_take_profit(data=self.dat[data._name], operation=operation, price=price)
                        tprofit = self.get_price_ceil(temp, datas=data)
                        #print(f"{data._name} takeprofit vs order: {temp} vs {tprofit} vs {self.highside[data._name].price}, lastprice: {lastPrice}, openDeal {self.getposition(data=data).price}, takeStatus: {self.highside[data._name].status}")
                        self.highside[data._name] = self.move_orders(newPrice=tprofit, oldPrice=self.highside[data._name].price, operation=operation,
                                                         order=self.highside[data._name], isStop=False, size = self.getposition(data=data).size, data=data)  #
                time.sleep(1)
                        #self.txt_parser.rewrite_ file(self.highside, self.datas[0].p.dataname, 'highside.dat')    #Сериализация тэйк профита

            
    # Проверяем исполнен ли ордер и пробуем выставиться повторно!
    def check_order(self, order_, data, size, operation, price=None, type=None):
        ord = order_
        time.sleep(3)
        if type is not None:
            if not (ord and ord.status == 2):
                self.log(f"Заявка при первой попытке не выставлена! Попытка (2/2)! {ord.status}")
                if operation == "B":
                    ord = self.buy(data=data, price=price, exectype=type, transmit = True, size = abs(size))
                else:
                    ord = self.sell(data=data, price=price, exectype=type, transmit=True, size=abs(size))
        else:
            if not (ord and ord.status == 2):
                self.log(f"Рыночная заявка при первой попытке не исполнена! Попытка (2/2)! {ord.status}")
                if operation == "B":
                    ord = self.buy(data=data, size=abs(size))
                else:
                    ord = self.sell(data=data, size=abs(size))
        return ord

    def move_orders(self, newPrice, oldPrice, operation, order, isStop, data, size=None):
        try:
            if newPrice != oldPrice:
                time.sleep(3)
                if order and order.status == bt.Order.Accepted:  # Если заявка не исполнена принята брокером удаляем
                    self.cancel(order)
                    time.sleep(3)
                if operation == "B":
                    if isStop:
                        order = self.buy(data=data, price=newPrice, exectype=bt.Order.Stop, transmit = True, size = abs(size))
                        # Проверяем исполнен ли ордер и пробуем выставиться повторно!
                        #order = self.check_order(order_=order, data=data, price=newPrice, type=bt.Order.Stop, size=size, operation=operation)
                    else:
                        order = self.buy(data=data, price=newPrice, exectype=bt.Order.Limit, size = abs(size), transmit = True)
                        #order = self.check_order(order_=order, data=data, price=newPrice, type=bt.Order.Limit, size=size,
                        #                         operation=operation)
                elif operation == "S":
                    if isStop:
                        order = self.sell(data=data, price=newPrice,  exectype=bt.Order.Stop, transmit = True, size = abs(size))
                        #order = self.check_order(order_=order, data=data, price=newPrice, type=bt.Order.Stop, size=size, operation=operation)
                    else:
                        order = self.sell(data=data, price=newPrice, size = abs(size), exectype=bt.Order.Limit, transmit = True)
                        #order = self.check_order(order_=order, data=data, price=newPrice, type=bt.Order.Limit, size=size,
                        #                         operation=operation)
        except Exception as e:
            self.log("Ошибка при перестановке Стоп/Тэйк заявок, error: ", e)
        return order

'''Точка входа бота !!!'''
if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    symbols = ('SPBFUT.SRZ3', 'SPBFUT.LKZ3', 'SPBFUT.SNZ3')
    #symbol = 'SPBFUT.RIU3'
    store = QKStore()
    cerebro = bt.Cerebro(stdstats=False)  #Инициируем "движок" BT
    delta = timedelta(days=20) #Количество дней для истории

    for symbol in symbols:  # Пробегаемся по всем тикерам
         data = store.getdata(dataname=symbol, timeframe=bt.TimeFrame.Minutes, compression=60, fromdate=datetime.now()-delta, sessionstart=time_(7, 0), LiveBars=True,
                             rtbar=True)
         cerebro.adddata(data)  # Привязываем исторические данные

   # data = store.getdata(dataname=symbol, timeframe=bt.TimeFrame.Minutes, fromdate=datetime.now()-delta, compression=60, sessionstart=time_(7, 0),
                         #LiveBars=True, rtbar=True)
    cerebro.adddata(data)  # Привязываем исторические данные
    
    clientCode = "#ВАШ КОД КЛИЕНТА QUIK"  # Код клиента (присваивается брокером)
    trade_account = "ВАШ ТОРГОВЫЙ СЧЕТ QUIK" #торовый счет
    firmId = "ВАШ КОД ФИРМЫ QUIK"  # Код фирмы (присваивается брокером)

    broker = store.getbroker(use_positions=False, FirmId=firmId, TradeAccountId=trade_account, clientCode=clientCode, IsFutures=True)  # Брокер со счетом фондового рынка РФ
    cerebro.setbroker(broker)
    #cerebro.addsizer(bt.sizers.SizerFix, stake=1000)
    #data = store.getdata(dataname=symbol, timeframe=bt.TimeFrame.Minutes, compression=1, fromdate=datetime(year=2023, month=4, day=19), sessionstart=time_(7, 0), LiveBars=True, rtbar=True)

    cerebro.addstrategy(Fractal_Strategy)  # Привязываем торговую систему с параметрами
    cerebro.run()  # Запуск торговой системы


