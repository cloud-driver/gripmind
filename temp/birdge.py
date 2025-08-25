import requests
import serial
import time

# 設定 Arduino 串列埠
arduino_port = 'COM3'
baud_rate = 9600
URL = "https://gripmind.onrender.com/gripdata"

try:
    # 初始化串列通訊
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"連接到 {arduino_port}，波特率為 {baud_rate}")
    
    time.sleep(2)
    
    while True:
        # 讀取 Arduino 傳回的資料
        if ser.in_waiting > 0:  # 檢查是否有資料
            raw_data = ser.readline().decode('utf-8').strip()
            print(f"接收到的資料: {raw_data}")
            
            try:
                # 將資料轉換為數字型態
                grip_value = float(raw_data)
                send_data = {
                    "device_id": "device100",
                    "grip": grip_value,
                    "token": "admin0990"
                }
                print("傳送的資料:", send_data)

                # 傳送資料到伺服器
                response = requests.post(URL, json=send_data)
                print("Status Code:", response.status_code)
                print("Response Text:", response.text)

                # 檢查伺服器回應
                if response.status_code == 500:
                    print("伺服器端錯誤，請聯絡管理員。")
                    break

            except ValueError:
                print(f"接收到無效的資料，無法轉換為數字: {raw_data}")
            except requests.exceptions.RequestException as e:
                print("發送失敗：", e)
                
except serial.SerialException as e:
    print(f"串列通訊錯誤: {e}")
except PermissionError as e:
    print(f"存取被拒: {e}")
    print("請檢查是否有其他程式佔用串列埠，或嘗試以管理員身份執行程式。")
except Exception as e:
    print(f"其他錯誤: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("串列通訊已關閉")