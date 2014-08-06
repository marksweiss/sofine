## What Problem Does sofine solve?

You need to get data related to a set of keys from many sources: web scrapers, Web APIs, flat files, data stores. Wouldn't it be nice to build one combine data set over multiple calls with one command line, REST or Python call? Wouldn't it be great if each data retrieval script you wrote was a reusable plugin that you could combine with any other?

You need a "glue API." 

This is the problem `sofine` solves. It's a small enough problem that you could solve it yourself. But `sofine` is minimal to deploy and write plugins for, and has already solved in an optimally flexible way the design decisions you would have to solve. 

## Features

1. Do (almost) no more work than if you wrote a one-off data collection scripts 
2. Manage your plugins in any directory with any directory structure you like
3. Call plugins from the command line, as REST resources or from Python
4.  Chain as many plugin calls as you want together and get back one JSON data set with all the data collected from all the chained calls
5. If called from the command line, `sofine` reads data from stdin if it is present, and always outputs to stdout. So `sofine` piped calls, such as the example above, can themselves be composed in larger piped expressions.

For fun, here is an example of features 4 and 5, combining a `sofine` pipeline with the fantastic [JSON query tool jq](https://github.com/stedolan/jq) for further filtering.

    echo '{"AAPL":{}}' | python $PYTHONPATH/sofine/runner.py '--SF-s ystockquotelib --SF-g example | --SF-s google_search_results --SF-g example' | jq 'map(recurse(.results) | {titleNoFormatting}'

## Overview

To get started, you install the library, create a plugin directory, assign the plugin directory to an environment variable, and start writing plugins. Plugins require two attributes and one method in the simple case and three methods in the most elaborate edge case. You can optionally define two additional attributes for clients to use to introspect your plugin.

`sofine` ships with a few useful plugins to get you started and give you the idea; you can combine these with your custom plugins with no additional configuration or code. The included plugins are:

* `sofine.plugins.standard.file_source` - Retrieves keys from a JSON file to add to the data set being built. See here TODO for the details.
* `example.archive_dot_org_search_results` - Takes a search query and returns results from www.archive.org
* `example.google_search_results` - Takes a search query and returns results from the Google Search API
* `example.fidelity` - Takes a userId, pin, accountId and email, logs into Fidelity, scrapes the account portfolio and returns the tickers found as keys and four attributes of data for each ticker
* `example.ystockquotelib` - Takes a list of tickers and returns the data available from Yahoo! Finance for each ticker

Here is what usage looks like ...

From the command line:

    $ echo '{"AAPL":{}}' | python $PYTHONPATH/sofine/runner.py '--SF-s ystockquotelib --SF-g example | --SF-s google_search_results --SF-g example'

REST-fully:

    $ python $PYTHONPATH/sofine/rest_runner.py
    
    $ curl -X POST -d '{"AAPL":{}}' --header "Content-Type:application/json" http://localhost:10000/SF-s/ystockquotelib/SF-g/example/SF-s/google_search_results/SF-g/example

From Python:

    import sofine.runner as runner
    
    data = {"AAPL": {}}
    data_sources = ['ystockquotelib', 'google_search_results']
    data_source_groups = ['example', 'example']
    data_source_args = [[], []]
    data = runner.get_data_batch(data, data_sources, data_source_groups, data_source_args)

All three calling styles return the same data set. `sofine` data sets map JSON objects of data to string keys. So here, we have the key "AAPL," with all the attributes retrieved from Yahoo! Finance and the Google Search API combined in a JSON object associated with the key.  Notice that the keys in the attribute data set are namespaced so multiple calls can't overwrite data from each other.

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

## Installing sofine

    pip install sofine 

Then, make sure your `$PYTHONPATH` variable is set and points to the site-packages directory of your Python where pip installed `sofine`.

    export PYTHONPATH=<MY PYTHON SITE-PACKAGES DIRECTORY>

Then, create a plugin directory and assign its path to an environment variable `SOFINE_PLUGIN_PATH`. You probably want to add it to your shell configuration file.

    export SOFINE_PLUGIN_PATH=<MY PATH>

`sofine` runs its REST server on port 10000. If you want to use a different port, set the environment variable `SOFINE_REST_PORT`. You probably want to add it to your shell configuration file.
    
    export SOFINE_REST_PORT=<MY PORT>

If you want to use the included `fidelity` and `ystockquotelib` plugins in the `plugins.examples' plugin group, also install the following:

    easy_install mechanize
    easy_install beautifulsoup4
    pip install ystockquote

## How Plugins Work and How to Write Them

All plugins inherit from a base class which defines four attributes:

* `self.name` - `string`. The name of the plugin
* `self.group` - `string`. The pluging group of the plugin. This the subdirectory in the plugin directory into which the plugin is deployed.
* `self.schema` - `list of string`. The set of attribute keys that calls to `get_data` can associate with a key passed to `get_data`.
* `self.adds_keys` - `boolean`. Indicates whether the plugin adds keys to the data set being built or only adds attributes to existing keys.

You must always define `name` and `group`. `name` must match the module name of the plugin module, that is the name you would use in an `import` statement. `group` must match the name of the subdirectory of your plugin directory where the plugin is deployed. `sofine` uses `name` and `group` to load and run your plugin, so they have to be there and they have to be correct.

`schema` and `adds_keys` are optional. They allow users of your plugin to introspect your plugin. `schema` is a list of strings that tells a client of your plugin the set of possible attribute keys that your plugin returns for each key it recieves. For example, if your plugin takes stock tickers as keys and looks up a current quote, its `schema` declaration might look like this:
    
    self.schema = ['quote']

`adds_keys` lets users ask your plugin if it adds keys to the data set being built when `sofine` calls it, or if it just adds attributes for the keys it receives. For example, the `ystockquotelib` plugin in the `sofine.plugins.example` group takes a set of stock tikckers as keys and retrieves the available data for each of them from Yahoo! Finance. This plugin has the attribute declaration `self.adds_keys = False`. On the other hand, the `sofine.plugins.fidelity` plugin is a scraper that can log into the Fidelity, go to the portfolio page for the logged in user, scrape all the tickers for the securities in that portfolio, and add those keys and whatever data it finds to the data set being built. This plugin has a value of `True` for `adds_keys`.

NOTE: A common design pattern is to start a chain of calls with a plugin that adds keys, and then pass those keys to one or more plugins that don't add keys but rather retrieve data for that set of keys.

Plugins also have three methods. `get_data` is not implemented in the base class and must be implemented by you in your plugin. This method takes a list of keys and a list of arguments. It must return a dict whose keys are a proper superset of the keys it received (the return set of keys can have more keys than were passed to `get_data` if the plugin adds keys). This dict must have string keys and a dict value for each key. The dict value is the data retrieved for each key. The keys in that dict must be a set of strings that is a proper subset of the set of strings in `self.schema`.

Here is an example of `get_data` from the `sofine` plugin `sofine.plugins.example.ystockquotelib`.

    def get_data(self, keys, args):
        """
        * `keys` - `list`. The list of keys to process.
        * `args` - `'list`. Empty for this plugin.
        Calls the Yahoo API to get all available fields for each ticker provided as a key in `keys`."""
        return {ticker : ystockquote.get_all(ticker) for ticker in keys}

The other method you will often need to implement is `parse_args`. If your `get_data` requires no arguments you need not implement `parse_args` and can just use the base class default implementation. But if your `get_data` call requires arguments, you must implement `parse_args`. The method takes an argv style list of alternating arg names and values and is responsible for validating the correctness of argument names and values and returing a tuple with two members. The first member is a boolean `is_valid`. The second is the parsed list of argument values (without the argument names).

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

The third method is `get_schema`. You will rarely need to implement this. Any plugin that knows the set of attributes it can return for a key doesn't need to implement `get_schema` and can rely on the default. Note that `get_schema` returns the set of attribute keys you define in `self.schema` in a namespace qualified with the plugin group and name. For example, if our stock quote plugin mentioned above is named `get_quotes` and it is in the `trading` group, the return value of `get_schema` would be `["trading::get_quotes::quote"]`.

Finally, the last line of your plugin should assign the module-scope variable `plugin` to the name of your plugin class.  For example:

    plugin = GoogleSearchResults 

### A Complete Plugin Example

This is a small amount of overhead compared to writing one-off scripts for the return on investment of being able to know where your plugins are, call them with standard syntax, and compose them with each other in any useful combination.

How small? Let's look at a small but not trivial example that ships with `sofine`, a plugin to call the Google Search API.

It starts with a module scope helper function that you would have to write in any one-off script to call the API.

    import urllib
    import urllib2
    import json

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

Now, here are the 10 additional lines of code you need to make your plugin run in `sofine`. 
    
    from sofine.plugins import plugin_base as plugin_base

    class GoogleSearchResults(plugin_base.PluginBase):

        def __init__(self):
            self.name = 'google_search_results'
            self.group = 'example'
            self.schema = ['results']
            self.adds_keys = False

        def get_data(self, keys, args):
            return {k : query_google_search(k) for k in keys}

    plugin = GoogleSearchResults

Now you're ready to write a unit test for `get_data`, which you can even leave in the same plugin subdirectory as the plugin, and you are done. 

Just for fun, here is a second example. This shows you how easy it is to wrap existing Python API wrappers as `sofine` plugins. For a a few lines of additional boilerplate, you can now take any of these and combine them any which way you can.

    froe sofine.plugins import plugin_base as plugin_base
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


## How to Call Plugins

As we saw above in the Introduction section, there are three ways to call plugins, from the command line, as REST resources, or in Python.  When calling plugins to retrieve data, you need to pass three or four arguments, `data`,  the plugin name, the plugin group and, depending on the call, the plugin action. 

There are four actions, which correspond to the three methods `get_data`, `parse_args` and `get_schema`, while `adds_keys` returns the value of the the plugin's `self.adds_keys`.

    get_data
    parse_args
    get_schema
    adds_keys

### Calling From the Command Line

When calling from the CLI you pass these arguments:

* `[--SF-s|--SF-data-source]` - The name of the data source being called. This is the
name of the plugin module being called. Required.
* `[--SF-g|--SF-data-source-group`] - The plugin group where the plugin lives. This is 
the plugins subdirectory where the plugin module is deployed. Required.
* `[--SF-a|--SF-action]` - The plugin action being called.

Get data is the default, so action can be ommitted on calls to `get_data`.

Any additional arguments that a call to `get_data` requires should be passed following the `--SF-s` and `--SF-g` arguments.

### Calling REST-fully

`sofine` ships with a server which you launch at `python sofine/rest_runner.py` to call plugins over HTTP. The servers runs by default on `localhost` on port `10000`. You can change the port it is running on by setting the environment variable `SOFINE_REST_PORT`.

### get_data Examples

Here are examples of calling get_data:
    
    python $PYTHONPATH/sofine/runner.py '--SF-s fidelity --SF-g example -c <CUSTOMER_ID> -p <PIN> -a <ACCOUNT_ID> -e <EMAIL> | --SF-s ystockquotelib --SF-g example'

Notice that `--SF-a` is ommitted, which means this is chained call to retrieve data, first from the `fidelity` plugin (which is called first becasue it adds the set of keys returned) and then from the `ystockquotelib` plugin (which adds attributes to the keys it received from `fidelity`).

If you wanted to call this REST-fully, it would look nearly the same. The syntax to chain calls is expressed by converting the sequence of argument names and values into a REST resource path.

    curl -X POST -d '{}' --header "Content-Type:application/json" http://localhost:10000/SF-s/fidelity/SF-g/example/c/<CUSTOMER_ID>/p/<PIN>/a/<ACCOUNT_ID>/e/<EMAIL>/SF-s/ystockquotelib/SF-g/example

Here is the same example from Python:

    import sofine.runner as runner
    
    data = {}
    data_sources = ['fidelity', 'ystockquotelib']
    data_source_groups = ['example', 'example']
    data_source_args = [[customer_id, pin, account_id, email], []]
    data = runner.get_data_batch(data, data_sources, data_source_groups, data_source_args)

### Other Actions 

Finally, let's discuss the other actions besides `get_data`. Note that none of these actions can be chained.

### get_data_batch

This is a helper action only available within Python, to support combining plugin calls into one batch call that returns one data set, equivalent to chaining command line or REST plugins in one call.

    import sofine.runner as runner
    
    data = {}
    data_sources = ['fidelity', 'ystockquotelib']
    data_source_groups = ['example', 'example']
    data_source_args = [[customer_id, pin, account_id, email], []]
    data = runner.get_data_batch(data, data_sources, data_source_groups, data_source_args)

Notice that the function takes a list of plugin names, a list of plugin groups, and a list of lists of args. Each of these must put corresponding plugins, groups and args in sequence.

### parse_args

You should rarely need to call a plugins `parse_args` directly. One use case is to test whether the arguments you plan to pass to `get_data` are valid -- you might want to do this before making a long-running `get_data` call, for example.

From the CLI:

    python sofine/runner.py '--SF-s file_source --SF-g standard --SF-a parse_args -p "./sofine/tests/fixtures/file_source_test_data.txt"'

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

### get_schema

There are several use cases for calling `get_schema`, particularly from Python. For example, you might want to retrieve the attribute keys from one or several plugins being called together, to filter or query the returned data for a subset of all the attribute keys.

CLI:

    python sofine/runner.py '--SF-s ystockquotelib --SF-g example --SF-a get_schema'

REST:

    curl -X POST -d '{}' --header "Content-Type:application/json" http://localhost:10000/SF-s/ystockquotelib/SF-g/example/SF-a/get_schema

Python:

    data_source = 'ystockquotelib'
    data_source_group = 'example'
    schema = runner.get_schema(data_source, data_source_group)

### adds_keys

The `adds_keys` action lets you ask a plugin programmatically whether it adds keys to the data set being built by `sofine`. Let's say you want to know which steps in a sequence of call to `sofine` plugins add keys and which keys they add.

    for name, group in plugin_map:
        prev_keys = set(data.keys())
        data = runner.get_data(data, name, group, args_map[name])
        
        if runner.adds_keys(name, group):
            new_keys = set(data.keys()) - prev_keys
            logger.log(new_keys)

Here are examples of calling `adds_keys`

CLI:

    python sofine/runner.py '--SF-s ystockquotelib --SF-g example --SF-a adds_keys'

REST:

    curl -X POST -d '{}' --header "Content-Type:application/json" http://localhost:10000/SF-s/ystockquotelib/SF-g/example/SF-a/adds_keys

Python:

    data_source = 'ystockquotelib'
    data_source_group = 'example'
    adds_keys = runner.adds_keys(data_source, data_source_group)

### get_plugin

The `get_plugin` action lets you get an instance of a plugin object in Python. This lets you access class-scope methods or instance attributes directly.

Python:
   
    data_source = 'google_search_results'
    data_source_group = 'example' 
    plugin = runner.get_plugin(data_source, data_source_group)
    schema = plugin.schema
    
### get_plugin_module

The `get_plugin_module` action lets you get an instance of a plugin module in Python. This lets you access module-scope methods or variables directly. For exmample, the Google Search Results module implements an additional helper called `get_child_schema` that returns the list of attributes in each of the `results` JSON objects that it returns for each key passed to it. Because this is nested data, the more interesting attributes are one level down in the data returned, so this helper is useful in this particular case.

    data_source = 'google_search_results'
    data_source_group = 'example' 
    mod = runner.get_plugin_module(data_source, data_source_group)
    # The google plugin implements an additional helper method in the module that returns 
    # the list of attributes in each 'results' object it returns mapped to each key 
    child_shema = mod.get_child_schema()


## Managing Plugins

Managing plugins is very simple. Pick a directory from which you want to call your plugins. Define the environment variable `SOFINE_PLUGIN_PATH` and assign it to the path to your plugin directory.

Plugins themselves are just Python modules fulfilling the requirements detailed in the section, "How Plugins Work and How to Write Them."

Plugins cannot be deployed at the root of your plugin directory. Instead you must create one or more subdirectories and place plugins in them. Any plugin can live in any subdirectory. If you want, you can even place a plugin in more than one plugin directory. The plugin module name must match the plugin's `self.name` attribute, and the plugin directory name must match the plugin's `self.group` attribute.

This approach means you can manage your plugin directory without any dependencies on `sofine`.  You can manage your plugins directory like any other source code repo, and include unit tests for plugins anywhere in the plugin directory if you want. 

## Appendix: The Data Retrieval Algorithm

* The returned data set (let's call it "data") is always a JSON object of string keys mapped to object values.
* On every call in a `sofine` chain, add any new keys returned to data, and add all key attribute data returned to that key in data.
* All attributes mapped to a key are JSON objects which themselves consist of string keys mapped to legal JSON values.
* All attribute keys are namespaced with the prefix of the plugin group and plugin name and then the attribute key name, guaranteeing they are unique.

So, formally, the result of a call to a `sofine` pipe is the union of all keys retrieved by all plugin calls, with each key mapped to the union of all attributes returned by all plugin calls for that key.


## Developing With the sofine Code Base

All of the above documentation covers the very common case of using sofine as a library to manage and call your own plugins.

However, you might want to develop with `sofine` more directly. Perhaps you want to use pieces of the library for other purposes, or fork the library to add features, or even contribute!

In that case, you'll want the developer documentation: http://marksweiss.github.io/sofine/

