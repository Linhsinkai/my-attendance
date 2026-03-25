from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    # 這裡放點名資料，之後你可以接 Google Sheets
    students = [
        {"name": "王大同", "school": "逢甲大學", "status": "未簽到"},
        {"name": "陳小花", "school": "逢甲大學", "status": "已簽到"},
    ]
    return render_template("index.html", student_list=students)


if __name__ == "__main__":
    app.run(debug=True)
