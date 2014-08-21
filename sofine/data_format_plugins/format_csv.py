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


quoting = csv.QUOTE_MINIMAL
def set_quoating_none():
    quoting = csv.QUOTE_NONE

def set_quoting_all():
    quoting = csv.QUOTE_ALL

def set_quoting_minimal():
    quoting = csv.MINIMAL

def set_quoting_nonnumeric():
    quoting = csv.NONNUMERIC


quotechar = '"'
def set_quote_char(c):
    quotechar = c


def deserialize(data):
    ret = {}
    schema = []
  
    in_strm = cStringIO.StringIO(data) 
    reader = csv.reader(in_strm, delimiter=delimiter, lineterminator=lineterminator, 
                        quoting=quoting, quotechar=quotechar)

    for row in reader:
        if not len(row):
            continue

        # 0th elem in CSV row is data row key
        key = row[0]
        key.encode('utf-8')
        # Remaining data in CSV row are the attribute key/vals. Convert to array of key/val dicts
        ret[key] = []
        # Curious off by 1 thing here. We skipped the key in 0th position
        #  and we are looking ahead by 1, so this is the rare time -2 is correct
        ret[key] = [{row[j].encode('utf-8') : row[j + 1].encode('utf-8')}
                    for j in range(1, len(row) - 2)]
   
    in_strm.close()
    
    return ret


def serialize(data):
    out_strm = cStringIO.StringIO()
    writer = csv.writer(out_strm, delimiter=delimiter, lineterminator=lineterminator,
                        quoting=quoting, quotechar=quotechar)
    
    # Flatten each key -> [attrs] 'row' in data into a CSV row with
    #  key in the 0th position, and the attr values in an array in fields 1 .. N
    for key, attrs in data.iteritems():
        row = []
        row.append(str(key).encode('utf-8'))
        for attr in attrs:
            row.append(str(attr.keys()[0]).encode('utf-8'))
            row.append(str(attr.values()[0]).encode('utf-8'))
        writer.writerow(row)

    ret = out_strm.getvalue()
    out_strm.close()

    return ret


def get_content_type():
    return 'text/csv'


