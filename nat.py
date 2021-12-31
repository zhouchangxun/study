import threading
import time
import queue


class Entity(threading.Thread):
    def __init__(self, interval):
        threading.Thread.__init__(self)
        self.interval = interval
        self.thread_stop = False

    def run(self):
        i = 1
        while not self.thread_stop:
            print("thread%d %s: i am alive hehe %d" % (self.ident, self.name, i))
            time.sleep(self.interval)
            i = i+1

    def stop(self):
        self.thread_stop = True


class NATDevice(threading.Thread):
    def __init__(self, name=None):
        threading.Thread.__init__(self, name=name)
        self.thread_stop = False
        self.pmd_interval = 1
        self.snat_sessions = [('192.168.1.10', 10001, '8.8.8.1', 80, '123.123.1.1', 20001)]
        self.snat_rules = []
        self.nic_recv_queue = queue.Queue(10)
        self.nic_send_queue = queue.Queue(10)

    def link_add(self, client):
        client.nic_send_queue = self.nic_recv_queue

    def recv_pkt(self, pkt):
        print(f'\n[{self.name}] recv a pkt, data=[{pkt}]')

    def send_pkt(self, pkt):
        print('send pkt: {}'.format(pkt))

    def load_cfg(self, rules):
        self.snat_rules = rules

    def show_snat_rules(self):
        print('snat rules:')
        print('-' * 40)
        print('{:20}, external_ip'.format('cidr'))
        for rule in self.snat_rules:
            print('{:20}, {}'.format(rule[0], rule[1]))
        print('-' * 40)

    def show_sessions(self):
        print('snat sessions:')
        print('-' * 40)
        print('{:20}, {:10}, {:20}, {:10}, {:20}, {:10}'
              .format('src-ip', 'src-port', 'dst-ip', 'dst-port', 'nat-ip', 'nat-port'))
        for item in self.snat_sessions:
            print('{:20}, {:<10}, {:20}, {:<10}, {:20}, {:<10}'
                  .format(*item))
        print('-' * 40)

    def stop(self):
        self.thread_stop = True

    def run(self):
        i = 1
        while not self.thread_stop:
            if not self.nic_recv_queue.empty():
                self.recv_pkt(self.nic_recv_queue.get())
            else:
                print('.')
                time.sleep(self.pmd_interval)
            i = i+1
        print(f'{self.name}: power off\n')


class Client(threading.Thread):
    def __init__(self, ip, mac, name=None):
        threading.Thread.__init__(self, name=name)
        self.nic = dict(ip=ip, mac=mac)
        self.nic_send_queue = None
        self.interval = 1
        self.thread_stop = False

    def run(self):
        i = 1
        while not self.thread_stop:
            time.sleep(self.interval)
            i = i+1
        print(f'{self.name}: power off\n')

    def stop(self):
        self.thread_stop = True

    def recv_pkt(self, pkt):
        print(f'[{self.nic["ip"]}] recv pkt {pkt}')

    def send_pkt(self, pkt):
        print(f'[{self.name}]: send pkt: {pkt}')
        self.nic_send_queue.put(f'{self.nic}|{pkt}')

    def info(self):
        print(f'{self.nic}')

    def power_on(self):
        self.start()


if __name__ == '__main__':
    snat_rules = [
        ('192.168.0.0/24', '123.123.1.1'),
        ('10.0.0.0/24', '123.123.1.2')
    ]
    nat_device = NATDevice(name='nat-gateway')
    nat_device.load_cfg(snat_rules)
    nat_device.start()
    nat_device.show_snat_rules()
    nat_device.show_sessions()

    client1 = Client('192.168.1.6', 'fa:16:00:00:00:01', name='client1')
    nat_device.link_add(client1)
    client1.power_on()
    client1.info()
    time.sleep(2)
    client1.send_pkt('hi')
    time.sleep(2)
    client1.stop()
    nat_device.stop()
    time.sleep(2)
