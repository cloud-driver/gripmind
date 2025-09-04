import requests
import random
import time

URL = "https://gripmind.onrender.com/gripdata"

for i in range(int(input("幾次："))):
    time.sleep(1)
    data = {
        "device_id": "device0581",
        "grip": random.uniform(2.0,5.0),
        "token": "admin0990"
    }

    try:
        response = requests.post(URL, json=data)
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)

    except requests.exceptions.RequestException as e:
        print("發送失敗：", e)