from .ma_10_signal import MA10Signal


class SignalFactory:
    @staticmethod
    def get_signal_type(name):
        if name == 'ma_10':
            return MA10Signal()
