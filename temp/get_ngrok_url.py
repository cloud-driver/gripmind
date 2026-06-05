import requests
import json
import os

def get_ngrok_url():
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = response.json()
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
    except Exception as e:
        print("Error fetching ngrok URL:", e)
    return None

url = get_ngrok_url()

if url == None:
    print("get url failed")
    os._exit(0)
else:
    with open('json/keep.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    data["URL"] = f"{url}"

    with open('json/keep.json', 'w', encoding='utf-8') as f:
        json.dump(data, f)
    
    print("get url successful")
    print(f"{url}/callback")
    print(f"{url}/webhook")
    