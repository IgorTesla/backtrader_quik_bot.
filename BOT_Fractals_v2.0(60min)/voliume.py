class voliume:
    def __init__(self, data, porog, candles=5):
        self.data = data
        self.candles = candles
        self.porog = porog

    def isPosition(self):
        sum = self.data['volume'][-self.candles:].sum()
        if sum>self.porog: return True
        else: return False

