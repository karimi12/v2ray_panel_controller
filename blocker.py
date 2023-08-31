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
    "s": "https://spanel.karimiblog.ir",
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

    print("clear log")
    os.system("> /etc/v2ray-agent/xray/access.log ")
    time.sleep(180)
    os.system("> /root/v2ray_manager/access.log && cat /etc/v2ray-agent/xray/access.log > /root/v2ray_manager/access.log ")
    with open("/root/v2ray_manager/access.log") as f:
        aa = f.readlines()
        for a in aa:
            a = a.split(" ")
            if len(a) == 10 and a[-2] == "email:":
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
                        c = user_id_device_server.split("_")
                        if len(c) == 3 and len(COUNTER[user_id_device_server]) > int(c[1])+2:
                            BLOCK_LIST.add(user_id_device_server)

    send_block_user()
    print("end")


if __name__ == '__main__':
    main()
