# -*- coding: utf-8 -*-
import os
import requests
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))


SYSTEM_PROMPT = """
你是 GripMind 智慧握力復健系統中的訓練回饋助手。
你的任務是根據使用者的握力紀錄、目標值與訓練資訊，提供簡短、清楚、保守的訓練回饋。

請遵守：
1. 使用繁體中文。
2. 語氣自然、鼓勵，但不要誇大。
3. 不要做醫療診斷。
4. 不要保證治療效果。
5. 不要建議危險或過度訓練。
6. 若資料不足，請明確說明資料不足，只能提供一般性建議。
"""


def ask_ai(question: str) -> str:
    """
    Call local Ollama server.

    Flask backend -> Ollama API -> local model

    Default endpoint:
    POST http://localhost:11434/api/chat
    """

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.strip()
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_ctx": 4096
        }
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()

        data = response.json()
        message = data.get("message", {})
        content = message.get("content", "").strip()

        if not content:
            return "目前 AI 沒有產生有效回覆，請稍後再試。"

        return content

    except requests.exceptions.Timeout:
        return "AI 回覆逾時，請稍後再試，或確認 Ollama 模型是否已啟動。"

    except requests.exceptions.ConnectionError:
        return "無法連線到 Ollama，請確認 Linux 伺服器上的 Ollama 是否正在執行。"

    except requests.exceptions.HTTPError as e:
        return f"Ollama API 回傳錯誤：{e}"

    except Exception as e:
        return f"AI 服務發生未知錯誤：{e}"