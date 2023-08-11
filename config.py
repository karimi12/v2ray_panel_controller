
import requests

PANEL_IP = "http://143.198.242.211:9090"
PANEL_IP = "http://"+requests.get("http://ip-api.com/json/").json()["query"]+":9090"

PANEL_TAG = "test_Vless_DigitalOcean"
MIN_USAGE_REPORT=1
INBOUNDS_ID=[1]
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