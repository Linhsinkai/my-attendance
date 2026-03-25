import os
import json
from flask import Flask, render_template, redirect, url_for
import gspread
from datetime import datetime

app = Flask(__name__)

VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def get_sheet_data(day_name):
    try:
        # 1. 優先檢查 Render 的 Secret File 是否存在
        if os.path.exists("credentials.json"):
            gc = gspread.service_account(filename="credentials.json")
        else:
            # 2. 備用方案：如果檔案不存在(本地開發)，嘗試環境變數
            creds_json = os.environ.get("GOOGLE_CREDS_JSON")
            if creds_json:
                creds_info = json.loads(creds_json)
                gc = gspread.service_account_from_dict(creds_info)
            else:
                # 如果都沒有，回傳 None (這會觸發網頁上的錯誤提示)
                return None

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


# --- 以下路由(home, index)維持不變 ---
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
        return f"讀取 {day} 資料失敗，請檢查 Google 試算表分頁名稱。"
    teachers = sorted(list(set([s["老師"] for s in students if s.get("老師")])))
    return render_template(
        "index.html", student_list=students, current_day=day, teachers=teachers
    )


if __name__ == "__main__":
    app.run(debug=True)
