import random
import socket
import string
import threading
import time

from DOSHelper import *
from TCPClient import send_packet

GATHER_PI_SCRIPT = "gather_Pi.py"
DETECT_FILE = "detect_data.csv"
ATTACK_LIST = ["synflood", "icmpflood", "dns_amp"]
WEBSITE_LIST = ["https://www.google.com/", "https://www.youtube.com/watch?v=ihS8__strtM", "https://www.apple.com/"]
TEST_DURATION = 3  # in hours
ATTACK_DURATION_MIN = 5  # in minutes
ATTACK_DURATION_MAX = 10  # in minutes
TIME_FOR_ATTACK_TO_DIE = 15  # in seconds
NO_ATTACK_DURATION_MIN = 5  # in minutes
NO_ATTACK_DURATION_MAX = 10  # in minutes
PING_ATTEMPTS_MIN = 200
PING_ATTEMPTS_MAX = 1000
STRING_LEN_MIN = 50
STRING_LEN_MAX = 200
RANDOM_SLEEP_TIME_MIN = 1  # in seconds
RANDOM_SLEEP_TIME_MAX = 6  # in seconds
SERVER_RESTART_TIME = 60  # in seconds
CLIENT_LOOP_DURATION = 25  # in minutes
NO_CLIENT_LOOP_DURATION = 8  # in minutes
ALL_CHARS = string.ascii_letters + string.digits + string.punctuation


def normal_client_loop():
    # loop to randomly send random messages to the server for random periods
    while not done:
        if random.randint(0, 1) == 1:
            s = time.time()
            start_pi_server()
            while time.time() - s < CLIENT_LOOP_DURATION * 60:
                try:
                    if random.randint(0, 9) > 0:
                        lst = [random.choice(ALL_CHARS) for _ in range(random.randint(STRING_LEN_MIN, STRING_LEN_MAX))]
                        random_string = "".join(lst)
                        send_packet(random_string.encode('utf-8'))
                        time.sleep(random.randint(RANDOM_SLEEP_TIME_MIN, RANDOM_SLEEP_TIME_MAX))
                except (ConnectionError, socket.timeout) as e:
                    time.sleep(SERVER_RESTART_TIME)  # wait before restarting server
                    start_pi_server()
            kill_pi_server()
        else:
            time.sleep(NO_CLIENT_LOOP_DURATION * 60)


def random_traffic_loop():
    # loop to randomly generate network traffic by accessing random websites on the pi
    global done
    while not done:
        if random.randint(0, 5) > 1:
            website = random.choice(WEBSITE_LIST)
            run_cmd("pi", f"host {website}")
            run_cmd("pi", f"curl {website}")
            run_cmd("pi", f"ping -c {random.randint(PING_ATTEMPTS_MIN, PING_ATTEMPTS_MAX)} {website.split('/')[2]}")
        time.sleep(random.randint(RANDOM_SLEEP_TIME_MIN, RANDOM_SLEEP_TIME_MAX))


if __name__ == "__main__":
    # start the python data gathering script on Pi, randomly launch attacks for test_duration, get csv file at the end
    put_file("pi", GATHER_PI_SCRIPT)
    run_cmd("pi", f"python3 {GATHER_PI_SCRIPT}")

    done = False

    t1 = threading.Thread(target=random_traffic_loop)
    t2 = threading.Thread(target=normal_client_loop)

    t1.start()
    t2.start()

    start = time.time()
    while time.time() - start < TEST_DURATION * 60 * 60:
        if random.randint(0, 3) != 0:
            attack = random.choice(ATTACK_LIST)
            run_cmd("pi", f"touch {attack}")
            exec(f"start_{attack}()")
            time.sleep(random.randint(ATTACK_DURATION_MIN * 60, ATTACK_DURATION_MAX * 60))
            exec(f"kill_{attack}()")
            time.sleep(TIME_FOR_ATTACK_TO_DIE)
            run_cmd("pi", f"rm {attack}")
        else:
            time.sleep(random.randint(NO_ATTACK_DURATION_MIN * 60, NO_ATTACK_DURATION_MAX * 60))

    done = True
    t1.join()
    t2.join()

    run_cmd("pi", f"pkill -f {GATHER_PI_SCRIPT}")
    get_file("pi", DETECT_FILE)
