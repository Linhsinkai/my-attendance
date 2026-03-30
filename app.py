import os
import gspread
import requests
from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime

app = Flask(__name__)

# 你的 Google 設定
GAS_URL = "https://script.google.com/macros/s/AKfycbyVzMnlJhyMHtSLbMTaDdLqQR_gPhMBejyI4oS5TQ-Cwee26862w8hQuLT2fmox3kCf/exec"
SHEET_ID = "1GlkGQiFIvGryanCt3jYDppD9pSqRm1tS1wgsWq6xa4U"
VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def get_sheet_data(day_name):
    # 用 .strip() 強制刪除前後可能存在的空白或換行符號
    RAW_KEY = "AIzaSyD5mK9GiL-qGN04KJlz4gvyF_8RvbpzloI"
    CLEAN_KEY = RAW_KEY.strip()

    SHEET_ID = "1GlkGQiFIvGryanCt3jYDppD9pSqRm1tS1wgsWq6xa4U"

    try:
        # 這裡加一個印出，讓我們確認 Key 是正確的
        print(f"--- 偵測開始 ---")
        print(f"正在連線到分頁: {day_name}")

        # 核心連線動作
        gc = gspread.api_key(CLEAN_KEY)
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.worksheet(day_name)
        data = worksheet.get_all_records()

        print(f"成功！讀取到 {len(data)} 筆學生資料")
        return data
    except Exception as e:
        print(f"偵測失敗: {e}")
        return None


@app.route("/")
def home():
    today = datetime.now().strftime("%A")
    if today not in VALID_DAYS:
        today = "Monday"
    return redirect(url_for("index", day=today))


@app.route("/<day>")
def index(day):
    if day not in VALID_DAYS:
        return redirect(url_for("index", day="Monday"))
    students = get_sheet_data(day)
    if students is None:
        return f"讀取 {day} 資料失敗，請檢查權限或 API Key。"

    # 提取老師名單供下拉選單使用
    teachers = sorted(list(set([s["老師"] for s in students if s.get("老師")])))
    return render_template(
        "index.html", student_list=students, current_day=day, teachers=teachers
    )


# 新增學生功能
@app.route("/add_student", methods=["POST"])
def add_student():
    day = request.form.get("day")
    payload = {
        "action": "add",
        "day": day,
        "name": request.form.get("name"),
        "phone": request.form.get("phone"),
        "teacher": request.form.get("teacher"),
    }
    requests.post(GAS_URL, json=payload)
    return redirect(url_for("index", day=day))


# 刪除學生功能
@app.route("/delete_student/<day>/<name>")
def delete_student(day, name):
    payload = {"action": "delete", "day": day, "name": name}
    requests.post(GAS_URL, json=payload)
    return redirect(url_for("index", day=day))


@app.route("/update_student", methods=["POST"])
def update_student():
    day = request.form.get("day")
    payload = {
        "action": "update",
        "day": day,
        "old_name": request.form.get("old_name"),
        "new_name": request.form.get("name"),
        "new_phone": request.form.get("phone"),
        "new_teacher": request.form.get("teacher"),
    }
    requests.post(GAS_URL, json=payload)
    return redirect(url_for("index", day=day))


if __name__ == "__main__":
    app.run(debug=True)
