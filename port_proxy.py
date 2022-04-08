#!/usr/bin/env python
import socket
import sys
import time
import argparse

print('python version: {}'.format(sys.version))
if sys.version.startswith('3'):
    from urllib.parse import parse_qs
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    def new_thread(loop_func, args):
        t = threading.Thread(target=loop_func, args=args)
        t.setDaemon()
        t.start()
else:
    import thread
    from urlparse import parse_qs
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    def new_thread(loop_func, args):
        thread.start_new_thread(loop_func, args)

import json
import cgi

runtime = dict(
    session=[],
    actions=[]
)

class ApiHandler(BaseHTTPRequestHandler):
    def _make_json_response(self, body, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body, indent=2).encode())

    def do_GET(self):
        print(self.path)
        path = str(self.path)
        if path == '/api/runtime':
            self._make_json_response(runtime['session'])
        else:
            self._make_json_response(dict(apis=[
                '/api/echo'
                '/api/runtime']))

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        # print(ctype, pdict)

        if ctype != 'application/json':
            self.send_error(415, "Only json data is supported.")
            return
        path = str(self.path)
        if path == '/api/echo':
            # print(path)
            length = int(self.headers['content-length'])
            datas = self.rfile.read(length)
            # print(datas)
            rjson = json.loads(datas.decode())
            # print(rjson,type(rjson))
            self._make_json_response({'code':'ok', 'data':rjson})
            
        elif path == '/api/traffic/':
            # print(path)
            length = int(self.headers['content-length'])
            datas = self.rfile.read(length)
            # print(datas)
            rjson = json.loads(datas.decode())
            # print(rjson,type(rjson))
            self._make_json_response({})
        else:
            self.send_error(404, "Not Found")
            

def api_server_thread():
    host = ('', 9527)
    server = HTTPServer(host, ApiHandler)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
    print('shutdown http server...')

"""
  topo:  [A:(*) -> B:b(proxy)] <- bridge -> [B:(*) -> C:c]
usage:
  (host B) python port_proxy.py 2201 192.168.1.10 22

 rules.conf as follows:
   <local incoming port> <dest hostname> <dest port>
"""

def parse_file(filename):
    settings = list()
    for line in file(filename):
        # skip comment line
        if line.startswith('#'):
            continue

        parts = line.split()
        settings.append((int(parts[0]), parts[1], int(parts[2])))
    return settings

def parse_rules(rules):
    settings = list()
    for line in rules.split(','):
        parts = line.split(":")
        settings.append((int(parts[0]), parts[1], int(parts[2])))
    return settings

def start_listener(*settings):
    try:
        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.bind(('', settings[0]))
        dock_socket.listen(5)
        print('start listener :{} <-> {}'.format(settings[0], settings[1:]))
        while True:
            client_socket = dock_socket.accept()[0]
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((settings[1], settings[2]))
            sess = '{}:{} <-> {}:{}'.format(
                client_socket.getsockname(), client_socket.getpeername(),
                server_socket.getsockname(), server_socket.getpeername())
            print('new session {}'.format(sess))
            runtime['session'].append((sess))
            new_thread(forwarder, (client_socket, server_socket))
            new_thread(forwarder, (server_socket, client_socket))
    finally:
        print('shutdown listner {}'.format(settings[0]))

def forwarder(source, destination):
    while True:
        try:
            string = source.recv(1024)
            if string:
                destination.sendall(string)
            else:
                source.shutdown(socket.SHUT_RD)
                destination.shutdown(socket.SHUT_WR)
        except socket.error as e:
            print(e)
            break

def exit_handler():
    # todo: close connected socket.
    print('exited.')

def heartbeat(msg='ping'):
    while True:
        print(msg)
        time.sleep(2)

def main():
    parser = argparse.ArgumentParser(description='Port proxy utility.')
    parser.add_argument('--rule', type=str, help='local_listen_port:remote_ip:remote_port')
    parser.add_argument('--file', type=str, help='file which contains rules')
    parser.add_argument('--log', help='redirect log to file.')
    args = parser.parse_args()

    if args.log:
        log_file = file(args.log, 'a')
        sys.stdout = log_file
        sys.stderr = log_file

    if args.file: 
        for setting in parse_file(args.file):
            new_thread(start_listener, setting)
    elif args.rule:
        # read settings for port forwarding
        for setting in parse_rules(args.rule):
            new_thread(start_listener, setting)
    else:
        print('error: missing rules. use --rule for one rule or --file rules.conf for multi rules')
        return 1
    # wait for <ctrl-c>
    try:
        api_server_thread()
    except KeyboardInterrupt:
        exit_handler()


if __name__ == '__main__':
    exit(main())
