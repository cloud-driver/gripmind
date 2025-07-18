# GripMind

**GripMind：結合 IoT 與智慧互動之手部肌力復健裝置**

## 專案簡介

GripMind 致力於以物聯網（IoT）結合智能互動，開發一套手部肌力復健裝置。系統由 **Arduino** 硬體端與 **Flask** Web 伺服器協同運作，用戶可透過網頁或行動裝置遠端控制機構，並將握力數據回傳至雲端進行儲存與分析。

## 功能特色

- **即時遠端控制**：透過網頁介面或 LINE Bot 下達控制指令，驅動伺服器端機構運作。
- **握力數據回傳**：Arduino 偵測握力感測器數值，並透過 ESP8266 模組傳送至後端 API。
- **自動化日常檢測**：`daily_check.py` 定時執行，統計使用者每日使用情況並發送提醒。
- **NGROK 動態網址更新**：`get_ngrok_url.py` 擷取當前公開網址，並更新至 LINE Bot 或其他服務。

## 架構說明

```
手部裝置 (Arduino + ESP8266)  <-->  Flask Server (app.py)  <-->  JSON 資料庫
                                              |
                                    daily_check.py / send.py
                                              |
                                        LINE Bot / Web UI
```

- `device.ino`：Arduino 端程式，讀取握力感測器並控制伺服器通訊。
- `app.py`：Flask 主程式，提供 RESTful API 端點與網頁介面。
- `daily_check.py`：排程腳本，每天檢查並統計使用狀況。
- `get_ngrok_url.py`：擷取 ngrok 公開網址，動態更新至服務。
- `send.py`：封裝通知功能，將訊息推播至 LINE 或其他通訊管道。

### 檔案架構圖

```
gripmind/
├── __pycache__/
├── json/
│   ├── data.json
│   ├── keep.json
│   ├── log.json
│   └── users.json
├── static/
│   └── favicon.ico
├── .gitattributes
├── .renderignore
├── Procfile
├── README.md
├── app.py
├── daily_check.py
├── device.ino
├── get_ngrok_url.py
├── render.yaml
├── requirements.txt
├── send.py
└── test.py
```

## 系統需求

- Python 3.9 以上
- Arduino IDE
- ngrok 帳號與 Authtoken
- LINE Messaging API 權杖（若要推播通知）
- LINE Login API 權杖（若要Line登入功能）

## 安裝與設定

1. **克隆專案**：
   ```bash
   git clone https://github.com/cloud-driver/gripmind.git
   cd gripmind
   ```
2. **安裝 Python 套件**：
   ```bash
   pip install -r requirements.txt
   ```
3. **設定變數**：
   ```bash
   (請自行編輯keep.json文件)
   ```
4. **配置 ngrok**：
   ```bash
   ngrok authtoken $NGROK_AUTHTOKEN
   ```

## 執行專案

1. 啟動 ngrok：
   ```bash
   ngrok http 5000
   ```

2. 自動抓取 ngrok 網址
   ```bash
   python get_ngrok_url.py
   ```

3. 啟動後端服務：
   ```bash
   python app.py
   ```

## 部署 (Deployment)

- **Heroku**：使用 `Procfile` 定義啟動指令。
- **Render**：`render.yaml` 已內含服務設定。

## 目錄結構

```plaintext
gripmind/
├── __pycache__/
├── json/  
│   ├── data.json  
│   ├── keep.json  
│   ├── log.json  
│   └── users.json  
├── static/  
│   └── favicon.ico  
├── .gitattributes  
├── .renderignore  
├── Procfile  
├── README.md  
├── app.py  
├── daily_check.py  
├── device.ino  
├── get_ngrok_url.py  
├── render.yaml  
├── requirements.txt  
├── send.py  
└── test.py  
```

## API 端點

| 路徑           | 方法   | 功能說明             |
| -------------- | ---- | ---------------- |
| `/gripdata`    | POST | 接收裝置推送的握力資料      |
| `/callback`    | POST | 接收 LINE 的控制指令 |
| `/webhook`    | POST | 接收 LINE 的訊息指令 |
| `/`            | GET  | 顯示 Web UI 主頁     |

## 貢獻 (Contributing)

歡迎提出 Issue 或 Pull Request，請先閱讀。

## 作者 (Author)

- GripMind團隊
