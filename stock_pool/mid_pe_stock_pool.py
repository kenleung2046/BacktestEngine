from pymongo import MongoClient, ASCENDING
from .base_stock_pool import BaseStockPool


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


class MidPeStockPool(BaseStockPool):
    def __init__(self, begin_date, end_date, interval):
        BaseStockPool.__init__(self, '中PE股票池', begin_date, end_date, interval)

    def get_option_stocks(self):
        date_cursor = db.Calendar.find(
            {'cal_date': {'$gte': self.begin_date, '$lte': self.end_date},
             'is_open': True},
            sort=[('cal_date', ASCENDING)],
            projection={'cal_date': True, '_id': False},
        )
        dates = [x['cal_date'] for x in date_cursor]

        last_adjust_date = None
        last_stocks = None
        adjust_dates = []
        date_stocks_dict = dict()

        for index in range(0, len(dates), self.interval):
            current_adjust_date = dates[index]

            pe_cursor = db.Fundamental.find(
                {'trade_date': current_adjust_date,
                 'pe': {'$gt': 30, '$lt': 60}},
                sort=[('pe', ASCENDING)],
                projection={'ts_code': True, '_id': False},
            )

            stocks = []
            if last_stocks is not None:
                suspension_daily_cursor = db.Quotation_Daily.find(
                    {'ts_code': {'$in': last_stocks},
                     'trade_date': current_adjust_date,
                     'is_trading': False},
                    projection={'ts_code': True, '_id': False}
                )

                for suspension_daily in suspension_daily_cursor:
                    stocks.append(suspension_daily['ts_code'])

            for pe in pe_cursor:
                code = pe['ts_code']

                daily = db.Quotation_Daily.find_one(
                    {'ts_code': code, 'trade_date': current_adjust_date, 'is_trading': True}
                )

                if daily is None:
                    continue

                if len(stocks) >= 50:
                    break

                stocks.append(code)

            adjust_dates.append(current_adjust_date)
            date_stocks_dict[current_adjust_date] = stocks
            last_adjust_date = current_adjust_date

        return adjust_dates, date_stocks_dict
