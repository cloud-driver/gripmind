# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from datetime import datetime, date
from send import (
    Keep,
    get_device_id,
    get_user_information,
    change_target_value,
)

from ai_client import ask_ai

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")


def parse_timestamp(timestamp: str):
    """
    Current format in data.json:
    20260605 09:30:00

    Return None if parsing fails.
    """
    try:
        return datetime.strptime(timestamp, "%Y%m%d %H:%M:%S")
    except Exception:
        return None


def get_records_by_device(device_id: str):
    all_records = Keep.datas()
    records = []

    for record in all_records:
        if record.get("device_id") == device_id:
            records.append({
                "device_id": record.get("device_id"),
                "grip": float(record.get("grip", 0)),
                "timestamp": record.get("timestamp")
            })

    records.sort(key=lambda r: r.get("timestamp", ""))
    return records


def get_target_by_device(device_id: str):
    user_information, code = get_user_information(device_id)

    if code != 200:
        return None

    target_weight, age, gender, condition, method, points = user_information

    return {
        "target_weight": float(target_weight),
        "age": age,
        "gender": gender,
        "condition": condition,
        "method": method,
        "points": points
    }


@api_v1.route("/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "ok",
        "service": "GripMind API v1"
    }), 200


@api_v1.route("/devices", methods=["GET"])
def api_devices():
    """
    Return all registered device ids.
    This is mainly for development/debugging.
    """
    return jsonify({
        "devices": get_device_id()
    }), 200


@api_v1.route("/devices/<device_id>/records", methods=["GET"])
def api_device_records(device_id):
    """
    Return grip records for one device.
    Optional query:
    - limit=20
    """
    records = get_records_by_device(device_id)

    limit = request.args.get("limit", type=int)
    if limit is not None and limit > 0:
        records = records[-limit:]

    return jsonify({
        "device_id": device_id,
        "count": len(records),
        "records": records
    }), 200


@api_v1.route("/devices/<device_id>/summary", methods=["GET"])
def api_device_summary(device_id):
    """
    Return summary for dashboard:
    - latest grip
    - today count
    - today max
    - today average
    - target weight
    - goal reached
    """
    records = get_records_by_device(device_id)
    profile = get_target_by_device(device_id)

    if profile is None:
        return jsonify({
            "error": "device_not_found",
            "message": f"Device '{device_id}' was not found."
        }), 404

    target_weight = profile["target_weight"]
    today = date.today()

    today_records = []
    for record in records:
        parsed_time = parse_timestamp(record["timestamp"])
        if parsed_time and parsed_time.date() == today:
            today_records.append(record)

    latest_record = records[-1] if records else None

    if today_records:
        today_values = [r["grip"] for r in today_records]
        today_max = max(today_values)
        today_average = round(sum(today_values) / len(today_values), 2)
        goal_reached = today_max >= target_weight
    else:
        today_max = None
        today_average = None
        goal_reached = False

    return jsonify({
        "device_id": device_id,
        "target_weight": target_weight,
        "latest_record": latest_record,
        "today": {
            "count": len(today_records),
            "max_grip": today_max,
            "average_grip": today_average,
            "goal_reached": goal_reached
        },
        "total_records": len(records)
    }), 200


@api_v1.route("/devices/<device_id>/profile", methods=["GET"])
def api_device_profile(device_id):
    profile = get_target_by_device(device_id)

    if profile is None:
        return jsonify({
            "error": "device_not_found",
            "message": f"Device '{device_id}' was not found."
        }), 404

    return jsonify({
        "device_id": device_id,
        "profile": profile
    }), 200


@api_v1.route("/devices/<device_id>/target", methods=["PATCH"])
def api_update_target(device_id):
    body = request.get_json(silent=True) or {}
    target_weight = body.get("target_weight")

    if target_weight is None:
        return jsonify({
            "error": "missing_target_weight",
            "message": "target_weight is required."
        }), 400

    try:
        target_weight = float(target_weight)
    except ValueError:
        return jsonify({
            "error": "invalid_target_weight",
            "message": "target_weight must be a number."
        }), 400

    if target_weight <= 0:
        return jsonify({
            "error": "invalid_target_weight",
            "message": "target_weight must be greater than 0."
        }), 400

    msg, code = change_target_value(device_id, target_weight)

    if code != 200:
        return jsonify({
            "error": "device_not_found",
            "message": msg
        }), code

    return jsonify({
        "device_id": device_id,
        "target_weight": target_weight,
        "message": "Target weight updated successfully."
    }), 200


@api_v1.route("/devices/<device_id>/analysis", methods=["POST"])
def api_device_analysis(device_id):
    """
    Generate a short training suggestion.

    Important:
    This is not medical diagnosis.
    It is only a training feedback prototype.
    """
    records = get_records_by_device(device_id)
    profile = get_target_by_device(device_id)

    if profile is None:
        return jsonify({
            "error": "device_not_found",
            "message": f"Device '{device_id}' was not found."
        }), 404

    if not records:
        return jsonify({
            "error": "no_records",
            "message": "No grip records found for this device."
        }), 400

    recent_records = records[-10:]

    history_lines = []
    for record in recent_records:
        history_lines.append(f"{record['timestamp']}：{record['grip']:.2f} kg")

    history_text = "\n".join(history_lines)

    question = (
        f"此使用者年齡為 {profile['age']}，性別為 {profile['gender']}，"
        f"身體狀況為 {profile['condition']}，訓練方式為 {profile['method']}，"
        f"目標握力為 {profile['target_weight']} kg。\n"
        f"以下是最近握力紀錄：\n{history_text}\n"
        "請用繁體中文給出 3 句以內的握力訓練回饋。"
        "請避免醫療診斷語氣，不要保證治療效果。"
    )

    suggestion = ask_ai(question)

    return jsonify({
        "device_id": device_id,
        "suggestion": suggestion,
        "disclaimer": "This suggestion is for training feedback only and is not a medical diagnosis."
    }), 200