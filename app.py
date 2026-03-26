import os
import gspread
from flask import Flask, render_template, redirect, url_for
from datetime import datetime

app = Flask(__name__)

VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def get_sheet_data(day_name):
    try:
        # 改用 API Key 方式連線 (最穩，避開 JWT 簽名問題)
        # 注意：你需要先在 Google Cloud 啟用 "Google Sheets API"
        api_key = os.environ.get("GOOGLE_API_KEY")

        if not api_key:
            # 本地測試時，如果沒設環境變數，就寫死測試 (正式上線請放環境變數)
            api_key = "AIzaSyD5mK9GiL-qGNO4KJlz4gvyF_8RvbpzloI"

        gc = gspread.api_key(api_key)

        # 開啟試算表 (注意：使用 API Key 時，試算表必須設為「任何知道連結的人都可以查看」)
        sh = gc.open_by_key(
            "1GlkGQiFIvGryanCt3jYDppD9pSqRm1tS1wgsWq6xa4U"
        )  # 試算表 URL 中間那串長代碼
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
