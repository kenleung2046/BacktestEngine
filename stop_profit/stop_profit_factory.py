from .fixed_ratio_stop_profit import FixedRatioStopProfit
from .drawback_stop_profit import DrawbackStopProfit


class StopProfitFactory:

    @staticmethod
    def get_stop_profit_method(name, strategy_properties, holding_stocks):

        if name == 'fixed':
            profit = float(strategy_properties['profit'])
            return FixedRatioStopProfit(profit, holding_stocks)

        elif name == 'drawback':
            base_profit = float(strategy_properties['base_profit'])
            drawdown = float(strategy_properties['drawdown'])

            return DrawbackStopProfit(base_profit, drawdown, holding_stocks)

        return None
