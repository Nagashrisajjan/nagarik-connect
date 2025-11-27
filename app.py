from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from ml.router import predict_department, predict_worker
from flask_babel import Babel
from translations import translations

# ---- ML router ----
from ml.router import predict_department

# ---- APP CONFIG ----
app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = ['en', 'kn', 'hi', 'te', 'ta']

def get_locale():
    return session.get("lang", "en")

babel = Babel(app, locale_selector=get_locale)
def _(key):
    lang = session.get('lang', 'en')
    return translations.get(lang, translations['en']).get(key, key)
@app.context_processor
def inject_translator():
    return dict(_=_)

# ---- IMAGE UPLOAD CONFIG ----
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = None
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return True
# ---- DATABASE CONNECTION ----
def get_db_connection():
    # Use environment variables for production, fallback to local for development
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', ''),
        database=os.environ.get('MYSQL_DATABASE', 'updatedicgs')
    )

def get_workers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM workers")
    workers = cursor.fetchall()
    cursor.close()
    conn.close()
    return workers


# ---- DEPARTMENT WORKERS ----


# ---- LANDING PAGE ----
@app.route("/", endpoint="home")
def landing():
    # Initialize language session if not set
    if 'lang' not in session:
        session['lang'] = 'en'
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM complaints")
    total_complaints = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS solved FROM complaints WHERE LOWER(status)='resolved'")
    solved_complaints = cursor.fetchone()["solved"]

    cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE LOWER(status)='pending'")
    pending_complaints = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) AS in_progress FROM complaints WHERE LOWER(status) LIKE '%in progress%'")
    in_progress_complaints = cursor.fetchone()["in_progress"]

    cursor.close()
    conn.close()

    current_lang = session.get('lang', 'en')
    print(f"Current language in home route: {current_lang}")  # Debug print
    
    return render_template(
        "home.html",
        total_complaints=total_complaints,
        solved_complaints=solved_complaints,
        pending_complaints=pending_complaints,
        in_progress_complaints=in_progress_complaints,
        current_lang=current_lang
    )

# ---- STATIC PAGES ----
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# ---- LOGIN ----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# ---- REGISTER ----
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Debug: Print all form data
        print("Form data received:", dict(request.form))
        
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        raw_password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        # Basic validation
        if not name or not email or not raw_password:
            flash("Please fill in all required fields!", "error")
            return render_template("register.html")
        
        # Validate password confirmation if confirm_password field exists
        if confirm_password and raw_password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("register.html")
        
        # Set default role as citizen
        role = "citizen"
        hashed_password = generate_password_hash(raw_password)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, hashed_password, role)
            )
            conn.commit()
            cursor.close()
            conn.close()

            flash("Registered successfully! Please login.", "success")
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            flash("Email already exists! Please use a different email.", "error")
            return render_template("register.html")

    return render_template("register.html")

# ---- USER DASHBOARD ----
@app.route("/user/dashboard", endpoint="user_dashboard")
def user_dashboard():
    if "user_id" not in session or session.get("role") != "citizen":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch complaints + assigned worker info
    cursor.execute("""
    SELECT 
        c.id,
        c.user_id,
        c.title,
        c.description,
        c.department,
        c.status,
        c.remarks,
        c.latitude,
        c.longitude,
        c.location,
        c.image,
        c.created_at,

        -- ✅ Worker details (from workers table)
        w.name AS assigned_worker_name,
        w.phone AS assigned_worker_phone,
        w.department AS worker_department,

        -- ✅ User info
        u.name AS user_name

    FROM complaints c
    JOIN users u ON c.user_id = u.id
    LEFT JOIN workers w ON c.assigned_worker_id = w.id   -- ✅ Correct worker join

    WHERE c.user_id = %s
    ORDER BY c.created_at DESC
""", (session["user_id"],))

    complaints = cursor.fetchall()

    # ✅ Format timestamps
    for c in complaints:
        if isinstance(c.get("created_at"), datetime):
            c["created_at"] = c["created_at"].strftime("%Y-%m-%d %H:%M")

    # ✅ Count totals
    cursor.execute(
        "SELECT COUNT(*) as total FROM complaints WHERE user_id=%s",
        (session["user_id"],)
    )
    total = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) as resolved FROM complaints WHERE user_id=%s AND status='Resolved'",
        (session["user_id"],)
    )
    resolved = cursor.fetchone()["resolved"]

    cursor.execute(
        "SELECT COUNT(*) as pending FROM complaints WHERE user_id=%s AND status='Pending'",
        (session["user_id"],)
    )
    pending = cursor.fetchone()["pending"]

    cursor.execute(
        "SELECT COUNT(*) as in_progress FROM complaints WHERE user_id=%s AND LOWER(status) LIKE '%in progress%'",
        (session["user_id"],)
    )
    in_progress = cursor.fetchone()["in_progress"]

    cursor.close()
    conn.close()

    return render_template(
        "user_dashboard.html",
        name=session["name"],
        complaints=complaints,
        total=total,
        resolved=resolved,
        pending=pending,
        in_progress=in_progress
    )

# ---- ADMIN LOGIN ----
@app.route("/admin", methods=["GET", "POST"], endpoint="admin_login")
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin@123":
            session["user_id"] = 0
            session["name"] = "Admin"
            session["email"] = "admin@example.com"
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

# ---- ADMIN DASHBOARD ----
@app.route("/admin/dashboard", endpoint="admin_dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch complaints with user name
    cursor.execute("""
    SELECT 
        c.*, 
        u.name AS user_name,
        w.name AS assigned_worker_name,
        w.phone AS assigned_worker_phone,
        w.department AS worker_department
    FROM complaints c
    JOIN users u ON c.user_id = u.id
    LEFT JOIN workers w ON c.assigned_worker_id = w.id
    ORDER BY c.created_at DESC
""")

    complaints = cursor.fetchall()

    # ✅ Fetch workers (same as workers = get_workers())
    cursor.execute("""
        SELECT id, name, phone, department 
        FROM workers 
        ORDER BY department, name
    """)
    all_workers = cursor.fetchall()

    # ✅ Complaint statistics
    cursor.execute("SELECT COUNT(*) AS total FROM complaints")
    total_all = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE status='Pending'")
    pending_all = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) AS in_progress FROM complaints WHERE status='In Progress'")
    in_progress_all = cursor.fetchone()["in_progress"]

    cursor.execute("SELECT COUNT(*) AS resolved FROM complaints WHERE status='Resolved'")
    resolved_all = cursor.fetchone()["resolved"]

    # ✅ Fetch department-wise complaint counts for chart
    cursor.execute("""
        SELECT department, COUNT(*) AS count 
        FROM complaints 
        GROUP BY department 
        ORDER BY count DESC
    """)
    dept_data = cursor.fetchall()
    
    dept_labels = [row["department"] for row in dept_data]
    dept_counts = [row["count"] for row in dept_data]

    # ✅ Format timestamps
    for c in complaints:
        if isinstance(c.get("created_at"), datetime):
            c["created_at"] = c["created_at"].strftime("%Y-%m-%d %H:%M")

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        name=session["name"],
        complaints=complaints,
        all_workers=all_workers,     # ✅ Pass worker list to template
        total_all=total_all,
        pending_all=pending_all,
        in_progress_all=in_progress_all,
        resolved_all=resolved_all,
        dept_labels=dept_labels,     # ✅ Department names for chart
        dept_counts=dept_counts      # ✅ Complaint counts per department
    )
# ---- DEPARTMENT DASHBOARD ----
from datetime import datetime
from flask import render_template, redirect, url_for, session

# ✅ Department name mapping (URL-friendly to DB name)
DEPARTMENT_MAP = {
    "water": "Water Crisis",
    "road": "Road Maintenance(Engg)",
    "garbage": "Solid Waste (Garbage) Related",
    "electrical": "Electrical",
    "general": "General Department"
}

# ✅ Worker assignments per department (optional)



@app.route("/department/<dept_name>")
@app.route("/department/<dept_name>")
def department_dashboard(dept_name):
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Normalize URL-friendly names to DB names if needed
    dept_name = DEPARTMENT_MAP.get(dept_name.lower(), dept_name)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.*, u.name AS user_name
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        WHERE c.department = %s
        ORDER BY c.created_at DESC
    """, (dept_name,))
    complaints = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total FROM complaints WHERE department=%s", (dept_name,))
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE department=%s AND status='Pending'", (dept_name,))
    pending = cursor.fetchone()["pending"]
    cursor.execute("SELECT COUNT(*) AS in_progress FROM complaints WHERE department=%s AND status='In Progress'", (dept_name,))
    in_progress = cursor.fetchone()["in_progress"]
    cursor.execute("SELECT COUNT(*) AS resolved FROM complaints WHERE department=%s AND status='Resolved'", (dept_name,))
    resolved = cursor.fetchone()["resolved"]

    for c in complaints:
        if isinstance(c.get("created_at"), datetime):
            c["created_at"] = c["created_at"].strftime("%Y-%m-%d %H:%M")
        # ✅ DO NOT override assigned_worker_* here — they already come from DB

    cursor.close(); conn.close()

    return render_template(
        "department_dashboard.html",
        department=dept_name,
        complaints=complaints,
        total=total, pending=pending, in_progress=in_progress, resolved=resolved
    )

# ---- SUBMIT COMPLAINT ----
@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    if "user_id" not in session or session.get("role") != "citizen":
        return redirect(url_for("login"))

    title = request.form["title"].strip()
    description = request.form["description"].strip()
    location_text = request.form.get("location_text")  # manual location text

    # ✅ ML prediction
    department = predict_department(title, description)

    # ✅ Extract location (GPS or manual)
    gps_location = request.form.get("location")  # "lat,lng" or empty
    latitude = None
    longitude = None

    if gps_location and "," in gps_location:
        # ✅ User clicked "Add Current Location" → store exact GPS
        lat, lng = gps_location.split(",")
        latitude = lat.strip()
        longitude = lng.strip()
    else:
        # ✅ Only manual location text
        latitude = None
        longitude = None

    # ✅ Handle image upload
    image_file = request.files.get("attachment")
    filename = None
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    # ✅ Insert complaint with GPS (if available)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints
        (user_id, title, description, department, status, created_at,
         image, location, latitude, longitude,
         assigned_worker_id, assigned_worker_name, assigned_worker_phone)
        VALUES (%s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s)
    """, (
        session["user_id"],
        title,
        description,
        department,
        "Pending",
        datetime.now(),
        filename,
        location_text,     # ✅ manual location text (optional)
        latitude,          # ✅ GPS latitude (if available)
        longitude,         # ✅ GPS longitude (if available)
        None, None, None   # worker fields empty
    ))
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Complaint submitted successfully! The admin will assign a worker soon.", "success")
    return redirect(url_for("user_dashboard"))


# ---- UPLOAD ADMIN IMAGE ----
@app.route("/admin/upload_image/<int:complaint_id>", methods=["POST"])
def upload_admin_image(complaint_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    image_file = request.files.get("admin_image")

    if not image_file or image_file.filename == "":
        flash("No image selected!", "danger")
        return redirect(url_for("admin_dashboard"))

    filename = secure_filename(image_file.filename)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image_file.save(image_path)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE complaints SET admin_image=%s WHERE id=%s",
        (filename, complaint_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Admin image uploaded successfully!", "success")
    return redirect(url_for("admin_dashboard"))

# ---- UPDATE COMPLAINT STATUS ----
@app.route("/update_status/<int:complaint_id>", methods=["POST"])
def update_status(complaint_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    new_status = request.form.get("status")
    if new_status not in ["Pending", "In Progress", "Resolved"]:
        flash("Invalid status selected", "danger")
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE complaints SET status=%s WHERE id=%s",
        (new_status, complaint_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Complaint #{complaint_id} status updated to {new_status}", "success")
    return redirect(url_for("admin_dashboard"))

# ---- LOGOUT ----
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---- ADD WORKER ----
@app.route('/add_worker', methods=['POST'])
def add_worker():
    name = request.form['name']
    phone = request.form['phone']
    department = request.form['department']
    complaint_id = request.form['complaint_id']

    # ✅ Create DB connection
    db = get_db_connection()
    cursor = db.cursor()

    # ✅ Insert new worker
    cursor.execute("""
        INSERT INTO workers (name, phone, department)
        VALUES (%s, %s, %s)
    """, (name, phone, department))

    worker_id = cursor.lastrowid  # get the ID of inserted worker

    # ✅ Assign this worker to the complaint
    cursor.execute("""
        UPDATE complaints 
        SET assigned_worker_id = %s
        WHERE id = %s
    """, (worker_id, complaint_id))

    # ✅ Save changes
    db.commit()

    # ✅ Close DB resources
    cursor.close()
    db.close()

    flash("Worker assigned successfully!", "success")
    return redirect(url_for('admin_dashboard'))

# ---- ASSIGN WORKER ----
@app.route("/assign_worker", methods=["POST"])
def assign_worker():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    complaint_id = request.form["complaint_id"]
    worker_id = request.form["worker_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch worker details
    cursor.execute("SELECT * FROM workers WHERE id=%s", (worker_id,))
    worker = cursor.fetchone()

    if not worker:
        flash("Invalid worker selected!", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("admin_dashboard"))

    # ✅ Assign worker to complaint
    cursor.execute("""
        UPDATE complaints
        SET 
            assigned_worker_id = %s,
            assigned_worker_name = %s,
            assigned_worker_phone = %s
        WHERE id = %s
    """, (
        worker["id"],
        worker["name"],
        worker["phone"],
        complaint_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Worker {worker['name']} assigned successfully!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/set_language/<lang>")
def set_language(lang):
    if lang in ['en', 'kn', 'hi', 'te', 'ta']:
        session['lang'] = lang
        session.modified = True  # Force session to save
        print(f"Language set to: {lang}")  # Debug print
    return redirect(request.referrer or url_for("home"))

# ---- FEEDBACK MANAGEMENT ----

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if "user_id" not in session or session.get("role") != "citizen":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Handle submission
    if request.method == "POST":
        title = request.form["title"].strip()
        message = request.form["message"].strip()
        rating = request.form.get("rating")
        complaint_id = request.form.get("complaint_id") or None

        image_file = request.files.get("image")
        filename = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        cursor.execute("""
            INSERT INTO feedback (user_id, title, message, image, rating, complaint_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (session["user_id"], title, message, filename, rating, complaint_id))
        conn.commit()
        flash(_("feedback_submitted_successfully"), "success")

    # Fetch user feedbacks
    cursor.execute("""
        SELECT f.*, c.title AS complaint_title
        FROM feedback f
        LEFT JOIN complaints c ON f.complaint_id = c.id
        WHERE f.user_id=%s
        ORDER BY f.created_at DESC
    """, (session["user_id"],))
    feedbacks = cursor.fetchall()

    # Fetch user's complaints for complaint-wise feedback
    cursor.execute("SELECT id, title FROM complaints WHERE user_id=%s", (session["user_id"],))
    complaints = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("feedback.html", feedbacks=feedbacks, complaints=complaints)


# ---- ADMIN: VIEW & REPLY FEEDBACK ----
@app.route("/admin/feedback", methods=["GET", "POST"])
def admin_feedback():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Handle admin reply
    if request.method == "POST":
        feedback_id = request.form["feedback_id"]
        reply_msg = request.form["reply"].strip()

        cursor.execute("""
            UPDATE feedback
            SET admin_reply=%s, replied_at=NOW()
            WHERE id=%s
        """, (reply_msg, feedback_id))
        conn.commit()
        flash(_("reply_sent_successfully"), "success")

    # Fetch all feedbacks
    cursor.execute("""
        SELECT f.*, u.name AS user_name, c.title AS complaint_title
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        LEFT JOIN complaints c ON f.complaint_id = c.id
        ORDER BY f.created_at DESC
    """)
    all_feedbacks = cursor.fetchall()

    # Get rating analytics
    cursor.execute("""
        SELECT 
            ROUND(AVG(rating), 1) AS avg_rating, 
            COUNT(*) AS total_feedback,
            SUM(CASE WHEN rating=5 THEN 1 ELSE 0 END) AS five_star,
            SUM(CASE WHEN rating=4 THEN 1 ELSE 0 END) AS four_star,
            SUM(CASE WHEN rating=3 THEN 1 ELSE 0 END) AS three_star,
            SUM(CASE WHEN rating=2 THEN 1 ELSE 0 END) AS two_star,
            SUM(CASE WHEN rating=1 THEN 1 ELSE 0 END) AS one_star
        FROM feedback
    """)
    analytics = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("admin_feedback.html", feedbacks=all_feedbacks, analytics=analytics)


# ==================== DEPARTMENT ADMIN ROUTES ====================

# ---- DEPARTMENT ADMIN LOGIN ----
@app.route("/dept_admin/login", methods=["GET", "POST"], endpoint="dept_admin_login")
def dept_admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM department_admins WHERE username=%s", (username,))
        dept_admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if dept_admin and check_password_hash(dept_admin["password"], password):
            session["dept_admin_id"] = dept_admin["id"]
            session["dept_admin_name"] = dept_admin["name"]
            session["dept_admin_username"] = dept_admin["username"]
            session["department"] = dept_admin["department"]
            session["role"] = "dept_admin"
            flash(f"Welcome {dept_admin['name']}!", "success")
            return redirect(url_for("dept_admin_dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("dept_admin_login"))

    return render_template("dept_admin_login.html")


# ---- DEPARTMENT ADMIN DASHBOARD ----
@app.route("/dept_admin/dashboard", endpoint="dept_admin_dashboard")
def dept_admin_dashboard():
    if "dept_admin_id" not in session or session.get("role") != "dept_admin":
        flash("Please login as department admin", "warning")
        return redirect(url_for("dept_admin_login"))

    department = session.get("department")
    admin_name = session.get("dept_admin_name")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch complaints for this department
    cursor.execute("""
        SELECT 
            c.*, 
            u.name AS user_name,
            w.name AS assigned_worker_name,
            w.phone AS assigned_worker_phone
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        LEFT JOIN workers w ON c.assigned_worker_id = w.id
        WHERE c.department = %s
        ORDER BY c.created_at DESC
    """, (department,))
    complaints = cursor.fetchall()

    # Statistics
    cursor.execute("SELECT COUNT(*) AS total FROM complaints WHERE department=%s", (department,))
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE department=%s AND status='Pending'", (department,))
    pending = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) AS in_progress FROM complaints WHERE department=%s AND status='In Progress'", (department,))
    in_progress = cursor.fetchone()["in_progress"]

    cursor.execute("SELECT COUNT(*) AS resolved FROM complaints WHERE department=%s AND status='Resolved'", (department,))
    resolved = cursor.fetchone()["resolved"]

    # Fetch workers for this department
    cursor.execute("""
        SELECT w.*, COUNT(c.id) as complaint_count
        FROM workers w
        LEFT JOIN complaints c ON w.id = c.assigned_worker_id
        WHERE w.department = %s
        GROUP BY w.id
        ORDER BY w.name
    """, (department,))
    workers = cursor.fetchall()

    # Monthly trend data (last 6 months)
    cursor.execute("""
        SELECT 
            DATE_FORMAT(created_at, '%%b') as month,
            COUNT(*) as count
        FROM complaints
        WHERE department = %s
        AND created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        GROUP BY DATE_FORMAT(created_at, '%%Y-%%m'), DATE_FORMAT(created_at, '%%b')
        ORDER BY DATE_FORMAT(created_at, '%%Y-%%m')
    """, (department,))
    trend_data_raw = cursor.fetchall()
    
    trend_labels = [row["month"] for row in trend_data_raw]
    trend_data = [row["count"] for row in trend_data_raw]

    # Format timestamps
    for c in complaints:
        if isinstance(c.get("created_at"), datetime):
            c["created_at"] = c["created_at"].strftime("%Y-%m-%d %H:%M")

    cursor.close()
    conn.close()

    return render_template(
        "dept_admin_dashboard.html",
        department=department,
        admin_name=admin_name,
        complaints=complaints,
        workers=workers,
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        trend_labels=trend_labels,
        trend_data=trend_data
    )


# ---- DEPARTMENT ADMIN: UPDATE STATUS ----
@app.route("/dept_admin/update_status/<int:complaint_id>", methods=["POST"], endpoint="dept_update_status")
def dept_update_status(complaint_id):
    if "dept_admin_id" not in session or session.get("role") != "dept_admin":
        return redirect(url_for("dept_admin_login"))

    new_status = request.form.get("status")
    remarks = request.form.get("remarks", "").strip()

    if new_status not in ["Pending", "In Progress", "Resolved"]:
        flash("Invalid status selected", "danger")
        return redirect(url_for("dept_admin_dashboard"))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    if remarks:
        cursor.execute(
            "UPDATE complaints SET status=%s, remarks=%s WHERE id=%s",
            (new_status, remarks, complaint_id)
        )
    else:
        cursor.execute(
            "UPDATE complaints SET status=%s WHERE id=%s",
            (new_status, complaint_id)
        )
    
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Complaint #{complaint_id} updated to {new_status}", "success")
    return redirect(url_for("dept_admin_dashboard"))


# ---- DEPARTMENT ADMIN: UPLOAD IMAGE ----
@app.route("/dept_admin/upload_image/<int:complaint_id>", methods=["POST"], endpoint="dept_upload_admin_image")
def dept_upload_admin_image(complaint_id):
    if "dept_admin_id" not in session or session.get("role") != "dept_admin":
        return redirect(url_for("dept_admin_login"))

    image_file = request.files.get("admin_image")

    if not image_file or image_file.filename == "":
        flash("No image selected!", "danger")
        return redirect(url_for("dept_admin_dashboard"))

    filename = secure_filename(image_file.filename)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image_file.save(image_path)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE complaints SET admin_image=%s WHERE id=%s",
        (filename, complaint_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Admin image uploaded successfully!", "success")
    return redirect(url_for("dept_admin_dashboard"))


# ---- DEPARTMENT ADMIN: ADD WORKER ----
@app.route('/dept_admin/add_worker', methods=['POST'], endpoint="dept_add_worker")
def dept_add_worker():
    if "dept_admin_id" not in session or session.get("role") != "dept_admin":
        return redirect(url_for("dept_admin_login"))

    name = request.form['name']
    phone = request.form['phone']
    department = request.form['department']
    complaint_id = request.form['complaint_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert new worker
    cursor.execute("""
        INSERT INTO workers (name, phone, department)
        VALUES (%s, %s, %s)
    """, (name, phone, department))

    worker_id = cursor.lastrowid

    # Assign worker to complaint
    cursor.execute("""
        UPDATE complaints 
        SET assigned_worker_id = %s
        WHERE id = %s
    """, (worker_id, complaint_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Worker assigned successfully!", "success")
    return redirect(url_for('dept_admin_dashboard'))


# ---- DEPARTMENT ADMIN: FEEDBACK ----
@app.route("/dept_admin/feedback", methods=["GET", "POST"], endpoint="dept_admin_feedback")
def dept_admin_feedback():
    if "dept_admin_id" not in session or session.get("role") != "dept_admin":
        return redirect(url_for("dept_admin_login"))

    department = session.get("department")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Handle reply
    if request.method == "POST":
        feedback_id = request.form["feedback_id"]
        reply_msg = request.form["reply"].strip()

        cursor.execute("""
            UPDATE feedback
            SET admin_reply=%s, replied_at=NOW()
            WHERE id=%s
        """, (reply_msg, feedback_id))
        conn.commit()
        flash("Reply sent successfully!", "success")

    # Fetch feedbacks related to this department's complaints
    cursor.execute("""
        SELECT f.*, u.name AS user_name, c.title AS complaint_title
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        LEFT JOIN complaints c ON f.complaint_id = c.id
        WHERE c.department = %s OR f.complaint_id IS NULL
        ORDER BY f.created_at DESC
    """, (department,))
    feedbacks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_feedback.html", feedbacks=feedbacks, analytics=None)


# ---- RUN APP ----
if __name__ == "__main__":
    app.run(debug=True)