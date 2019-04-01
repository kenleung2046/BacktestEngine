from .low_pe_stock_pool import LowPeStockPool
from .mid_pe_stock_pool import MidPeStockPool


class StockPoolFactory:
    @staticmethod
    def get_stock_pool(name, strategy):

        if name == 'low_pe_stock_pool':
            return LowPeStockPool(
                strategy.begin_date, strategy.end_date, strategy.stock_pool_interval)

        elif name == 'mid_pe_stock_pool':
            return MidPeStockPool(
                strategy.begin_date, strategy.end_date, strategy.stock_pool_interval)

        return None
