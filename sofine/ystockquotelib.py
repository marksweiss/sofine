import ystockquote

def get_yahoo_additional_position_data(data):
    for ticker in data.keys():
        data[ticker].update(ystockquote.get_all(ticker))
    return data

