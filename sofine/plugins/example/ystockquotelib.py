"""Plugin that wraps calling the Yahoo! Finance library `ystockquote`.
"""

from sofine.plugins import plugin_base as plugin_base
import ystockquote


class YStockQuoteLib(plugin_base.PluginBase):
    
    def __init__(self):
        """
* `self.name = 'ystockquotelib'`
* `self.group = 'example'`
* `self.schema = ['fifty_two_week_low', 'market_cap', 'price', 'short_ratio', 
                       'volume','dividend_yield', 'avg_daily_volume', 'ebitda', 
                       'change', 'dividend_per_share', 'stock_exchange', 
                       'two_hundred_day_moving_avg', 'fifty_two_week_high', 
                       'price_sales_ratio', 'price_earnings_growth_ratio',
                       'fifty_day_moving_avg', 'price_book_ratio', 'earnings_per_share', 
                       'price_earnings_ratio', 'book_value']`
* `self.adds_keys = False`
"""
        super(YStockQuoteLib, self).__init__()
        self.name = 'ystockquotelib'
        self.group = 'example'
        self.schema = ['fifty_two_week_low', 'market_cap', 'price', 'short_ratio', 
                       'volume','dividend_yield', 'avg_daily_volume', 'ebitda', 
                       'change', 'dividend_per_share', 'stock_exchange', 
                       'two_hundred_day_moving_avg', 'fifty_two_week_high', 
                       'price_sales_ratio', 'price_earnings_growth_ratio',
                       'fifty_day_moving_avg', 'price_book_ratio', 'earnings_per_share', 
                       'price_earnings_ratio', 'book_value']
        self.adds_keys = False

            
    def get_data(self, keys, args):
        """
* `keys` - `list`. The list of keys to process.
* `args` - `list`. Empty for this plugin. 

Calls the Yahoo API to get all available fields for each ticker provided as a key in `keys`."""
        return {ticker : ystockquote.get_all(ticker) for ticker in keys} 


plugin = YStockQuoteLib

