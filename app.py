from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import dashscope
import os
import sys
import webbrowser
import threading
import time

# ==============================
# 关键：兼容 PyInstaller 路径
# ==============================
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 静态文件目录（前端）
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)

# ==============================
# API KEY
# ==============================
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# ==============================
# 登录页（入口）
# ==============================
@app.route("/")
def login_page():
    return send_from_directory(STATIC_DIR, "login.html")

# ==============================
# 主页（预测页面）
# ==============================
@app.route("/index.html")
def index_page():
    return send_from_directory(STATIC_DIR, "index.html")

# ==============================
# 图片访问（修复 images）
# ==============================
@app.route("/image/<path:filename>")
def get_image(filename):
    image_dir = os.path.join(BASE_DIR, "images")  # ✅ 修复这里
    return send_from_directory(image_dir, filename)

# ==============================
# 预测接口（完全不动你的 prompt）
# ==============================
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    flower = data.get("flower")
    location = data.get("location")
    month = data.get("month")

    temp = data.get("temp")
    sun = data.get("sun")

    prompt = f"""
你是一个中国花期预测专家，请结合常识、气候带、历史经验，给出一个合理的花期范围（允许误差）。

输入：
花卉：{flower}
地点：{location}
计划月份：2026年{month}月
平均温度{temp}摄氏度
平均日照时间{sun}小时

请考虑：
- 联网搜索该月份的气象预测数据
- 中国南北气候差异
- 温度、降水的影响
- 常见开花时间规律

输出格式：
花期：xx月xx日 - xx月xx日
推荐景点：xx、xx

输出要求：
1.不要使用Markdown格式，所有输出都是正文，仅以缩进、换行
2.第一行输出花期，第二行输出推荐的游玩地点，列举景点名字即可
3.第三行给出交通建议，比如到达哪个动车站或到达哪个机场
4.如果用户计划的旅游季节、地点，真的很反时节，比如夏天在南方看腊梅是不合理的事情，那么请你给出“季节不合适，推荐变更赏花计划”等劝谏，简短温和
"""

    response = dashscope.Generation.call(
        model="qwen-turbo",
        prompt=prompt
    )

    result = response.output.text

    return jsonify({"result": result})

# ==============================
# 自动打开浏览器
# ==============================
def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")

# ==============================
# 启动
# ==============================
if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    app.run(host="127.0.0.1", port=5000)