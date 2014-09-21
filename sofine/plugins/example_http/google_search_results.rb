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
  
  # TEMP DEBUG
  puts url
  
  
  ret = Net::HTTP.get_response(URI(url)) 
  ret = JSON.load(ret.body)
    
  if ret and ret.code == '200'
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


get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/test' do
  puts 'TEST CALL'
end


# This overrides Sinatra's annoying default behavior of restarting itself when you kill it
# Without this automated test from shell process kills this process' PID but then the at_exit
#  handler in Sinatra restarts Sinatra again. This is exposed by Sinatra to kill itself cleanly
get '/' + PLUGIN_NAME + '/' + PLUGIN_GROUP + '/kill' do
  Sinatra::Application.quit!
end

