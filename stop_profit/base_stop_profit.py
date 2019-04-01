from abc import abstractmethod


class BaseStopProfit:
    def __init__(self):
        pass

    def update_holding_stock(self, code):
        pass

    @abstractmethod
    def is_stop_profit(self, code, date):
        return False
