from flask import Flask, render_template, request, redirect, session, send_file, url_for
import os
import sqlite3
import cv2
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "2027"

# ---------------- GLOBAL PASSWORD LOCK ----------------
def lock_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'feature_lock' not in session:
            session['next_page'] = request.path
            return redirect("/lock")

        return f(*args, **kwargs)

    return decorated_function


# ---------------- LOCK PAGE ----------------
@app.route('/lock', methods=['GET','POST'])
def lock():

    if request.method == "POST":

        password = request.form.get("password")

        if password == "3806":

            session['feature_lock'] = True
            next_page = session.get("next_page","/dashboard")
            return redirect(next_page)

        else:
            return render_template("lock.html", error="Wrong Password")

    return render_template("lock.html")


# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        roll TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        date TEXT,
                        time TEXT
                    )''')

    conn.commit()
    conn.close()


init_db()

# ---------------- LOGIN PAGE ----------------
@app.route('/')
def home():
    return render_template('login.html')


# ---------------- CHECK PASSWORD ----------------
@app.route('/check', methods=['POST'])
def check():
    password = request.form.get('password')

    if password == "2027":
        session['user'] = "admin"
        return redirect('/dashboard')
    else:
        return render_template("login.html", error="Wrong Password! Try Again")


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT name FROM students")
    rows = cursor.fetchall()
    student_list = [r[0] for r in rows]

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        student_list=student_list
    )


# ---------------- ADD STUDENT PAGE ----------------
@app.route('/add_student')
@lock_required
def add_student():

    if 'user' not in session:
        return redirect('/')

    return render_template('register_camera.html')


# ---------------- AUTO CAPTURE 20 IMAGES ----------------
@app.route('/capture_images')
@lock_required
def capture_images():

    if 'user' not in session:
        return redirect('/')

    name = request.args.get("name")
    roll = request.args.get("roll")

    if not name:
        return redirect('/add_student')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO students (name, roll) VALUES (?, ?)", (name, roll))

    conn.commit()
    conn.close()

    folder_path = f"static/dataset/{name}"
    os.makedirs(folder_path, exist_ok=True)

    cam = cv2.VideoCapture(0)

    count = 0

    while count < 20:

        ret, frame = cam.read()

        if not ret:
            break

        cv2.imwrite(f"{folder_path}/{count}.jpg", frame)

        count += 1

        cv2.waitKey(100)

    cam.release()

    cv2.destroyAllWindows()

    os.system("python train.py")

    return redirect("/dashboard")


# ---------------- CAPTURE ----------------
@app.route('/capture', methods=['POST'])
@lock_required
def capture():

    if 'user' not in session:
        return redirect('/')

    name = request.form['name']
    roll = request.form['roll']

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO students (name, roll) VALUES (?, ?)", (name, roll))

    conn.commit()
    conn.close()

    folder_path = f"static/dataset/{name}"

    os.makedirs(folder_path, exist_ok=True)

    cam = cv2.VideoCapture(0)

    count = 0

    while True:

        ret, frame = cam.read()

        if not ret:
            break

        cv2.imshow("Capturing Images", frame)

        cv2.imwrite(f"{folder_path}/{count}.jpg", frame)

        count += 1

        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

        if count >= 25:
            break

    cam.release()

    cv2.destroyAllWindows()

    os.system('python train.py')

    return redirect('/dashboard')


# ---------------- REMOVE STUDENT ----------------
@app.route('/remove_student', methods=['POST'])
@lock_required
def remove_student():

    if 'user' not in session:
        return redirect('/')

    name = request.form.get("name")

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE name=?", (name,))

    conn.commit()
    conn.close()

    folder_path = f"static/dataset/{name}"

    if os.path.exists(folder_path):

        os.system(f'rmdir /s /q "{folder_path}"')

    os.system("python train.py")

    return redirect("/dashboard")


# ---------------- START ATTENDANCE ----------------
@app.route('/recognize')
@lock_required
def recognize():

    if 'user' not in session:
        return redirect('/')

    os.system('python face_recognize.py')

    return redirect('/dashboard')


# ---------------- VIEW ATTENDANCE ----------------
@app.route('/attendance')
@lock_required
def attendance():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, date, time FROM attendance ORDER BY id DESC")

    data = cursor.fetchall()

    conn.close()

    return render_template('attendance.html', data=data)


# ---------------- EXPORT ATTENDANCE ----------------
@app.route('/export')
@lock_required
def export_attendance():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, date, time FROM attendance")

    rows = cursor.fetchall()

    conn.close()

    filename = "attendance_export.csv"

    with open(filename, "w") as f:

        f.write("Name,Date,Time\n")

        for r in rows:

            f.write(f"{r[0]},{r[1]},{r[2]}\n")

    return send_file(filename, as_attachment=True)


# ---------------- ABOUT PAGE ----------------
@app.route('/about')
@lock_required
def about():

    if 'user' not in session:
        return redirect('/')

    return render_template('about.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


# ---------------- RUN ----------------
if __name__ == '__main__':
    from flask import Flask, render_template, request, redirect, session, send_file
    import os
    import sqlite3
    import cv2
    from datetime import datetime

    app = Flask(__name__)
    app.secret_key = "2027"

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        roll TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        date TEXT,
                        time TEXT
                    )''')

    conn.commit()
    conn.close()


init_db()

# ---------------- LOGIN PAGE ----------------
@app.route('/')
def home():
    return render_template('login.html')


# ---------------- CHECK PASSWORD ----------------
@app.route('/check', methods=['POST'])
def check():
    password = request.form.get('password')

    if password == "2027":
        session['user'] = "admin"
        return redirect('/dashboard')
    else:
        return render_template("login.html", error="Wrong Password! Try Again")


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT name FROM students")
    rows = cursor.fetchall()
    student_list = [r[0] for r in rows]

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        student_list=student_list
    )


# ---------------- ADD STUDENT PAGE ----------------
@app.route('/add_student')
def add_student():
    if 'user' not in session:
        return redirect('/')
    return render_template('register_camera.html')


# ---------------- AUTO CAPTURE 20 IMAGES ----------------
@app.route('/capture_images', methods=['GET'])
def capture_images():
    if 'user' not in session:
        return redirect('/')

    name = request.args.get("name")
    roll = request.args.get("roll")

    if not name:
        return redirect('/add_student')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, roll) VALUES (?, ?)", (name, roll))
    conn.commit()
    conn.close()

    folder_path = f"static/dataset/{name}"
    os.makedirs(folder_path, exist_ok=True)

    cam = cv2.VideoCapture(0)

    count = 0
    while count < 20:
        ret, frame = cam.read()
        if not ret:
            break

        cv2.imwrite(f"{folder_path}/{count}.jpg", frame)
        count += 1
        cv2.waitKey(100)

    cam.release()
    cv2.destroyAllWindows()

    os.system("python train.py")

    return redirect("/dashboard")


# ---------------- CAPTURE (OLD METHOD) ----------------
@app.route('/capture', methods=['POST'])
def capture():
    if 'user' not in session:
        return redirect('/')

    name = request.form['name']
    roll = request.form['roll']

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, roll) VALUES (?, ?)", (name, roll))
    conn.commit()
    conn.close()

    folder_path = f"static/dataset/{name}"
    os.makedirs(folder_path, exist_ok=True)

    cam = cv2.VideoCapture(0)
    count = 0

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        cv2.imshow("Capturing Images", frame)
        cv2.imwrite(f"{folder_path}/{count}.jpg", frame)
        count += 1

        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

        if count >= 25:
            break

    cam.release()
    cv2.destroyAllWindows()

    os.system('python train.py')
    return redirect('/dashboard')


# ---------------- REMOVE STUDENT ----------------
@app.route('/remove_student', methods=['POST'])
def remove_student():
    if 'user' not in session:
        return redirect('/')

    name = request.form.get("name")

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE name=?", (name,))
    conn.commit()
    conn.close()

    folder_path = f"static/dataset/{name}"
    if os.path.exists(folder_path):
        os.system(f'rmdir /s /q "{folder_path}"')

    os.system("python train.py")

    return redirect("/dashboard")


# ---------------- START ATTENDANCE ----------------
@app.route('/recognize')
def recognize():
    if 'user' not in session:
        return redirect('/')

    os.system('python face_recognize.py')
    return redirect('/dashboard')


# ---------------- VIEW ATTENDANCE ----------------
@app.route('/attendance')
def attendance():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, date, time FROM attendance ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()

    return render_template('attendance.html', data=data)


# ---------------- EXPORT ATTENDANCE ----------------
@app.route('/export')
def export_attendance():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, date, time FROM attendance")
    rows = cursor.fetchall()
    conn.close()

    filename = "attendance_export.csv"

    with open(filename, "w") as f:
        f.write("Name,Date,Time\n")
        for r in rows:
            f.write(f"{r[0]},{r[1]},{r[2]}\n")

    return send_file(filename, as_attachment=True)


# ---------------- ABOUT PAGE ----------------
@app.route('/about')
def about():
    if 'user' not in session:
        return redirect('/')
    return render_template('about.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN (IMPORTANT FOR MOBILE ACCESS) ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
