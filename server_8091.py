import http.server
import socketserver
import urllib.parse
import os
import mimetypes

PORT = 8091
DIRECTORY = os.getcwd()

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def guess_type(self, path):
        # If there is no extension, assume it's an HTML file (e.g. Nuxt generated pages like /platform/welzijn)
        if '.' not in os.path.basename(path):
            return 'text/html'
        return super().guess_type(path)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Intercept Nuxt Image requests
        if parsed_path.path == '/_amplify/image':
            query = urllib.parse.parse_qs(parsed_path.query)
            if 'url' in query:
                image_url = query['url'][0]
                if image_url.startswith('/images/'):
                    self.path = image_url
                    return super().do_GET()
                    
        # Intercept Icon requests to prevent 404 noise
        if parsed_path.path.startswith('/api/_nuxt_icon'):
            self.send_response(200)
            self.send_header("Content-type", "image/svg+xml")
            self.end_headers()
            self.wfile.write(b'<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M5 17.59L15.59 7H9V5h10v10h-2V8.41L6.41 19L5 17.59z"/></svg>')
            return

        return super().do_GET()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

with ThreadedTCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
