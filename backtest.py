from pymongo import MongoClient, ASCENDING, DESCENDING
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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


class Backtest:
    def __init__(self, strategy):
        self.strategy = strategy

    def start(self):

        cash = self.strategy.capital
        total_capital = cash
        position = self.strategy.position
        add_position = self.strategy.add_position
        stop_loss_method = self.strategy.stop_loss
        stop_profit_method = self.strategy.stop_profit
        signal = self.strategy.signal

        # 时间为key的净值、收益和同期沪深基准
        df_portfolio = pd.DataFrame(columns=['net_value', 'total_return', 'hs300'])

        begin_date = self.strategy.begin_date
        end_date = self.strategy.end_date

        all_dates = get_trading_dates(begin_date, end_date)
        print(all_dates, flush=True)
        print('回测交易日总数：', len(all_dates), flush=True)

        hs300_begin_value = db.index_daily.find_one(
            {'ts_code': '000300.SH',
             'trade_date': all_dates[0]},
            projection={'close': True})['close']

        stock_pool = self.strategy.stock_pool
        if stock_pool is None:
            print('股票池不存在。', flush=True)
            return
        adjust_dates, date_codes_dict = stock_pool.get_option_stocks()

        last_phase_codes = None
        this_phase_codes = None
        to_be_sold_codes = set()
        to_be_bought_codes = set()
        to_be_added_codes = set()
        holding_code_dict = self.strategy.holding_stocks
        last_date = None

        # 按照日期一步步回测
        for _date in all_dates:
            print('Backtest at %s.' % _date)

            # 当期持仓股票列表
            before_sell_holding_codes = list(holding_code_dict.keys())

            # 处理复权
            if last_date is not None and len(before_sell_holding_codes) > 0:
                last_daily_cursor = db.adj_factor.find(
                    {'ts_code': {'$in': before_sell_holding_codes}, 'trade_date': last_date},
                    projection={'ts_code': True, 'adj_factor': True})

                code_last_aufactor_dict = dict()

                for last_daily in last_daily_cursor:
                    code_last_aufactor_dict[last_daily['ts_code']] = last_daily['adj_factor']

                current_daily_cursor = db.adj_factor.find(
                    {'ts_code': {'$in': before_sell_holding_codes}, 'trade_date': _date},
                    projection={'ts_code': True, 'adj_factor': True})

                for current_daily in current_daily_cursor:
                    current_aufactor = current_daily['adj_factor']
                    code = current_daily['ts_code']
                    before_volume = holding_code_dict[code]['volume']
                    if code in code_last_aufactor_dict:
                        last_aufactor = code_last_aufactor_dict[code]
                        after_volume = int(before_volume * (current_aufactor / last_aufactor))
                        holding_code_dict[code]['volume'] = after_volume
                        print('持仓量调整：%s, %6d, %10.6f, %6d, %10.6f' %
                              (code, before_volume, last_aufactor, after_volume, current_aufactor))

            # 卖出
            print('待卖股票池：', to_be_sold_codes, flush=True)
            print('待卖股票池总数：', len(to_be_sold_codes), flush=True)
            if len(to_be_sold_codes) > 0:
                sell_daily_cursor = db.quotation_daily.find(
                    {'ts_code': {'$in': list(to_be_sold_codes)}, 'trade_date': _date, 'is_trading': True},
                    projection={'open': True, 'ts_code': True}
                )

                for sell_daily in sell_daily_cursor:
                    code = sell_daily['ts_code']
                    if code in before_sell_holding_codes:
                        holding_stock = holding_code_dict[code]
                        holding_volume = holding_stock['volume']
                        sell_price = sell_daily['open']
                        sell_amount = holding_volume * sell_price
                        cash += sell_amount

                        cost = holding_stock['cost']
                        single_profit = (sell_amount - cost) * 100 / cost
                        print('卖出 %s, %6d, %6.2f, %8.2f, %4.2f' %
                              (code, holding_volume, sell_price, sell_amount, single_profit))

                        del holding_code_dict[code]
                        to_be_sold_codes.remove(code)

            print('卖出后，现金: %10.2f' % cash)

            # 买入
            print('待买股票池：', to_be_bought_codes, flush=True)
            print('待买股票池总数：', len(to_be_bought_codes), flush=True)
            if len(to_be_bought_codes) > 0:
                buy_daily_cursor = db.quotation_daily.find(
                    {'ts_code': {'$in': list(to_be_bought_codes)}, 'trade_date': _date, 'is_trading': True},
                    projection={'ts_code': True, 'open': True}
                )

                for buy_daily in buy_daily_cursor:
                    code = buy_daily['ts_code']
                    single_position = position.get_single_position(total_capital)
                    if cash > single_position:
                        buy_price = buy_daily['open']
                        volume = int(int(single_position / buy_price) / 100) * 100
                        buy_amount = buy_price * volume
                        cash -= buy_amount
                        holding_code_dict[code] = {
                            'volume': volume,
                            'cost': buy_amount,
                            'last_value': buy_amount}

                        print('买入 %s, %6d, %6.2f, %8.2f' % (code, volume, buy_price, buy_amount))

            print('买入后，现金: %10.2f' % cash)

            # 处理加仓
            print('待加仓股票池', to_be_added_codes, flush=True)
            print('待加仓股票池总数：', len(to_be_added_codes), flush=True)
            if add_position is not None:
                if len(to_be_added_codes) > 0:
                    added_daily_cursor = db.quotation_daily.find(
                        {'ts_code': {'$in': list(to_be_added_codes)}, 'trade_date': _date, 'is_trading': True},
                        projection={'ts_code': True, 'open': True}
                    )

                    for added_daily in added_daily_cursor:
                        code = added_daily['ts_code']
                        added_single_position = add_position.get_single_position(code)
                        if cash > added_single_position > 0:
                            added_price = added_daily['open']
                            added_volume = int(int(added_single_position / added_price) / 100) * 100
                            added_amount = added_price * added_volume
                            cash -= added_amount

                            add_position.update_holding_stock(code, added_amount, added_volume)

                            print('加仓 %s, %6d, %6.2f, %8.2f' % (code, added_volume, added_price, added_amount))

            print('加仓后，现金: %10.2f' % cash)

            # 持仓股代码列表
            holding_codes = list(holding_code_dict.keys())
            # 如果调整日，则获取新一期的股票列表
            if _date in adjust_dates:
                print('股票池调整日：%s，备选股票列表：' % _date, flush=True)

                # 暂存为上期的日期
                if this_phase_codes is not None:
                    last_phase_codes = this_phase_codes
                this_phase_codes = date_codes_dict[_date]
                print(this_phase_codes, flush=True)
                print('股票池总数', len(this_phase_codes), flush=True)

                # 找到所有调出股票代码，在第二日开盘时卖出
                if last_phase_codes is not None:
                    out_codes = find_out_stocks(last_phase_codes, this_phase_codes)
                    for out_code in out_codes:
                        if out_code in holding_code_dict:
                            to_be_sold_codes.add(out_code)

            # 检查是否有需要第二天卖出的股票
            for holding_code in holding_codes:
                sell_signal = signal.get_stock_signal(holding_code, _date)
                if sell_signal == 'down_break':
                    print('计算信号MA10，K线下穿MA10，股票：%s，日期：%s，down_break突破' %
                          (holding_code, _date), flush=True)
                    to_be_sold_codes.add(holding_code)

            # 检查是否有需要第二天买入的股票
            to_be_bought_codes.clear()
            to_be_added_codes.clear()
            if this_phase_codes is not None:
                for _code in this_phase_codes:
                    buy_signal = signal.get_stock_signal(_code, _date)
                    if buy_signal == 'up_break':
                        print('计算信号MA10，K线上穿MA10，股票：%s，日期：%s，up_break突破' %
                              (_code, _date), flush=True)
                        if _code not in holding_codes:
                            to_be_bought_codes.add(_code)
                        else:
                            to_be_added_codes.add(_code)

            # 计算总资产
            total_value = 0
            holding_daily_cursor = db.quotation_daily.find(
                {'ts_code': {'$in': holding_codes}, 'trade_date': _date},
                projection={'close': True, 'ts_code': True}
            )
            # 算每只持仓股的市值
            for holding_daily in holding_daily_cursor:
                code = holding_daily['ts_code']
                holding_stock = holding_code_dict[code]
                value = holding_daily['close'] * holding_stock['volume']
                total_value += value

                profit = (value - holding_stock['cost']) * 100 / holding_stock['cost']
                one_day_profit = (value - holding_stock['last_value']) * 100 / holding_stock['last_value']

                holding_stock['last_value'] = value
                print('持仓: %s, %10.2f, %4.2f, %4.2f' %
                      (code, value, profit, one_day_profit))

            # 检查是否需要止损
            if stop_loss_method is not None:
                for holding_code in holding_codes:
                    if stop_loss_method.is_stop(holding_code, _date):
                        print('股票需要止损，代码：%s' % holding_code, flush=True)
                        to_be_sold_codes.add(holding_code)

            # 检查是否有需要止盈的股票
            if stop_profit_method is not None:
                for holding_code in holding_codes:
                    # 更新持仓股
                    stop_profit_method.update_holding_stock(holding_code)

                    if stop_profit_method.is_stop_profit(holding_code, _date):
                        print('股票需要止盈，代码：%s' % holding_code, flush=True)
                        to_be_sold_codes.add(holding_code)

            total_capital = total_value + cash

            hs300_current_value = db.index_daily.find_one(
                {'ts_code': '000300.SH', 'trade_date': _date},
                projection={'close': True})['close']

            print('收盘后，现金: %10.2f, 总资产: %10.2f' % (cash, total_capital))
            last_date = _date
            df_portfolio.loc[_date] = {
                'net_value': round(total_capital / int(self.strategy.capital), 4),
                'total_return': round(100 * (total_capital - int(self.strategy.capital)) / int(self.strategy.capital), 2),
                'hs300': round(100 * (hs300_current_value - hs300_begin_value) / hs300_begin_value, 2)
            }

        # 评估回测效果
        backtest_estimate(df_portfolio)

        # 画图
        if self.strategy.position_name == 'fixed_amount':
            position_method = 'fixed_amount'
            buy_single_position = self.strategy.single_position_amount
        else:
            position_method = 'fixed_percentage'
            buy_single_position = self.strategy.single_position_percentage

        title = '%s,interval:%s,signal:%s,single position:%s-%s,stop loss:%s,stop profit:%s,total return:%s' %\
                (self.strategy.stock_pool_name, self.strategy.stock_pool_interval, self.strategy.signal_name,
                 position_method, buy_single_position, self.strategy.stop_loss_ratio, self.strategy.stop_profit_ratio,
                 df_portfolio.iloc[-1]['total_return'])
        df_portfolio.plot(title=title, y=['total_return', 'hs300'], kind='line')
        plt.show()


def find_out_stocks(last_phase_codes, this_phase_codes):
    out_stocks = []

    for code in last_phase_codes:
        if code not in this_phase_codes:
            out_stocks.append(code)

    return out_stocks


def get_trading_dates(begin_date, end_date):

    date_cursor = db.calendar.find(
        {'cal_date': {'$gte': begin_date, '$lte': end_date},
         'is_open': True},
        sort=[('cal_date', ASCENDING)],
        projection={'cal_date': True, '_id': False},
    )
    dates = [x['cal_date'] for x in date_cursor]

    return dates


def backtest_estimate(df_portfolio):
    # 评估回测效果
    df_portfolio['daily_return'] = df_portfolio['net_value'].pct_change(1)
    df_portfolio['daily_return'].dropna()
    risk_free_rate = np.power(1.0375, 1 / 365) - 1
    sharpe_ratio = (df_portfolio['daily_return'].mean() - risk_free_rate) / df_portfolio['daily_return'].std()
    adjust_sharpe_ratio = np.sqrt(244) * sharpe_ratio
    trading_days = len(df_portfolio['net_value'])
    win_ratio = len(df_portfolio[df_portfolio['daily_return'] > 0]) / trading_days
    annual_return = np.power(df_portfolio.iloc[-1]['net_value'], 244 / trading_days) - 1

    # 计算最大回撤
    net_values = list(df_portfolio['net_value'])
    max_drawdown = 0
    index = 0
    for net_value in net_values:
        for next_net_value in net_values[index:]:
            drawdown = 1 - next_net_value / net_value
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        index += 1

    print(df_portfolio)
    print('sharpe_ratio = ', round(adjust_sharpe_ratio, 3))
    print('win_ratio = ', round(win_ratio * 100, 1))
    print('max_drawdown = ', round(max_drawdown * 100, 1))
    print('annual_return = ', round(annual_return * 100, 3))
    print('annual_return/max_drawdown = ', round(annual_return / max_drawdown, 2))
