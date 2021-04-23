import configparser
import os
import threading
import time

import matplotlib.pyplot as plt

from DOSHelper import *
from TCPClient import send_packet

config = configparser.ConfigParser()
config.read('DOSHelperConfig.ini')

FIG_NAME = "gg.png"
MEM_FREE_FILE = "mem_free.txt"
CAPTURE_FILE = "capture.txt"
PI_IP = config["pi"]["IP"]

CAPTURE_CMD = f"tshark -i eth0 -f tcp -T fields -e frame.time_epoch -e ip.src -e ip.dst -E separator=, > {CAPTURE_FILE}"

RUN_TIME = 1800


def process_capture_file():
    cap_file = os.path.join(os.getcwd(), CAPTURE_FILE)
    with open(cap_file, "r") as f:
        all_info = [l.strip().split(",") for l in f.readlines()[:-1] if l.strip().split(",")[2] == PI_IP]
        synflood_packets = [[packet[1], packet[2]] for packet in all_info]
        t_packets_arr = [float(packet[0]) for packet in all_info]
    return synflood_packets, t_packets_arr


def process_mem_file():
    mem_file = os.path.join(os.getcwd(), MEM_FREE_FILE)
    mem_arr = []
    t_arr = []
    with open(mem_file, "r") as f:
        for line in f.readlines()[:-1]:
            t, mem = line.split(",")
            mem_arr.append(float(mem)/1000)
            t_arr.append(float(t.strip()))
    return mem_arr, t_arr


def normal_client_loop(t_sent_arr, rtt_arr):
    start = time.time()
    while time.time() - start < RUN_TIME:
        try:
            sent = time.time()
            rtt_arr.append(send_packet())
            t_sent_arr.append(sent)
        except Exception as e:
            print(e)
            break


if __name__ == "__main__":
    pi_mem_pid = start_pi_mem_loop()

    start_pi_server()

    t_sent_arr = []
    rtt_arr = []
    client_thread = threading.Thread(target=normal_client_loop, args=(t_sent_arr, rtt_arr))
    client_thread.start()

    start_packet_capture("kali", CAPTURE_CMD)
    start_synflood()

    client_thread.join()

    kill_synflood()
    kill_packet_capture("kali")

    kill_pi_server()

    kill_pi_mem_loop(pi_mem_pid)

    synflood_packets, t_packets_arr = process_capture_file()
    mem_arr, t_arr = process_mem_file()

    min_time = min(min(t_packets_arr), min(t_arr), min(t_sent_arr))
    max_time = max(max(t_packets_arr), max(t_arr), max(t_sent_arr))

    plt.style.use('dark_background')
    plt.figure(figsize=(14, 7))

    plt.subplot(311)
    plt.xlim((0, max_time - min_time))
    plt.plot([t - min_time for t in t_arr], mem_arr)
    plt.ylabel("Pi Mem Used (kB)")

    plt.subplot(312)
    plt.xlim((0, max_time - min_time))
    plt.plot([t - min_time for t in t_sent_arr], rtt_arr)
    plt.ylabel("Response Time (s)")

    plt.subplot(313)
    plt.xlim((0, max_time - min_time))
    plt.plot([t - min_time for t in t_packets_arr], [i for i in range(1, len(t_packets_arr)+1)])
    plt.ylabel("Synflood Packets")

    plt.xlabel("Time")

    plt.savefig(FIG_NAME)

    plt.figure(figsize=(14, 7))

    plt.hist(rtt_arr, bins=1200, density=True)
    plt.ylabel("Response Time Histogram (s)")

    plt.savefig("hist.png")
