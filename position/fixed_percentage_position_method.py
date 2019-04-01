from .base_position import BasePosition


class FixedPercentagePositionMethod(BasePosition):
    def __init__(self, fixed_percentage):
        BasePosition.__init__(self)
        self.fixed_percentage = fixed_percentage

    def get_single_position(self, total_capital):
        single_position = self.fixed_percentage * total_capital
        return single_position
