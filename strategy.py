import sys
import os
from datetime import datetime 
from backtest import Backtest
from stock_pool.stock_pool_factory import StockPoolFactory
from position.position_factory import PositionFactory
from stop_loss.stop_loss_factory import StopLossFactory
from stop_profit.stop_profit_factory import StopProfitFactory
from signal.signal_factory import SignalFactory


class Strategy:
    def __init__(self, name):
        self.properties = dict()
        self.holding_stocks = dict()
        self.parse(name)

    def parse(self, strategy_txt):
        strategy_file = os.path.join(sys.path[0], strategy_txt)
        print(strategy_file, flush=True)

        if os.path.exists(strategy_file) is False:
            print('策略文件【%s】不存在，请确认。' % strategy_txt, flush=True)
            return

        with open(strategy_file, encoding='UTF-8') as file:
            for line in file:
                line = line.replace('\n', '')
                if len(line) == 0:
                    continue

                if line.startswith('#') is False:
                    name_value_pair = line.split('=')
                    self.properties[name_value_pair[0]] = name_value_pair[1]

            print(self.properties, flush=True)

    @property
    def name(self):
        if 'name' in self.properties:
            return self.properties['name']
        return ''

    @property
    def begin_date(self):
        begin_date = None
        if 'begin_date' in self.properties:
            begin_date = self.properties['begin_date']
        if begin_date is None or begin_date == '':
            begin_date = '20050101'
        return begin_date

    @property
    def end_date(self):
        end_date = None
        if 'end_date' in self.properties:
            end_date = self.properties['end_date']
        if end_date is None or end_date == '':
            # 判断是不是盘中，如果是盘中就用上一个交易日；
            # 若是盘后，就用当日
            end_date = datetime.now().strftime('%Y%m%d')
        return end_date

    @property
    def stock_pool_interval(self):
        if 'stock_pool_interval' in self.properties:
            return int(self.properties['stock_pool_interval'])
        return 0

    @property
    def stock_pool(self):
        if 'stock_pool' in self.properties:
            return StockPoolFactory.get_stock_pool(
                self.properties['stock_pool'], self)
        return None

    @property
    def stock_pool_name(self):
        return self.properties['stock_pool']

    @property
    def capital(self):
        capital = 1E7
        if 'capital' in self.properties:
            capital = float(self.properties['capital'])
        return capital

    @property
    def position(self):
        if 'position' in self.properties:
            position = self.properties['position']
            return PositionFactory.get_position_method(position, self.properties)

    @property
    def position_name(self):
        return self.properties['position']

    @property
    def single_position_amount(self):
        return self.properties['fixed_amount']

    @property
    def single_position_percentage(self):
        return self.properties['fixed_percentage']

    @property
    def add_position(self):
        if 'add_position' in self.properties:
            add_position = self.properties['add_position']
            return PositionFactory.get_add_position_method(add_position, self)

    @property
    def stop_loss(self):
        stop_loss = None

        if 'stop_loss' in self.properties:
            stop_loss_name = self.properties['stop_loss']
            return StopLossFactory.get_stop_loss_method(
                stop_loss_name, self.properties, self.holding_stocks)

        return stop_loss

    @property
    def stop_loss_ratio(self):
        return self.properties['stop_loss_ratio']

    @property
    def stop_profit(self):
        stop_profit = None

        if 'stop_profit' in self.properties:
            stop_profit_name = self.properties['stop_profit']
            return StopProfitFactory.get_stop_profit_method(
                stop_profit_name, self.properties, self.holding_stocks)

        return stop_profit

    @property
    def stop_profit_ratio(self):
        return self.properties['profit']

    @property
    def signal(self):
        if 'signal' in self.properties:
            signal = self.properties['signal']
            return SignalFactory.get_signal_type(signal)

    @property
    def signal_name(self):
        return self.properties['signal']

    def backtest(self):
        Backtest(self).start()


if __name__ == '__main__':
    strategy = Strategy('low_pe_strategy')
    # strategy = Strategy('mid_pe_strategy')
    print(strategy.name, strategy.begin_date, '-', strategy.end_date, flush=True)
    strategy.backtest()
