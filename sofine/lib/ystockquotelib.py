import ystockquote


def get_data(data, *args):
    """Calls the Yahoo API to get all available fields for each ticker provided 
as a key in 'data'."""
    for ticker in data.keys():
        data[ticker].update(ystockquote.get_all(ticker))
    return data


# get_data() takes no arguments so this is a trivial pass-through
def parse_args(argv):
    is_valid = True
    return is_valid, argv
