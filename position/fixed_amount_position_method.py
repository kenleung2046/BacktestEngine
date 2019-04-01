from .base_position import BasePosition


class FixedAmountPositionMethod(BasePosition):
    def __init__(self, fixed_amount):
        BasePosition.__init__(self)
        self.fixed_amount = fixed_amount

    def get_single_position(self, total_capital):
        return self.fixed_amount
