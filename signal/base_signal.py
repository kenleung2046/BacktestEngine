from abc import abstractmethod


class BaseSignal:
    def __init__(self):
        pass

    @abstractmethod
    def get_stock_signal(self, code, date):
        return 0
