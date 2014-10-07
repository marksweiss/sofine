require 'rubygems'
require 'net/http'
require 'open-uri'
require 'json'

# TODO Document this as a requirement for HTTP plugins if you want sofine to manage them
# Record the PID of this process before Sinatra starts (i.e. of the parent before the 
#  child server process starts), so we can kill it later from the outer shell script
#  running this plugin. This is mainly so this plugin can be tested with automated tests
#  running in Python, which is what sofine is implemented in.
File.open(__FILE__ + '.pid', 'w') {|f| f.write Process.pid }
require 'sinatra'


PLUGIN_NAME = 'ystockquotelib_mock'
PLUGIN_GROUP = 'mock_http'

SCHEMA = ['fifty_two_week_low', 'market_cap', 'price', 'short_ratio', 
          'volume','dividend_yield', 'avg_daily_volume', 'ebitda', 
          'change', 'dividend_per_share', 'stock_exchange', 
          'two_hundred_day_moving_avg', 'fifty_two_week_high', 
          'price_sales_ratio', 'price_earnings_growth_ratio',
          'fifty_day_moving_avg', 'price_book_ratio', 'earnings_per_share', 
          'price_earnings_ratio', 'book_value']

MOCK_ATTRS = Hash[SCHEMA.map {|f| [f, 1.0]}]


get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/parse_args' do
  JSON.dump({"parsed_args" => params['args'], "is_valid" => true})
end


get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/get_data' do
  keys = params['keys'].split(',')
  ret = Hash[keys.map {|k| [k, MOCK_ATTRS]}]
  JSON.dump(ret)
end


get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/get_schema' do
  "{\"schema\" : #{SCHEMA} }"
end


get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/adds_keys' do
  '{"adds_keys" : false}'
end


get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/test' do
  'TEST CALL'
end


# This overrides Sinatra's annoying default behavior of restarting itself when you kill it
# Without this automated test from shell process kills this process' PID but then the at_exit
#  handler in Sinatra restarts Sinatra again. This is exposed by Sinatra to kill itself cleanly
get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/kill' do
  Sinatra::Application.quit!
end


