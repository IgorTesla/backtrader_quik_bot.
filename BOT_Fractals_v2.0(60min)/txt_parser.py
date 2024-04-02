import os
import pickle

class txt_parser:
    def __init__(self):
        self.repository = "temp"

    def create_repository(self, rep2= ''):
        if not os.path.exists(self.repository):
            os.makedirs(self.repository)
        if rep2 != '':
            if not os.path.exists(self.repository+'/'+rep2):
                os.makedirs(self.repository+'/'+rep2)

    def rewrite_file(self, data, ticker, name_file):
        self.create_repository(rep2=ticker) # Создаем репозиторий если его нет
        try:
            with open(self.repository+'/'+ticker+'/'+name_file, 'wb') as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        except: pass

    def delete_dump_file(self, ticker):
        if os.path.exists(self.repository+'/'+ticker): #Если папка имеется
            os.remove(self.repository+'/'+ticker)

    def read_dump_file(self, ticker, name_file):
        data = None
        if os.path.exists(self.repository + '/' +ticker+ '/' + name_file):  # Если файл имеется
            with open(self.repository + '/' +ticker+ '/' + name_file, 'rb') as inp:
                data = pickle.load(inp)
        print(f'файл {self.repository + "/" +ticker+ "/" + name_file} отсутствует')
        return data

