# GripMind

![Python Version](https://img.shields.io/badge/python-3.9-blue.svg)
![License](https://img.shields.io/github/license/cloud-driver/gripmind.svg)
![Issues](https://img.shields.io/github/issues/cloud-driver/gripmind.svg)
![Stars](https://img.shields.io/github/stars/cloud-driver/gripmind.svg)

**GripMind：結合 IoT 與智慧互動之手部肌力復健裝置**

---

## 目錄

- [專案簡介](#專案簡介)
- [功能特色](#功能特色)
- [系統架構](#系統架構)
- [使用說明](#使用說明)
- [目錄結構](#目錄結構)
- [API 端點](#api-端點)
- [授權](#授權)
- [作者](#作者)

---

## 專案簡介

GripMind 致力於以物聯網（IoT）結合智能互動，開發一套手部肌力復健裝置。  
系統由 **Arduino** 硬體端與 **Flask** Web 伺服器協同運作，用戶可透過網頁或行動裝置遠端控制機構，並將握力數據回傳至雲端進行儲存與分析。

---

## 開發動機

在構思智慧照護方案時，我最初是想要研究後期治療的相關議題，例如如何減輕長期臥床者的不適。然而，在瀏覽長者健康相關網站與影片時，我偶然看到一部手指肌肉訓練的教學影片，之後先查詢網路文章，開始注意到 **「握力訓練」** 以及 **「手部肌肉控制」** 對老年人腦部的影響。深入查找相關研究後，我意識到預防與居家訓練在智慧照護中重要性。

---
## 功能特色

- 即時遠端控制：透過 Web UI 或 LINE Bot 下達控制指令，驅動伺服器端機構運作。  
- 握力數據回傳：Arduino 偵測握力感測器數值，並透過 Wifi 傳送至後端 API。  

---

## 系統架構

```plaintext
手部裝置
(Arduino + ESP8266)
     ↕
Flask Server (app.py、send.py)
     ↕
 JSON 資料庫
     ↓
daily_check.py / 
     ↓
LINE Bot / Web UI

手部裝置 (Arduino + ESP8266)  -->  Flask Server (app.py、send.py)  <-->  JSON 資料庫
                                                ↓
                                          LINE Bot / Web UI
```

---

## 使用說明

1. 在瀏覽器開啟 `https://gripmind.onrender.com/`，進入 Web GUI，直接操作。  
2. 或透過 LINE Bot 傳送訊息，即可了解專案資訊。  
3. 所有握力數據均儲存於 `json/data.json`，可由網頁查看過往訓練資料。  

---

## 目錄結構

```plaintext
gripmind/
├── Procfile
├── README.md
├── __pycache__
│   └── send.cpython-39.pyc
├── app.py
├── json
│   ├── arduino_api.json
│   ├── data.json
│   ├── keep.json
│   ├── log.json
│   └── users.json
├── render.yaml
├── requirements.txt
├── send.py
├── static
│   ├── L_gainfriends_2dbarcodes_BW.png
│   ├── administrator.webp
│   ├── apple-touch-icon-precomposed.png
│   ├── apple-touch-icon.png
│   └── favicon.ico
├── temp
│   ├── birdge.py
│   ├── data_maker.py
│   └── get_ngrok_url.py
├── templates
│   ├── 404.html
│   ├── callback.html
│   ├── cannot_find.html
│   ├── change.html
│   ├── history.html
│   ├── index.html
│   ├── log.html
│   ├── secret.html
│   ├── secret_login.html
│   ├── send_to_all.html
│   ├── setup.html
│   └── target.html
└── zip
    └── datas.zip
```

---

## API 端點

| 路徑         | 方法 | 說明                     |
| ------------ | ---- | ------------------------ |
| `/gripdata`  | POST | 接收裝置推送的握力資料   |
| `/callback`  | POST | 接收 LINE 的控制指令     |
| `/webhook`   | POST | 接收 LINE 的訊息指令     |

範例：
```bash
curl -X POST https://gripmind.onrender.com/gripdata \
     -H "Content-Type: application/json" \
     -d '{"device_id":"deviceXXXX","grip":5,"token":"<SECRET_TOKEN>"}'
```

---

## 授權

本專案採用 [MIT License](./LICENSE) 開源授權。

---

## 作者

- GripMind 團隊  
