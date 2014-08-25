"""Supports taking in data and returning data from calls to `get_data` and `get_namespaced_data` as CSV."""

import csv
import sys
from io import BytesIO

# TODO Document only supported CSV format
# - No column headers
# - Key is always position 0
# - Attr keys and values alternate in positions 1..n


delimiter = ','
def set_delimiter(c):
    delimiter = c


lineterminator = '|'
def set_line_terminator(s):
    lineterminator = s


quoting = csv.QUOTE_MINIMAL
def set_quoting_none():
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
    """
* `data` - `dict mapping string keys to lists of dicts of string keys and arbitrary values`. 
    
    Required function for a data format plugin. Converts data in CSV format to the sofine Python data 
structure for data sets. In particular, data passed to `sofine` on `stdin` will be processed with this call. 
This data is expected to adhere to this format (assuming the comma is the delimiter):
    
    Key,attribute_name_1,attribute_value_1, Key,attribute_name_1, ...

which will be translated to:

    {   "Key": [attribute_name_1: attribute_value_1, ...]
        ...
    }
"""
    
    ret = {}
    schema = []
   
    # Note this hack with lineterminator. The alternative to manually splitting lines is
    #  to put 'data' into a StringIO, because csv.reader needs an iterable
    reader = csv.reader(data.split(lineterminator), delimiter=delimiter, lineterminator='', 
                        quoting=quoting, quotechar=quotechar)

    for row in reader:
        if not len(row):
            continue

        # 0th elem in CSV row is data row key
        key = row[0]
        key.encode('utf-8')
        
        attr_row = row[1:]
        ret[key] = [{attr_row[j].encode('utf-8') : attr_row[j + 1].encode('utf-8')}
                    for j in range(0, len(attr_row) - 1, 2)]
  
    return ret


def serialize(data):
    """
* `data` - `dict mapping string keys to lists of dicts of string keys and arbitrary values`. 
    
    Required function for a data format plugin. Converts data from the sbfine Python data 
structure for data sets into CSV. In particular, data passed from `sofine` to `stdout` will be processed with this call. 
This data is expected to adhere to this format (assuming the comma is the delimiter):
    
    {   
        "Key": [attribute_name_1: attribute_value_1, ...]
        ...
    }

which is be translated to:
    
    Key,attribute_name_1,attribute_value_1,Key,attribute_name_1, ...

"""
    # Python docs cryptically say the csv Writer should set the 'b' flag on its
    #  File writer "on platforms that support it." Googling finds that to make this work
    #  with streams you should use BytesIO. StringIO also works (at least for ASCII).
    out_strm = BytesIO()
    writer = csv.writer(out_strm, delimiter=delimiter, lineterminator='|',
                        quoting=quoting, quotechar=quotechar)
    
    # Flatten each key -> [attrs] 'row' in data into a CSV row with
    #  key in the 0th position, and the attr values in an array in fields 1 .. N
    for key, attrs in data.iteritems():
        row = []
        row.append(key)
        for attr in attrs:
            row.append(attr.keys()[0])
            row.append(attr.values()[0])
        writer.writerow(row)

    ret = out_strm.getvalue()
    out_strm.close()

    return ret


def get_content_type():
    """
Required for a data format plugin. Returns the value for the HTTP Content-Type header. 
"""
    return 'text/csv'


