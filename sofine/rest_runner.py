import runner
import lib.utils.conf as conf
from cgi import parse_qs, escape
from sys import exc_info
from traceback import format_tb


# Borrows from here: http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
#  which is the best basic DIY wsgi tutorial I found


def application(environ, start_response):
    result = ''
    status = ''
    headers = None

    method = environ['REQUEST_METHOD']
    if method != 'POST':
        status = '405 Method Not Allowed'
        headers = [('Content-type', 'text/plain')]
        result = status + '. Only POST method is allowed'
    else:
        try:
            params = parse_qs(environ.get('QUERY_STRING'))
            params_list = []
            for k, v in params.iteritems():
                params_list.append(escape(k))
                params_list.append(escape(v[0]))
        
            result = runner.main(params_list)
            # result = ' '.join(params_list)

            status = '200 OK'
            headers = [('Content-type', 'application/json')]
        except:
            e_type, e_value, tb = exc_info()
            traceback = format_tb(tb)
            traceback.append('%s: %s' % (e_type.__name__, e_value))
            result = '\n'.join(traceback)
        
            status = '500 Internal Error'
            headers = [('Content-type', 'text/plain')]
    
    start_response(status, headers)
    return [result]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('localhost', conf.REST_PORT, application)
    server.serve_forever()

