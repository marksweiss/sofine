## What Problem Does sofine solve?

You need to get data related to a set of keys from many sources: web scrapers, Web APIs, flat files, data stores. Wouldn't it be nice to build one combined data set over multiple calls with one command line, REST or Python call? Wouldn't it be great if each data retrieval script you wrote was a reusable plugin that you could combine with any other?

You need a "glue API." 

This is the problem `sofine` solves. It's a small enough problem that you could solve it yourself. But `sofine` is minimal to deploy and write plugins for, and has already decided in an optimally flexible way the same design decisions you would have to make if you wrote this yourself. 

## Features

1. Do (almost) no more work than if you wrote one-off data collection scripts 
2. Manage your data retrieval plugins in any directory with any directory structure you like
3. Call plugins from the command line, as REST resources or from Python
4.  Chain as many plugin calls as you want together and get back one JSON data set with all the data collected from all the chained calls
5. If called from the command line, `sofine` reads data from `stdin` if it is present, and always outputs to `stdout`. So `sofine` piped calls can themselves be composed in larger piped expressions.

For fun, here is an example of features 4 and 5, combining a `sofine` pipeline with the fantastic [JSON query tool jq](https://github.com/stedolan/jq) for further filtering.

    echo '{"AAPL":[]}' | python $PYTHONPATH/sofine/runner.py '--SF-s ystockquotelib --SF-g example | --SF-s google_search_results --SF-g example' | jq 'map(recurse(.results) | {titleNoFormatting}'

## Overview

To get started, you:

1. `pip install sofine`
2. Make sure your `$PYTHONPATH` points to the package directory where pip installed `sofine`
3. Create a plugin directory and assign it's path to the environment `SOFINE_PLUGIN_PATH`
4. Write and call some data retrieval plugins (or just start using the included ones)

Plugins require two attributes and one method in the simple case and three methods in the most elaborate edge case. You can optionally define two additional attributes for clients to use to introspect your plugins.

`sofine` ships with a few useful plugins to get you started and give you the idea; you can combine these with your custom plugins with no additional configuration or code. The included plugins are:

* `sofine.plugins.standard.file_source` - Retrieves keys from a JSON file to add to the data set being built. See [here](http://marksweiss.github.io/sofine/docs/sofine/plugins/standard/file_source.m.html) for the details.
* `example.archive_dot_org_search_results` - Takes a search query and returns results from www.archive.org
* `example.google_search_results` - Takes a search query and returns results from the Google Search API
* `example.fidelity` - Takes a userId, pin, accountId and email, logs into Fidelity, scrapes the account portfolio and returns the tickers found as keys and four attributes of data for each ticker
* `example.ystockquotelib` - Takes a list of tickers and returns the data available from Yahoo! Finance for each ticker

Here is what usage looks like ...

From the command line:

    $ echo '{"AAPL":[]}' | python $PYTHONPATH/sofine/runner.py '--SF-s ystockquotelib --SF-g example | --SF-s google_search_results --SF-g example'

REST-fully:

    $ python $PYTHONPATH/sofine/rest_runner.py
    
    $ curl -X POST -d '{"AAPL":[]}' --header "Content-Type:application/json" http://localhost:10000/SF-s/ystockquotelib/SF-g/example/SF-s/google_search_results/SF-g/example

From Python:

    import sofine.runner as runner
    
    data = {"AAPL": []}
    data_sources = ['ystockquotelib', 'google_search_results']
    data_source_groups = ['example', 'example']
    data_source_args = [[], []]
    data = runner.get_data_batch(data, data_sources, data_source_groups, data_source_args)

All three calling styles return the same data set. `sofine` data sets map string keys to arrays of attributes, which are Python dicts. By default, these are returned as JSON to stdout. `sofine` also ships with support for CSV, and you can write your own data format plugins (more on that below).

Here is an example retrieved using included data retrieval plugins: the key "AAPL," with all the attributes retrieved from Yahoo! Finance and the Google Search API combined. 

    {
    "AAPL": 
        [
            {
                "results": [
                {
                    "GsearchResultClass": "GwebSearch",
                    "cacheUrl": "http://www.google.com/search?q=cache:XhbIlCyrcXMJ:finance.yahoo.com",
                    "content": "View the basic <b>AAPL</b> stock chart on Yahoo! Finance. Change the date range, chart type and compare Apple Inc. against other companies.",
                    "title": "<b>AAPL</b>: Summary for Apple Inc.- Yahoo! Finance",
                    "titleNoFormatting": "AAPL: Summary for Apple Inc.- Yahoo! Finance",
                    "unescapedUrl": "http://finance.yahoo.com/q?s=AAPL",
                    "url": "http://finance.yahoo.com/q%3Fs%3DAAPL",
                    "visibleUrl": "finance.yahoo.com"
                },
                ...
                ...
                ]
            },
            {"avg_daily_volume": "59390100"},
            {"book_value": "20.193"},
            {"change": "+1.349"},
            {"dividend_per_share": "1.7771"},
            {"dividend_yield": "1.82"},
            {"earnings_per_share": "6.20"},
            {"ebitda": "59.128B"},
            {"fifty_day_moving_avg": "93.8151"},
            {"fifty_two_week_high": "99.24"},
            {"fifty_two_week_low": "63.8886"},
            {"market_cap": "592.9B"},
            {"price": "99.02"},
            {"price_book_ratio": "4.84"},
            {"price_earnings_growth_ratio": "1.26"},
            {"price_earnings_ratio": "15.75"},
            {"price_sales_ratio": "3.28"},
            {"short_ratio": "1.70"},
            {"stock_exchange": "\"NasdaqNM\""},
            {"two_hundred_day_moving_avg": "82.8458"},
            {"volume": "55317688"}
        ]
    }  

## Installing sofine

    pip install sofine 

Then, make sure your `$PYTHONPATH` variable is set and points to the site-packages directory of your Python where pip installed `sofine`.

    export PYTHONPATH=<MY PYTHON SITE-PACKAGES DIRECTORY>

Then, create a plugin directory and assign its path to an environment variable `SOFINE_PLUGIN_PATH`. You probably want to add it to your shell configuration file.

    export SOFINE_PLUGIN_PATH=<MY PATH>

`sofine` runs its REST server on port 10000. If you want to use a different port, set the environment variable `SOFINE_REST_PORT`. You probably want to add it to your shell configuration file.
    
    export SOFINE_REST_PORT=<MY PORT>

If you are going to create data format plugins, create a data format lugin directory and assign its path to the environment variable `SOFINE_DATA_FORMAT_PLUGIN_PATH`.

    export SOFINE_DATA_FORMAT_PLUGIN_PATH=<MY PATH>

If you want to use the included `fidelity` and `ystockquotelib` plugins in the `plugins.examples` plugin group, also install the following:

    easy_install mechanize
    easy_install beautifulsoup4
    pip install ystockquote

## Two Kinds of Plugins: Data Retrieval and Data Format 

`sofine` uses two kinds of plugins. _Data retrieval plugins_ are what you call singly or in chained expressions to return data sets. When the documentation says "plugin," it means data retrieval plugin. But `sofine` also supports plugins for the data format of data sets. By default `sofine` expects input on `stdin` in JSON format and writes JSON to `stdout`. But there is also a plugin for CSV.

## How Python Data Retrieval Plugins Work and How to Write Them

### Boilerplate

All plugins inherit from a super class, `sofine.plugins.plugin_base.PluginBase`. Your plugin `__init__` method must call the super class `__init__`.

    class ArchiveDotOrgSearchResults(plugin_base.PluginBase):
        def __init__(self):
            super(ArchiveDotOrgSearchResults, self).__init__()

The last line of your plugin should assign the module-scope variable `plugin` to the name of your plugin class.  For example:

    plugin = ArchiveDotOrgResults 

### Plugin Attributes

The base class defines four attributes:

* `self.name` - `string`. The name of the plugin
* `self.group` - `string`. The pluging group of the plugin. This the subdirectory in the plugin directory into which the plugin is deployed.
* `self.schema` - `list of string`. The set of attribute keys that calls to `get_data` can associate with a key passed to `get_data`.
* `self.adds_keys` - `boolean`. Indicates whether the plugin adds keys to the data set being built or only adds attributes to existing keys.

You must always define `name` and `group`.

#### `name`

`name` must match the module name of the plugin module, that is the name you would use in an `import` statement.

#### `group`

`group` must match the name of the subdirectory of your plugin directory where the plugin is deployed. `sofine` uses `name` and `group` to load and run your plugin, so they have to be there and they have to be correct.

#### `schema`

`schema` is optional. It allows users of your plugin to introspect it.

`schema` is a list of strings that tells a client of your plugin the set of possible attribute keys that your plugin returns for each key it recieves. For example, if your plugin takes stock tickers as keys and looks up a current quote, its `schema` declaration might look like this:
    
    self.schema = ['quote']

#### `adds_keys`

`adds_keys` lets users ask your plugin if it adds keys to the data set being built when `sofine` calls it, or if it just adds attributes for the keys it receives.

For example, the `ystockquotelib` plugin in the `sofine.plugins.example` group takes a set of stock tikckers as keys and retrieves the available data for each of them from Yahoo! Finance. This plugin has the attribute declaration `self.adds_keys = False`. On the other hand, the `sofine.plugins.fidelity` plugin is a scraper that can log into the Fidelity, go to the portfolio page for the logged in user, scrape all the tickers for the securities in that portfolio, and add those keys and whatever data it finds to the data set being built. This plugin has a value of `True` for `adds_keys`.

### Plugin Methods

Plugins also have four methods.

#### `get_data`

`get_data` is not implemented in the base class and must be implemented by you in your plugin.

This method takes a list of keys and a list of arguments. It must return a dict whose keys are a proper superset of the keys it received (the return set of keys can have more keys than were passed to `get_data` if the plugin adds keys). This dict must have string keys and a dict value for each key. The dict value is the data retrieved for each key. The keys in that dict must be a set of strings that is a proper subset of the set of strings in `self.schema`.

Here is an example of `get_data` from the `sofine` plugin `sofine.plugins.example.ystockquotelib`.

    def get_data(self, keys, args):
        """
        * `keys` - `list`. The list of keys to process.
        * `args` - `'list`. Empty for this plugin.
        Calls the Yahoo API to get all available fields for each ticker provided as a key in `keys`."""
        return {ticker : ystockquote.get_all(ticker) for ticker in keys}

#### `get_namespaced_data`

A wrapper around `get_data` provided by `sofine`, which return the same data with attribute keys wrapped in a namespace of the plugin group and name. So our example `quote` attribute above would look like this in the returned data set:

    {"trading::get_quotes::quote" : 47.65}

#### `parse_args`

The other method you will often need to implement is `parse_args`. If your `get_data` requires no arguments you need not implement `parse_args`. But if your `get_data` call requires arguments, you must implement `parse_args`. The method takes an `argv`-style list of alternating arg names and values and is responsible for validating the correctness of argument names and values and returing a tuple with two members. The first member is a boolean `is_valid`. The second is the parsed list of argument values (without the argument names).

Here is an example from the `sofine` plugin `sofine.plugins.standard.file_source`.

    def parse_args(self, argv):
        """`[-p|--path]` - Path to the file listing the keys to load into this data source."""

        usage = "[-p|--path] - Path to the file listing the keys to load into this data source."
        parser = OptionParser(usage=usage)
        parser.add_option("-p", "--path", 
                        action="store", dest="path",
                        help="Path to the file listing the keys to load into this data source. Required.") 
        (opts, args) = parser.parse_args(argv)
    
        is_valid = True
        if not opts.path:
            print "Invalid argument error."
            print "Your args: path {0}".format(opts.path)
            print usage
            is_valid = False

        return is_valid, [opts.path]

#### `get_schema`

The third method is `get_schema`. You will rarely need to implement this. Any plugin that knows the set of attributes it can return for a key doesn't need to implement `get_schema` and can rely on the default, which returns the set of attribute keys you define.

#### `get_namespaced_schema`

`get_namespaced_schema` returns the set of attribute keys you define in `self.schema` in a namespace qualified with the plugin group and name. For example, if our stock quote plugin mentioned above is named `get_quotes` and it is in the `trading` group, the return value of `get_schema` would be `["trading::get_quotes::quote"]`. You do not have to implement this, whether or not you implemented `get_schema`, because `sofine` provides it by wrapping `get_schema`.

### A Complete Plugin Example

This is a small amount of overhead compared to writing one-off scripts for the return on investment of being able to know where your plugins are, call them with standard syntax, and compose them with each other in any useful combination.

How small? Here is the Google Search API plugin that ships with `sofine`.

It starts with a helper function that you would have to write in any one-off script to call the API.

    import urllib
    import urllib2
    import json

    def query_google_search(k):
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={0}'.format(urllib.quote(k))
        ret = urllib2.urlopen(url)
        ret = ret.read()
        ret = json.loads(ret)
    
        if ret: 2
            ret = {'results' : ret['responseData']['results']}
        else:
            ret = {'results' : []}
    
        return ret

Now, here are the 11 additional lines of code you need to make your plugin run in `sofine`. 
    
    from sofine.plugins import plugin_base as plugin_base

    class GoogleSearchResults(plugin_base.PluginBase):

        def __init__(self):
            super(GoogleSearchResults, self).__init__()
            self.name = 'google_search_results'
            self.group = 'example'
            self.schema = ['results']
            self.adds_keys = False

        def get_data(self, keys, args):
            return {k : query_google_search(k) for k in keys}

    plugin = GoogleSearchResults

Just for fun, here is a second example. This shows you how easy it is to wrap existing Python API wrappers as `sofine` plugins. 

    from sofine.plugins import plugin_base as plugin_base
    import ystockquote

    class YStockQuoteLib(plugin_base.PluginBase):
    
        def __init__(self):
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
            return {ticker : ystockquote.get_all(ticker) for ticker in keys} 

    plugin = YStockQuoteLib




# TODO RIGHT HERE
## How Python Data Retrieval Plugins Work and How to Write Them



## How Data Format Plugins Work and How to Write Them

`sofine` defaults to expecting input and returning output in JSON format. The library also includes a CSV data format plugin. If these don't meet your needs you can write your own, deploy them in your `SOFINE_DATA_FORMAT_PLUGIN_PATH` plugin directory and the use them by passing an additional data format argument in your calls.

* `deserialize(data)` - converts data in the data format to a Python data structure
* `serialize(data)` - converts a Python data structure to the data format
* `get_content_type()` - returns the correct value for the HTTP Content-Type header for the data format

The included `format_json` plugin provides a trivial example:

    import json

    def deserialize(data):
        return json.loads(data)

    def serialize(data):
        return json.dumps(data)

    def get_content_type():
        return 'application/json'

Formats without an isomorphic mapping to Python dicts and lists (which correspond to JSON objects and arrays) require some implementation. Specifically, your plugin needs to be aware of the `sofine` data structure for its data retrieval data sets, so that it can convert from the data format into that Python data structure in `deserialize` anc convert from that Python data structure into your data format (in a way that makes sense and is documented in your plugin) in `serialize`.

Remember, `sofine` data sets look like this:

    {
     "AAPL": 
        [
            {
                "results": [
                {
                    "GsearchResultClass": "GwebSearch",
                    ...

                },
                ...
                ]
            },
            {"avg_daily_volume": "59390100"},
            {"book_value": "20.193"},
            ...
        ]
    } 

As an example, here are the two methods in the included `format_csv` plugin:

    def deserialize(data):
        ret = {}
        schema = []
   
        reader = csv.reader(data.split(lineterminator), delimiter=delimiter, i
                            lineterminator='', quoting=quoting, quotechar=quotechar)

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

### Data Formats of Included Data Format Plugins

#### format_json

The `format_json` plugin is isomorphic to the internal `sofine` data format. Input data is in JSON that maps string keys to array of objects, with each object having one string key and one string value. The keys are sofine data set keys; the array of objects is the array of key/value attributes associted with that key.

So the JSON input and output is in this format:
    
    {
     "AAPL": 
        [
            {"avg_daily_volume": "59390100"},
            {"book_value": "20.193"},
            ...
        ]
    } 

#### format_csv

CSV data is not hierarchical, so `sofine` must make some design decision about how to represent its data format in CSV.  The library expects input and output in CSV to be structured so that the key for each record is in the first field in a row, and the attribute keys and values mapped to that key follow on the same row with keys and values alternating.  Essentially, each `sofine` record is just flattened into a CSV row.

Using the same example:

    AAPL, avg_daily_volume, 59390100, book_value, 20.193

#### format_xml

The XML format attempts to map the JSON hierarchical data format of `sofine` onto a reasonable XML representation.XML input and output looks like this, for the same example:

    <data>
        <row>
            <key>AAPL</key>
            <attributes>
                <attribute>
                    <attribute_key>avg_daily_volume</attribute_key>
                    <attribute_value>59390100</attribute_value>
                </attribute>
                <attribute>
                    <attribute_key>book_value</attribute_key>
                    <attribute_value>20.193</attribute_value>
                </attribute>
                ...
                ...
            </attributes>
        </row>
        ...
        ...
    </data>

## How to Call Data Retrieval Plugins

As we saw above in the Introduction section, there are three ways to call plugins, from the command line, as REST resources, or in Python.  When calling plugins to retrieve data, you need to pass three or four arguments, `data`,  the plugin name, the plugin group and the plugin action. 

There are six actions, which correspond to the five methods `get_data`, `get_namespaced_data`, `parse_args`, `get_schema` and `get_namespaced_schema`, while `adds_keys` returns the value of the the plugin's `self.adds_keys`.

    get_data
    get_namespaced_data
    parse_args
    get_schema
    get_namespaced_schema
    adds_keys

### Calling From the Command Line

When calling data retrieval plugins, you can optionally pass this argumehnt to control the data_format `sofine` expects any input to be in and the data format for the returned data set. This arguement is passed once before any sofine data retrieval calls, and applies that format to all of the data retrieval calls.

* `[--SF-d|--SF-data-format]` - The data format for input to a data retrieval call and for the returned data set. Optional. Default is 'json'.

You then pass these arguments for each data retreival call:

* `[--SF-s|--SF-data-source]` - The name of the data source being called. This is the
name of the plugin module being called. Required.
* `[--SF-g|--SF-data-source-group`] - The plugin group where the plugin lives. This is 
the plugins subdirectory where the plugin module is deployed. Required.
* `[--SF-a|--SF-action]` - The plugin action being called. Optional if the action is `get_data`.

Any additional arguments that a call to `get_data` requires should be passed following the `--SF-s` and `--SF-g` arguments.

### Calling REST-fully

`sofine` ships with a server which you launch at `python sofine/rest_runner.py` to call plugins over HTTP. The servers runs by default on `localhost` on port `10000`. You can change the port it is running on by setting the environment variable `SOFINE_REST_PORT`. REST calls use the same arguments as CLI calls without the leading dashes. Args and their values alternate for form the resource path. See the examples in the following sections.

### get_data Examples

Here are examples of calling `get_data`:
    
    python $PYTHONPATH/sofine/runner.py '--SF-s fidelity --SF-g example -c <CUSTOMER_ID> -p <PIN> -a <ACCOUNT_ID> -e <EMAIL> | --SF-s ystockquotelib --SF-g example'

Notice that `--SF-a` is ommitted, which means this is chained call using the default action `get_data`, first from the `fidelity` plugin (which is called first becasue it adds the set of keys returned) and then from the `ystockquotelib` plugin (which adds attributes to the keys it received from `fidelity`).

If you wanted to call this REST-fully, it would look nearly the same. The syntax to chain calls is expressed by converting the sequence of argument names and values into a REST resource path.

    curl -X POST -d '{}' --header "Content-Type:application/json" http://localhost:10000/SF-s/fidelity/SF-g/example/c/<CUSTOMER_ID>/p/<PIN>/a/<ACCOUNT_ID>/e/<EMAIL>/SF-s/ystockquotelib/SF-g/example

Here is the same example from Python:

    import sofine.runner as runner
    
    data = {}
    data_sources = ['fidelity', 'ystockquotelib']
    data_source_groups = ['example', 'example']
    data_source_args = [[customer_id, pin, account_id, email], []]
    data = runner.get_data_batch(data, data_sources, data_source_groups, data_source_args)

This call returns a data set of the form described above. Here is the JSON output:

    {
        "key_1": [{"attribute_1": value_1}, {"attribute_2": value_2}, ...],
        "key_2": ...
    }

### get_data Example Using a Data Format Plugin

Here is the same call except using `CSV` instead of the default `JSON` as the data format:

    python $PYTHONPATH/sofine/runner.py '--SF-d format_csv --SF-s fidelity --SF-g example -c <CUSTOMER_ID> -p <PIN> -a <ACCOUNT_ID> -e <EMAIL> | --SF-s ystockquotelib --SF-g example'

### Other Actions 

Finally, let's discuss the other actions besides `get_data`. Note that none of these actions can be chained.

###get_namespaced_data

Works identically to `get_data` but you must included the `--SF-a` argument in CLI calls or the `SF-a` argument in REST calls.
    
    python $PYTHONPATH/sofine/runner.py '--SF-s fidelity --SF-g example --SF-a get_namespaced_data -c <CUSTOMER_ID> -p <PIN> -a <ACCOUNT_ID> -e <EMAIL> | --SF-s ystockquotelib --SF-g example --SF-a get_namespaced_data'

    curl -X POST -d '{}' --header "Content-Type:application/json" http://localhost:10000/SF-s/fidelity/SF-g/example/SF-a/get_namespaced_data/c/<CUSTOMER_ID>/p/<PIN>/a/<ACCOUNT_ID>/e/<EMAIL>/SF-s/ystockquotelib/SF-g/example/SF-a/get_namespaced_data

This call returns a data set of the form described above. Here is the JSON output.

    {
        "key_1": [{"plugin_group::plugin_name::attribute_1": value_1}, 
        i         {"plugin_group::plugin_name::attribute_2": value_2}, ...],
        "key_2": ...
    }


###get_data_batch

This is a helper action only available within Python, to support combining plugin calls into one batch call that returns one data set, equivalent to chaining command line or REST plugins in one call.

    import sofine.runner as runner
    
    data = {}
    data_sources = ['fidelity', 'ystockquotelib']
    data_source_groups = ['example', 'example']
    data_source_args = [[customer_id, pin, account_id, email], []]
    data = runner.get_data_batch(data, data_sources, data_source_groups, data_source_args)

Notice that the function takes a list of plugin names, a list of plugin groups, and a list of lists of args. Each of these must put corresponding plugins, groups and args in sequence.

###parse_args

You should rarely need to call a plugins `parse_args` directly. One use case is to test whether the arguments you plan to pass to `get_data` are valid -- you might want to do this before making a long-running `get_data` call, for example.

From the CLI:

    python $PYTHONPATH/sofine/runner.py '--SF-s file_source --SF-g standard --SF-a parse_args -p "./sofine/tests/fixtures/file_source_test_data.txt"'

From REST:

    curl -X POST -d '{}' --header "Content-Type:application/json" http://localhost:10000/SF-s/file_source/SF-g/standard/SF-a/parse_args/p/.%2Fsofine%2Ftests%2Ffixtures%2Ffile_source_test_data.txt

From Python:

    def test_parse_args_file_source(self):
        data_source = 'file_source'
        data_source_group = 'standard'
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        args = ['-p', path]
        actual = runner.parse_args(data_source, data_source_group, args)

        self.assertTrue(actual['is_valid'] and actual['parsed_args'] == [path])

This call returns the following JSON and only JSON output is supported for this call:

    {"is_valid": true|false, "parsed_args": [arg_1, arg_2, ...]}

###get_schema

There are several use cases for calling `get_schema`, particularly from Python. For example, you might want to retrieve the attribute keys from one or several plugins being called together, to filter or query the returned data for a subset of all the attribute keys.

CLI:

    python $PYTHONPATH/sofine/runner.py '--SF-s ystockquotelib --SF-g example --SF-a get_schema'

REST:

    curl -X POST -d '{}' --header "Content-Type:application/json" http://localhost:10000/SF-s/ystockquotelib/SF-g/example/SF-a/get_schema

Python:

    data_source = 'ystockquotelib'
    data_source_group = 'example'
    schema = runner.get_schema(data_source, data_source_group)

This call returns the following JSON and only JSON output is supported for this call:

    {"schema": [attribute_key_name_1, attribute_key_name_2, ...]}

###get_namespaced_schema

Works identically to `get_schema` but returns the schema fields in namespaced form.

CLI:

    python $PYTHONPATH/sofine/runner.py '--SF-s ystockquotelib --SF-g example --SF-a get_namespaced_schema'

REST:

    curl -X POST -d '{}' --header "Content-Type:application/json" http://localhost:10000/SF-s/ystockquotelib/SF-g/example/SF-a/get_namespaced_schema

Python:

    data_source = 'ystockquotelib'
    data_source_group = 'example'
    schema = runner.get_namespaced_schema(data_source, data_source_group)

This call returns the following JSON and only JSON output is supported for this call:

    {
        "schema": [plugin_group::plugin_name::attribute_key_name_1, 
                   plugin_group::plugin_name::attribute_key_name_2, ...]
    }

###adds_keys

The `adds_keys` action lets you ask a plugin programmatically whether it adds keys to the data set being built by `sofine`. Let's say you want to know which steps in a sequence of call to `sofine` plugins add keys and which keys they add.

    for name, group in plugin_map:
        prev_keys = set(data.keys())
        data = runner.get_data(data, name, group, args_map[name])
        
        if runner.adds_keys(name, group):
            new_keys = set(data.keys()) - prev_keys
            logger.log(new_keys)

Here are examples of calling `adds_keys`

CLI:

    python $PYTHONPATH/sofine/runner.py '--SF-s ystockquotelib --SF-g example --SF-a adds_keys'

REST:

    curl -X POST -d '{}' --header "Content-Type:application/json" http://localhost:10000/SF-s/ystockquotelib/SF-g/example/SF-a/adds_keys

Python:

    data_source = 'ystockquotelib'
    data_source_group = 'example'
    adds_keys = runner.adds_keys(data_source, data_source_group)

This call returns the following JSON and only JSON output is supported for this call:
    
    {"adds_keys": true|false} 

## Additional Convenience Methods

Plugins called from Python also expose two convenience methods that let you get a reference to the plugin's module or to the plugin's class.

###get_plugin

The `get_plugin` action lets you get an instance of a plugin object in Python. This lets you access class-scope methods or instance attributes directly.

Python:
   
    data_source = 'google_search_results'
    data_source_group = 'example' 
    plugin = runner.get_plugin(data_source, data_source_group)
    schema = plugin.schema

###get_plugin_module

The `get_plugin_module` action lets you get an instance of a plugin module in Python. This lets you access module-scope methods or variables directly. For exmample, the Google Search Results module implements an additional helper called `get_child_schema` that returns the list of attributes in each of the `results` JSON objects that it returns for each key passed to it. Because this is nested data, the more interesting attributes are one level down in the data returned, which the helper tells us about.

    data_source = 'google_search_results'
    data_source_group = 'example' 
    mod = runner.get_plugin_module(data_source, data_source_group)
    # The google plugin implements an additional helper method in the module that returns 
    # the list of attributes in each 'results' object it returns mapped to each key 
    child_shema = mod.get_child_schema()


## Managing Python Data Retrieval Plugins

Managing data retrieval plugins is very simple. Pick a directory from which you want to call your plugins. Define the environment variable `SOFINE_PLUGIN_PATH` and assign to it the path to your plugin directory.

Plugins themselves are just Python modules (or code files exposing the required HTTP endpoints in the cast of HTTP plugins) fulfilling the requirements detailed in the section, "How Plugins Work and How to Write Them."

Plugins cannot be deployed at the root of your plugin directory. Instead you must create one or more subdirectories and place plugins in them. Any plugin can live in any subdirectory. If you want, you can even place a plugin in more than one plugin directory. The plugin module name must match the plugin's `self.name` attribute, and the plugin directory name must match the plugin's `self.group` attribute.

This approach means you can manage your plugin directory without any dependencies on `sofine`.  You can manage your plugins directory as their own code repo, and include unit tests or config files in the plugin directory, etc.

## Managing HTTP Data Retrieval Plugins

Managing HTTP data retrieval plugins is very similar to managing Python data retrieval plugins. One difference is that `sofine` doesn't care what language you use to implement an HTTP plugin, or where the code files or compiled binaries are deployed.  Instead you simply define the environment variable `SOFINE_HTTP_PLUGIN_URL`.

When you run a `sofine` command line or REST call, `sofine` will attempt to resolve any plugin it can't load as a Python module by making an HTTP call to the url defined in this environment variable. The values in the call for plugin name, plugin group and action are concatenated to this URL to form the route that your plugin must expose. If your HTTP endpoint is reachable, sofine will call it. For example, the `sofine/plugins/http_examples` directory that ships with `sofine` includes a plugin to retrieve Google search results written in ruby, which exposes itself as an HTTP endpoint to `sofine`.

The CLI call looks like this:
    
    python $PYTHONPATH/sofine/runner.py '--SF-s google_search_results --SF-g example_http'

The call to the web server implementing the plugin looks like this:

    127.0.0.1 - - [06/Oct/2014 23:55:16] "GET /google_search_results/example_http/get_data?keys=AAPL,MSFT&args= HTTP/1.1" 200 4648 0.1324

The code for this server happens to be a ruby file located in the local file system, but that is incidental. You are free to manage plugins as you wish as long as your plufing fulfills the requirements detailed in the section "How Python Data Retrieval Plugins Work and How to Write Them."

## Managing Data Format Plugins

Pick a direcgory from which you want to call your plugins. Define the environment variable `SOFINE_DATA_FORMAT_PLUGIN_PATH` and assign it to the path of your plugin directory.

Unlike data retrieval plugins, data format plugins should be deployed directly in your plugin directory, not in a subdirectory.

Data format plugins are simply modules. By convention they should be named `format_<FORMAT_NAME>.py`, for example, `format_json.py`. This is optional, but provides a standard way to avoid name clashes with built-in or third-party modules named after a data format, such as the Python standard library `json` and `csv` modules.

## Appendix: The Data Retrieval Algorithm

* The returned data set (let's call it "data") is always a JSON object of string keys mapped to an array of zero or more object values, where each object is a single attribute key and attribute value pair.
* On every call in a `sofine` chain, add any new keys returned to data, and add all key attribute data returned to that key in data.
* All attributes mapped to a key are JSON objects which themselves consist of string keys mapped to legal JSON values.

So the result of a call to a `sofine` pipe is the union of all keys retrieved by all plugin calls, with each key mapped to the union of all attributes returned by all plugin calls for that key.


## Developing With the sofine Code Base

All of the above documentation covers the very common case of using sofine as a library to manage and call your own plugins.

However, you might want to develop with `sofine` more directly. Perhaps you want to use pieces of the library for other purposes, or fork the library to add features, or even contribute!

In that case, you'll want the developer documentation: http://marksweiss.github.io/sofine/


