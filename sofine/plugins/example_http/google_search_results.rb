require 'net/http'
require 'open-uri'
require 'json'
require 'sinatra'


PLUGIN_NAME = 'google_search_results'
PLUGIN_GROUP = 'example_http'


def query_google_search(k) 
'
* `k` - `string`. The query term.

Helper that calls Google Search API with a query and returns JSON results set. 
Returns an array of JSON objects in the `["responseData"]["results"]` value  as 
described in the documentation for `get_child_schema`.
'    
  k = URI::encode(k)
  url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=#{k}"
  ret = Net::HTTP.get_response(URI(url)) 
  ret = JSON.load(ret.body)
    
  if ret 
    ret = {'results' => ret['responseData']['results']}
  else
    ret = {'results' => []}
  end
  
  ret
end


get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/parse_args' do
    JSON.dump({"parsed_args" => params['args'], "is_valid" => true})
end


get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/get_data' do
  keys = params['keys'].split(',')
  
  # This is the kind of ruby one-liner you need to keep around a ruby 2-liner to understand
  # But this is why ruby is fun! When you get your head around these things you're happy.
  # ret = {} 
  # keys.each {|key| ret[key] = Array.new(1) {query_google_search(key)}}
  ret = Hash[keys.map {|key| [key, query_google_search(key)]}] 

  JSON.dump(ret)
end


get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/get_schema' do
  '{"schema" : ["results"]}'
end


get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/adds_keys' do
  '{"adds_keys" : false}'
end

