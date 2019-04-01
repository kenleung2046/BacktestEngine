from .base_stop_profit import BaseStopProfit


class DrawbackStopProfit(BaseStopProfit):
    def __init__(self, base_profit, drawdown, holding_stocks):
        BaseStopProfit.__init__(self)
        self.base_profit = base_profit
        self.drawdown = drawdown
        self.holding_stocks = holding_stocks

    def update_holding_stock(self, code):
        if code in self.holding_stocks:
            holding_stock = self.holding_stocks[code]

            if 'highest_value' in holding_stock:
                if holding_stock['last_value'] > holding_stock['highest_value']:
                    holding_stock['highest_value'] = holding_stock['last_value']
            else:
                profit = (holding_stock['last_value'] - holding_stock['cost']) / holding_stock['cost']
                profit *= 100

                print('回撤止盈持仓股更新，股票代码：%s, 当前收益：%4.2f' % (code, profit), flush=True)

                if profit > self.base_profit:
                    holding_stock['highest_value'] = holding_stock['last_value']

    def is_stop_profit(self, code, date):
        if code in self.holding_stocks:
            holding_stock = self.holding_stocks[code]

            if 'highest_value' in holding_stock:
                highest = holding_stock['highest_value']
                value = holding_stock['last_value']

                profit = (value - highest) * 100 / highest

                print('达到回撤止盈阀值，股票代码：%s, 当前回撤：%4.2f' % (code, profit), flush=True)

                return (profit < 0) & (abs(profit) >= self.drawdown)

        return False
