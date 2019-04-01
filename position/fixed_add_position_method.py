from .base_position import BasePosition


class FixedAddPositionMethod(BasePosition):
    def __init__(self, holding_stocks):
        BasePosition.__init__(self)
        self.holding_stocks = holding_stocks

    def update_holding_stock(self, code, added_cost, added_volume):
        if code in self.holding_stocks:
            holding_stock = self.holding_stocks[code]
            holding_stock['cost'] += added_cost
            holding_stock['volume'] += added_volume
            holding_stock['added'] = True
            holding_stock['last_value'] += added_cost

    def get_single_position(self, code):
        if code in self.holding_stocks:
            holding_stock = self.holding_stocks[code]

            # 如果股票已经加过一次仓，就不再加仓
            # if 'added' in holding_stock:
            #     return 0
            # else:
            return holding_stock['cost']

        return 0
