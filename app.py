import os

# 必要そうなライブラリを取りあえずコピペ（後々増えたり減ったりするはず）
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# 起動時、必ずHomeが表示されるように
@app.route("/")
def home():
    # ただHome画面を表示するだけ
    return render.template('home.html')

# ログイン処理
@app.route("/login", methods=["GET", "POST"])
def login():
    # それまで保存されていたセッションを消去
    session.clear()

    # POST通信だった（フォームが送信された）場合
    if request.method == "POST":
        # データベースとフォームの情報を照合

    # /loginにアクセスしただけの場合
    else:
        return render_template("login.html")

# 