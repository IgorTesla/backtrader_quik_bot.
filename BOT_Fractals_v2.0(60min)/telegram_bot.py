import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class telegram_bot():

    def __init__(self):
        self.TOKEN = '#YOUR TELEGRAM TOKEN' # Bot Token Telegram
        self.Bot = telebot.TeleBot(self.TOKEN)
        self.Message = None
        self.status = "OK"
        self.tickers = {}
        @self.Bot.message_handler(content_types=['text'])
        def get_text_messages(message): # Использую для функций если будет необходимо
            if message.text == "Stat":
                self.Bot.send_message(message.from_user.id, f"Статус: {self.status}")
            elif message.text == "Stop":
                self.Bot.send_message(message.from_user.id, f"Введите инструмент по которому необходимо выставить стоп лосс: {self.tickers}")

            elif message.text == "/help":
                self.Bot.send_message(message.from_user.id, "stat - выводит статус робота /n")
            else:
                self.Bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")
            self.Message = message
            print(message.text)

        @self.Bot.message_handler(commands=['start'])
        def send_start(message):
            main_kb = InlineKeyboardMarkup(row_width=2)
            buttons = []
            for name, value in self.tickers.items():
                buttons.append(InlineKeyboardButton(name, callback_data=name))
            main_kb.add(*buttons)
            self.Bot.send_message(message.chat.id, 'Список торгуемых инструментов', reply_markup=main_kb)
            
        #Функция не доработана!
        @self.Bot.callback_query_handler(func=lambda call: True)
        def callback(call):

            for name, value in self.tickers.items():
                if name in call.data:

                    if call.data.startswith('stop_'):
                        self.Bot.send_message(call.message.chat.id, 'Stop Loss {}'.format(name))

                    elif call.data.startswith('take_'):
                        self.Bot.send_message(call.message.chat.id, 'Take Profit {}'.format(name))

                    else:
                        stop_button = InlineKeyboardMarkup()
                        stop_button.add(InlineKeyboardButton('Активировать стоп лосс {}'.format(name),
                                                            callback_data='stop_{}'.format(name)))
                        self.Bot.send_message(call.message.chat.id, value['desc'], reply_markup=stop_button)
                        take_button = InlineKeyboardMarkup()
                        take_button.add(InlineKeyboardButton('Активировать тэйк профит {}'.format(name),
                                                             callback_data='take_{}'.format(name)))
                        self.Bot.send_message(call.message.chat.id, value['desc'], reply_markup=take_button)

    def run(self):
            self.Bot.polling()


