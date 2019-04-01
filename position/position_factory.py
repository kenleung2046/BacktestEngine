from .fixed_amount_position_method import FixedAmountPositionMethod
from .fixed_percentage_position_method import FixedPercentagePositionMethod
from .fixed_add_position_method import FixedAddPositionMethod


class PositionFactory:

    @staticmethod
    def get_position_method(name, strategy_properties):
        if name == 'fixed_amount':
            fixed_amount = float(strategy_properties['fixed_amount'])
            return FixedAmountPositionMethod(fixed_amount)

        if name == 'fixed_percentage':
            fixed_percentage = float(strategy_properties['fixed_percentage'])
            return FixedPercentagePositionMethod(fixed_percentage)

    @staticmethod
    def get_add_position_method(name, strategy):
        if name == 'fixed':
            return FixedAddPositionMethod(strategy.holding_stocks)
