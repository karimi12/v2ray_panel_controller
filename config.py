
import requests
import socket

HOSTNAME = socket.gethostname()
PANEL_IP = "http://159.65.197.72:9090"
# PANEL_IP = "http://"+requests.get("http://ip-api.com/json/").json()["query"]+":9090"

PANEL_TAG = socket.gethostname()
MIN_USAGE_REPORT=1
INBOUNDS_IDS=[3,5]
INBOUNDS_FLOW={
}
LOADBALCER_MODE=False
BANDWITH_TYPE="dedicated" # i = dedicated , l = limted
MAIN_SERVER_GROUPE = 'y'
# MAIN_SERVER_GROUPE='s'
MAIN_SERVER = {
    "y": "https://npanel4.karimiblog.ir",
    # "s": "https://spanel.karimiblog.ir",
}
SERVER_ID = {
    "y": list(range(20, 65)),
    # "s": list(range(20,50)),
}