from abc import abstractclassmethod


class BaseStockPool:
    def __init__(self, name, begin_date, end_date, interval):
        self.name = name
        self.begin_date = begin_date
        self.end_date = end_date
        self.interval = interval

    @abstractclassmethod
    def get_option_stocks(cls):
        return [], dict()
