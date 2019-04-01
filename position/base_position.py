from abc import abstractmethod


class BasePosition:
    def __init__(self):
        pass

    @abstractmethod
    def get_single_position(self, total_capital):
        return 0
