import os
import json
import gspread
from flask import Flask, render_template, redirect, url_for
from datetime import datetime

app = Flask(__name__)

VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def get_sheet_data(day_name):
    try:
        # 1. 優先從環境變數讀取
        creds_json = os.environ.get("GOOGLE_CREDS_JSON")

        if creds_json:
            creds_info = json.loads(creds_json)
            # 【關鍵修正】：強制將私鑰中的 \\n 換回真正的換行符號
            if "private_key" in creds_info:
                creds_info["private_key"] = creds_info["private_key"].replace(
                    "\\n", "\n"
                )
            gc = gspread.service_account_from_dict(creds_info)
        else:
            # 2. 本地開發環境
            gc = gspread.service_account(filename="credentials.json")

        sh = gc.open("Mobile_Attendance")
        worksheet = sh.worksheet(day_name)
        return worksheet.get_all_records()
    except Exception as e:
        print(f"DEBUG ERROR: {e}")  # 這會印在 Render Logs
        return None


# 後面路由 (home, index) 維持不變
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
        return f"讀取 {day} 資料失敗，請查看 Render Logs 錯誤訊息。"
    teachers = sorted(list(set([s["老師"] for s in students if s.get("老師")])))
    return render_template(
        "index.html", student_list=students, current_day=day, teachers=teachers
    )


if __name__ == "__main__":
    app.run(debug=True)
