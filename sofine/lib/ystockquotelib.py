import ystockquote


def get_data(data, args):
    """Calls the Yahoo API to get all available fields for each ticker provided 
as a key in 'data'."""
    for ticker in data.keys():
        data[ticker].update(ystockquote.get_all(ticker))
    return data


# get_data() takes no arguments so this is a trivial pass-through
def parse_args(argv):
    is_valid = True
    return is_valid, argv


def is_source():
    return False


def schema():
    return ['fifty_two_week_low', 'market_cap', 'price', 'short_ratio', 'volume',
            'dividend_yield', 'avg_daily_volume', 'ebitda', 'change',
            'dividend_per_share', 'stock_exchange', 'two_hundred_day_moving_avg', 
            'fifty_two_week_high', 'price_sales_ratio', 'price_earnings_growth_ratio',
            'fifty_day_moving_avg', 'price_book_ratio', 'earnings_per_share', 
            'price_earnings_ratio', 'book_value']
