# -*- coding: utf-8 -*-
from google.genai import Client
from google.genai import types
import json
import requests
import uuid
import os
from datetime import datetime
import time

USER_FILE = r"json/users.json"
KEEP_FILE = r"json/keep.json"
DATA_FILE = r"json/data.json"
LOG_FILE = r"json/log.json"
DIALOGUE_FILE = r"json/dialogue.json"
SECRET_TOKEN = "admin0990"
API_KEY = "AIzaSyC72Bw38usXWc6w8CSARBccvOuvFlcZ9YY"
CLIENT = Client(api_key=API_KEY)
TEXT = "GripMind 是什麼的答案是 GripMind 是一款結合物聯網（IoT）與智慧互動提醒功能的手部肌力復健裝置，能即時測量握力並提供每日數據回饋。GripMind 的功能有哪些的答案是 GripMind 擁有三大功能：智慧握力測量、即時 LINE 推播提醒，以及多模式手部訓練設計，能依不同族群需求提供個人化復健方案。GripMind 使用了哪些感測器的答案是 本裝置使用 HX711 壓力感測模組搭配應變規（strain gauge），透過非線性數學模型轉換為握力重量（公斤數）進行即時監測。GripMind 的資料會儲存在哪裡的答案是 所有使用者的握力紀錄會以 JSON 檔案儲存於本地端伺服器，包含 data.json（握力資料）與 users.json（裝置與 LINE 使用者綁定資訊）。裝置的提醒功能怎麼運作的答案是 系統每天會在固定時間（18:01）自動檢查是否上傳握力資料，若未達成，將透過 LINE Bot 自動推播提醒使用者進行測量。GripMind 的訓練模式有哪些的答案是 GripMind 提供多種訓練模式，包括輕壓復健、靜態握持訓練與進階挑戰訓練，未來亦可透過 LINE 設定模式以因應不同需求。這套裝置是給誰用的答案是 本裝置主要針對高齡長者、術後復健者與行動不便者設計，也適合需進行手部肌肉訓練的族群，如運動員或長期久坐者。為什麼握力訓練對失智有幫助的答案是 研究顯示握力與認知功能具高度正相關，透過穩定的手部肌力訓練可有效減緩腦部退化、降低失智與中風等風險。GripMind 的成本與售價大概是多少的答案是 裝置預估成本為 519.5 元，含塑膠外殼、感測器、LCD 顯示器等，預計依三倍定價法設定建議售價為新台幣 1800 元。這套系統的後端是怎麼設計的答案是 GripMind 系統使用 Python Flask 框架作為後端伺服器，提供握力數據接收 API，整合 LINE Messaging API 推播功能，並儲存資料於本地 JSON 檔案中。GripMind 可以記錄每天的握力變化嗎的答案是 是的，GripMind 會自動紀錄每日握力數值，使用者可以透過圖表或資料回顧自己每週、每月的訓練變化趨勢。GripMind 怎麼把感測器的數值轉換成公斤的答案是 裝置使用非線性曲線擬合公式將壓力感測器回傳的電阻值轉換為公斤數，精準度經實測驗證可應用於復健場域。LINE Bot 的提醒會每天發送嗎的答案是 系統每天固定於 18:01 檢查是否上傳握力資料，若尚未完成訓練，將由 LINE Bot 自動提醒使用者。這套裝置是否有 APP 的答案是 目前 GripMind 的使用介面以 LINE Bot 與網頁介面為主，未來將視需求推出手機 App 版本以強化互動與紀錄功能。這個產品可以商業化嗎的答案是 GripMind 已進行市場競爭力分析與成本試算，具備量產潛力，未來可導入長照機構、家庭照護或健康保險產業中。可以多台裝置連接一個 LINE 嗎的答案是 目前一個 LINE 使用者綁定一個裝置，但系統結構具備擴充性，未來可支援多裝置對一帳號的資料分辨與管理。GripMind 和市售握力器有什麼不同的答案是 市售握力器多以運動訓練為導向，無數據回饋；GripMind 主打復健照護與智慧提醒，支援低強度握力、資料紀錄與目標追蹤。資料是儲存在雲端還是本地的答案是 目前資料儲存在本地端 JSON 檔案中，未來將考慮導入雲端資料庫以支援跨裝置同步與遠端資料備份。使用 GripMind 時需要電源嗎的答案是 是的，GripMind 裝置需外部供電，可透過行動電源或 USB 接口供電，亦可根據需求改裝電池模組。我可以設定自己的每日訓練目標嗎的答案是 目前系統預設目標值為開發者指定數值，後續版本將開放使用者在 LINE 中自定訓練強度與目標。"


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
        
    @staticmethod
    def logs():
        with open(LOG_FILE, "r", encoding="utf8") as a:
            data = json.load(a)
            return data

def send_push_message(user_id, messages):
    """發送打包好的訊息給指定使用者"""
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
    save_log(f"Have allready send {messages} to {user_id}")
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.text

def daily_check_task():
    """每天19:00檢查所有使用者今日有無更新資料"""
    while True:
        now = datetime.now()
        if now.hour == 18 and now.minute == 1:
            save_log("正在執行每日資料檢查...")

            try:
                with open(USER_FILE, "r", encoding="utf-8") as f:
                    users = json.load(f)
            except Exception as e:
                save_log(f"讀取使用者失敗: {e}")
                users = []

            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    grip_data = json.load(f)
            except Exception as e:
                save_log(f"讀取握力資料失敗: {e}")
                grip_data = []

            today = datetime.now().date()

            for user in users:
                user_id = user.get("userId")
                device_id = user.get("deviceId")

                found_today = False
                for record in grip_data:
                    if record.get("device_id") == device_id:
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
                    save_log(f"已提醒 {user_id}：{status}, {response}")

            time.sleep(61)
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
                save_log("data.json 檔案格式錯誤，將重新初始化")
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
                save_log({"error": "使用者資料格式錯誤（可能為空檔）"})
                return {"error": "使用者資料格式錯誤（可能為空檔）"}, 500
    except FileNotFoundError:
        save_log({"error": "找不到使用者資料"})
        return {"error": "找不到使用者資料"}, 500

    target = next((u for u in users if u.get("deviceId") == device_id), None)
    if not target:
        save_log({"error": f"找不到對應的裝置 ID: {device_id}"})
        return {"error": f"找不到對應的裝置 ID: {device_id}"}, 404

    user_id = target["userId"]
    message = {
        "type": "text",
        "text": f"今日握力紀錄：{grip_value} kg，{check_done_the_goal(grip_value)}"
    }
    if grip_value == 2.3:
        message = {
        "type": "text",
        "text": f"今日握力紀錄：{grip_value} kg，{check_done_the_goal(grip_value)},(this is test of API)"
        }
    status, response = send_push_message(user_id, [message])
    save_result = save_grip_data(device_id, grip_value)
    save_log({"message": f"已發送給 {user_id}：{status}, {response}, 資料庫儲存狀況：{save_result}"})
    return {"message": f"已發送給 {user_id}：{status}, {response}, 資料庫儲存狀況：{save_result}"}, 200
        
def disable_get_users():
    """把users.json中的所有資訊讀出來"""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = []
    return 404

def get_device_id():
    """把users.json中所有的device id讀出來"""
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

def save_log(text):
    with open(LOG_FILE, "r", encoding="utf8") as f:
        logs = json.load(f)

    logs.append({"time": time.ctime(time.time()), "log": text})

    with open(LOG_FILE, "w", encoding="utf8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)
        
def replay_msg(user_msg):
    response = CLIENT.models.generate_content(
        model="gemini-2.5-flash", contents=f"請先閱讀下列資料再回答「{user_msg}」，我要3句話內的純文字。如果問題在資料中找不到答案，就用風趣的方式回答吧，可以不需要按照資料來回答\n\n {TEXT}", config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0))
    )
    return response.text

def clean_users():
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)
        
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)

if __name__ == "__main__":
    print("這裡是自建函式庫，你點錯了，請使用 app.py 發送資料測試")
