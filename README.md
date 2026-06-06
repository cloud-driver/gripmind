# GripMind

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Flask](https://img.shields.io/badge/Backend-Flask-green)
![License](https://img.shields.io/github/license/cloud-driver/gripmind)
![Stars](https://img.shields.io/github/stars/cloud-driver/gripmind)

**GripMind** 是一套結合 **IoT、LINE Bot、Web Dashboard 與 AI 訓練回饋** 的智慧握力復健原型系統。  
系統可接收握力裝置上傳的量測資料，記錄使用者每日訓練狀況，並透過 LINE 推播、網頁圖表與 AI 回饋，協助使用者建立更穩定的手部肌力訓練習慣。

> 本專案為智慧照護與復健輔助系統原型，不提供醫療診斷，也不應取代醫師、物理治療師或職能治療師的專業建議。

---

## Project Overview

GripMind 的核心目標是解決傳統握力訓練裝置缺乏「紀錄、提醒、回饋」的問題。

一般握力器通常只能提供單次訓練，使用者很難知道：

- 今天是否有完成訓練
- 握力是否有進步
- 是否達成個人目標
- 是否需要調整訓練強度
- 長期資料是否能被追蹤與分析

因此，GripMind 將握力訓練流程拆成四個階段：

1. **量測**：由握力裝置取得握力數值
2. **上傳**：裝置將資料送至 Flask API
3. **紀錄**：後端儲存使用者與握力歷史資料
4. **回饋**：透過 LINE、Web Dashboard 與 AI 產生訓練建議

---

## Key Features

### 1. IoT Grip Data Upload

裝置端可透過 API 上傳握力資料：

- 裝置 ID
- 握力數值
- 驗證 Token

後端會將資料儲存至 JSON 檔案，並保留歷史紀錄。

---

### 2. LINE Login Device Binding

使用者可透過 LINE Login 綁定自己的握力裝置。  
系統會將 LINE 使用者與裝置 ID 對應起來，後續即可針對特定使用者推播訓練提醒與握力回饋。

---

### 3. LINE Bot Push Notification

當裝置上傳握力資料後，系統會透過 LINE Bot 推播使用者當日握力紀錄，例如：

```text
今日握力紀錄：3.8 kg，你已完成今日目標，繼續加油！
```

系統也具備每日檢查邏輯，可用於提醒尚未完成訓練的使用者。

---

### 4. Web Dashboard

使用者可透過網頁查看指定裝置的握力歷史紀錄。

目前包含：

* 裝置資料查詢
* 握力歷史紀錄
* 目標握力顯示
* 使用者點數顯示
* AI 分析入口

---

### 5. Target Weight Management

每位使用者可設定或更新自己的目標握力值。
系統會根據目標值判斷當日訓練是否達標。

---

### 6. AI Training Feedback

GripMind 整合本地端 Ollama 模型，根據使用者的：

* 年齡
* 性別
* 身體狀況
* 訓練方式
* 目標握力
* 最近握力紀錄

產生簡短、保守、繁體中文的訓練回饋。

AI 回饋只作為訓練輔助，不作為醫療診斷。

---

### 7. REST API v1

本專案提供 `/api/v1` API，方便未來串接：

* 手機 App
* 管理後台
* 研究資料分析工具
* 其他 IoT 裝置

---

## System Architecture

```text
Grip Device
Arduino / ESP8266 / Sensor
        │
        │ POST /gripdata
        ▼
Flask Backend
app.py / send.py / api_v1.py
        │
        ├── JSON Data Storage
        │   ├── users.json
        │   ├── data.json
        │   └── log.json
        │
        ├── LINE Bot
        │   ├── Login Binding
        │   ├── Push Message
        │   └── Auto Reply
        │
        ├── Web Dashboard
        │   ├── History Page
        │   ├── Target Setting
        │   └── Admin Page
        │
        └── AI Feedback
            └── Ollama Local Model
```

---

## Repository Structure

```text
gripmind/
├── app.py                 # Main Flask application
├── api_v1.py              # REST API v1 routes
├── send.py                # LINE push, data storage, user binding logic
├── ai_client.py           # Ollama AI client
├── requirements.txt       # Python dependencies
├── render.yaml            # Render deployment configuration
├── Procfile               # Deployment process file
├── docs/
│   └── api.md             # API v1 documentation
├── json/
│   ├── users.json         # User and device binding data
│   ├── data.json          # Grip records
│   ├── keep.json          # Runtime data
│   └── log.json           # System logs
├── templates/             # HTML templates
├── static/                # Static assets
├── temp/                  # Development utilities
└── zip/                   # Exported data archive
```

---

## Tech Stack

| Layer          | Technology            |
| -------------- | --------------------- |
| Backend        | Python, Flask         |
| API            | Flask Blueprint       |
| Frontend       | HTML, Jinja Templates |
| Data Storage   | JSON files            |
| Messaging      | LINE Messaging API    |
| Authentication | LINE Login            |
| AI Feedback    | Ollama local model    |
| Deployment     | Render, Gunicorn      |
| License        | MIT License           |

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/cloud-driver/gripmind.git
cd gripmind
```

---

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create `.env`

Create a `.env` file in the project root.

```env
SECRET_TOKEN=your_device_upload_token
SECRET_KEY=your_flask_secret_key
SECRET_PAGE_PASSWORD=your_admin_page_password

URL=http://localhost:10000

LINE_LOGIN_CHANNEL_ID=your_line_login_channel_id
LINE_LOGIN_CHANNEL_SECRET=your_line_login_channel_secret
MESSAGING_API_ACCESS_TOKEN=your_line_messaging_api_access_token

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct
OLLAMA_TIMEOUT=120
```

---

### 5. Run the Server

```bash
python app.py
```

Default local URL:

```text
http://localhost:10000
```

---

## API Usage

### Upload Grip Data

```http
POST /gripdata
Content-Type: application/json
```

Request body:

```json
{
  "device_id": "device_demo_001",
  "grip": 3.8,
  "token": "your_device_upload_token"
}
```

Example:

```bash
curl -X POST http://localhost:10000/gripdata \
  -H "Content-Type: application/json" \
  -d '{"device_id":"device_demo_001","grip":3.8,"token":"your_device_upload_token"}'
```

---

## API v1

Base URL:

```text
/api/v1
```

### Health Check

```http
GET /api/v1/health
```

---

### Get Device Records

```http
GET /api/v1/devices/{device_id}/records
```

Optional query:

```text
?limit=20
```

---

### Get Device Summary

```http
GET /api/v1/devices/{device_id}/summary
```

Returns:

* Latest grip record
* Today’s record count
* Today’s maximum grip
* Today’s average grip
* Target weight
* Goal reached status

---

### Get Device Profile

```http
GET /api/v1/devices/{device_id}/profile
```

---

### Update Target Weight

```http
PATCH /api/v1/devices/{device_id}/target
Content-Type: application/json
```

Request body:

```json
{
  "target_weight": 4.0
}
```

---

### Generate AI Training Suggestion

```http
POST /api/v1/devices/{device_id}/analysis
```

Response example:

```json
{
  "device_id": "device_demo_001",
  "suggestion": "最近握力表現穩定，建議您維持目前訓練頻率...",
  "disclaimer": "This suggestion is for training feedback only and is not a medical diagnosis."
}
```

For more details, see:

```text
docs/api.md
```

---

## Deployment

This project includes a Render configuration file:

```yaml
services:
  - type: web
    name: gripmind-api
    env: python
    buildCommand: ""
    startCommand: gunicorn app:app
    autoDeploy: true
```

When deploying, remember to set the required environment variables in the Render dashboard.

---

## Current Status

GripMind is currently a working prototype.

Implemented:

* Flask backend
* Web dashboard
* LINE Login binding flow
* LINE Bot message push
* Grip data upload API
* JSON-based local data storage
* Target weight management
* AI training feedback through Ollama
* API v1 documentation
* Render deployment configuration

Planned improvements:

* Replace JSON files with a real database
* Add complete hardware setup documentation
* Add Arduino / ESP8266 firmware examples
* Add unit tests
* Add Docker support
* Improve admin dashboard security
* Add mobile app interface
* Add multi-device support for one user
* Add data export for rehabilitation tracking

---

## Important Notes

This project is a prototype for smart rehabilitation assistance.

Please do not use GripMind as:

* A medical diagnosis system
* A substitute for professional rehabilitation treatment
* A certified medical device
* A final clinical decision-making tool

The AI feedback module is designed to provide conservative training suggestions only.

---

## License

This project is licensed under the MIT License.

See:

```text
LICENSE
```

---

## Author

GripMind Team
Created by Justus Cheng

