#!/anaconda/bin/python -tt

from optparse import OptionParser
import sys
from fidelity import get_data, send_data


def _parse_args(argv):
    usage = """
WARNING: This script requires that you pass your username, password 
and accountId. This script calls cleartext only to the login form. 
Once logged in subsequent HTML calls are https. That said, you are 
passing this in clear text when running this from your shell, 
so your system must be secure and that is YOUR responsibility. Also, 
of course, do NOT store this information unencryted in a plain text
file anywhere, ever.

[-c|--customer-id] - customer Id. Required.
[-p|--pin] - customer PIN number or password. Required.
[-a|--account-id] - customer account from which to retrieve position information. Required.
[-e|--customer-email] - customer email. Required.
    """
    parser = OptionParser(usage=usage)

    parser.add_option("-c", "--customer-id", 
                      action="store", dest="customer_id",
                      help="Customer Id of the customer to retrieve position data for. Required.") 

    parser.add_option("-p", "--pin", 
                      action="store", dest="pin",
                      help="Customer pin number. Required.") 

    parser.add_option("-a", "--account-id", 
                      action="store", dest="account_id",
                      help="Customer account from which to retrieve position information. Required.") 
    
    parser.add_option("-e", "--customer-email", 
                      action="store", dest="customer_email",
                      help="Customer account from which to retrieve position information. Required.") 

    (options, args) = parser.parse_args(argv)
    
    if not options.customer_id or not options.pin or not options.account_id or not options.customer_email:
        print "Invalid argument error."
        print """
Your args:  
  customer_id {0} 
  pin {1} 
  account_id {2} 
  customer_email {3}""".format(options.customer_id, options.pin, options.account_id, options.customer_email)
        print usage
    
    return options.customer_id, options.pin, options.account_id, options.customer_email


def main(argv):
    data = None
    customer_id, pin, account_id, customer_email = _parse_args(argv)
    if customer_id and pin and account_id and customer_email:
        data = get_data(customer_id, pin, account_id, customer_email)
        send_data(data)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

