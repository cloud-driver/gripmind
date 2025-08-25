import os
import requests
import secrets
import jwt as pyjwt
from flask import Flask, request, redirect, jsonify, session, send_from_directory, Response, render_template
from send import Keep, send_grip_data, save_user_device, SECRET_TOKEN, daily_check_task, get_device_id, save_log, send_push_message, replay_msg, clean_users, DATA_FILE
import threading
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.secret_key = secrets.token_hex(16)

CLIENT_ID = int(Keep.channel_id())
CLIENT_SECRET = str(Keep.channel_secret())
REDIRECT_URI = f"{str(Keep.url())}/callback"

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/secret")
def haha():
    return render_template('secret.html')

@app.route("/send_to_all")
def send_to_all_users():
    users = get_device_id()
    for u in users:
        send_grip_data(u, 2.3)
    return render_template('send_to_all.html')

@app.route("/clear")
def clear():
    clean_users()
    return render_template('send_to_all.html')

@app.route("/login")
def login_redirect():
    device_id = request.args.get("device_id")
    if not device_id:
        return "請提供裝置 ID", 400

    state = secrets.token_hex(16)
    session['oauth_state'] = state
    session['device_id'] = device_id

    login_url = (
        f"https://access.line.me/oauth2/v2.1/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid%20profile"
        f"&state={state}"
    )
    return redirect(login_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    device_id = session.get("device_id")

    if not state or state != session.get("oauth_state"):
        print("fail by state")
        return "驗證失敗，state 不一致", 400

    token_url = "https://api.line.me/oauth2/v2.1/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_response = requests.post(token_url, data=payload, headers=headers)

    if token_response.status_code != 200:
        return "無法獲取 Access Token", 400

    token_data = token_response.json()
    id_token = token_data.get("id_token")
    decoded = pyjwt.decode(id_token, options={"verify_signature": False}, algorithms=["HS256"])
    user_id = decoded.get("sub")
    display_name = decoded.get("name", "未知")
    save_log(f"{user_id} have allready login with deviceID in {device_id}")

    save_user_device(user_id, device_id)

    return render_template('callback.html')

@app.route("/gripdata", methods=["POST"])
def grip_data():
    data = request.get_json()
    device_id = data.get("device_id")
    grip = data.get("grip")
    token = data.get("token")

    if token != SECRET_TOKEN:
        return jsonify({"error": "驗證失敗，token 不正確"}), 403

    if not device_id or grip is None:
        return jsonify({"error": "缺少 device_id 或 grip"}), 400

    result, status_code = send_grip_data(device_id, grip)
    return jsonify(result), status_code

@app.route("/history", methods=["GET"])
def history():
    device_id = request.args.get("device_id", "").strip()
    labels = []
    data = []
    if device_id:
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                all_records = json.load(f)
            device_records = [
                r for r in all_records if r.get("device_id") == device_id
            ]
            device_records.sort(key=lambda x: x["timestamp"])
            labels = [r["timestamp"] for r in device_records]
            data   = [r["grip"] for r in device_records]
        except Exception as e:
            save_log(f"讀取歷史數據失敗: {e}")
    # 傳入 template
    return render_template("history.html", device_id=device_id, labels=labels, data=data)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/log')
def log():
    data = Keep.logs()
    response = Response(
        json.dumps(data, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    return response

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    events = body.get("events", [])

    for event in events:
        if event.get("type") == "message" and event["message"]["type"] == "text":
            user_id = event["source"]["userId"]
            user_message = event["message"]["text"]
            reply_text = replay_msg(user_message)

            send_push_message(user_id, [{
                "type": "text",
                "text": reply_text
            }])

    return jsonify({"status": "ok"})

@app.route("/healthz")
def health():
    return "ok", 200

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    checker_thread = threading.Thread(target=daily_check_task, daemon=True)
    checker_thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    