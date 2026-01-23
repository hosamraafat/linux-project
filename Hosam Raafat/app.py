from flask import Flask, render_template, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import logging

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Logging
logging.basicConfig(filename='notesapp.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="notes_user",
        password="password",
        database="notes_app"
    )

# ------------------ Register ------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        cursor.close()
        db.close()
        logging.info(f"New user registered: {username}")
        return redirect("/login")
    return render_template("register.html")

# ------------------ Login ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            logging.info(f"User logged in: {username}")
            return redirect("/")
        return "Invalid credentials"
    return render_template("login.html")

# ------------------ Logout ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ------------------ Index / Notes ------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    cursor = db.cursor(dictionary=True)
    user_id = session["user_id"]

    # إضافة Note جديدة
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        cursor.execute("INSERT INTO notes (title, content, user_id) VALUES (%s, %s, %s)",
                       (title, content, user_id))
        db.commit()
        logging.info(f"Note added by {session['username']}: {title}")
        return redirect("/")

    # جلب كل Notes للمستخدم الحالي
    cursor.execute("SELECT * FROM notes WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    notes = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("index.html", notes=notes, username=session["username"])

# ------------------ Delete Note ------------------
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM notes WHERE id=%s AND user_id=%s", (id, session["user_id"]))
    db.commit()
    logging.info(f"Note deleted by {session['username']}: ID {id}")
    cursor.close()
    db.close()
    return redirect("/")

# ------------------ Edit Note ------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        # حفظ نسخة من Note الحالية في notes_history
        cursor.execute("SELECT title, content FROM notes WHERE id=%s AND user_id=%s", (id, session["user_id"]))
        old_note = cursor.fetchone()
        cursor.execute("INSERT INTO notes_history (note_id, title, content, user_id) VALUES (%s, %s, %s, %s)",
                       (id, old_note["title"], old_note["content"], session["user_id"]))

        # تحديث Note
        cursor.execute("UPDATE notes SET title=%s, content=%s WHERE id=%s AND user_id=%s",
                       (title, content, id, session["user_id"]))
        db.commit()
        logging.info(f"Note edited by {session['username']}: ID {id}")
        cursor.close()
        db.close()
        return redirect("/")

    cursor.execute("SELECT * FROM notes WHERE id=%s AND user_id=%s", (id, session["user_id"]))
    note = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template("edit.html", note=note)

# ------------------ Run App ------------------
app.run(host="0.0.0.0", port=5000)