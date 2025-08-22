import requests

URL = "https://gripmind.onrender.com/gripdata"

data = {
    "device_id": "device100",
    "grip": 2.3,
    "token": "admin0990"
}

try:
    response = requests.post(URL, json=data)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

except requests.exceptions.RequestException as e:
    print("發送失敗：", e)