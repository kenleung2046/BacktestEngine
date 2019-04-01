from .fixed_ratio_stop_loss import FixedRatioStopLoss


class StopLossFactory:
    @staticmethod
    def get_stop_loss_method(name, strategy_properties, holding_stocks):
        if name == 'fixed_ratio':
            stop_loss_ratio = float(strategy_properties['stop_loss_ratio'])
            return FixedRatioStopLoss(stop_loss_ratio, holding_stocks)

        return None
