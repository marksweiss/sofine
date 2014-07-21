from sofine.plugins import plugin_base as plugin_base


class YstockquoteLibMock(plugin_base.PluginBase):

    def __init__(self):
        self.name = 'ystockquotelib_mock'
        self.group = 'mock'
        self.schema = ['fifty_two_week_low', 'market_cap', 'price', 'short_ratio', 
                       'volume','dividend_yield', 'avg_daily_volume', 'ebitda', 
                       'change', 'dividend_per_share', 'stock_exchange', 
                       'two_hundred_day_moving_avg', 'fifty_two_week_high', 
                       'price_sales_ratio', 'price_earnings_growth_ratio',
                       'fifty_day_moving_avg', 'price_book_ratio', 'earnings_per_share', 
                       'price_earnings_ratio', 'book_value']


    def get_data(self, keys, args):
        """Pretends to call the Yahoo API to get all available fields for each ticker provided 
as a key in 'keys'."""
        mock_attributes = dict.fromkeys(self.schema, 1.0)
        return {ticker : mock_attributes for ticker in keys}


    def parse_args(self, argv):
        """get_data() takes no arguments so this is a trivial pass-through."""
        is_valid = True
        return is_valid, argv


    def adds_keys(self):
        """This data source cannot be the first in a chain of calls. It will add available 
attributes to those mapped to each key in the data arg passed to get_data()"""
        return False


plugin = YstockquoteLibMock

