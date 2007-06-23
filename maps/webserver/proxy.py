#############################################################
# Simple proxy
#############################################################

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urllib2
import re

class WebProxyRequestHandler(BaseHTTPRequestHandler):
	"""A subclass of BaseHTTPRequestHandler that acts as a web proxy
	server and can be chained with other web proxies.
	"""
	def do_GET(self):
		print "do_GET()"
		self.get_post_impl()

 	def do_POST(self):
		print "do_POST()"
		length = self.headers["Content-Length"]
		d = self.rfile.read(int(length))
		self.get_post_impl(d)
        
	def get_post_impl(self, data=None):
		if self.path=="/maps/":
			self.path="/index.html"
			server = self.server
			url = "%s:%d" % server.proxy_addr
			self.retrieve_request(data, {'http':url})

	def retrieve_request(self, data, proxies={}):
		request = urllib2.Request(self.path)
		for header in self.headers.keys():
			if header.lower() != "host" and header.lower() != "user-agent":
				values = self.headers.getheaders(header)
				value_string = " ".join(values)
				request.add_header(header, value_string)
		for proxy_type in proxies:
			print "setting proxy: (%s, %s)" % (proxies[proxy_type],proxy_type)
			request.set_proxy(proxies[proxy_type], proxy_type)
        	if data != None:
            		request.add_data(data)
       		print "Attempting to open %s ..." % self.path
        	f = urllib2.urlopen(request)
		print "Successfully opened %s" % self.path
            
		self.send_response(200) #OK
		print "-- Response Info --" 
		for item in f.info().keys():
			print "%s: %s" % (item, f.info()[item])
			self.send_header(item, f.info()[item])
		print "-- end Response Info --"
		self.end_headers()
		print "Reading..."
		s = f.read()
		print "Read successful."
		f.close()
		print "Writing..."
		self.wfile.write(s)
		print "Write successful."
		#self.wfile.close()
	def write_error(self, error):
		self.send_response(200)
		self.wfile.write("""<html>
		<head>
		    <title>Error</title>
		</head>
		<body>
		    An error occured connecting to the address given.
		    <br/>
		</body>
		</html>""") 
	        self.wfile.close()

class WebProxy(HTTPServer):
	def __init__(self, server_addr, proxy_addr=None):
	        HTTPServer.__init__(self, server_addr, WebProxyRequestHandler)
	        self.proxy_addr = proxy_addr

if __name__ == "__main__":
	import sys
	host = "localhost"
	port = 7987
	proxy_addr = "localhost"
	proxy_port = 7988

	proxy = WebProxy((host, port), (proxy_addr, proxy_port))
	print "Listening on %s:%d\nForwarding to %s:%d" % (host,port, proxy_addr, proxy_port)
	proxy.serve_forever()
