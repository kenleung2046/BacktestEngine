from abc import abstractmethod


class BaseStopLoss:
    def __init__(self):
        pass

    @abstractmethod
    def is_stop(self, code, date):

        return False
