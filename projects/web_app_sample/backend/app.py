
#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer

class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(b'{"status":"ok","service":"backend"}')

if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 8080), AppHandler).serve_forever()
