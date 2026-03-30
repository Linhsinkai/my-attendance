import os
import gspread
import requests
from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime

app = Flask(__name__)

# --- 你的 Google 設定 ---
# 已更新為你剛剛提供的最新 GAS 資訊
GAS_URL = "https://script.google.com/macros/s/AKfycbz4QekCt_X0kTRTpN9PR4ngYlW8m1Z6luXi6rLaCwqEKO1ZI5B0ZJvN5-tiUMeahtFF/exec"
SHEET_ID = "1GlkGQiFIvGryanCt3jYDppD9pSqRm1tS1wgsWq6xa4U"
VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def get_sheet_data(day_name):
    """從 Google 試算表讀取學生資料"""
    try:
        # 從環境變數讀取 API KEY (Render 端設定)
        api_key = os.environ.get("GOOGLE_API_KEY")

        if not api_key:
            print("ERROR: 找不到環境變數 GOOGLE_API_KEY")
            return None

        # 建立連線並清理可能的空白字元
        gc = gspread.api_key(api_key.strip())
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.worksheet(day_name)

        data = worksheet.get_all_records()

        # 處理電話號碼補 0 (避免 09xx 變成 9xx)
        for row in data:
            phone = str(row.get("電話", ""))
            if phone.startswith("9") and len(phone) == 9:
                row["電話"] = "0" + phone
        return data
    except Exception as e:
        print(f"讀取資料失敗: {e}")
        return None


@app.route("/")
def home():
    """首頁自動根據星期跳轉"""
    today = datetime.now().strftime("%A")
    if today not in VALID_DAYS:
        today = "Monday"
    return redirect(url_for("index", day=today))


@app.route("/<day>")
def index(day):
    """顯示特定星期的學生清單"""
    if day not in VALID_DAYS:
        return redirect(url_for("index", day="Monday"))

    students = get_sheet_data(day)

    # 如果抓不到資料，顯示錯誤訊息（方便除錯）
    if students is None:
        return f"讀取 {day} 資料失敗。請檢查 Render 的 GOOGLE_API_KEY 是否與 Google Cloud 一致。"

    # 提取老師名單供下拉選單使用
    teachers = sorted(list(set([s["老師"] for s in students if s.get("老師")])))

    return render_template(
        "index.html", student_list=students, current_day=day, teachers=teachers
    )


@app.route("/add_student", methods=["POST"])
def add_student():
    """透過 GAS 新增學生"""
    day = request.form.get("day")
    payload = {
        "action": "add",
        "day": day,
        "name": request.form.get("name"),
        "phone": request.form.get("phone"),
        "teacher": request.form.get("teacher"),
    }
    try:
        requests.post(GAS_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"新增失敗: {e}")
    return redirect(url_for("index", day=day))


@app.route("/delete_student/<day>/<name>")
def delete_student(day, name):
    """透過 GAS 刪除學生"""
    payload = {"action": "delete", "day": day, "name": name}
    try:
        requests.post(GAS_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"刪除失敗: {e}")
    return redirect(url_for("index", day=day))


@app.route("/update_student", methods=["POST"])
def update_student():
    """透過 GAS 修改學生資訊"""
    day = request.form.get("day")
    payload = {
        "action": "update",
        "day": day,
        "old_name": request.form.get("old_name"),
        "new_name": request.form.get("name"),
        "new_phone": request.form.get("phone"),
        "new_teacher": request.form.get("teacher"),
    }
    try:
        requests.post(GAS_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"修改失敗: {e}")
    return redirect(url_for("index", day=day))


if __name__ == "__main__":
    app.run(debug=True)
