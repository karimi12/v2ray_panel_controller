
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
import config
import log


# VERSION = 15
PANEL_IP = config.PANEL_IP
PANEL_TAG = config.PANEL_TAG
MIN_USAGE_REPORT = config.MIN_USAGE_REPORT
INBOUNDS_IDS = config.INBOUNDS_IDS
INBOUNDS_FLOW = config.INBOUNDS_FLOW
BANDWITH_TYPE = config.BANDWITH_TYPE  # i = dedicated , l = limted
MAIN_SERVER_GROUPE = config.MAIN_SERVER_GROUPE
MAIN_SERVER = config.MAIN_SERVER
SERVER_ID = config.SERVER_ID


print("\nServer IP: {}\nTag: {}\nServers ID:".format(
    PANEL_IP, PANEL_TAG, str(SERVER_ID)))

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
        tt["email"] = str(str(ts["id"])+"_"+k).strip()
        tt["id"] = ts["shadow_password"]
        tt["server_id"] = ts["id"]

        if BANDWITH_TYPE == "limted":
            tt["total"] = (ts.get("total_quota_limit", 0) -

                           ts.get("used_total_quota", 0)) * 1024*1024
        else:
            tt["total"] = ts.get("total_quota_limit", 0) * 1024*1024
        tt["totalGB"] = tt["total"]
        # tt["device"] = ts.get("device", 0)
        tt["device"] = 0
        tt["limitIp"] = ts.get("device", 0)
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
        tt["expiryTime"] = tt["expiry_time"]
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
            add = MAIN_SERVER[k]+"/api/shadow/config/temp?servers="+sid
            print("server: "+add)
            j = requests.get(add).json()
            # MAIN_SERVER[k]+"/shadow/keys/"+str(sid)).json()
            secrets = secrets + transform(j, k)

        except Exception as e:
            logging.error(e)
    return secrets


def add_user(inbound_id, user, inbound_flow=""):

    c = {
        "clients": [
            {
                "id": user["id"],
                "password": user["id"],
                "flow": inbound_flow,
                "email": user["email"]+"_"+str(inbound_id),
                "limitIp": user["device"],
                "totalGB": user["total"],
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


def update_user(inbound_id, user_panel, user_server, inbound_flow=""):

    # print("update user: "+str(user_panel))

    c = {
        "clients": [
            {
                "id": user_server["id"],
                "flow": inbound_flow,
                "email": user_server["email"]+"_"+str(inbound_id),
                "limitIp": user_server["device"],
                "totalGB": user_server["total"],
                "enable": user_server["enable"],
                "expiryTime": user_server["expiry_time"]
            }
        ]
    }

    data = {
        'id': str(inbound_id),
        'settings': json.dumps(c)
    }

    temp_id = user_panel["id"] if "id" in user_panel else user_panel["password"]
    response = requests.post(
        '{}/panel/inbound/updateClient/{}'.format(PANEL_IP, temp_id),
        cookies=cookies,
        data=data,
        verify=False,
    )
    print(response.text)


def del_user(inbound_id, user):
    """
    Delete a user from the specified inbound panel.

    Args:
        inbound_id (str): The ID of the inbound panel.
        user (dict): The user object to be deleted. (should be passed server user ti this user)

    Returns:
        None
    """
    print("delete: "+str(user))
    response = requests.post(
        '{}/panel/inbound/{}/delClient/{}'.format(
            PANEL_IP, inbound_id, user["id"]),
        cookies=cookies,
        verify=False,
    )

    print("delete: "+response.text)


def getInbound(id,array):
    for i in range(len(array.get("obj"))):
        if array.get("obj")[i]["id"] == id:
            return array.get("obj")[i]

def get_user_list_from_panel(inbound_id):

    response = requests.post(
        '{}/panel/inbound/list'.format(PANEL_IP), cookies=cookies, verify=False)
    j = response .json()
    p=getInbound(inbound_id,j)
    return p["clientStats"], json.loads(p["settings"])["clients"]


def xray_restart():
    response = requests.post(
        '{}/server/restartXrayService'.format(PANEL_IP), cookies=cookies)
    print(response.json())


def xray_stop():
    response = requests.post(
        '{}/server/stopXrayService'.format(PANEL_IP), cookies=cookies)
    print(response.json())

# def update_user_trrafic(inbound_id, user):

#     t = True
#     s_id = user["email"].split("_")[-1]
#     while t:
#         try:
#             j = requests.get("{}/api/shadow/traffic?id={}&server_tag={}&total={}".format(
#                 MAIN_SERVER[s_id], user["email"], PANEL_TAG+"_"+str(inbound_id), (user["up"]+user["down"])/(1024*1024)))
#             print(j.text)
#             if (j.status_code):
#                 t = False
#                 return True
#             print("error in update")
#             time.sleep(5)
#         except Exception as e:
#             print(e)
#             time.sleep(10)
#     return True


def restart_traffic_on_panel(inbound_id, user):

    response = requests.post(
        '{}/panel/inbound/{}/resetClientTraffic/{}'.format(
            PANEL_IP, inbound_id, user["email"]),
        cookies=cookies,
        verify=False,
    )
    print("reset traffic: "+response.text)


def restart_traffic_on_panel_user_by_user(inbound_id, users_panel):

    for p in users_panel:
        if (p["up"]+p["down"])/(1024*1024) > MIN_USAGE_REPORT:
            restart_traffic_on_panel(inbound_id, p)
            print("reset traffic: "+str(p))
            time.sleep(2)

        if (p["up"]+p["down"])/(1024*1024) > MIN_USAGE_REPORT*10:
            print("*** WARNING *** Many mistake: "+str(p))


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

                if ((s["email"]+"_"+str(inbound_id) == p["email"] and k in p["email"]) or "test" in p["email"]):
                    find = True
                    break
                index_ss = index_ss+1
            user_panel_details = find_user_in_panel(
                users_panel_with_details, p)

            if (find and user_panel_details != None):

                if (p["up"]+p["down"])/(1024*1024) > MIN_USAGE_REPORT:
                    restart_traffic_on_panel(inbound_id, p)
                    time.sleep(0.1)

                temp_id = "id" if "id" in user_panel_details else "password"

                if (s["id"] != user_panel_details[temp_id] or s["total"] != p["total"] or s["expiryTime"] != p["expiryTime"] or s["device"] != user_panel_details["limitIp"]):
                    print("update: True -->"+str(user_panel_details))
                    update_user(inbound_id, user_panel_details, s,
                                INBOUNDS_FLOW.get(inbound_id, ""))

                else:
                    print("update: False -->"+str(user_panel_details))
                ss.remove(s)

            elif (user_panel_details != None):
                del_user(inbound_id, user_panel_details)
                print("del:"+str(user_panel_details))
            i = i+1
            print("loding: {} % ".format(i*100/len(pss)))
            print("============================")
        for s in users_server:
            add_user(inbound_id, s, INBOUNDS_FLOW.get(inbound_id, ""))


def reset_traffic_all_users():
    response = requests.post('{}/panel/inbound/resetAllClientTraffics/-1'.format(
        PANEL_IP), cookies=cookies, verify=False)
    print("reset all traffic: "+response.text)


def update_trrafic_on_server(inbound_id, panel_users):
    """Send update trrafic on server as bulk to main server 
    """
    print("update trrafic on server")
    # return True  #debug
    user_list = []
    for p in panel_users:

        if (p["up"]+p["down"])/(1024*1024) > MIN_USAGE_REPORT:
            user = {
                "id": p["email"],
                "total": math.floor((p["up"]+p["down"])/(1024*1024)),
                "inbound_id": inbound_id
            }
            user_list.append(user)
            log.logger.info("update trrafic on server", extra={
                            "id": user["id"], "inbound_id": inbound_id, "total": user["total"], "panel_tag": PANEL_TAG})

    url = "{}/api/shadow/traffic/bulk".format(MAIN_SERVER[MAIN_SERVER_GROUPE])
    payload = json.dumps({
        "panel_tag": PANEL_TAG+"_"+str(inbound_id),
        "usage_report": user_list
    })
    headers = {
        'key': '2969075850',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    print("=========\n"+response.text+"\n=========")
    return "update" == response.text


def remove_duplicates(inbound_id, json_array, ):
    seen = set()
    duplicates = set()
    duplicate_items = []

    key = "email"
    for item in json_array:
        item_key = item.get(key)
        if item_key in seen:
            duplicates.add(item_key)
            duplicate_items.append(item)
        else:
            seen.add(item_key)

    print("removed duplicated users:")
    for  item in duplicate_items:
        del_user(inbound_id, item)

    return duplicate_items


def verify(inbound_id, users_server, users_panel):
    result = False
    for s in users_server:
        find = True

        for p in users_panel:
            if s["email"]+"_"+str(inbound_id) == p["email"]:
                find = True
                break
            else:
                find = False
        if find == False:
            print(p)
            add_user(inbound_id, s, INBOUNDS_FLOW.get(inbound_id, ""))
            result = True
            ss.remove(s)
    return result


def verifyExpired(inbound_id, users_server, users_panel):

    result = False
    for p in users_panel:
        find = True

        for s in users_server:
            if s["email"]+"_"+str(inbound_id) == p["email"]:
                find = True
                break
            else:
                find = False
        if find == False:
            print("==========================\ndel user -->"+str(p))
            time.sleep(1)
            del_user(inbound_id, s)
            result = True
            ss.remove(s)
    return result


if __name__ == '__main__':

    parser = argparse.ArgumentParser("simple_example")
    # just update traffic
    parser.add_argument('--ut', choices=['true', 'false'], default="true")
    # just update users
    parser.add_argument('--uu', choices=['true', 'false'], default="true")
    args = parser.parse_args()
    sl = random.randint(5, 10)
    print(f"Sleeping for {sl}")
    time.sleep(sl)
    login()
    if config.LOADBALCER_MODE:
        xray_stop()
    time.sleep(20)
    ss = get_secrets()

    for inbound_id in INBOUNDS_IDS:
        ps, pss = get_user_list_from_panel(inbound_id)

        if len(ss) == 0 or pss is None or len(ps) == 0:
            add_user(inbound_id, ss[0], INBOUNDS_FLOW.get(inbound_id, ""))
            print("error in panel")
            # exit(1)

        if (args.ut == "true"):
            update_trrafic_on_server(inbound_id, ps)

        if (args.uu == "true"):
            sync_users(inbound_id, ss, ps, pss)
            ss = get_secrets()
            ps, pss = get_user_list_from_panel(inbound_id)
            remove_duplicates(inbound_id=inbound_id, json_array=ps)
            for i in range(0, 2):
                print("================= verifyExpired: "+str(i))
                verifyExpired(inbound_id, ss, ps)
                print("================= verifiacation: "+str(i))
                verify(inbound_id, ss, ps)

            print("================= reset trrafic on panel")
            restart_traffic_on_panel_user_by_user(inbound_id, ps)
    reset_traffic_all_users()
    if config.LOADBALCER_MODE:
        xray_restart()
    os.system("systemctl restart x-ui.service")
