#!/usr/bin/env python3
# udp_chat.py - 支持多播发现的 UDP 聊天程序

import argparse
import socket
import sys
import threading
import signal
import json
import re
import time

# ==================== 配置 ====================
MULTICAST_GROUP = "224.0.0.1"
MULTICAST_PORT = 50000
DISCOVERY_INTERVAL = 3  # 每 3 秒广播一次
# =============================================

# 全局控制
running = True

# 已知用户映射
known_peers = {}  # nickname -> (ip, port)
peer_addresses = {}  # (ip, port) -> nickname

# 自己的信息
my_nick = None
sock = None
discovery_sock = None
local_addr = None  # 主通信地址

# 锁
peers_lock = threading.Lock()

# 正则：匹配 @ip:port
IP_PORT_PATTERN = re.compile(r'^@(\d+\.\d+\.\d+\.\d+):(\d+)(?:\s+(.*))?$')


def parse_address(addr_str, name="address"):
    try:
        host, port = addr_str.split(":")
        port = int(port)
        return host.strip(), port
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid {name} format 'IP:PORT': '{addr_str}'")


def send_message(target_addr, packet):
    """发送主通道消息"""
    try:
        payload = json.dumps(packet).encode('utf-8')
        sock.sendto(payload, target_addr)
    except Exception as e:
        print(f"\n❌ 无法发送到 {target_addr}: {e}", file=sys.stderr)


def broadcast_message(packet, exclude_addr=None):
    """广播给所有已知 peer"""
    with peers_lock:
        for addr in known_peers.values():
            if addr != exclude_addr:
                send_message(addr, packet)


def receive_loop():
    """主接收线程：处理聊天消息"""
    global running
    sock.settimeout(1.0)
    print(f"🟢 监听主通道 {sock.getsockname()}，等待消息...\n", file=sys.stderr)

    while running:
        try:
            data, addr = sock.recvfrom(65535)
            try:
                packet = json.loads(data.decode('utf-8'))
                sender_nick = packet.get("nick", f"{addr[0]}:{addr[1]}")
                content = packet.get("msg", "")
            except json.JSONDecodeError:
                sender_nick = f"{addr[0]}:{addr[1]}"
                content = data.decode('utf-8', errors='replace')

            # 学习 sender
            with peers_lock:
                old_nick = peer_addresses.get(addr)
                if old_nick != sender_nick:
                    if old_nick in known_peers and known_peers[old_nick] == addr:
                        del known_peers[old_nick]
                    known_peers[sender_nick] = addr
                    peer_addresses[addr] = sender_nick

            print(f"\r📩 [{sender_nick}@{addr[0]}:{addr[1]}] {content}\n{my_nick} >>> ", end="", flush=True)

        except socket.timeout:
            continue
        except Exception as e:
            if running:
                print(f"\n❌ 接收错误: {e}", file=sys.stderr)


def send_discovery_hello():
    """发送一条发现消息"""
    msg = {
        "type": "HELLO",
        "nick": my_nick,
        "address": local_addr  # 主通信地址
    }
    try:
        payload = json.dumps(msg).encode('utf-8')
        discovery_sock.sendto(payload, (MULTICAST_GROUP, MULTICAST_PORT))
    except Exception as e:
        print(f"\n⚠️ 多播发送失败: {e}", file=sys.stderr)


def discovery_receive_loop():
    """多播接收线程：发现局域网内其他用户"""
    global running
    print(f"🔍 开始监听多播发现 {MULTICAST_GROUP}:{MULTICAST_PORT}", file=sys.stderr)

    while running:
        try:
            data, addr = discovery_sock.recvfrom(1024)
            try:
                packet = json.loads(data.decode('utf-8'))
                if packet.get("type") == "HELLO":
                    sender_nick = packet["nick"]
                    main_addr = tuple(packet["address"])  # (ip, port)

                    # 忽略自己
                    if main_addr == local_addr:
                        continue

                    with peers_lock:
                        # 更新映射
                        old_nick = peer_addresses.get(main_addr)
                        if old_nick != sender_nick:
                            if old_nick in known_peers and known_peers[old_nick] == main_addr:
                                del known_peers[old_nick]
                            known_peers[sender_nick] = main_addr
                            peer_addresses[main_addr] = sender_nick
                            print(f"\n✅ 发现新用户: {sender_nick} @ {main_addr[0]}:{main_addr[1]}", file=sys.stderr)
            except (json.JSONDecodeError, KeyError) as e:
                continue
        except socket.timeout:
            continue
        except Exception as e:
            if running:
                print(f"\n❌ 多播接收错误: {e}", file=sys.stderr)


def discovery_broadcast_loop():
    """定期广播 HELLO 消息"""
    global running
    while running:
        send_discovery_hello()
        time.sleep(DISCOVERY_INTERVAL)


def show_known_users():
    """显示 /who 列表"""
    with peers_lock:
        if not known_peers:
            print("\n🔍 当前没有已知用户", file=sys.stderr)
        else:
            print("\n🔍 已知用户列表:", file=sys.stderr)
            for nick, addr in known_peers.items():
                print(f"   {nick} @ {addr[0]}:{addr[1]}", file=sys.stderr)
        print(f"{my_nick} >>> ", end="", flush=True)


def send_loop():
    """发送主循环"""
    global running
    print(f"🎯 当前昵称: {my_nick}", file=sys.stderr)
    print("💬 可用命令:\n"
          "  直接输入 -> 广播\n"
          "  @nick msg -> 发给昵称\n"
          "  @ip:port msg -> 发给任意地址\n"
          "  /who -> 查看已知用户\n"
          "  quit -> 退出\n", file=sys.stderr)

    while running:
        try:
            user_input = input(f"{my_nick} >>> ").strip()
            if not user_input:
                continue

            if user_input.lower() in ('quit', 'exit', 'bye'):
                running = False
                break
            elif user_input == "/who":
                show_known_users()
                continue

            packet = {"nick": my_nick, "msg": user_input}

            if user_input.startswith('@'):
                match = IP_PORT_PATTERN.match(user_input)
                if match:
                    ip, port, msg = match.group(1), int(match.group(2)), match.group(3) or ""
                    target_addr = (ip, port)
                    packet["msg"] = msg
                    send_message(target_addr, packet)
                    print(f"📤 发送给 {ip}:{port}: {msg}")
                else:
                    at_idx = user_input.find(' ')
                    if at_idx <= 1:
                        print("⚠️ 用法: @nickname message 或 @1.2.3.4:5678 message")
                        continue
                    target_nick = user_input[1:at_idx]
                    with peers_lock:
                        if target_nick not in known_peers:
                            print(f"❌ 未知昵称: {target_nick}")
                            continue
                        target_addr = known_peers[target_nick]
                    packet["msg"] = user_input[at_idx+1:]
                    send_message(target_addr, packet)
                    print(f"📤 发送给 {target_nick}: {packet['msg']}")
            else:
                broadcast_message(packet)
                print(f"📤 广播: {user_input}")

        except (EOFError, KeyboardInterrupt):
            running = False
            break
        except Exception as e:
            print(f"\n❌ 发送失败: {e}", file=sys.stderr)

    running = False


def signal_handler(signum, frame):
    global running
    if running:
        print("\n👋 正在退出...", file=sys.stderr)
        running = False


def main():
    global running, my_nick, sock, discovery_sock, local_addr

    parser = argparse.ArgumentParser(description="支持多播发现的 UDP 聊天程序")
    parser.add_argument("-b", "--bind", required=True, type=parse_address,
                        help="本地绑定地址: IP:PORT")
    parser.add_argument("--nick", type=str,
                        help="设置昵称（不设置则用 IP:PORT）")
    parser.add_argument("remote", nargs="*", type=parse_address,
                        help="初始远程地址（可选）")

    args = parser.parse_args()
    local_addr = args.bind

    # 创建主通信 socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(local_addr)
        print(f"🏠 主通道绑定: {local_addr[0]}:{local_addr[1]}", file=sys.stderr)
    except Exception as e:
        print(f"❌ 主通道绑定失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 设置自己的昵称
    if args.nick:
        my_nick = args.nick
    else:
        my_nick = f"{local_addr[0]}:{local_addr[1]}"

    # 创建多播 socket（发送和接收）
    discovery_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    discovery_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 允许端口重用（Linux）
    try:
        discovery_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass  # Windows 不支持

    # 绑定到多播端口
    discovery_sock.bind(('', MULTICAST_PORT))

    # 加入多播组
    group = socket.inet_aton(MULTICAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    discovery_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # 设置非阻塞
    discovery_sock.settimeout(1.0)

    # 添加初始 remote
    with peers_lock:
        for addr in args.remote:
            if addr == local_addr:
                continue
            nick = f"{addr[0]}:{addr[1]}"
            known_peers[nick] = addr
            peer_addresses[addr] = nick
            print(f"📌 添加初始目标: {nick}", file=sys.stderr)

    # 注册信号
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动线程
    threading.Thread(target=receive_loop, daemon=True).start()
    threading.Thread(target=discovery_receive_loop, daemon=True).start()
    threading.Thread(target=discovery_broadcast_loop, daemon=True).start()

    # 主发送循环
    send_loop()

    # 清理
    running = False
    sock.close()
    discovery_sock.close()
    print("\n👋 聊天结束。", file=sys.stderr)


if __name__ == "__main__":
    import struct  # 用于多播组管理
    main()
