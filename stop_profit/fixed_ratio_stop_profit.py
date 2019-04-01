from .base_stop_profit import BaseStopProfit


class FixedRatioStopProfit(BaseStopProfit):
    def __init__(self, profit, holding_stocks):
        BaseStopProfit.__init__(self)

        self.profit = profit
        self.holding_stocks = holding_stocks

    def is_stop_profit(self, code, date):
        if code in self.holding_stocks:
            holding_stock = self.holding_stocks[code]

            profit = (holding_stock['last_value'] - holding_stock['cost']) / holding_stock['cost']
            profit *= 100

            print('判断是否需要止盈，股票代码：%s， 日期：%s，当前收益：%5.2f， 止盈线：%4.2f' %
                  (code, date, profit, self.profit), flush=True)
            return profit >= self.profit

        return False
