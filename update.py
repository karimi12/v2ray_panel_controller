
import requests
import json
import time
import threading
import logging
import os
import time
import random
import argparse
import datetime
import shutil
import argparse
import math


PANEL_IP = "http://185.126.3.104:9090"
PANEL_TAG = "test"
INBOUNDS_ID=[1]
print("Server IP:{}\nTag: {}".format(PANEL_IP, PANEL_TAG))


MAIN_SERVER_GROUPE = 'y'
# MAIN_SERVER_GROUPE='s'
MAIN_SERVER = {
    "y": "https://npanel4.karimiblog.ir",
    # "s": "https://spanel.karimiblog.ir",
}
SERVER_ID = {
    "y": list(range(20, 34)),
    # "s": list(range(20,50)),
}


cookies = {
    # 'lang': 'en-US',
    # 'ab.storage.deviceId.a9882122-ac6c-486a-bc3b-fab39ef624c5': '%7B%22g%22%3A%22a6acc7e9-0519-59b9-7905-2fb53c7e8680%22%2C%22c%22%3A1684596144193%2C%22l%22%3A1684596144193%7D',
    # 'session': 'MTY4NDYwMDU1NHxEdi1CQkFFQ180SUFBUkFCRUFBQWRmLUNBQUVHYzNSeWFXNW5EQXdBQ2t4UFIwbE9YMVZUUlZJWWVDMTFhUzlrWVhSaFltRnpaUzl0YjJSbGJDNVZjMlZ5XzRNREFRRUVWWE5sY2dIX2hBQUJCQUVDU1dRQkJBQUJDRlZ6WlhKdVlXMWxBUXdBQVFoUVlYTnpkMjl5WkFFTUFBRUxURzluYVc1VFpXTnlaWFFCREFBQUFCcl9oQmNCQWdFSWVXRnpaWEl4TWpNQkNIbGhjMlZ5TVRJekFBPT18KdMD40mJ8fLhtpP3bA_Z7Tnl9cGj241NBJBANucTmVA=',
}
requests.packages.urllib3.disable_warnings()


def login():
    global cookies
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    payload = 'username=asghar123&password=asghar123'
    response = requests.request(
        "POST", "{}/login".format(PANEL_IP), headers=headers, data=payload, verify=False)
    print(response.text)
    print(response.cookies.get_dict())
    cookies = response.cookies.get_dict()


def transform(secrets, k):
    """
    transfer a list of secrets to a list of email and id 
    id -> shadow password

    email -> id_device_server
    """
    ss = []
   
    for ts in secrets:

        tt = {}
        tt["email"] = str(ts["id"])+"_"+k
        tt["id"] = ts["shadow_password"]
        tt["panel_id"] = ts["id"]
        tt["total"] = (ts.get("total_quota_limit", 0) -
                       ts.get("used_total_quota", 0)) * 1024*1024
        tt["device"] = ts.get("device", 0)
        tt["enable"] = True
        if (ts.get("deactivate", 0) != 0):
            tt["enable"] = False

        tt["expiry_time"] = 0
        # print(ts.get("end_date", None))
        try:
            if ts.get("end_date", None) != None:
                date_object = datetime.datetime.strptime(
                    ts["end_date"], "%Y-%m-%d %H:%M:%S")
                tt["expiry_time"] = int(date_object.timestamp()*1000)
        except Exception as e:
            print(e)

        ss.append(tt)
    return ss


def get_secrets():
    logging.info("start get_secrets ")
    secrets = []
    for k in MAIN_SERVER:
        sid = [str(item) for item in SERVER_ID[k]]
        sid = ",".join(sid)
        try:
            logging.info("get secrets panel: %s server_id: %s".format(k, sid))
            j = requests.get(
                MAIN_SERVER[k]+"/api/shadow/config/temp?servers="+sid).json()
            # MAIN_SERVER[k]+"/shadow/keys/"+str(sid)).json()
            secrets = secrets + transform(j, k)

        except Exception as e:
            logging.error(e)
    return secrets


def add_user(inbound_id, user):

    c = {
        "clients": [
            {
                "id": user["id"],
                "flow": "",
                "email": user["email"],
                "limitIp":user["device"],
                "totalGB":user["total"],
                "enable": user["enable"],
                "expiryTime": user["expiry_time"]
            }
        ]
    }
    data = {
        'id': str(inbound_id),
        'settings': json.dumps(c)
    }
    response = requests.post(
        '{}/panel/inbound/addClient'.format(PANEL_IP), cookies=cookies, data=data, verify=False)
    print(response.text)


def update_user(inbound_id, user_panel, user_server):

    # print("update user: "+str(user_panel))

    c = {
        "clients": [
            {
                "id": user_server["id"],
                "flow": "",
                "email": user_server["email"],
                "limitIp":user_server["device"],
                "totalGB":user_server["total"],
                "enable": user_server["enable"],
                "expiryTime": user_server["expiry_time"]
            }
        ]
    }

    data = {
        'id': str(inbound_id),
        'settings': json.dumps(c)
    }

    response = requests.post(
        '{}/panel/inbound/updateClient/{}'.format(PANEL_IP, user_panel["id"]),
        cookies=cookies,
        data=data,
        verify=False,
    )
    print(response.text)


def get_user_list_from_panel():

    response = requests.post(
        '{}/panel/inbound/list'.format(PANEL_IP), cookies=cookies, verify=False)
    j = response .json()
    return j.get("obj")[0]["clientStats"], json.loads(j.get("obj")[0]["settings"])["clients"]


def del_user(inbound_id, user):

    print("delete: "+str(user))
    response = requests.post(
        '{}/panel/inbound/{}/delClient/{}'.format(
            PANEL_IP, inbound_id, user["id"]),
        cookies=cookies,
        verify=False,
    )
    print("delete: "+response.text)


def update_user_trrafic(inbound_id, user):

    t = True
    s_id = user["email"].split("_")[-1]
    while t:
        try:
            j = requests.get("{}/api/shadow/traffic?id={}&server_tag={}&total={}".format(
                MAIN_SERVER[s_id], user["email"], PANEL_TAG+"_"+str(inbound_id), (user["up"]+user["down"])/(1024*1024)))
            print(j.text)
            if (j.status_code):
                t = False
                return True
            print("error in update")
            time.sleep(5)
        except Exception as e:
            print(e)
            time.sleep(10)
    return True


def restart_traffic_on_panel(inbound_id, user):

    response = requests.post(
        '{}/panel/inbound/{}/resetClientTraffic/{}'.format(
            PANEL_IP, inbound_id, user["email"]),
        cookies=cookies,
        verify=False,
    )
    print("reset traffic: "+response.text)


def find_user_in_panel(panel_users, panel_user):

    for t in panel_users:
        if panel_user["email"] == t["email"]:
            return t

    return None


def sync_users(inbound_id, users_server, users_panel, users_panel_with_details):
    for k in MAIN_SERVER:

        i = 0
        for p in users_panel:
            print("================ panel email: {}".format(p["email"]))
            find = False
            index_ss = 0
            for s in users_server:

                if ((s["email"] == p["email"] and k in p["email"]) or "test" in p["email"]):
                    find = True
                    break
                index_ss = index_ss+1
            user_panel_details = find_user_in_panel(
                users_panel_with_details, p)

            if (find and user_panel_details != None):
                time.sleep(0.5)
                update_user(1, user_panel_details, s)
                restart_traffic_on_panel(1, p)
                ss.remove(s)
                print("update:"+str(user_panel_details))
            elif (user_panel_details != None):
                del_user(1, user_panel_details)
                print("del:"+str(user_panel_details))
            i = i+1
            print("loding: {} % ".format(i*100/len(pss)))
            print("============================")
        for s in users_server:
            add_user(1, s)

    '''
    while  len(users_server) !=  0 and  len(users_panel_with_details) != 0:
        user_panel_details = users_panel_with_details.pop()
        s = users_server.pop()
        p = users_panel.pop()
        update_user(inbound_id,user_panel_details,s)
        restart_traffic_on_panel(inbound_id,p)
        # users_panel.remove(p)
        # users_server.remove(s)
        # users_panel_with_details.remove(user_panel_details)

    if  len(users_server) > len(users_panel_with_details):
        for s in  users_server :
             add_user(inbound_id,s)
    elif  len(users_server) < len(users_panel_with_details):
        for p in users_panel_with_details:
            del_user(inbound_id,p)
    '''


def update_trrafic_on_server(inbound_id, panel_users):

    print("update trrafic on server")
    return True
    user_list = []
    for p in panel_users:
        if (p["up"]+p["down"])/(1024*1024) > 1:
            user = {
                "id": p["email"],
                "total": math.floor((p["up"]+p["down"])/(1024*1024)),
                "inbound_id": inbound_id
            }
            user_list.append(user)

    url = "{}/api/shadow/traffic/bulk".format(MAIN_SERVER[MAIN_SERVER_GROUPE])
    payload = json.dumps({
        "panel_tag": PANEL_TAG,
        "usage_report": user_list
    })
    headers = {
        'key': '2969075850',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return "update" == response.text


def verify(users_server, users_panel):
    for s in users_server:
        find = True

        for p in users_panel:
            if s["email"] == p["email"]:
                find = True
                break
            else:
                find = False
        if find == False:
            print(p)
            add_user(1, s)
            ss.remove(s)


if __name__ == '__main__':

    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument('--ut', choices=['true', 'false'], default="true") # just update traffic
    parser.add_argument('--uu', choices=['true', 'false'], default="true") # just update users
    args = parser.parse_args()
    sl=random.randint(5,10)
    print (f"sleeping for {sl}")
    time.sleep(sl)
    
    login()
    

    ss = get_secrets()
    ps, pss = get_user_list_from_panel()

    if len(ss) == 0 or len(pss) == 0 or len(ps) == 0:
        print ("error in panel")
        exit(1)

    if (args.ut == "true"):
        update_trrafic_on_server(1, ps)

    if (args.uu == "true"):
        sync_users(1, ss, ps, pss)
        login()
        ss = get_secrets()
        ps, pss = get_user_list_from_panel()
        verify(ss, ps)
