import os
import subprocess

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


def analyse_packets(capture):
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

    # check for synflood
    try:
        if syn/ack > SYNFLOOD_DETECTION_THRESHOLD:
            print(f"{FAIL}Synflood detected{RESET}", end=" ")
        else:
            print(f"SYN/ACK ratio: {syn/ack}", end=" ")
    except ZeroDivisionError:
        print("SYN/ACK ratio: N/A", end=" ")

    # check for icmpflood
    if icmp > ICMPFLOOD_DETECTION_THRESHOLD:
        print(f"{FAIL}ICMP flood detected{RESET}", end=" ")
    else:
        print(f"ICMP count: {icmp}", end=" ")

    # check for dns amp attack
    try:
        if outgoing_dns/incoming_dns < DNSAMP_DETECTION_THRESHOLD:
            print(f"{FAIL}DNS amplification detected{RESET}")
        else:
            print(f"Outgoing/Incoming DNS ratio: {outgoing_dns/incoming_dns}")
    except ZeroDivisionError:
        print("Outgoing/Incoming DNS ratio: N/A")


if __name__ == "__main__":
    cmd = CAPTURE_COMMAND.split("'")
    cmd = cmd[0].strip(" ").split(" ") + [cmd[1]] + cmd[2].strip(" ").split(" ")
    while True:
        with open(os.path.expanduser(os.path.join("~", "capture.txt")), 'w') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL)
        with open(os.path.expanduser(os.path.join("~", "capture.txt")), 'r') as f:
            analyse_packets(f.readlines())
