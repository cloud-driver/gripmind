import json
import requests
import uuid
import os
from flask import jsonify
from datetime import datetime
import time

USER_FILE = r"json\users.json"
KEEP_FILE = r"json\keep.json"
DATA_FILE = r"json\data.json"
SECRET_TOKEN = "admin0990"

class Keep():
    """讀取keep.json中的隱私資訊"""
    @staticmethod
    def access_token():
        with open(KEEP_FILE, "r", encoding="utf-8") as a:
            data = json.load(a)
            return data["Messaging_api"]["ACCESS_TOKEN"]
    
    @staticmethod
    def channel_id():
        with open(KEEP_FILE, "r", encoding="utf-8") as a:
            data = json.load(a)
            return data["Line_login"]["channel_id"]
    
    @staticmethod
    def channel_secret():
        with open(KEEP_FILE, "r", encoding="utf-8") as a:
            data = json.load(a)
            return data["Line_login"]["channel_secret"]
    
    @staticmethod
    def url():
        with open(KEEP_FILE, "r", encoding="utf-8") as a:
            data = json.load(a)
            return data["URL"]

def send_push_message(user_id, messages):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {str(Keep.access_token())}",
        "X-Line-Retry-Key": str(uuid.uuid4())
    }
    payload = {
        "to": user_id,
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.text

def daily_check_task():
    while True:
        now = datetime.now()
        # 每天 19:00 檢查一次
        if now.hour == 19 and now.minute == 0:
            print("正在執行每日資料檢查...")

            # 載入資料
            try:
                with open(USER_FILE, "r", encoding="utf-8") as f:
                    users = json.load(f)
            except Exception as e:
                print(f"讀取使用者失敗: {e}")
                users = []

            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    grip_data = json.load(f)
            except Exception as e:
                print(f"讀取握力資料失敗: {e}")
                grip_data = []

            # 今天日期
            today = datetime.now().date()

            for user in users:
                user_id = user.get("userId")
                device_id = user.get("deviceId")

                found_today = False
                for record in grip_data:
                    if record.get("device_id") == device_id:
                        # 判斷 json 檔案寫入時間是否為今天（不夠準，但簡單）
                        file_time = datetime.fromtimestamp(
                            os.path.getmtime(DATA_FILE)
                        ).date()
                        if file_time == today:
                            found_today = True
                            break

                if not found_today:
                    msg = {
                        "type": "text",
                        "text": "⚠️ 你今天還沒有上傳握力資料喔，記得量測一下吧！"
                    }
                    status, response = send_push_message(user_id, [msg])
                    print(f"已提醒 {user_id}：{status}, {response}")

            time.sleep(61)  # 避免在這分鐘內重複發送
        else:
            time.sleep(30)

def check_done_the_goal(grip_value):
    if grip_value >= 3.0:
        return "你已完成今日目標，繼續加油！"
    else:
        return "你已經很努力了，明天再接再厲！"
    
def save_grip_data(deviceid, grip_value):
    """儲存握力資料進 json/data.json，若 device_id 存在則更新，否則新增"""
    devices = []

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                devices = json.load(f)
            except json.JSONDecodeError:
                print("JSON 檔案格式錯誤，將重新初始化")
                devices = []

    for device in devices:
        if device["device_id"] == deviceid:
            device["grip"] = grip_value
            device["timestamp"] = datetime.now().isoformat()
            break
    else:
        devices.append({
            "device_id": deviceid,
            "grip": grip_value,
            "timestamp": datetime.now().isoformat()
        })

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(devices, f, ensure_ascii=False, indent=2)
        return "資料儲存成功"
    except Exception as e:
        return f"資料儲存失敗：{e}"

def send_grip_data(device_id, grip_value):
    """根據裝置 ID 發送握力訊息給對應 userId"""
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                return {"error": "使用者資料格式錯誤（可能為空檔）"}, 500
    except FileNotFoundError:
        return {"error": "找不到使用者資料"}, 500

    target = next((u for u in users if u.get("deviceId") == device_id), None)
    if not target:
        return {"error": f"找不到對應的裝置 ID: {device_id}"}, 404

    user_id = target["userId"]
    message = {
        "type": "text",
        "text": f"今日握力紀錄：{grip_value} kg，{check_done_the_goal(grip_value)}"
    }
    status, response = send_push_message(user_id, [message])
    save_result = save_grip_data(device_id, grip_value)
    return {"message": f"已發送給 {user_id}：{status}, {response}, 資料庫儲存狀況：{save_result}"}, 200
        
def disable_get_users():
    """把users.json中的所有資訊讀出來"""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = []
    return jsonify(users)

def get_device_id():
    devices = []
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = []

    for i in users:
        devices.append(i['deviceId'])
    return devices

def save_user_device(user_id, device_id):
    """新增或更新userid及其對應的deviceid"""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = []

    for user in users:
        if user["userId"] == user_id:
            user["deviceId"] = device_id
            break
    else:
        users.append({"userId": user_id, "deviceId": device_id})

    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

if __name__ == "__main__":
    print("這裡是自建函式庫，你點錯了，請使用 app.py 發送資料測試")
