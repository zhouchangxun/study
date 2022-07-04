#!/usr/bin/env python
# UDP Client - support send to multi udp endpoint.
import socket, sys
import cmd
import threading
import time

def recv_handler(sock):
    while 1:
        try:
            message, address = sock.recvfrom(8192)
            print("Got data from", address, ": ", message)
            # s.sendto(message, address)
        except (KeyboardInterrupt, SystemExit):
            print('recv thread exited')
            raise

def start_receiver():
    host = ''
    port = int(sys.argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    print("listening udp port : ", port)
    t = threading.Thread(target=recv_handler, args=(s,))
    t.setDaemon(True)   # 把子线程设置为守护线程，必须在start()之前设置
    t.start()
    return s

class Shell(cmd.Cmd):
    intro = 'Type help or ? to list commands.\n'
    prompt = '(udpclient) '
    sock = None

    # ----- basic turtle commands -----
    def do_sendto(self, args):
      if not self.sock:
        print('execute recv_on before send.')
        return
      print('send to {}'.format(args))
      host, port, data = args.split()
      self.sock.sendto(data.encode(), (host, int(port)))

    def do_recv_on(self, args):
      self.sock = start_receiver()  

    def emptyline(self):
        pass

    def do_q(self, args):
      return True

if __name__ == '__main__':
    Shell().cmdloop()
