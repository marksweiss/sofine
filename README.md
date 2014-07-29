## What is sofine?

`sofine` is a minimal framework for creating a library of data collection plugins that follow simple conventions so that they can composed as you wish.

How minimal? Let's write a Google search results plugin. This is the part you would have to write in any case -- it takes a search term and calls the Google API.

    def query_google_search(k):
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={0}'.format(urllib.quote(k))
        ret = urllib2.urlopen(url)
        ret = ret.read()
        ret = json.loads(ret)
    
        if ret: 
            ret = {'results' : ret['responseData']['results']}
        else:
            ret = {'results' : []}
    
        return ret

Here is the additional code you have to add to make your plugin sofine.

    class GoogleSearchResults(plugin_base.PluginBase):

        def __init__(self):
            self.name = 'google_search_results'
            self.group = 'example'
            self.schema = ['results']
            self.adds_keys = False

        def get_data(self, keys, args):
            data = {}
            for k in keys:
                data[k] = query_google_search(k)
            return data

    plugin = GoogleSearchResults 

## Why is it sofine?

The core value proposition of `sofine` is this: 

* You do (almost) no more work than if you wrote a one-off data collection script 
* You can manage your plugins in any directory with any directory structure you like, with a single entry in a single configuration file as the sole dependency on the library
* You can call plugins from the command line, as REST resources or from Python
* You can chain as many plugin calls as you want together and get back one JSON data set with all the data collected from all the chained calls

That last bullet is really the point -- the idea is that rather than writing one offs, you are just a tiny bit more thoughtful when wrapping various APIs and data resources.  In return, each plugin you write becomes much more valuable because you can combine it with all the others.  As time goes on and you write more plugins, you discover more things you can do by combining your plugins together.

## Your Data Pipeline is sofine!

`sofine` aims to support exactly one use case, but it is very flexible, general, composable, and (hopefully) useful.

Each call to `sofine` chains together calls to one or more data source plugins. Plugins always receive a set of string keys, and they retrieve JSON objects of data for those keys which are collected from each plugin and all mapped to the keys.

Imagine you are chaining calls operating on stock ticker keys.  The final output would look lik this:

    {"AAPL" : {"plugin_1::attr_name_1" : value, "plugin_1::attr_name_2" : value, "plugin_2::attr_name_1, value},
    "MSFT" : {"plugin_1::attr_name_1" : value, "plugin_1::attr_name_2" : value, "plugin_2::attr_name_1, value} 
    }

Here is a real example, combining calls to Yahoo! Finance and Goole Search Results plugins:

    $ echo '{"AAPL":{}}' | python sofine/runner.py '--SF-s ystockquotelib --SF-g example | --SF-s google_search_results --SF-g example'

    {
    "AAPL": {
        "example::google_search_results::results": [
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
        ],
        "example::ystockquotelib::avg_daily_volume": "59390100",
        "example::ystockquotelib::book_value": "20.193",
        "example::ystockquotelib::change": "+1.349",
        "example::ystockquotelib::dividend_per_share": "1.7771",
        "example::ystockquotelib::dividend_yield": "1.82",
        "example::ystockquotelib::earnings_per_share": "6.20",
        "example::ystockquotelib::ebitda": "59.128B",
        "example::ystockquotelib::fifty_day_moving_avg": "93.8151",
        "example::ystockquotelib::fifty_two_week_high": "99.24",
        "example::ystockquotelib::fifty_two_week_low": "63.8886",
        "example::ystockquotelib::market_cap": "592.9B",
        "example::ystockquotelib::price": "99.02",
        "example::ystockquotelib::price_book_ratio": "4.84",
        "example::ystockquotelib::price_earnings_growth_ratio": "1.26",
        "example::ystockquotelib::price_earnings_ratio": "15.75",
        "example::ystockquotelib::price_sales_ratio": "3.28",
        "example::ystockquotelib::short_ratio": "1.70",
        "example::ystockquotelib::stock_exchange": "\"NasdaqNM\"",
        "example::ystockquotelib::two_hundred_day_moving_avg": "82.8458",
        "example::ystockquotelib::volume": "55317688"
    }
    }  

### Some sofine Terminology

Each chain of one of more calls builds a JSON object `data set`. That object has a set of one or more string `keys`. Each key in turn has as its value another JSON object. Each call to a plugin recieves the set of keys, does its thing in its `get_data` implementation to get whatever data it can for those keys, and returns a set of objects mapped to the keys. In `sofine` we call the values mapped to the top-level `keys` `attributes`. Because `attributes` are JSON objects they in turn have `attribute keys` which are mapped to values. We call this set of attribute keys the `schema` of the plugin.

### The Algorithm for Filling the Data Pipeline

* If this is the first call in the chain, data is empty, so just fill it with the return of this call
* If there is already data, add any new keys retrieved and add attribute key/value pairs associated with any new or existing keys 
* Attribute key names are namespaced with the plugin name and plugin group to guarantee they are unique and do not overwrite other attributes with the same name from other plugins  
* So, the set of keys on each call is the union of all previously collected keys
* So, the set of attributes associated with each key is the union of all previously collected attribute/value pairs collected for that key

## Those Examples are sofine!

Here is an example, which retrieves attributes about all the securities in a portfolio by ticker from Fidelity and then takes the same set of tickers and adds data from the Yahoo! Finance API:

    python sofine/runner.py '--SF-s fidelity --SF-g example -c <CUSTOMER_ID> -p <PIN> -a <ACCOUNT_ID> -e <EMAIL> | --SF-s ystockquotelib --SF-g example'

`sofine` automatically takes care of the following:

* Loading each plugin from its `SF-s` "source" and `SF-g` "group"
* Adding to the JSON data set it is building on each call
* Namespacing all data added from each call so that none is lost
* Returning the data to stdout as JSON

If you wanted to call this REST-fully, it would look nearly the same. In curl:

    curl -X POST -d '{}' --header "Content-Type:application/json" http://localhost:10000/SF-s/fidelity/SF-g/example/c/<CUSTOMER_ID>/p/<PIN>/a/<ACCOUNT_ID>/e/<EMAIL>/SF-s/ystockquotelib/SF-g/example

`sofine` ships with a server which you launch at `python sofine/rest_runner.py`. The server returns the same JSON. The same ability to chain calls is simply expressed as a REST resource path.

## Your Pipes are sofine!

Just as `sofine` allows you to compose plugin calls, when run from the command line it takes input from stdin if it is present and always sends output to stdout.  So you can do this:

    echo '{"AAPL":{}}' | python sofine/runner.py '--SF-s ystockquotelib --SF-g example | --SF-s google_search_results --SF-g example' | jq 'map(recurse(.SOME_KEY) | {SOME_OTHER_KEY}'

This gets you the data that Yahoo! Finance has on Apple and combines it with search results from the Google Search API and then passes the result to the [JSON query tool jq](https://github.com/stedolan/jq), a fantastic uber-`grep` for JSON data that I highly recommend.

## Managing Plugins

* You put all plugins into subdirectories of your parent plugin directory. Typically you think of these as plugin groups and name the directories meaningfully.
* You put a file in the root `sofine` directory called `sofine.conf` and put a JSON object there with the key `"plugin_path"` and the value the path to your plugin directory
* You can always combine calls to your plugins with those the five that are included with `sofine`:
* standard.file_source
* example.archive_dot_org_search_results
* example.google_search_results
* example.fidelity
* example.ystockquotelib
* These combinations of plugin group and name are reserved plugin identifiers. You can name yourplugin groups and names anything else you want without clashing with the built-in plugins
* You can put anything else into your plugin group directories and `sofine` will ignore it. So, for example, you could have a `tests` directory with unit tests for the plugins in that group in each plugin directory.

## Creating Plugins

To create plugins you do the following:

* Derive from the base class `sofine/plugins/plugin_base.PluginBase`
* You must define these two attributes:
  * `name`
  * `group`
* You really should define these two attributes, to let clients introspect your plugin:
  * `schema` - the list of all possible attribute keys returned by this plugin in the attributes associated with the keys of the `data` set being built
  * `adds_keys` - indicates whether the plugin adds keys or just adds attributes to the existing keys
* You must define one method for every plugin:
  * `get_data()`, which recieves a list of strings which are the keys for which data is being collected, and also a list of arguments in case the plugin requires them to do its work
* If your `get_data` requires arguments, you must implement `parse_args()`, which takes the args in argv format as a list of arg names and values in sequence and validates them. If your plugin takes no arguments then the default implementation in PluginBase is all you need.
* Plugins inherit two other introspection methods from PluginBase. You don't need to implement these in general, but your plugin will have them.
  * `get_schema` returns the list of attribute keys you set in `self.schema`, properly namespaced with the plugin group and name.
    * Note that if your plugin doesn't know what attributes it might retrieve, then you need to override and implement `get_schema`. Your plugin might query a datastore that could return a varying set of attributes for a key, so you can't statically set `self.schema` and so need to implement `get_schema` to dynamically discover and return the schema attribute keys.

Here is a complete example, minus the docstrings:

    from sofine.plugins import plugin_base as plugin_base
    import ystockquote


    class YStockQuoteLib(plugin_base.PluginBase):
    
        def __init__(self):
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

### Plugin Methods

This is the complete documenation of the attributes and methods of a plugin.

#### Plugin Instance Fields

* `self.name` - `string`. The name of the plugin
* `self.group` - `string`. The pluging group of the plugin. This the subdirectory in the plugin directory into which the plugin is deployed.
* `self.schema` - `list of string`. The set of attribute keys that calls to `get_data` can associate with a key passed to `get_data`.
* `self.adds_keys` - `boolean`. Indicates whether the plugin adds keys to the data set being built or only adds attributes to existing keys.

#### Plugin Instance Methods

    # Required
    def get_data(self, keys, args):
        # keys - list of string. The list of keys to process.
        # args - list of string. Any args required to call get_data(). 

    Returns JSON objects for each key received, in a dict mapping keys to the objects, which 
    we call attributes in sofine

    # Required *only* if schema is dynamic
    def parse_args(self, argv):
        # Takes any args required to call get_data, validates them and returns a tuple of a boolean indicating whether the parse succeeded and a possibly altered set of args.
        # Returns a boolean indicating `args` is valid, and the args. 
        # Required *only* if the schema is dyanmic 
    
    def get_schema(self, args=None):
        # Returns the set of attributes that the call might return in association with keys. Return type is list `[string]`

## Developing sofine

All of the above documentation covers the very common case of using sofine as a library to manage and call your own plugins and use them in your own applications, without ever needing to understand how `sofine` works. It's a library and it works if it follows the rules.

However, you might want to develop with `sofine` more directly.

### make Targets

To run core unit tests:
    make test

To run unit tests on the example plugins:
    make test_examples

To rebuild the documentation, which is everthing in `docs` and `index.html` in project root:
    make docs

To support using the plugins in `PROJECT_ROOT/sofine/plugins/examples and 
running the tests in PROJECT_ROOT/tests/*_examples.py`:
    
    easy_install mechanize
    easy_install beautifulsoup4
    pip install ystockquote

*NOTE: Tests for fidelity example plugin must be run manually, because this 
plugin requires arguments that contain sensitive data*

### Complete Code Documentation

<strong>Command Runners</strong><br/>
<a href="docs/sofine/runner.m.html">runner</a><br/>
<a href="docs/sofine/rest_runner.m.html">rest_runner</a><br/>
<p/>
<strong>Plugins</strong><br/>
<a href="docs/sofine/plugins/plugin_base.m.html">plugin_base</a><br/>
<a href="docs/sofine/plugins/standard/file_source.m.html">standard/file_source</a><br/>
<a href="docs/sofine/plugins/example/ystockquotelib.m.html">example/ystockquotelib</a><br/>
<a href="docs/sofine/plugins/example/google_search_results.m.html">example/google_search_results</a><br/>
<a href="docs/sofine/plugins/example/fidelity.m.html">example/fidelity</a><br/>
<a href="docs/sofine/plugins/example/archive_dot_org_search_results.m.html">example/archive_dot_org_search_results</a><br/>
<a href="docs/sofine/plugins/mock/ystockquotelib_mock.m.html">mock/ystockquotelib</a><br/>
<p/>
<strong>Tests</strong><br/>
<a href="docs/sofine/tests/test_runner_from_rest.m.html">tests/test_runner_from_rest</a><br/>
<a href="docs/sofine/tests/test_runner_from_py_examples.m.html">tests/`test_runner_from_py_examples</a><br/>
<a href="docs/sofine/tests/test_runner_from_py.m.html">tests/test_runner_from_py</a><br/>
<a href="docs/sofine/tests/test_runner_from_cli_examples.m.html">tests/test_runner_from_cli_examples</a><br/>
<a href="docs/sofine/tests/test_runner_from_cli.m.html">tests/test_runner_from_cli</a><br/>
<p/>
<strong>Utils and Conf</strong><br/>
<a href="docs/sofine/lib/utils.m.html">lib/utils</a><br/>
<a href="docs/sofine/lib/conf.m.html">lib/conf</a><br/>
</body>

