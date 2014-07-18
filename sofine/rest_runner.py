import runner
import lib.utils.conf as conf
from cgi import parse_qs, escape
from sys import exc_info
from traceback import format_tb
import json


# Borrows from here: http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
#  which is the best basic DIY wsgi tutorial I found


def application(environ, start_response):
    ret = '{}'
    status = ''
    headers = None

    method = environ['REQUEST_METHOD']
    if method != 'POST':
        status = '405 Method Not Allowed'
        headers = [('Content-type', 'text/plain')]
        ret = status + '. Only POST method is allowed'
    else:
        try:
            # Get ret, which initializes to any data provided in the POST body 
            ret_len = int(environ['CONTENT_LENGTH'])
            ret = environ['wsgi.input'].read(ret_len)
            ret = json.loads(ret)
                
            # Parse call args from PATH_INFO
            # Loop through args from QS. Split into key/val pairs. Each time
            #  a new --SF-s is encounted this delimits the start of a new call.
            #  NOTE: Must pass args in order: --SF-s, --SF-g, --SF-a, args
            #  Must document this!
            # Put each new list of args making up a call into calls. Then loop
            #  through calls to make each call and append to ret. Just like CLI impl.
            args = environ.get('PATH_INFO')
            args = args[1:].split('/')

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
                
            for call in calls:
                data_source, data_source_group, action, data_source_args = \
                        runner._parse_runner_args(call)
                
                
                ret = runner._run_action(action, ret, data_source, data_source_group, data_source_args)

            status = '200 OK'
            headers = [('Content-type', 'application/json')]
        except:
            e_type, e_value, tb = exc_info()
            traceback = format_tb(tb)
            traceback.append('%s: %s' % (e_type.__name__, e_value))
            result = '\n'.join(traceback)
        
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain')]
    
    start_response(status, headers)
    return [json.dumps(ret)]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('localhost', conf.REST_PORT, application)
    server.serve_forever()

