import requests
import logging
import os
import time
import json
import log
import socket
SERVER_ID = 1

BLOCK_LIST = set()

REPORT_SERVERS = {
    "y": "https://npanel4.karimiblog.ir",
    # "s": "https://spanel.karimiblog.ir",
}

COUNTER = {}

HOSTNAME = socket.gethostname()


def send_block_user():
    global BLOCK_LIST
    global COUNTER

    # logging.info("send block list: {}".format(len(BLOCK_LIST)))
    # print ("Block list:")
    # print (BLOCK_LIST)
    print("*******************")
    for i in BLOCK_LIST:
        c = i.split('_')
        r = COUNTER[i]
        print(i+"  --> "+", ".join(r), end=" --> ")
        j = requests.get(
            REPORT_SERVERS[c[2]]+"/shadow/report/{}?id={}&ips={}".format(SERVER_ID, i, ",".join(r)))
        print(str(j.status_code)+"  "+j.text)
        log.logger.info("block user", extra={
                        "hostname": HOSTNAME, "id_device_server": i, "ips": r})


def main():
    global BLOCK_LIST
    global COUNTER
    COUNTER = {}
    BLOCK_LIST.clear()

    current_working_directory = os.getcwd()
    # log_file= "access.log"
    log_file= "/usr/local/x-ui/access.log"

    print("clear log")
    os.system(f"> {log_file} ")
    time.sleep(180)
    os.system(f"> {current_working_directory}/access.log && cat {log_file} > {current_working_directory}/access.log ")
    with open(f"{current_working_directory}/access.log") as f:
        aa = f.readlines()
        for a in aa:
            a = a.split(" ")


            if  a[-2] == "email:":
                user_id_device_server = a[-1].strip()
                user_ip = "_".join(a[2].split(":")[0:-1])
                if COUNTER.get(user_id_device_server) == None:
                    if not ("127.0.0.1" in user_ip or "tcp" in user_ip):
                        COUNTER[user_id_device_server] = [user_ip]
                    # print("counter: ", end="")
                    # print(COUNTER)
                else:
                    if not ("127.0.0.1" in user_ip or "tcp" in user_ip) and not (user_ip in COUNTER[user_id_device_server]):
                        COUNTER[user_id_device_server] .append(user_ip)
                        
                        if  len(COUNTER[user_id_device_server]) > 6:
                            BLOCK_LIST.add(user_id_device_server)

    send_block_user()
    print("end")


if __name__ == '__main__':
    main()
