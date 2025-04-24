import requests
import json

def url():
    with open(r"json\keep.json", "r", encoding="utf-8") as a:
        data = json.load(a)
        return data["URL"]

URL = f"{url()}/gripdata"

data = {
    "device_id": "device100",
    "grip": 4.17,
    "token": "admin0990"
}

try:
    response = requests.post(URL, json=data)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

except requests.exceptions.RequestException as e:
    print("發送失敗：", e)
