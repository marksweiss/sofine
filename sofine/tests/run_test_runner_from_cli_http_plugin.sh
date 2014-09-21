# This writes it's pid into __FILE__.pid
ruby ./sofine/plugins/example_http/google_search_results.rb & 

# Yeah, I know. But we need to pause execution so that the web server in the
#  plugin above (Sinatra) is running before the Python tests start to call it
sleep 3s

# Read pid for ruby process to kill from the file, read here so we don't leak the Sinatra process
#  even if running the tests throws and this script aborts
pid=`cat ./sofine/plugins/example_http/google_search_results.rb.pid`

python ./sofine/tests/test_runner_from_cli_http_plugin.py

# This kills the script which itself launched Sinatra, as a child process
kill $pid
# Cleanup the pid file
rm ./sofine/plugins/example_http/google_search_results.rb.pid

# This calls a route defined in the parent script (whose process is now killed) but loaded and running
#  as the handler for a route in Sinatra, at path /kill. This route calls the Sinatra Application::quit!
#  method, which Sinatra exposes to cleanly shut itself down. If you don't call this, the Sinatra::at_exit
#  module method restarts the Sinatra process. i.e. you can't kill it programatically any other way.
curl $SOFINE_HTTP_PLUGIN_URL"/google_search_results/example_http/kill"


