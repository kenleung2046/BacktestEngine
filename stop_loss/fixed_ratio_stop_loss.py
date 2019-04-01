from .base_stop_loss import BaseStopLoss


class FixedRatioStopLoss(BaseStopLoss):
    def __init__(self, ratio, holding_stocks):
        BaseStopLoss.__init__(self)
        
        self.ratio = ratio
        self.holding_stocks = holding_stocks

    def is_stop(self, code, date):
        if code in self.holding_stocks:
            holding_stock = self.holding_stocks[code]
            
            profit = (holding_stock['last_value'] - holding_stock['cost']) * 100 / holding_stock['cost']

            print('判断是否需要止损，股票代码：%s， 日期：%s，当前收益：%5.2f， 止损线：%4.2f' %
                  (code, date, profit, self.ratio), flush=True)

            return (profit < 0) & (abs(profit) >= self.ratio)

        return False
