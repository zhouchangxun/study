#coding: utf-8
import json
import socket
import select

def server_loop():
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建一个套接字对象
    ipaddr = ('127.0.0.1', 9998)  # ip 和端口号
    sk.bind(ipaddr)   # 绑定
    sk.listen(5)   # 监听
    print('start listener {}'.format(ipaddr))

    inputs = [sk, ]  # io 多路复用
    outputs = []  # 存放要输出的I/O
    massages = {}  # 存放读入的消息
    while True:
        rlist, wlist, erro = select.select(inputs, outputs, [], 1)  # 使用select 监听IO对象

        for r in rlist:
            if r == sk:
                conn, addr = r.accept()
                print('new connection from {}'.format(addr))
                conn.sendall(b'hello boy!')
                inputs.append(conn)
                massages[conn] = []
            else:  # read
                try:
                    data = r.recv(1024).decode(encoding='utf-8')
                    if not data:
                        print('disconnect from {}'.format(r.getpeername()))
                        raise Exception('disconnect')
                except Exception as e: # 异常处理，防止客户端突然断开然后 程序保存崩溃
                    inputs.remove(r)
                    del massages[r]
                    continue

                print('recv from {}: [{}]'.format(r.getpeername(), data))
                if data.strip() == 'q':
                    r.close()
                    inputs.remove(r)
                    del massages[r]
                    continue
                elif data.strip() == 'who':
                    data = json.dumps(['{}:{}'.format(*conn.getpeername()) for conn in inputs if conn != sk], indent=2)
                outputs.append(r)
                massages[conn].append(data)

        for w in wlist:  # write
            msg = massages[w].pop()
            buf = ('response:'+msg).encode(encoding='utf-8')
            print('send to   {}: [{}]'.format(w.getpeername(), buf))
            w.sendall(buf)
            outputs.remove(w)

server_loop()
