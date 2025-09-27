# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
from werkzeug.utils import secure_filename
import pandas as pd
import joblib

from utils import extract_text_from_image, extract_text_from_link, write_to_csv, check_minimum_matches, is_malicious_url, extract_job_details

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = "replace_this_with_a_random_secret_in_production"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
DB_PATH = os.path.join(BASE_DIR, "users.db")

# load vectorizer and models (assume these files exist in project root)
vectorizer = joblib.load(os.path.join(BASE_DIR, "vectorizer.pkl"))
models = {
    'naive_bayes': joblib.load(os.path.join(BASE_DIR, 'model_nb.pkl')),
    'random_forest': joblib.load(os.path.join(BASE_DIR, 'model_rf.pkl')),
    'xgboost': joblib.load(os.path.join(BASE_DIR, 'model_xgb.pkl')),
    'svm': joblib.load(os.path.join(BASE_DIR, 'model_svm.pkl'))
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )"""
    )
    conn.commit()
    conn.close()

init_db()

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access that page.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def landing():
    # If user logged in -> redirect to main index/dashboard, else show landing quote
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("landing.html")

# --- Authentication routes ---
@app.route('/register', methods=['GET','POST'])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        password2 = request.form.get("password2","")
        if not username or not email or not password:
            flash("Fill all fields", "danger")
            return render_template("register.html")
        if password != password2:
            flash("Passwords do not match", "danger")
            return render_template("register.html")
        pw_hash = generate_password_hash(password)
        try:
            query_db("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, pw_hash))
            flash("Registered. Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash("User with that username or email already exists.", "danger")
            return render_template("register.html")
    return render_template("register.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        email_or_username = request.form.get("email_or_username","").strip()
        password = request.form.get("password","")
        user = query_db("SELECT id, username, email, password_hash FROM users WHERE email = ? COLLATE NOCASE", (email_or_username,), one=True)
        if not user:
            user = query_db("SELECT id, username, email, password_hash FROM users WHERE username = ?", (email_or_username,), one=True)
        if not user:
            flash("No user found", "danger")
            return render_template("login.html")
        user_id, username, email, pw_hash = user
        if check_password_hash(pw_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            flash(f"Welcome, {username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        else:
            flash("Incorrect password", "danger")
            return render_template("login.html")
    info = request.args.get("info")
    return render_template("login.html", info=info)

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("landing"))

# --- Main index (after login) which shows three input ways ---
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    description = ""
    extra_msg = None
    job_details = {}
    match_count = 0
    matched_cols = []
    if request.method == "POST":
        # same logic as your previous /predict route
        raw_link = request.form.get('job_link', '').strip()
        if raw_link:
            if is_malicious_url(raw_link):
                extra_msg = f"⚠️ Entered link looks malicious or unsupported: {raw_link}. I did not open it."
            else:
                description = extract_text_from_link(raw_link)
        elif 'job_text' in request.form and request.form['job_text'].strip():
            description = request.form['job_text'].strip()
        elif 'job_image' in request.files and request.files['job_image'].filename != "":
            image = request.files['job_image']
            path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
            image.save(path)
            description = extract_text_from_image(path)

        if not description:
            if not extra_msg:
                extra_msg = "No valid data found from input. Please try again."
            return render_template("index.html", description="", extra_msg=extra_msg, job_details={}, match_count=0, matched_cols=[])

        if isinstance(description, str) and description.startswith("__MALICIOUS_LINK__::"):
            link = description.split("::",1)[1]
            return render_template('result.html', description="", extra_msg=f"⚠️ The link appears unsafe: {link}. Not opened.", job_details={}, match_count=0, matched_cols=[], is_genuine=False)

        is_genuine, msg, match_count, matched_cols = check_minimum_matches(description)
        job_details = extract_job_details(description)

        if is_genuine:
            write_to_csv(description)

        # Render result template which will show count/message and conditionally show ML buttons
        return render_template('result.html',
                               description=description,
                               extra_msg=msg,
                               job_details=job_details,
                               match_count=match_count,
                               matched_cols=matched_cols,
                               is_genuine=is_genuine)

    return render_template("index.html")

# Route to serve uploaded images (protected)
@app.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- ML model runner (same behavior as earlier) ---
@app.route('/run_model/<model_name>', methods=['GET'])
@login_required
def run_model(model_name):
    try:
        if not os.path.exists("uploaded_data.csv"):
            return "No uploaded data found. Upload a job first.", 400
        df = pd.read_csv("uploaded_data.csv")
        description = df['description'].iloc[-1]
        X = vectorizer.transform([description])
        model = models.get(model_name)
        if model is None:
            return "Invalid model selected", 400
        proba = model.predict_proba(X)[0]
        confidence = round(max(proba) * 100, 2)

        if confidence <= 50:
            prediction_label = "Fake"
        elif 50 < confidence <= 80:
            prediction_label = "Moderate"
        else:
            prediction_label = "Genuine"

        result = {
            'prediction': prediction_label,
            'confidence': confidence,
            'model_name': model_name.replace("_", " ").title()
        }

        extra_checks = None
        if prediction_label == "Moderate":
            extra_checks = [
                "✅ Check if the company has an official website",
                "✅ Verify LinkedIn profile of company",
                "✅ See employee reviews on Glassdoor/Reddit",
                "✅ Check YouTube/Social media/X for feedback",
                "✅ Confirm salary realism & contact info"
            ]

        return render_template("algorithm_result.html", result=result, extra_checks=extra_checks)
    except Exception as e:
        return str(e), 500

# Static pages: about & contact
@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
