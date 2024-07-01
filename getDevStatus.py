#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
import socket
import struct
import select
import time

ICMP_ECHO_REQUEST = 8  # Platform specific
DEFAULT_TIMEOUT = 0.1
DEFAULT_COUNT = 4


class Pinger(object):
    """ Pings to a host -- the Pythonic way"""

    def __init__(self, target_host, count=DEFAULT_COUNT, timeout=DEFAULT_TIMEOUT):
        self.target_host = target_host
        self.count = count
        self.timeout = timeout

    def do_checksum(self, source_string):
        """  Verify the packet integritity """
        sum = 0
        max_count = (len(source_string) / 2) * 2
        count = 0
        while count < max_count:
            val = source_string[count + 1] * 256 + source_string[count]
            sum = sum + val
            sum = sum & 0xffffffff
            count = count + 2

        if max_count < len(source_string):
            sum = sum + ord(source_string[len(source_string) - 1])
            sum = sum & 0xffffffff

        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer

    def receive_pong(self, sock, ID, timeout):
        """
        Receive ping from the socket.
        """
        time_remaining = timeout
        while True:
            start_time = time.time()
            readable = select.select([sock], [], [], time_remaining)
            time_spent = (time.time() - start_time)
            if readable[0] == []:  # Timeout
                return

            time_received = time.time()
            recv_packet, addr = sock.recvfrom(1024)
            icmp_header = recv_packet[20:28]
            type, code, checksum, packet_ID, sequence = struct.unpack(
                "bbHHh", icmp_header
            )
            if packet_ID == ID:
                bytes_In_double = struct.calcsize("d")
                time_sent = struct.unpack("d", recv_packet[28:28 + bytes_In_double])[0]
                return time_received - time_sent

            time_remaining = time_remaining - time_spent
            if time_remaining <= 0:
                return

    def send_ping(self, sock, ID):
        """
        Send ping to the target host
        """
        target_addr = socket.gethostbyname(self.target_host)

        my_checksum = 0

        # Create a dummy heder with a 0 checksum.
        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
        bytes_In_double = struct.calcsize("d")
        data = (192 - bytes_In_double) * "Q"
        data = struct.pack("d", time.time()) + bytes(data.encode('utf-8'))

        # Get the checksum on the data and the dummy header.
        my_checksum = self.do_checksum(header + data)
        header = struct.pack(
            "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
        )
        packet = header + data
        sock.sendto(packet, (target_addr, 1))

    def ping_once(self):
        """
        Returns the delay (in seconds) or none on timeout.
        """
        icmp = socket.getprotobyname("icmp")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        except socket.error as e:
            if e.errno == 1:
                # Not superuser, so operation not permitted
                e.msg += "ICMP messages can only be sent from root user processes"
                raise socket.error(e.msg)
        except Exception as e:
            print("Exception: %s" % (e))

        my_ID = os.getpid() & 0xFFFF

        self.send_ping(sock, my_ID)
        delay = self.receive_pong(sock, my_ID, self.timeout)
        sock.close()
        return delay

    def ping(self):
        """
        Run the ping process
        """
        for i in range(self.count):
            print("Ping to %s..." % self.target_host, )
            try:
                delay = self.ping_once()
            except socket.gaierror as e:
                print("Ping failed. (socket error: '%s')" % e[1])
                break

            if delay == None:
                print("Ping failed. (timeout within %ssec.)" % self.timeout)
            else:
                delay = delay * 1000
                print("Get pong in %0.4fms" % delay)


def getRunStatus(equipment_list):
    for equipment_i in equipment_list:
        pinger = Pinger(target_host=equipment_i['equipment_ip'])
        delay = pinger.ping_once()
        if delay == None:
            equipment_i['online'] = 2
        else:
            equipment_i['online'] = 1
    return equipment_list


# if __name__ == '__main__':
    # alive = []
    # host_prefix = '192.168.14.'
    # for i in range(1, 255):
    #     host = host_prefix + str(i)
    #     pinger = Pinger(target_host=host)
    #
    #     delay = pinger.ping_once()
    #     if delay == None:
    #         print("Ping %s 失败，超时2秒" % host)
    #     else:
    #         print("ping %s = %s ms" % (host, round(delay * 1000, 4)))
    #         alive.append(host)
    #     # time.sleep(0.5)
    # print(alive)

    # ip_true = ['192.168.14.3', '192.168.14.4', '192.168.14.9', '192.168.14.10', '192.168.14.14',
    #            '192.168.14.16', '192.168.14.17', '192.168.14.18', '192.168.14.21', '192.168.14.24',
    #            '192.168.14.25', '192.168.14.26', '192.168.14.27', '192.168.14.28', '192.168.14.32',
    #            '192.168.14.33', '192.168.14.34', '192.168.14.35', '192.168.14.39', '192.168.14.45',
    #            '192.168.14.46', '192.168.14.57', '192.168.14.58', '192.168.14.69', '192.168.14.71',
    #            '192.168.14.72', '192.168.14.75', '192.168.14.76', '192.168.14.77', '192.168.14.78',
    #            '192.168.14.80', '192.168.14.82', '192.168.14.86', '192.168.14.87', '192.168.14.88',
    #            '192.168.14.90', '192.168.14.91', '192.168.14.92', '192.168.14.93', '192.168.14.94',
    #            '192.168.14.95', '192.168.14.96', '192.168.14.97', '192.168.14.98', '192.168.14.100',
    #            '192.168.14.102', '192.168.14.103', '192.168.14.104', '192.168.14.105', '192.168.14.106',
    #            '192.168.14.108', '192.168.14.165', '192.168.14.201', '192.168.14.216', '192.168.14.246',
    #            '192.168.14.254']
    #
    # for i in ip_true:
    #     pinger = Pinger(target_host=i)
    #     delay = pinger.ping_once()
    #     if delay == None:
    #         print("Ping %s 失败" % i,'---监控点离线')
    #     else:
    #         print("ping %s = %s ms" % (i, round(delay * 1000, 4)),'---监控点在线')

    # 定时任务请求设备，来返回状态