import configparser
import socket
import threading
import time

from DOSHelper import *
from TCPClient import send_packet

config = configparser.ConfigParser()
config.read('DOSHelperConfig.ini')

CAPTURE_FILE = "capture.txt"
PI_IP = config["pi"]["IP"]

NUM_CLIENTS = 4
NUM_TESTS = 5
TIME_BETWEEN_TESTS = 100
done = False
failed = False
TOO_LONG = 15  # in minutes
BREAK_BETWEEN_RUNS = 6  # in minutes


def normal_client_loop():
    global failed
    global done
    while not done:
        try:
            send_packet()
        except (ConnectionError, socket.timeout) as e:
            failed = True
            done = True
            break


def process_capture():
    cap_file = os.path.join(os.getcwd(), CAPTURE_FILE)
    count = 0
    start_found = False
    start_time = 0
    end_time = 0
    with open(cap_file, "r") as f:
        all_info = f.readlines()[:-1]
        for line in all_info:
            t, ip, syn = line.split(",")
            if int(syn) and ip == PI_IP:
                count += 1
                if not start_found:
                    start_time = float(t)
                    start_found = True
                else:
                    end_time = float(t)

    if end_time - start_time == 0:
        return -1

    return count/(end_time - start_time)


def test():
    global failed
    global done
    done = False
    failed = False
    time_taken = -1

    start_pi_server()

    client_threads = []
    for _ in range(NUM_CLIENTS):
        client_threads.append(threading.Thread(target=normal_client_loop))

    for thread in client_threads:
        thread.start()

    start_packet_capture("kali", f"tshark -f tcp -T fields -e frame.time_epoch -e ip.dst -e tcp.flags.syn -E "
                                 f"separator=, > {CAPTURE_FILE}")

    start_synflood()

    start = time.time()

    while not failed and time.time() - start < TOO_LONG * 60:
        pass

    if failed:
        time_taken = time.time() - start

    kill_synflood()

    for thread in client_threads:
        done = True
        thread.join()

    kill_packet_capture("kali")

    kill_pi_server()

    return time_taken


def run_test_multiple(n):
    for _ in range(n):
        t = test()
        if t == -1:
            print(f"Nothing happened after {TOO_LONG} seconds")
        else:
            print(f"Took {t} seconds to have error")
        attack_strength = process_capture()
        print(f"Normalized: {t * attack_strength/2000}")
        time.sleep(BREAK_BETWEEN_RUNS * 60)


if __name__ == "__main__":
    val = ""
    while val != "q":
        reset_all_measures()
        val = input("Parameters to try (q to quit): ")
        exec(f"change_{val.split(':')[0]}({val.split(':')[1]})")
        run_test_multiple(3)

    # reset_all_measures()
    #
    # backlog = 128
    # while backlog < 33000:
    #     change_backlog(backlog)
    #     print(f"Current backlog: {backlog}")
    #     run_test_multiple(3)
    #     print("\n\n")
    #     backlog *= 2
    #
    # reset_all_measures()
    #
    # for timer in [5, 4, 3, 2, 1, 0]:
    #     change_timer(timer)
    #     print(f"Current timer: {timer}")
    #     run_test_multiple(3)
    #     print("\n\n")
    #
    # reset_all_measures()
    #
    # for cookies in [0, 1, 2]:
    #     change_cookies(cookies)
    #     print(f"Current cookies: {cookies}")
    #     run_test_multiple(3)
    #     print("\n\n")
    #
    # reset_all_measures()
