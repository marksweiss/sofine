"""This module is the main driver for running plugins from the REST interface. It 
provides its own lightweight server, which runs at `http://localhost:[PORT]`,
where `[PORT]` is the value set in the JSON configuration file `sofine.conf` 
in the sofine project root for the key `plugin_path`.

The request handler expects calls to represent calls to plugins as REST-ful 
resources. Just as in the CLI interface, there are four elements to a plugin call:

* `SF-s|SF-data-source` - Required, the name of the plugin being called
* `SF-g|SF-data-source-group` - Required, the group of the plugin being called
* `SF-a|SF-action` - Required for `adds_keys`, `get_schema` and `parse_args` and 
optional for `get_data`. Value must be `[adds_keys|get_schema|parse_args|get_data]`.
* Optional additional args required by the plugin call.

All elements are represented in the path of the HTTP call. The path must pass args
in order: 
    
    /SF-s/<SOURCE>/SF-g/<GROUP>/SF-a/<ACTION>/<ARG1_NAME>/<ARG1_VAL>/ ...

Calls can be chained by repeating the above sequence as many time as desired. 
That is, each time a new 'SF-s' path element is encounted this marks 
the start of a new call. 

This module doesn't stand on its own. Rather, its main responsibility is to provide 
robust but very simple application server, parse and validate REST routes as calls 
to run plugins by name, group and with their arguments, and dispatch to `runner.py` 
and capture the return value, and package that for return as HTTP response.

"""


import sofine.runner as runner
import sofine.lib.utils.conf as conf
from cgi import parse_qs, escape
from sys import exc_info
from traceback import format_tb
import json


# Borrows from here: http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
#  which is the best basic DIY wsgi tutorial I found


def _parse_calls_from_path(path): 
    # Put each new list of args making up a call into calls. Then loop
    #  through calls to make each call and append to ret. Just like CLI impl.
    args = path[1:].split('/')

    calls = []
    call = [] 
    count = 0
    for a in args:
        # A bit ugly. Loop over args. Key args can trigger a new call 
        #  so detect whether position is key or value position in list of args.
        if count % 2 == 0:
            # Pretty lame but the runner method that validates args expects
            #  a list that looks like CLI args/values in sequence, so prepend '--'
            a = '--' + escape(a)
            if a == '--SF-s' or a == '--SF-data-source':
                # Sigh. Guard to not copy first empty call into calls
                if call:
                    calls.append(list(call))
                call = []
        call.append(escape(a))
        count += 1
    # Copy the last call left from the loop we didn't copy into calls
    if len(call):
        calls.append(list(call))
    
    return calls


def _get_traceback():
    e_type, e_value, tb = exc_info()
    traceback = format_tb(tb)
    traceback.append('%s: %s' % (e_type.__name__, e_value))
    return '\n'.join(traceback)


def _run_action(ret, call):
    data_source, data_source_group, action, data_source_args = \
            runner._parse_runner_args(call)
    return runner._run_action(action, ret, data_source, data_source_group, data_source_args)


def application(environ, start_response):
    """
* `environ` - `dict`. A wsgi standard variable, containing all the header names/values in the 
HTTP call being handled.
* `start_response` - A wsgi standard variable, a callable that the response handler (this 
function) must call, which itself takes two arguments, an HTTP status code and a list of 
two-element tuples of strings, each of which is an HTTP header name and header value.

The runner for REST calls to plugins. This method only allows GET and POST calls, depending 
on the action of the call. Calls to `get_data` are POST, because they pass in the JSON 
data being built by the call as JSON in the POST body. This is true despite the fact that 
the semantics of the call are to retrieve resource state, not change it. (REST semantics 
aside, POST-ing is the only practical way to do data retrieval over HTTP, because it 
supports large payloads.) Calls to `parse_args`, `adds_keys` and `get_schema` are GET.

Valid calls return `200 OK`. Failed calls always return `404 Not Found`. Calls to 
verbs other than POST or GET return `405 Method Not Allowed`. The return payload is JSON 
object which is the data set of keys mapped to JSON objects built by the call(s). The 
structure of this data is described in the the documentation of `runner.get_data`.

NOTE: Use of the `file_source` plugin included in the `standard` sofine plugins directory 
is NOT supported, for security reasons. Allowing it would allow HTTP calls access to 
the local file system.
"""
    ret = {} 
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    
    calls = _parse_calls_from_path(environ.get('PATH_INFO'))

    method = environ['REQUEST_METHOD']
    # This is a POST call to get_data. Get any data from the POST body, and support
    #  parsing out and looping over multiple calls in the REST path
    if method == 'POST':
        try:
            # Get ret, which initializes to any data provided in the POST body 
            ret_len = int(environ['CONTENT_LENGTH'])
            ret = environ['wsgi.input'].read(ret_len)
            ret = json.loads(ret)
                
            for call in calls:
                ret = _run_action(ret, call)

            status = '200 OK'
            headers = [('Content-type', 'application/json')]
        except:
            ret = _get_traceback()
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain')]
    # This is a GET call to get_schema, adds_keys or parse_args
    elif method == 'GET':
        try:
            # The query GET methods don't support chaining. _parse_calls_from_path()
            #  returns a list of calls. So here just get the first call.
            ret = _run_action(ret, calls[0])
        except:
            ret = _get_traceback()
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain')]
    # Only POST and GET are allowed
    else:
        status = '405 Method Not Allowed'
        headers = [('Content-type', 'text/plain')]
        ret = status + '. Only the POST and GET verbs are allowed'

    start_response(status, headers)
    return [json.dumps(ret)]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('localhost', conf.REST_PORT, application)
    server.serve_forever()

