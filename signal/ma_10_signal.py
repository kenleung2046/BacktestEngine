from pymongo import MongoClient
from .base_signal import BaseSignal


_database_ip_ = '127.0.0.1'
_database_port_ = 27017
_authentication_ = 'admin'
_user_ = 'analyst'
_pwd_ = 'Kl123456'
_database_name_ = 'A-Shares'
_client = MongoClient(_database_ip_, _database_port_)
db_auth = _client[_authentication_]
db_auth.authenticate(_user_, _pwd_)
db = _client[_database_name_]


class MA10Signal(BaseSignal):
    def __init__(self):
        BaseSignal.__init__(self)

    def get_stock_signal(self, code, date):
        signal = db.signal.find_one(
            {'ts_code': code, 'trade_date': date, 'signal_ma_10': {'$in': ['up_break', 'down_break']}},
        )

        if signal is not None:
            return signal['signal_ma_10']
        else:
            return 0
