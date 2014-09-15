require 'net/http'
require 'open-uri'
require 'sinatra'
set :server, 'thin'


def query_google_search(k):
    """
* `k` - `string`. The query term.

Helper that calls Google Search API with a query and returns JSON results set. 
Returns an array of JSON objects in the `['responseData']['results']` value  as 
described in the documentation for `get_child_schema`.
"""    
  k = URI::encode(k)
  url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=#{k}'
  ret = Net::HTTP.get_response(URI(url)) 
  ret = ret.body
    
  if ret: 
    ret = {'results' : ret['responseData']['results']}
  else:
    ret = {'results' : []}
  
  ret



get '/parse_args' do
  args = params['args']
  '{"parsed_args" : "#{args}", "is_valid" : true}'   
end


get '/get_data' do
  keys = params['keys']
  args = params['args']
  
end


get '/get_schema' do
  '{"schema" : ["results"]}'
end


get '/adds_keys' do
  '{"adds_keys" : false}'
end


run Sinatra::Application

