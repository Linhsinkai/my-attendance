import os
import gspread
from flask import Flask, render_template, redirect, url_for
from datetime import datetime

app = Flask(__name__)

VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def get_sheet_data(day_name):
    try:
        # 強制只讀取 credentials.json 檔案
        # 在 Render 上，這會讀取你設定的 Secret File
        # 在本地端，這會讀取你資料夾裡的檔案
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
        print(f"DEBUG ERROR: {e}")
        return None


# --- 路由部分保持不變 ---
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
        return f"讀取 {day} 資料失敗，請查看 Render Logs。"
    teachers = sorted(list(set([s["老師"] for s in students if s.get("老師")])))
    return render_template(
        "index.html", student_list=students, current_day=day, teachers=teachers
    )


if __name__ == "__main__":
    app.run(debug=True)
