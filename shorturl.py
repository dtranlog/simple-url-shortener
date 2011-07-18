import BaseHTTPServer
c = ('127.0.0.1',7777)
redirections = {}

with open("redirects.txt", "r") as f:
	redirects = f.readlines()
for r in redirects:
	r = r.rstrip("\n")
	if not r.startswith("#") and r:
		[short,long] = r.split(" => ")
		redirections[short] = long
print redirections
		
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
			for line in redirects:
				#s.wfile.write("%s => %s\n" % (url, redirections[url]))
				s.wfile.write(line)
		else:
			s.do_HEAD()
		
if __name__ == '__main__':
	server_class = BaseHTTPServer.HTTPServer
	httpd = server_class(c, ShortURLHandler)
	try: httpd.serve_forever()
	except KeyboardInterrupt: pass
	httpd.server_close()
	