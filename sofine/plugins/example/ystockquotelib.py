import ystockquote


def get_data(data, args):
    """Calls the Yahoo API to get all available fields for each ticker provided 
as a key in 'data'."""
    for ticker in data.keys():
        data[ticker].update(ystockquote.get_all(ticker))
    return data


def parse_args(argv):
    """get_data() takes no arguments so this is a trivial pass-through."""
    is_valid = True
    return is_valid, argv


def is_source():
    """This data source cannot be the first in a chain of calls. It will add available 
attributes to those mapped to each key in the data arg passed to get_data()"""
    return False


def get_schema():
    """The set of all possible attribute keys returned for each key from this data
source. This data source can return a different arbitrary subset of these keys
in the dict of attributes returned for each key passed in the 'data' arg to get_data()."""
    return ['fifty_two_week_low', 'market_cap', 'price', 'short_ratio', 'volume',
            'dividend_yield', 'avg_daily_volume', 'ebitda', 'change',
            'dividend_per_share', 'stock_exchange', 'two_hundred_day_moving_avg', 
            'fifty_two_week_high', 'price_sales_ratio', 'price_earnings_growth_ratio',
            'fifty_day_moving_avg', 'price_book_ratio', 'earnings_per_share', 
            'price_earnings_ratio', 'book_value']
