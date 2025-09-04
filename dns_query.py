#!/usr/bin/env python3
import sys,socket
import struct
import random

def build_dns_query(domain, qtype=1):
    """
    构造 DNS 查询请求
    :param domain: 域名，如 "www.example.com"
    :param qtype: 查询类型，1=A记录, 28=AAAA, 15=MX 等
    :return: 二进制 DNS 查询包
    """
    # 1. Header Section (12 bytes)
    transaction_id = random.randint(0, 0xFFFF)  # 2字节 事务ID
    flags = 0x0100  # 标准查询；RD=1 (递归查询)
    qdcount = 1     # 问题数 = 1
    ancount = 0
    nscount = 0
    arcount = 0

    header = struct.pack('!HHHHHH',
                         transaction_id,  # ID
                         flags,           # FLAGS
                         qdcount,         # QDCOUNT
                         ancount,         # ANCOUNT
                         nscount,         # NSCOUNT
                         arcount          # ARCOUNT
                         )

    # 2. Question Section
    question = b""
    for label in domain.split('.'):
        question += bytes([len(label)]) + label.encode('utf-8')
    question += b'\x00'  # 结束符（根）

    # QTYPE (A=1, AAAA=28, MX=15)
    question += struct.pack('!H', qtype)
    # QCLASS (IN = 1)
    question += struct.pack('!H', 1)

    return header + question


def parse_dns_response(data):
    """
    简单解析 DNS 响应，提取 A 记录
    """
    if len(data) < 12:
        print("❌ 响应太短")
        return

    # 解析 Header
    header = struct.unpack('!HHHHHH', data[:12])
    tid, flags, qdcount, ancount, nscount, arcount = header

    print(f"事务ID: {tid}")
    print(f"响应标志: {hex(flags)}")
    print(f"回答记录数: {ancount}")

    # 检查是否成功
    rcode = flags & 0xF
    if rcode != 0:
        print(f"❌ DNS 错误码: {rcode}")
        return

    if ancount == 0:
        print("❌ 无回答记录")
        return

    # 跳过 Header 和 Question（我们不解析 Question）
    offset = 12

    # 跳过 Question 部分（QNAME 是变长的）
    while True:
        length = data[offset]
        offset += 1
        if length == 0 or offset >= len(data):
            break
        if length & 0xC0 == 0xC0:  # 压缩指针
            offset += 1
            break
        offset += length
    # 跳过 QTYPE 和 QCLASS
    offset += 4

    # 解析 Answer RRs
    answers = []
    for _ in range(ancount):
        if offset >= len(data):
            break

        # NAME: 可能是压缩指针
        if data[offset] & 0xC0 == 0xC0:
            offset += 2  # 跳过指针
        else:
            while data[offset] != 0:
                offset += 1
            offset += 1

        # TYPE (2), CLASS (2), TTL (4)
        if offset + 10 > len(data):
            break
        qtype, qclass, ttl, rdlength = struct.unpack('!HHIH', data[offset:offset+10])
        offset += 10

        if qtype == 1 and qclass == 1:  # A 记录
            if rdlength == 4:
                ip = socket.inet_ntoa(data[offset:offset+4])
                answers.append(ip)
                print(f"✅ A 记录: {ip}")
        offset += rdlength

    return answers


def send_dns_query(domain, dns_server="8.8.8.8", timeout=5):
    """
    发送 DNS 查询
    """
    query = build_dns_query(domain, qtype=1)  # A 记录

    # 创建 UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        print(f"📤 向 {dns_server}:53 发送 DNS 查询: {domain}")
        sock.sendto(query, (dns_server, 53))
        response, addr = sock.recvfrom(1024)
        print(f"📥 收到响应来自 {addr}")
        parse_dns_response(response)
    except socket.timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        sock.close()


# ======================
# 使用示例
# ======================
if __name__ == "__main__":
    domain = sys.argv[1]
    send_dns_query(domain)
