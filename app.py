# -*- coding: utf-8 -*-
import os
import requests
import secrets
import jwt as pyjwt
import threading
import json
import markdown
import zipfile
from flask import Flask, request, redirect, jsonify, session, send_from_directory, Response, render_template, url_for, flash
from send import Keep, send_grip_data, save_user_device, daily_check_task, get_device_id, save_log, send_push_message, replay_msg, clean_users, change_target_value, ask_ai, get_user_information
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect, generate_csrf
from datetime import timedelta

if os.path.exists(".env"): load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.secret_key = secrets.token_hex(16)
app.config['SECRET_PAGE_PASSWORD'] = os.getenv('SECRET_PAGE_PASSWORD')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=10)
app.config.update(SESSION_COOKIE_SECURE=True, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
limiter = Limiter( app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
csrf = CSRFProtect(app)

CLIENT_ID = int(os.getenv('LINE_LOGIN_CHANNEL_ID'))
CLIENT_SECRET = str(os.getenv('LINE_LOGIN_CHANNEL_SECRET'))
REDIRECT_URI = f"{str(os.getenv('URL'))}/callback"

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

@csrf.exempt
@app.route("/")
def home():
    return render_template('index.html')

@app.route('/secret_login', methods=['GET', 'POST'])
def secret_login():
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if pwd == app.config['SECRET_PAGE_PASSWORD']:
            session['secret_ok'] = True
            return redirect(url_for('haha'))
        else:
            flash('密碼錯誤，請再試一次。', 'danger')
    return render_template('secret_login.html')

@csrf.exempt
@app.route('/secret')
def haha():
    if not session.get('secret_ok'):
        return redirect(url_for('secret_login'))
    return render_template('secret.html')

@csrf.exempt
@app.route('/secret_logout')
def secret_logout():
    session.pop('secret_ok', None)
    flash('已登出 secret 區', 'info')
    return redirect(url_for('secret_login'))

@csrf.exempt
@app.route("/send_to_all")
def send_to_all_users():
    if not session.get('secret_ok'):
        return redirect(url_for('secret_login'))
    users = get_device_id()
    for u in users:
        send_grip_data(u, 2.3)
    return render_template('send_to_all.html')

@csrf.exempt
@app.route("/clear")
def clear():
    if not session.get('secret_ok'):
        return redirect(url_for('secret_login'))
    clean_users()
    return render_template('send_to_all.html')

@csrf.exempt
@app.route("/download")
def download():
    if not session.get('secret_ok'):
        return redirect(url_for('secret_login'))
    with zipfile.ZipFile('zip/datas.zip', mode='w') as zf:
        zf.write('json/users.json')
        zf.write('json/data.json')
    return send_from_directory('zip', "datas.zip", as_attachment=True)

@csrf.exempt
@app.route("/setup")
def setup():
    device_id = request.args.get("device_id")
    if not device_id:
        return "請提供裝置 ID", 400
    return render_template("setup.html", device_id=device_id)

@csrf.exempt
@limiter.limit("5 per minute")
@app.route("/login")
def login_redirect():
    device_id = request.args.get("device_id")
    age = request.args.get("age")
    gender = request.args.get("gender")
    condition = request.args.get("condition")
    method = request.args.get("method")
    state = secrets.token_hex(16)

    session['oauth_state'] = state
    session['device_id'] = device_id
    session['age'] = age
    session['gender'] = gender
    session['condition'] = condition
    session['method'] = method

    login_url = (
        f"https://access.line.me/oauth2/v2.1/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid%20profile"
        f"&state={state}"
    )
    return redirect(login_url)

@csrf.exempt
@limiter.limit("10 per minute")
@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    device_id = session.get("device_id")
    age = session['age']
    gender = session['gender']
    condition = session['condition']
    method = session['method']

    if not state or state != session.get("oauth_state"):
        save_log("fail by state")
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

    suggest_target = save_user_device(user_id, device_id, age, gender, condition, method)

    return render_template('callback.html', suggest_target=suggest_target)

@csrf.exempt
@limiter.limit("20 per minute")
@app.route("/gripdata", methods=["POST"])
def grip_data():
    data = request.get_json()
    device_id = data.get("device_id")
    grip = data.get("grip")
    token = data.get("token")

    if token != os.getenv('SECRET_TOKEN'):
        return jsonify({"error": "驗證失敗，token 不正確"}), 403

    if not device_id or grip is None:
        return jsonify({"error": "缺少 device_id 或 grip"}), 400

    result, status_code = send_grip_data(device_id, grip)
    return jsonify(result), status_code

@csrf.exempt
@app.route("/history", methods=["GET"])
def history():
    device_id = request.args.get("device_id", "").strip()
    labels = []
    data = []

    if device_id:
        if device_id not in get_device_id():
            return render_template("cannot_find.html", device_id=device_id)
        try:
            all_records = Keep.datas()
            device_records = [r for r in all_records if r.get("device_id") == device_id]
            device_records.sort(key=lambda x: x["timestamp"])
            labels = [r["timestamp"] for r in device_records]
            data   = [r["grip"] for r in device_records]
            user_information, code = get_user_information(device_id)
            if code != 200:
                target_weight, age, gender, condition, method = None
            else:
                target_weight, age, gender, condition, method = user_information

            history_str_lines = []
            for ts, g in zip(labels, data):
                history_str_lines.append(f"{ts}：{g:.2f} kg")
            history_str = "\n".join(history_str_lines)

            question = (
                f"此使用者的年齡是 {age} 歲，性別 {gender}，"
                f"身體狀況為 {condition}，握力使用方式為 {method}，"
                f"目標公斤數為 {target_weight} kg。\n"
                f"以下是此使用者過去的握力歷史數據：\n"
                f"{history_str}\n"
                "請根據以上資訊，給我一小段針對他的握力訓練建議，主詞都用您，用台灣人會用的繁體中文。"
            )

            ai_msg_md = ask_ai(question)
            ai_msg_html = markdown.markdown(ai_msg_md)

        except Exception as e:
            save_log(f"讀取歷史數據失敗: {e}")
            ai_msg_html = "<p>讀取歷史資料時發生錯誤，無法提供建議。</p>"

    return render_template(
        "history.html",
        device_id=device_id,
        labels=labels,
        data=data,
        msg_html=ai_msg_html,
        target_weight=target_weight
    )

@app.route("/change", methods=["GET"])
def change():
    device_id = request.args.get("device_id", "").strip()
    if device_id not in get_device_id():
        return render_template("cannot_find.html", device_id=device_id)
    return render_template("change.html", device_id=device_id)

@csrf.exempt
@app.route("/target", methods=["GET", "POST"])
def target():
    if request.method == "POST":
        device_id   = request.form.get("device_id", "").strip()
        target_value = float(request.form.get("target_value", "").strip() or 0)
    else:
        device_id   = request.args.get("device_id", "").strip()
        target_value = float(request.args.get("target_value", "").strip() or 0)

    msg, code = change_target_value(device_id, target_value)
    save_log(f"對於將{device_id}的目標設為{target_value}的結果是{msg}，{code}")
    return render_template("target.html", device_id=device_id, target_value=target_value, msg=msg), code

@csrf.exempt
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@csrf.exempt
@app.route('/log')
def log_page():
    if not session.get('secret_ok'):
        return redirect(url_for('secret_login'))
    return render_template('log.html')

@csrf.exempt
@app.route('/log/data')
def log_data():
    if not session.get('secret_ok'):
        return redirect(url_for('secret_login'))
    data = Keep.logs()
    response = Response(
        json.dumps(data, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    return response

@csrf.exempt
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

@csrf.exempt
@app.route("/test", methods=["POST"])
def grip_data():
    return render_template('test.html')

@csrf.exempt
@limiter.limit("100 per minute")
@app.route("/test/api", methods=["POST"])
def grip_data():
    data = request.get_json()
    student_id = data.get("student_id")
    token = data.get("token")

    if token != os.getenv('SECRET_TOKEN'):
        return jsonify({"error": "驗證失敗，token 不正確"}), 403
    
    url = 'https://script.google.com/macros/s/AKfycbx1EXa9t7thW7iqGGYZQJj51zClFVMl_wxNTSkq425Y-cF4YWimcljmEziRjdsx7Kdr/exec'
    post_data_payload = {
        'action': 'writeData', # Example action, adjust if your script uses a different one
        'student_id': student_id, # Replace with the actual student ID
        'column': 'F', # Column to write to
        'value': 'TRUE' # Value to write
    }

    json_data_string = json.dumps(post_data_payload)
    post_url = f'{url}?data={json_data_string}'

    try:
        response = requests.post(post_url)
        if response.status_code == 200:
            save_log("Data successfully written to the sheet.")
            save_log("Response:", response.text)
        else:
            save_log(f"Failed to write data. Status code: {response.status_code}")
            save_log("Response:", response.text)

    except requests.exceptions.RequestException as e:
        save_log(f"An error occurred during the request: {e}")

    return jsonify(response.text), response.status_code

@csrf.exempt
@app.route("/healthz")
def health():
    return "ok", 200

@csrf.exempt
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    checker_thread = threading.Thread(target=daily_check_task, daemon=True)
    checker_thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    