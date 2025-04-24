import json
import os
import datetime
from send import USER_FILE, DATA_FILE, send_push_message, Keep

def load_json_file(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def check_data_for_today():
    users = load_json_file(USER_FILE)
    grip_data = load_json_file(DATA_FILE)
    today = datetime.datetime.now().date()

    # 檢查每位使用者的資料是否是今天的
    for user in users:
        user_id = user.get("userId")
        device_id = user.get("deviceId")
        found = False
        for record in grip_data:
            if record.get("device_id") == device_id:
                record_time = datetime.datetime.fromtimestamp(os.path.getmtime(DATA_FILE)).date()
                if record_time == today:
                    found = True
                    break
        if not found:
            message = {
                "type": "text",
                "text": "⚠️ 你今天還沒有上傳握力資料喔，記得量測一下吧！"
            }
            send_push_message(user_id, [message])
            print(f"已提醒 {user_id}")

if __name__ == "__main__":
    check_data_for_today()
