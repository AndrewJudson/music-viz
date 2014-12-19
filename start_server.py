import SimpleHTTPServer
import SocketServer
import sys

if len(sys.argv) < 2:
   PORT = 8000
else:
   PORT = int(sys.argv[1])

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()
