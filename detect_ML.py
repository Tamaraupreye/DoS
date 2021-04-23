import os
import subprocess
import time
import threading

from joblib import dump, load


FAIL = '\033[91m'
RESET = '\033[0m'

PI_IP = "192.168.1.192"

SYNFLOOD_DETECTION_THRESHOLD = 0.7
ICMPFLOOD_DETECTION_THRESHOLD = 12000
DNSAMP_DETECTION_THRESHOLD = 0.1

TSHARK_DURATION = 15
CAPTURE_COMMAND = f"tshark -f 'tcp or icmp or src port 53 or dst port 53' -a duration:{TSHARK_DURATION} -T fields -e " \
                  f"frame.time_epoch -e frame.protocols -e ip.src -e ip.dst -e tcp.flags.syn -e tcp.flags.ack -E " \
                  f"separator=, "


def is_tcp(line):
    t, pr, src, dst, syn, ack = line
    return "tcp" in pr


def is_syn(line):
    t, pr, src, dst, syn, ack = line
    return is_tcp(line) and bool(int(syn))


def is_ack(line):
    t, pr, src, dst, syn, ack = line
    return is_tcp(line) and bool(int(ack))


def is_icmp(line):
    t, pr, src, dst, syn, ack = line
    return "icmp" in pr


def is_outgoing_dns(line):
    t, pr, src, dst, syn, ack = line
    return "dns" in pr and src == PI_IP


def is_incoming_dns(line):
    t, pr, src, dst, syn, ack = line
    return "dns" in pr and dst == PI_IP


def analyse_packets(capture, ml):
    ack = 0
    syn = 0
    incoming_dns = 0
    outgoing_dns = 1
    icmp = 0

    for line in capture:
        line = line.split(",")
        if len(line) == 8:
            line = line[0:4] + line[6:]

        ack += int(is_ack(line))
        syn += int(is_syn(line))

        incoming_dns += int(is_incoming_dns(line))
        outgoing_dns += int(is_outgoing_dns(line))

        icmp += int(is_icmp(line))

    # check for attack
    try:
        syn_ack_ratio = syn/ack
    except ZeroDivisionError:
        syn_ack_ratio = -1

    try:
        dns_ratio = outgoing_dns/incoming_dns
    except ZeroDivisionError:
        dns_ratio = -1

    classification = ml.predict([[syn_ack_ratio, icmp, dns_ratio]])[0]
    if classification == 1:
        return 1
    return 0
    # elif classification == 2:
    #     print(f"{FAIL}ICMP flood detected{RESET}")
    # elif classification == 3:
    #     print(f"{FAIL}DNS amplification detected{RESET}")


if __name__ == "__main__":
    ml = load("model.model")
    cmd = CAPTURE_COMMAND.split("'")
    cmd = cmd[0].strip(" ").split(" ") + [cmd[1]] + cmd[2].strip(" ").split(" ")
    was_synflood = False
    while True:
        with open(os.path.expanduser(os.path.join("~", "capture.txt")), 'w') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL)
        with open(os.path.expanduser(os.path.join("~", "capture.txt")), 'r') as f:
            synflood = analyse_packets(f.readlines(), ml)
            if int(synflood):
                print(f"{FAIL}SYN flood detected{RESET}")
                if not was_synflood:
                    print(f"Countermeasure: Increasing backlog to 8192")
                was_synflood = True
            else:
                print(f"Nothing happening")
                if was_synflood:
                    print(f"Reducing backlog back to 128")
                was_synflood = False
