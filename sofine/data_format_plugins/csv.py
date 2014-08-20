import csv
import cStringIO
import sys

# TODO Document only supported CSV format
# - No column headers
# - Key is always position 0
# - Attr keys and values alternate in positions 1..n


delimiter = ','
def set_delimiter(c):
    delimiter = c


lineterminator = '\n'
def set_line_terminator(s):
    lineterminator = s


quoting = csv.QUOTE_NONE
def set_quoating_none():
    quoting_policy = csv.QUOTE_NONE

def set_quoting_all():
    quoting_policy = csv.QUOTE_ALL

def set_quoting_minimal():
    quoting_policy = csv.MINIMAL

def set_quoting_nonnumeric():
    quoting_policy = csv.NONNUMERIC


quotechar = '"'
def set_quote_char(c):
    quotechar = c


def deserialize(data):
    ret = {}
    schema = []
  
    in_strm = cStringIO.StringIO(data) 
    reader = csv.reader(in_strm, encoding="utf-8", delimiter=delimiter,
                        lineterminator=lineterminator, quoting=quoting, quotechar=quotechar)

    for row in reader:
        # 0th elem in CSV row is data row key
        key = row[0]
        # Remaining data in CSV row are the attribute key/vals. Convert to array of key/val dicts
        ret[key] = [{row[j] : row[j + 1]} for j in range(1, len(row) - 1)]
   
    in_data_strm.close()
    
    return ret


def serialize(data):
    out_strm = cStringIO.StringIO()
    writer = csv.writer(out_strm, encoding="utf-8", delimiter=delimiter,
                        lineterminator=lineterminator, quoting=quoting, quotechar=quotechar)
    
    # Flatten each key -> [attrs] 'row' in data into a CSV row with
    #  key in the 0th position, and the attr values in an array in fields 1 .. N
    for key, attrs in data.iteritems():
        row = []
        row.append(str(key))
        for attr in attrs:
            row.append(str(attr.keys()[0]))
            row.append(str(attr.values()[0]))
        writer.writerow(row)

    ret = out_strm.getvalue()
    out_strm.close()

    return ret


def get_content_type():
    return 'text/csv'


