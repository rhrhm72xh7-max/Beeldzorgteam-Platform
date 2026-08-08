import http.server
import socketserver
import urllib.parse
import os

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

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Intercept Nuxt Image requests
        if parsed_path.path == '/_amplify/image':
            query = urllib.parse.parse_qs(parsed_path.query)
            if 'url' in query:
                image_url = query['url'][0] # e.g. /images/image-features-nudges-2.webp
                
                # Check if it's pointing to /images/
                if image_url.startswith('/images/'):
                    self.path = image_url
                    return super().do_GET()
                    
        return super().do_GET()

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
