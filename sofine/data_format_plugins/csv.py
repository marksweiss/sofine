import csv
import sys


def deserialize(data):
    data = {}
    schema = []

    idx = 0
    reader = csv.reader(sys.stdin)
    for row in reader:
        # TODO Figure out whether we can support a format without column names
        # TODO This conditional sucks
        if idx == 0:
            # TODO Support configuring csv delimiter
            schema = row.split(',')
        else:
            # 0th elem in CSV row is data row key
            key = row[0]
            data[key] = []
            # Loop over the schema and attr values in the rest of CSV row
            #  and build dicts an put in array of attrs for this key
            for attr_idx in range(1, len(row)):
                schema_idx = attr_idx - 1
                data[key].append({schema[schema_idx] : row[attr_idx]})
    
    return data


def serialize(data):
    # TODO Support quote-qualifying each value
    # csv.QUOTE_ALL, QUOTE_MINIMAL, QUOTE_NONNUMERIC, QUOTE_NONE
    # TODO Look at the Dialect object, many other settings around espcaping, etc.
    # Support this by exposing a config interface similar to file_source
    rows = []
    # Flatten each key -> [attrs] 'row' in data into a CSV row with
    #  key in the 0th position, and the attr values in an array in fields 1 .. N
    for key, attrs in data.iteritems():
        row = []
        row.append(str(key))
        for attr in attrs:
            # TODO Support column headers on first line with call to get_schema()
            # TODO Figure out whether we can support something without column headers
            # row.append(str(attr.keys()[0]))
            row.append(str(attr.values()[0]))
        rows.append(row)
    
    # TODO Support configuring csv delimiter
    return ','.join(rows)


def get_content_type():
    return 'application/csv'
