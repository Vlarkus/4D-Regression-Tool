import http.server
import socketserver
import webbrowser
import threading
import os
import time
import json
import csv
import urllib.parse

PORT = 8501
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIRECTORY, 'data')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # API: list CSV files
        if path == '/api/files':
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
            files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
            self._send_json(files)

        # API: load a specific CSV
        elif path == '/api/data':
            filename = params.get('file', [None])[0]
            if not filename:
                self._send_json({'error': 'No file specified'}, 400)
                return
            filepath = os.path.join(DATA_DIR, os.path.basename(filename))
            if not os.path.exists(filepath):
                self._send_json({'error': 'File not found'}, 404)
                return
            try:
                # Try common encodings — Excel often saves as UTF-16
                for enc in ('utf-8-sig', 'utf-16', 'latin-1'):
                    try:
                        with open(filepath, newline='', encoding=enc) as f:
                            content = f.read()
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        continue
                else:
                    self._send_json({'error': 'Could not decode file (tried utf-8, utf-16, latin-1)'}, 500)
                    return
                import io
                reader = csv.DictReader(io.StringIO(content))
                rows = []
                for row in reader:
                    parsed_row = {}
                    for k, v in row.items():
                        if k is None:
                            continue
                        k = k.strip()
                        v = (v or '').strip()
                        try:
                            parsed_row[k] = float(v)
                        except (ValueError, TypeError):
                            parsed_row[k] = v
                    rows.append(parsed_row)
                headers = [h.strip() for h in (reader.fieldnames or []) if h]
                self._send_json({'headers': list(headers), 'rows': rows})
            except Exception as e:
                self._send_json({'error': str(e)}, 500)

        else:
            super().do_GET()

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # suppress request logs

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    print("Opening browser at http://localhost:8501/index.html")
    webbrowser.open(f"http://localhost:{PORT}/index.html")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down.")
