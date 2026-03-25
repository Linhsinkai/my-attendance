import os
import json
from flask import Flask, render_template, redirect, url_for
import gspread
from datetime import datetime

app = Flask(__name__)

VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def get_sheet_data(day_name):
    try:
        # 1. 檢查是否有環境變數 (Render 環境)
        creds_json = os.environ.get("GOOGLE_CREDS_JSON")

        if creds_json:
            # 雲端環境：從變數讀取 JSON 字串
            creds_info = json.loads(creds_json)
            gc = gspread.service_account_from_dict(creds_info)
        else:
            # 本地環境：從檔案讀取
            gc = gspread.service_account(filename="credentials.json")

        sh = gc.open("Mobile_Attendance")
        worksheet = sh.worksheet(day_name)
        data = worksheet.get_all_records()

        # 修正電話補 0
        for row in data:
            phone = str(row.get("電話", ""))
            if phone.startswith("9") and len(phone) == 9:
                row["電話"] = "0" + phone
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None


@app.route("/")
def home():
    # 自動跳轉到今天星期幾
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
        return f"讀取 {day} 資料失敗，請檢查 Google 試算表分頁名稱。"

    # 自動提取當天有出現的老師名單 (去除重複並排序)
    teachers = sorted(list(set([s["老師"] for s in students if s.get("老師")])))

    return render_template(
        "index.html", student_list=students, current_day=day, teachers=teachers
    )


if __name__ == "__main__":
    app.run(debug=True)
