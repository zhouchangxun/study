import sys
import time
import datetime
import socket


def now():
  return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

def connect_remote():
  ipaddr = (sys.argv[1], int(sys.argv[2]))
  s = socket.socket()
  print('{} connecting {}'.format(now(), ipaddr))
  s.connect(ipaddr)
  print('%s connected.' % now())
  return s

def interactive_shell(sock):
  while True:
    t = now()
    input_data = input(f'{t} >>>')

    sock.sendall(bytes(input_data, encoding='utf-8'))
    if input_data.strip() == 'q':
        break
    elif input_data.strip() == '':
        continue

    recv_data = sock.recv(1024)
    print(str(recv_data, encoding='utf-8'))

def tcping(sock, interval):
  seq = 1
  while True:
    #print('{} > tcping time {}'.format(now(), seq))
    t1 = time.time()
    sock.sendall(bytes('ping', encoding='utf-8'))
    recv_data = sock.recv(1024)
    t2= time.time()
    print('{} < tcping seq={} time={} data={}'.format(now(), seq, '{:f} ms'.format((t2-t1)*1000), str(recv_data, encoding='utf-8')))
    time.sleep(interval)
    seq += 1

sock = connect_remote()
if '-i' in sys.argv:
    tcping(sock, 0.2)
else:
    interactive_shell(sock)
