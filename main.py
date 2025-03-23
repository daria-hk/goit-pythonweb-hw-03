import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from jinja2 import Template
from datetime import datetime
import json

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        message_data = {
            "username": data_dict.get("username"),
            "message": data_dict.get("message")
        }

        try:
            with open("storage/data.json", "r") as f:
                all_data = json.load(f)
        except FileNotFoundError:
            all_data = {}

        all_data[timestamp] = message_data

        with open("storage/data.json", "w") as f:
            json.dump(all_data, f, indent=4)

        print(message_data)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/read':
            self.display_msg()
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def display_msg(self):
        try:
            with open('storage/data.json', 'r') as f:
                all_data = json.load(f)
        except FileNotFoundError:
            all_data = {}

        with open('read.html', 'r') as f:
            rows_tmp = Template(f.read())

        rendered_templt = rows_tmp.render(messages=all_data)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(rendered_templt.encode('utf-8'))

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()