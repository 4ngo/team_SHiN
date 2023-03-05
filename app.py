import os

# 必要そうなライブラリを取りあえずコピペ（後々増えたり減ったりするはず）
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# session用にキーを設定
app.secret_key = 'dugfvbqeako'

# 空の辞書
# REGISTANTS = {}

# 人気な言語をあらかじめ用意しておく
LANGUAGES = [
    "Python",
    "C",
    "C++",
    "C#",
    "Java",
    "JavaScript",
    "VB",
    "SQL",
    "PHP",
    "Assembly language",
    "Ruby",
    "Go",
    "Kotlin",
    "AWS",
    "Swift",
    "HTML",
    "CSS",
    "その他"
]

# データベースを紐付ける
db = SQL("sqlite:///sns.db")

# 起動時、必ずHomeが表示されるように
@app.route("/")
def home():
    # ただHome画面を表示するだけ
    return render_template('home.html')

# ログイン処理
@app.route("/login", methods=["GET", "POST"])
def login():
    # それまで保存されていたセッションを消去
    session.clear()

    # POST通信だった（フォームが送信された）場合
    if request.method == "POST":

        # フォームの情報を取得
        login_id = request.form.get("login_id") # ユーザー名
        login_pass = request.form.get("login_pass") # パスワード

        # データベースから（ユーザー名・パスワード）が一致する行を抜き出し
        line = db.execute("SELECT * FROM users WHERE name = ?", login_id)

        if not line:
            # flash(" ユーザー名が一致しません")
            return render_template("login.html")

        # # ユーザー名が一致しない場合
        # if login_id != line[0]["name"]:
        #     flash("ユーザー名が一致しません")
        #     return redirect("/login")

        # パスワードが一致しない場合
        elif not check_password_hash(line[0]["password"], login_pass):
            # flash("パスワードが一致しません")
            return render_template("login.html")

        # セッションにidを代入
        session["user_id"] = line[0]["name"] # user_idではない！

        # page移動
        # flash("ログインしました")
        return redirect("/solved")

    # /loginにアクセスしただけの場合
    else:
        return render_template("login.html")

# 登録処理
@app.route("/register", methods=["GET", "POST"])
def register():

    # POST通信だった（フォームが送信された）場合
    if request.method == "POST":

        # フォームの情報を取得
        register_id = request.form.get("register_id") # ユーザー名
        register_pass = request.form.get("register_pass") # パスワード

        # 名前被りチェック（formでの入力名がデータベースに存在するなら1以上の戻り値になる）
        name_check = db.execute('SELECT EXISTS(SELECT * FROM users WHERE name = ?) AS name_check', register_id)
        if name_check[0]['name_check'] != 0:
            flash("この名前は既に使われています")
            return redirect("/register")

        # パスワードをハッシュ化
        hashed_password = generate_password_hash(register_pass, method='pbkdf2:sha256', salt_length=8)

        # データベースにformのデータを記録
        db.execute("INSERT INTO users (name, password) VALUES (?,?)", register_id, hashed_password)

        # セッションにregister_id（ユーザー名）を代入
        session["user_id"] = register_id

        # page移動
        # flash("登録しました")
        return redirect("/solved")

    # /registerにアクセスしただけの場合
    else:
        return render_template("register.html")

# 記録処理
# 中井が担当
@app.route("/record", methods=["GET", "POST"])
@login_required
def record():

    if request.method == "POST":

        # エラー言語（選ぶ）formじゃないかも?
        language = request.form.get("language")

        # 追加言語
        # add = request.form.get("add")
        # LANGUAGES.append(add)

        # エラー
        error = request.form.get("error")
        # 状況説明
        explanation = request.form.get("explanation")
        # 解決策
        solution = request.form.get("solution")

        # ユーザーと結びつける
        username = db.execute("SELECT username FROM users WHERE id = ?" ,session["user_id"])

        # apology 作らないといけない,helpers.pyみたいなの
        # if not language:
        #     return apology("missing language", 400)


        # if not error:
        #     return apology("please enter an error", 400)

        # if not explanation:
        #     return apology("Please explain the situation", 400)

        # 未解決の場合（ボタンが押されたらにした方がいい？）
        if not solution:
            flash("記録しました！頑張ったね！")
            db.execute("INSERT INTO errors (username, language, message, explain) VALUES(?, ?, ?, ?)", username, language, error, explanation)
            return render_template("unsolved.html")

        # 解決できた場合
        else:
            flash("記録しました！解決できてすごい！")
            db.execute("INSERT INTO errors (username, language, message, explain, solved) VALUES(?, ?, ?, ?, ?)", username, language, error, explanation, solution)
            return render_template("solved.html")

    else:
        return render_template("record.html", language=LANGUAGES)

#イシモリ #最終更新 2/26
# 未解決を表示
@app.route("/unsolved", methods=["GET", "POST"])
@login_required
def display_unsolved():

    # 後で消す
    session["user_id"] = 2

    if request.method == "GET":

        # すべての未解決を全てデータベースから取り出し、格納
        unsolved_errors = db.execute("SELECT * FROM errors WHERE solved LIKE 'unsolved' AND username=?", session["user_id"]) # これ以降AND user_id=?の部分AND usernmae=?に変えてます

        return render_template("unsolved.html", unsolved_errors=unsolved_errors, languages=LANGUAGES)

    else:
        # どの言語で絞るか form から受け取る
        language = request.form.get("language")

        if language == "すべての言語":
            # すべての未解決をデータベースから取り出し、格納
            unsolved_errors = db.execute("SELECT * FROM errors WHERE solved LIKE 'unsolved' AND username=?", session["user_id"])
        else:
            # 特定の言語の未解決をデータベースから取り出し、格納
            unsolved_errors = db.execute("SELECT * FROM errors WHERE solved LIKE 'unsolved' AND username=? AND language=?", session["user_id"], language)

        return render_template("unsolved.html", unsolved_errors=unsolved_errors, languages=LANGUAGES)


#解決済みのエラーを表示
@app.route("/solved", methods=["GET", "POST"])
# @login_required
def display_solved():

    # 後で消す
    session["user_id"] = 2

    if request.method == "GET":

        # 解決済みを全てデータベースから取り出し、格納
        solved_errors = db.execute("SELECT * FROM errors WHERE solved LIKE 'solved' AND username=?", session["user_id"])

        return render_template("solved.html", solved_errors=solved_errors, languages=LANGUAGES)

    else:
        # どの言語で絞るか form から受け取る
        language = request.form.get("language")

        if language == "すべての言語":
            # すべての解決済みをデータベースから取り出し、格納
            solved_errors = db.execute("SELECT * FROM errors WHERE solved LIKE 'solved' AND username=?", session["user_id"])
        else:
            # 特定の言語の未解決エラーをデータベースから取り出し、格納
            solved_errors = db.execute("SELECT * FROM errors WHERE solved LIKE 'solved' AND username=? AND language=?", session["user_id"], language)

        return render_template("solved.html", solved_errors=solved_errors, languages=LANGUAGES)
#####イシモリ


if __name__ == "__main__":
    app.run(debug=True)