import BaseHTTPServer

connection_tuple = ('127.0.0.1',7777)
redirections = {}
FILE = "redirects.txt"


with open(FILE, "r") as f:
	redirects = f.readlines()
for r in redirects:
	r = r.rstrip("\n")
	if not r.startswith("#") and r:
		[short,long] = r.split(" => ")
		redirections[short] = long

def write_urls(shorturl,longurl,file=FILE):
	with open(file, "a") as f:
		f.write("%s => %s\n" % (shorturl, longurl))
	return 0

class ShortURLHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(s):
		if s.path == "/404":
			s.send_response(404)
		else:
			s.send_response(301)
			s.send_header("Location", redirections.get(s.path, "404"))
			s.end_headers()
			
	def do_GET(s):
		if s.path == "/":
			s.send_response(200)
			s.send_header("Content-type","text/plain")
			s.end_headers()
			for url in redirections.keys():
				s.wfile.write("%s => %s\n" % (url, redirections[url]))
		else:
			s.do_HEAD()
			
	def do_POST(s):
		query_length = int(s.headers['Content-Length'])
		urls = s.rfile.read(query_length) # curl --data "/shorturl=>longurl" 127.0.0.1:7777
		try:
			short, long = urls.split("=>")
		except:
			s.send_response(418)
			s.send_header("Content-type","text/teapot")
			s.end_headers()
			s.wfile.write("Invalid url format. Use \"shorturl=>longurl\"\n")
			return 1
		if short == '' or long == '' or not long.startswith("http://"): # any other way?
			return 0 # silently drop
		
		if not short.startswith("/"):
			short = '/'+short

		redirections[short] = long # it's brilliant because it will replace existing urls
		write_urls(short, long)
		print "added %s => %s" % (short,long)
		s.send_response(200)
		s.send_header("Content-type", "text/plain")
		s.end_headers()
		s.wfile.write("added %s => %s\n" % (short,long))
		
		
		
		
if __name__ == '__main__':
	server_class = BaseHTTPServer.HTTPServer
	httpd = server_class(connection_tuple, ShortURLHandler)
	print "Server starting."
	try: httpd.serve_forever()
	except KeyboardInterrupt: pass
	httpd.server_close()
	