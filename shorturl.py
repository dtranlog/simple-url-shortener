#!/usr/bin/env python
#
#
#



import BaseHTTPServer
import sys
import cgi
import operator

connection_tuple = ('127.0.0.1',7777)
redirections = {}
FILE = "redirects.txt"

def load_file(file=FILE):
	with open(file, "r") as f:
		redirects = f.readlines()
	for r in redirects:
		r = r.rstrip("\n")
		if not r.startswith("#") and r:
			try:
				urls, count = r.split("(")
				count = count.split(")")[0].rstrip().lstrip()
				[short,long] = urls.split(" => ")
				redirections[short.rstrip().lstrip()] = [long.rstrip().lstrip(), int(count)]
			except:
				short,long = r.split(" => ")
				redirections[short.lstrip().rstrip()] = [long.rstrip().lstrip(), 0]
	#print redirections
	
def dump_file(file=FILE):
	with open(FILE,"w") as f:
		f.write("")
	with open(FILE, "a") as f:
		for short in redirections.keys():
			f.write("%s => %s (%s)\n" % (short, redirections[short][0], str(redirections[short][1])))
			


class ShortURLHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	
	load_file()
	
				
	
		
				
	def write_urls(self,shorturl,longurl,file=FILE):
		if not shorturl.startswith("/"):
			shorturl = '/' + shorturl
		with open(file, "a") as f:
			f.write("%s => %s (%s)\n" % (shorturl, longurl,0))
		redirections[shorturl] = [longurl, 0]
		print "=> Added %s => %s" % (shorturl,longurl)
		return 0
	
	def do_404(self):
			print "=> sent 404 on \"" + self.path + "\""
			self.send_response(404)
			self.send_header("Content-type","text/plain")
			self.end_headers()
			self.wfile.write("not found")


	def do_HEAD(self):
			self.send_response(301)
			print "=> Match for redirect was",redirections.get(self.path)
			#print redirections
			if redirections.get(self.path):
				redirections[self.path][1] += 1
				print "=> Redirected to "+redirections[self.path][0],"and incremented by one (to",redirections[self.path][1],")."
			self.send_header("Location", redirections.get(self.path, "http://%s:%s/404" % connection_tuple)[0])
			self.end_headers()
			
	def do_GET(self):
		if self.path == "/":
			self.send_response(200)
			self.send_header("Content-type","text/plain")
			self.send_header("Pragma","no-cache")
			self.send_header("Expires", "Wed, 11 Jan 1984 05:00:00 GMT")
			self.end_headers()
			for line in sorted(redirections.items(), key=lambda x: x[1][1], reverse=True):
				self.wfile.write("%s => %s (%s)\n" % (line[0], line[1][0], line[1][1]))
				
		elif self.path == "/submit.html" or self.path == "/submit":
			self.send_response(200)
			self.send_header("Content-type","text/html")
			self.end_headers()
			with open("submit.html") as f:
				self.wfile.write(f.read())
		elif redirections.get(self.path) != None:
			self.do_HEAD()
		else:
			self.do_404()
			
	def do_POST(self):
		query_length = int(self.headers['Content-Length'])
		string = self.rfile.read(query_length)
		self.args = dict(cgi.parse_qsl(string))
		
		try:
			if self.args['shorturl'] == '' or self.args['longurl'] == '' or not self.args['longurl'].startswith("http://") or self.args['shorturl'] == '404': # any other way?
				self.send_response(400)
				self.send_header("Content-type","text/plain")
				self.end_headers()
				self.wfile.write("Invalid url format(s).\n")
				return 1
			
		except:
			return 0
		
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		html ="""<html><head>
		<meta http-equiv="refresh" content="3;url=http://%s:%s">
		</head><body>
		<pre>Accepted %s => %s</pre>
		</body></html>""" \
		% (connection_tuple[0], connection_tuple[1],self.args['shorturl'], self.args['longurl'])
		self.wfile.write(html)	
		self.write_urls(self.args['shorturl'], self.args['longurl'])
		
		
		
		
if __name__ == '__main__':
	server_class = BaseHTTPServer.HTTPServer
	httpd = server_class(connection_tuple, ShortURLHandler)
	print "=> Server starting."
	try: httpd.serve_forever()
	except KeyboardInterrupt:
		dump_file()
	httpd.server_close()
	