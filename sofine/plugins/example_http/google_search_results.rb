require 'net/http'
require 'open-uri'
require 'json'
require 'sinatra'


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


get '/parse_args' do
  JSON.dump({"parsed_args" => params[args], "is_valid" => true})
end


get '/get_data' do
  keys = params['keys'].split(',')
  
  # TEMP DEBUG
  # query_google_search(keys[0])

  ret = {}
  keys.each {|key| 
    attrs = []
    attrs.insert(0, query_google_search(key))
    ret[key] = attrs 
  }

  JSON.dump(ret)
end


get '/get_schema' do
  '{"schema" : ["results"]}'
end


get '/adds_keys' do
  '{"adds_keys" : false}'
end

