from random import shuffle, randint
import re as regex
import ipaddress

class Anonymizer:
    def __init__(self, hosts_pool, other_pool):
        self.hpool = hosts_pool
        self.opool = other_pool
        self.map = {}
        shuffle(self.hpool)

    def add_host(self, original):
        new_addr = self.hpool.pop()
        self.map[original] = {'new' : new_addr, 'omap' : {}, 'pool' : [x for x in self.opool]}
        shuffle(self.map[original]['pool'])
        return new_addr

    def anonimize(self, packet, original):
        try : hostmap = self.map[original]
        except IndexError: raise ValueError('The host must be added before trying to anonimize')

        if packet.ip_src == original:
            packet.ip_src = hostmap['new']
            try : packet.ip_dst = hostmap['omap'][packet.ip_dst]
            except KeyError: # The other_host has not been seen for this host
                other = hostmap['pool'].pop()
                hostmap['omap'][packet.ip_dst] = other
                packet.ip_dst = other

        elif packet.ip_dst == original:
            packet.ip_dst = hostmap['new']
            try : packet.ip_src = hostmap['omap'][packet.ip_src]
            except KeyError: # The other_host has not been seen for this host
                other = hostmap['pool'].pop()
                hostmap['omap'][packet.ip_src] = other
                packet.ip_src = other

        #return packet (packet is modified by reference)

class IpAnonymizer:
    def __init__(self, anonimize_private = False):
        self.map = {}
        self.anon_private = anonimize_private

    @staticmethod
    def generate_ip():
        new_addr = '.'.join([str(randint(1, 254)) for x in range(4)])
        ip_addr = ipaddress.ip_address(new_addr)
        while ip_addr.is_private or ip_addr.is_multicast or ip_addr.is_link_local:
            new_addr = '.'.join([str(randint(1, 254)) for x in range(4)])
            ip_addr = ipaddress.ip_address(new_addr)

        return new_addr

    def anonimize(self, addr):
        ipaddr = ipaddress.ip_address(addr)

        if ipaddr.is_multicast or ipaddr.is_link_local:
            return addr
        if self.anon_private == False and ipaddr.is_private:
            return addr

        if addr in self.map:
            return self.map[addr]


        new_addr = IpAnonymizer.generate_ip()
        while new_addr in self.map.values():
            new_addr = IpAnonymizer.generate_ip()

        self.map[addr] = new_addr
        return new_addr
