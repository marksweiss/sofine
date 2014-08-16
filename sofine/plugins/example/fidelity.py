"""WARNING: This script requires that you pass your username, password 
and accountId. This script calls cleartext only to the login form. 
Once logged in subsequent HTML calls are https. That said, you are 
passing this in clear text when running this from your shell, 
so your system must be secure and that is YOUR responsibility. Also, 
of course, do NOT store this information unencryted in a plain text
file anywhere, ever.

A plugin that wraps logging into Fidelity.com and retrieving porfolio keys and attributes by
by scraping the page displaying a portfolio for an account.

Based on a project with the license and credited contributors listed in the comment to this
module, which is immediately after this.
"""


# www.fidelity.com account positions scraper

# Copyright (c) 2009 Matthew J Ernisse <mernisse@ub3rgeek.net>
# Copyright (c) 2009 John Morrissey <jwm@horde.net>
# Copyright (c) 2014 Mark Weiss <marksweiss@yahoo.com>

# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided
# that the following conditions are met:
#
#    * Redistributions of source code must retain the
#      above copyright notice, this list of conditions
#      and the following disclaimer.
#    * Redistributions in binary form must reproduce
#      the above copyright notice, this list of conditions
#      and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# $Id$

import logging
import os
import re
import sys
from urllib2 import HTTPError
from optparse import OptionParser

from bs4 import BeautifulSoup
import mechanize

from sofine.plugins import plugin_base as plugin_base


HOST = 'www.fidelity.com'
LOGIN_PAGE = 'https://login.fidelity.com/ftgw/Fidelity/RtlCust/Login/Init'
LOGIN_FORM_ACTION = 'https://login.fidelity.com/ftgw/Fas/Fidelity/RtlCust/Login/Response'
DEBUG = False 
PROXY = ''
ACCOUNT_PAGE = 'https://oltx.fidelity.com/ftgw/fbc/ofpositions/brokerageAccountPositions?ACCOUNT=%s'


def _get_fidelity_logged_in_browser_session(customer_id, pin, account_id, customer_email):
    # By default, store the RRD file in the same directory as this script.
    # RRD = '%s/fidelity-balance.rrd' % os.path.dirname(sys.argv[0])
    # Keep this many years of data in the RRD.
    # RRD_KEEP_LENGTH = 3

    # Set this to a filename if you want to write a tab file instead of
    # creating/updating an RRD. The file format is compatible with the
    # T. Rowe Price (trp) scraper by John Morrissey <jwm@horde.net>.
    # TAB = ''

    # Initialize mechanize settings
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.set_handle_refresh(True, 10, True)
    br.set_handle_redirect(True)
    # This e-mail address will be appended to the User-Agent header, so
    # the site can contact you about your scraping if they so desire.
    br.addheaders = [
        ('User-agent',
            'Mozilla/5.0 (X11; U; Linux i686; en-US; rv 1.0) %s' % customer_email),
    ]
    if PROXY:
        br.set_proxies({
            'http': PROXY,
            'https': PROXY,
        })

    if DEBUG:
        br.set_debug_http(True)
        br.set_debug_responses(True)
        br.set_debug_redirects(True)
        logger = logging.getLogger('mechanize')
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.DEBUG)

    try:
        br.open(LOGIN_PAGE)
    except HTTPError, e:
        sys.exit('%d %s' % (e.code, e.msg))

    if not br.viewing_html():
        sys.exit('Unable to retrieve HTML for login page, has %s changed?' % HOST)
    try:
        br.select_form('Login')
    except mechanize.FormNotFoundError:
        sys.exit('Unable to locate login form, has %s changed?' % HOST)

    # The form action is set by some validation JavaScript, so we have to
    # blindly set it ourselves.
    br.form.action = LOGIN_FORM_ACTION
    br.form.set_all_readonly(False)
    br['SSN'] = customer_id 
    br['PIN'] = pin

    try:
        r = br.submit()
    except HTTPError, e:
        sys.exit('%d %s' % (e.code, e.msg))

    return br


def _get_fidelity_position_data(br, account_id):
    r = br.open(ACCOUNT_PAGE % account_id)
    strip_script = re.compile(r'<script\s+.*?</script>', re.I + re.S)
    soup = BeautifulSoup(strip_script.sub('', r.get_data()), "lxml")

    # This is the data structure we fill up with data about each position in the portfolio
    # Keyed to ticker for that security
    position_data = {}

    try:
        positions_div = soup.find(attrs={'class' : 'layout-open-positions-data-tables-region'})
        
    except:
        sys.exit('Unable to locate positions div')

    ticker_re = re.compile('^javascript:popWin\(\'https://fastquote.fidelity.com/webxpress/popup_frameset.phtml\?SID_VALUE_ID=')
    for posn in positions_div.find_all('tbody'):
        ticker = ''
        description = ''
        quantity = '' 
        change_since_purchase = ''
        change_since_purchase_pct = ''

        posn_list = list(posn.find_all('td'))
        if len(posn_list) > 1:
            quantity = posn_list[2].contents[0].strip()
            
            cspl = posn_list[8].contents
            if len(cspl) > 1:
                change_since_purchase = cspl[1].string.strip()

            csppl = posn_list[9].contents
            if len(csppl) > 1:
                change_since_purchase_pct = csppl[1].string.strip()
        
        for elem in posn.find_all('td'):
            # First cell in the row has the ticker
            ticker_elem = elem.find(attrs={'href' : ticker_re})
            # ticker_elem = elem.find(attrs={'id' : 'anchor_{0}_DrillDown'.format(account_id)})
            if ticker_elem:
                ticker_str = ticker_elem.string
                if ticker_str:
                    ticker_str = ticker_str.strip()
                    if ticker_str != 'News':
                        ticker = ticker_str
            # Second cell in the row has the short and full description
            desc_elem = elem.find(attrs={'id' : 'fullDesc'})
            if desc_elem and len(desc_elem.contents):
                desc_str = None
                # Sometimes this has an anchor tag etc., but only if it's a row
                #  with cash or something else that doesn't have a ticket
                # So try to get string and we will be able to if there is a ticker
                try:
                    desc_str = desc_elem.contents[0].string
                except:
                    pass
                if desc_str:
                    description = desc_str
       
        if ticker:
            position_data[ticker] = \
                {
                    'description' : description, 
                    'quantity' : quantity,
                    'change_since_purchase' : change_since_purchase,
                    'change_since_purchase_pct' : change_since_purchase_pct
                }

    return position_data


class FidelityPortfolioScraper(plugin_base.PluginBase):

    def __init__(self):
        """
* `self.name = 'fidelity'`
* `self.group = 'example'`
* `self.schema = ['change_since_purchase', 'description', 
                  'change_since_purchase_pct', 'quantity']`
* `self.adds_keys = True`
"""
        super(FidelityPortfolioScraper, self).__init__()
        self.name = 'fidelity'
        self.group = 'example'
        self.schema = ['change_since_purchase', 'description', 
                       'change_since_purchase_pct', 'quantity']
        self.adds_keys = True


    def get_data(self, keys, args):
        """
* `keys` - `list`. The list of keys to process.
* `args` - `'list`. Must include, in order the users `customer_id`, `pin`, 
`account_id`, `customer_email`.

Retrieves data for the portfolio identified by the args passed in. 
"""
        customer_id, pin, account_id, customer_email = args
        br = _get_fidelity_logged_in_browser_session(customer_id, pin, account_id, customer_email)
        data = _get_fidelity_position_data(br, account_id)
        return data


    def parse_args(self, argv):
        """
WARNING: This script requires that you pass your username, password 
and accountId. This script calls cleartext only to the login form. 
Once logged in subsequent HTML calls are https. That said, you are 
passing this in clear text when running this from your shell, 
so your system must be secure and that is YOUR responsibility. Also, 
of course, do NOT store this information unencryted in a plain text
file anywhere, ever.

* `[-c|--customer-id]` - Customer Id. Required.
* `[-p|--pin]` - Customer PIN number or password. Required.
* `[-a|--account-id]` - Customer account from which to retrieve position information. Required.
* `[-e|--customer-email]` - Customer email. Required.
"""

        usage = """
WARNING: This script requires that you pass your username, password 
and accountId. This script calls cleartext only to the login form. 
Once logged in subsequent HTML calls are https. That said, you are 
passing this in clear text when running this from your shell, 
so your system must be secure and that is YOUR responsibility. Also, 
of course, do NOT store this information unencryted in a plain text
file anywhere, ever.

[-c|--customer-id] - Customer Id. Required.
[-p|--pin] - Customer PIN number or password. Required.
[-a|--account-id] - Customer account from which to retrieve position information. Required.
[-e|--customer-email] - Customer email. Required.
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

        (opts, args) = parser.parse_args(argv)
    
        is_valid = True
        if not (opts.customer_id and \
                opts.pin and \
                opts.account_id and \
                opts.customer_email):
            print "Invalid argument error."
            print """
Your args:  
  customer_id {0} 
  pin {1} 
  account_id {2} 
  customer_email {3}""".format(opts.customer_id, opts.pin, opts.account_id, opts.customer_email)
            print usage
            is_valid = False
    
        # NOTE: the protocol for parse_args is to pass the returned args in a list
        return is_valid, [opts.customer_id, opts.pin, opts.account_id, opts.customer_email]


plugin = FidelityPortfolioScraper

