import os
import subprocess


PI_IP = "192.168.1.192"

TSHARK_DURATION = 15
CAPTURE_COMMAND = f"tshark -f 'tcp or icmp or src port 53 or dst port 53' -a duration:{TSHARK_DURATION} -T fields -e " \
                  f"frame.time_epoch -e frame.protocols -e ip.src -e ip.dst -e tcp.flags.syn -e tcp.flags.ack -E " \
                  f"separator=, "
DETECT_FILE = "detect_data.csv"
CAPTURE_FILE = "capture.txt"


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
    syn = 1
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
    with open(os.path.expanduser(os.path.join("~", DETECT_FILE)), 'a+') as f:
        try:
            f.write(f"{syn/ack},")
        except ZeroDivisionError:
            f.write("-1,")

        # check for icmpflood
        f.write(f"{icmp},")

        # check for dns amp attack
        try:
            f.write(f"{outgoing_dns/incoming_dns},")
        except ZeroDivisionError:
            f.write("-1,")

        if "synflood" in os.listdir():
            f.write("1")
        elif "icmpflood" in os.listdir():
            f.write("2")
        elif "dns_amp" in os.listdir():
            f.write("3")
        else:
            f.write("0")
        f.write("\n")


if __name__ == "__main__":
    cmd = CAPTURE_COMMAND.split("'")
    cmd = cmd[0].strip(" ").split(" ") + [cmd[1]] + cmd[2].strip(" ").split(" ")
    with open(os.path.expanduser(os.path.join("~", DETECT_FILE)), 'w') as data:
        data.write("SYN-ACK_Ratio,ICMP_Count,DNS_Ratio,Attack\n")
    while True:
        with open(os.path.expanduser(os.path.join("~", CAPTURE_FILE)), 'w') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL)
        with open(os.path.expanduser(os.path.join("~", CAPTURE_FILE)), 'r') as f:
            analyse_packets(f.readlines())
