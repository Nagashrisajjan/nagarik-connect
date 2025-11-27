from database import get_db
from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from ml.router import predict_department, predict_worker
from flask_babel import Babel
from translations import translations

# ML router already imported above with fallback

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
# Database connection handled by database.py

def get_workers():
    db = get_db()
    workers = list(db.workers.find())
    for w in workers:
        w["id"] = str(w["_id"])
    return workers
    return workers


# ---- DEPARTMENT WORKERS ----


# ---- LANDING PAGE ----
@app.route("/", endpoint="home")
def landing():
    # Initialize language session if not set
    if 'lang' not in session:
        session['lang'] = 'en'
    
    db = get_db()

    total_complaints = db.complaints.count_documents({})

    solved_complaints = db.complaints.count_documents({"status": {"$regex": "resolved", "$options": "i"}})

    pending_complaints = db.complaints.count_documents({"status": {"$regex": "pending", "$options": "i"}})

    in_progress_complaints = db.complaints.count_documents({"status": {"$regex": "in progress", "$options": "i"}})

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

        db = get_db()
        user = db.users.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])

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
            db = get_db()
            # Check if email already exists
            if db.users.find_one({"email": email}):
                flash("Email already exists! Please use a different email.", "error")
                return render_template("register.html")
            
            db.users.insert_one({
                "name": name,
                "email": email,
                "password": hashed_password,
                "role": role,
                "created_at": datetime.now().isoformat()
            })

            flash("Registered successfully! Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Registration error: {str(e)}", "error")
            return render_template("register.html")

    return render_template("register.html")

# ---- USER DASHBOARD ----
@app.route("/user/dashboard", endpoint="user_dashboard")
def user_dashboard():
    if "user_id" not in session or session.get("role") != "citizen":
        return redirect(url_for("login"))

    db = get_db()
    user_id = session["user_id"]

    # MongoDB aggregation to join complaints with workers and users
    complaints = list(db.complaints.aggregate([
        {"$match": {"user_id": user_id}},
        {"$lookup": {
            "from": "workers",
            "let": {"worker_id": "$assigned_worker_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$_id", {"$toObjectId": "$$worker_id"}]}}}
            ],
            "as": "worker_info"
        }},
        {"$unwind": {
            "path": "$worker_info",
            "preserveNullAndEmptyArrays": True
        }},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "assigned_worker_name": {"$ifNull": ["$worker_info.name", None]},
            "assigned_worker_phone": {"$ifNull": ["$worker_info.phone", None]},
            "user_name": session.get("name")
        }},
        {"$sort": {"created_at": -1}}
    ]))

    # Format timestamps
    for c in complaints:
        if c.get("created_at"):
            try:
                if isinstance(c["created_at"], str):
                    c["created_at"] = datetime.fromisoformat(c["created_at"]).strftime("%Y-%m-%d %H:%M")
                elif isinstance(c["created_at"], datetime):
                    c["created_at"] = c["created_at"].strftime("%Y-%m-%d %H:%M")
            except:
                pass

    # Count totals
    total = db.complaints.count_documents({"user_id": user_id})
    resolved = db.complaints.count_documents({"user_id": user_id, "status": "Resolved"})
    pending = db.complaints.count_documents({"user_id": user_id, "status": "Pending"})
    in_progress = db.complaints.count_documents({"user_id": user_id, "status": {"$regex": "in progress", "$options": "i"}})

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

    db = get_db()

    # Fetch all complaints with user and worker info using MongoDB aggregation
    complaints = list(db.complaints.aggregate([
        {"$lookup": {
            "from": "users",
            "let": {"user_id_str": "$user_id"},
            "pipeline": [
                {"$addFields": {"id_str": {"$toString": "$_id"}}},
                {"$match": {"$expr": {"$eq": ["$id_str", "$$user_id_str"]}}}
            ],
            "as": "user_info"
        }},
        {"$lookup": {
            "from": "workers",
            "let": {"worker_id": "$assigned_worker_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$worker_id"]}}}
            ],
            "as": "worker_info"
        }},
        {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
        {"$unwind": {"path": "$worker_info", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "user_name": "$user_info.name",
            "assigned_worker_name": "$worker_info.name",
            "assigned_worker_phone": "$worker_info.phone",
            "worker_department": "$worker_info.department"
        }},
        {"$sort": {"created_at": -1}}
    ]))

    # Fetch all workers
    all_workers = list(db.workers.find().sort([("department", 1), ("name", 1)]))
    for w in all_workers:
        w["id"] = str(w["_id"])

    # ✅ Complaint statistics
    total = db.complaints.count_documents({})

    pending = db.complaints.count_documents({"status": "Pending"})

    in_progress = db.complaints.count_documents({"status": "In Progress"})

    resolved = db.complaints.count_documents({"status": "Resolved"})

    # Fetch department-wise complaint counts using MongoDB aggregation
    dept_data = list(db.complaints.aggregate([
        {"$group": {"_id": "$department", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))
    
    dept_labels = [d["_id"] for d in dept_data]
    dept_counts = [d["count"] for d in dept_data]

    # ✅ Format timestamps
    for c in complaints:
        if isinstance(c.get("created_at"), datetime):
            c["created_at"] = c["created_at"].strftime("%Y-%m-%d %H:%M")

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

    db = get_db()

    # Fetch complaints for this department with user info
    complaints = list(db.complaints.aggregate([
        {"$match": {"department": dept_name}},
        {"$lookup": {
            "from": "users",
            "let": {"user_id_str": "$user_id"},
            "pipeline": [
                {"$addFields": {"id_str": {"$toString": "$_id"}}},
                {"$match": {"$expr": {"$eq": ["$id_str", "$$user_id_str"]}}}
            ],
            "as": "user_info"
        }},
        {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "user_name": "$user_info.name"
        }},
        {"$sort": {"created_at": -1}}
    ]))

    total = db.complaints.count_documents({"department": dept_name})
    pending = db.complaints.count_documents({"department": dept_name, "status": "Pending"})
    in_progress = db.complaints.count_documents({"department": dept_name, "status": "In Progress"})
    resolved = db.complaints.count_documents({"department": dept_name, "status": "Resolved"})

    for c in complaints:
        if isinstance(c.get("created_at"), datetime):
            c["created_at"] = c["created_at"].strftime("%Y-%m-%d %H:%M")
        # ✅ DO NOT override assigned_worker_* here — they already come from DB;

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

    # Insert complaint into MongoDB
    db = get_db()
    db.complaints.insert_one({
        "user_id": session["user_id"],
        "user_name": session["name"],
        "title": title,
        "description": description,
        "department": department,
        "status": "Pending",
        "created_at": datetime.now().isoformat(),
        "image": filename,
        "location": location_text,
        "latitude": latitude,
        "longitude": longitude,
        "assigned_worker_id": None,
        "assigned_worker_name": None,
        "assigned_worker_phone": None,
        "remarks": None,
        "admin_image": None
    })

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

    db = get_db()
    db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"admin_image": filename}}
    )

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

    db = get_db()
    db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"status": new_status}}
    )

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

    db = get_db()
    
    # Insert new worker
    result = db.workers.insert_one({
        "name": name,
        "phone": phone,
        "department": department,
        "created_at": datetime.now().isoformat()
    })
    worker_id = str(result.inserted_id)

    # Assign this worker to the complaint
    db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {
            "assigned_worker_id": worker_id,
            "assigned_worker_name": name,
            "assigned_worker_phone": phone
        }}
    )

    flash("Worker assigned successfully!", "success")
    return redirect(url_for('admin_dashboard'))

# ---- ASSIGN WORKER ----
@app.route("/assign_worker", methods=["POST"])
def assign_worker():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    complaint_id = request.form["complaint_id"]
    worker_id = request.form["worker_id"]

    db = get_db()

    # Fetch worker details
    worker = db.workers.find_one({"_id": ObjectId(worker_id)})
    
    if not worker:
        flash("Invalid worker selected!", "danger")
        return redirect(url_for("admin_dashboard"))

    # Assign worker to complaint
    db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {
            "assigned_worker_id": worker_id,
            "assigned_worker_name": worker["name"],
            "assigned_worker_phone": worker["phone"]
        }}
        )

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

    db = get_db()

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

        db.feedback.insert_one({
            "user_id": session["user_id"],
            "title": title,
            "message": message,
            "image": filename,
            "rating": rating,
            "complaint_id": complaint_id,
            "created_at": datetime.now().isoformat(),
            "admin_reply": None,
            "replied_at": None
        })
        flash(_("feedback_submitted_successfully"), "success")

    # Fetch user feedbacks with complaint titles
    feedbacks = list(db.feedback.aggregate([
        {"$match": {"user_id": session["user_id"]}},
        {"$lookup": {
            "from": "complaints",
            "let": {"complaint_id": "$complaint_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$complaint_id"]}}}
            ],
            "as": "complaint_info"
        }},
        {"$unwind": {"path": "$complaint_info", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "complaint_title": "$complaint_info.title"
        }},
        {"$sort": {"created_at": -1}}
    ]))

    # Fetch user's complaints for dropdown
    complaints = list(db.complaints.find({"user_id": session["user_id"]}).sort("created_at", -1))
    for c in complaints:
        c["id"] = str(c["_id"])

    return render_template("feedback.html", feedbacks=feedbacks, complaints=complaints)


# ---- ADMIN: VIEW & REPLY FEEDBACK ----
@app.route("/admin/feedback", methods=["GET", "POST"])
def admin_feedback():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    db = get_db()

    # Handle admin reply
    if request.method == "POST":
        feedback_id = request.form["feedback_id"]
        reply_msg = request.form["reply"].strip()

        db.feedback.update_one(
            {"_id": ObjectId(feedback_id)},
            {"$set": {
                "admin_reply": reply_msg,
                "replied_at": datetime.now().isoformat()
            }}
        )
        flash(_("reply_sent_successfully"), "success")

    # Fetch all feedbacks with user and complaint info
    all_feedbacks = list(db.feedback.aggregate([
        {"$lookup": {
            "from": "users",
            "let": {"user_id_str": "$user_id"},
            "pipeline": [
                {"$addFields": {"id_str": {"$toString": "$_id"}}},
                {"$match": {"$expr": {"$eq": ["$id_str", "$$user_id_str"]}}}
            ],
            "as": "user_info"
        }},
        {"$lookup": {
            "from": "complaints",
            "let": {"complaint_id": "$complaint_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$complaint_id"]}}}
            ],
            "as": "complaint_info"
        }},
        {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
        {"$unwind": {"path": "$complaint_info", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "user_name": "$user_info.name",
            "complaint_title": "$complaint_info.title"
        }},
        {"$sort": {"created_at": -1}}
    ]))

    # Get rating analytics
    analytics_data = list(db.feedback.aggregate([
        {"$group": {
            "_id": None,
            "avg_rating": {"$avg": "$rating"},
            "total_feedback": {"$sum": 1},
            "five_star": {"$sum": {"$cond": [{"$eq": ["$rating", "5"]}, 1, 0]}},
            "four_star": {"$sum": {"$cond": [{"$eq": ["$rating", "4"]}, 1, 0]}},
            "three_star": {"$sum": {"$cond": [{"$eq": ["$rating", "3"]}, 1, 0]}},
            "two_star": {"$sum": {"$cond": [{"$eq": ["$rating", "2"]}, 1, 0]}},
            "one_star": {"$sum": {"$cond": [{"$eq": ["$rating", "1"]}, 1, 0]}}
        }}
    ]))
    
    analytics = analytics_data[0] if analytics_data else {
        "avg_rating": 0, "total_feedback": 0,
        "five_star": 0, "four_star": 0, "three_star": 0, "two_star": 0, "one_star": 0
    }

    return render_template("admin_feedback.html", feedbacks=all_feedbacks, analytics=analytics)


# ==================== DEPARTMENT ADMIN ROUTES ====================

# ---- DEPARTMENT ADMIN LOGIN ----
@app.route("/dept_admin/login", methods=["GET", "POST"], endpoint="dept_admin_login")
def dept_admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        dept_admin = db.dept_admins.find_one({"username": username})
        if dept_admin:
            dept_admin["id"] = str(dept_admin["_id"])

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

    db = get_db()

    # Fetch complaints for this department with user and worker info
    complaints = list(db.complaints.aggregate([
        {"$match": {"department": department}},
        {"$lookup": {
            "from": "users",
            "let": {"user_id_str": "$user_id"},
            "pipeline": [
                {"$addFields": {"id_str": {"$toString": "$_id"}}},
                {"$match": {"$expr": {"$eq": ["$id_str", "$$user_id_str"]}}}
            ],
            "as": "user_info"
        }},
        {"$lookup": {
            "from": "workers",
            "let": {"worker_id": "$assigned_worker_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$worker_id"]}}}
            ],
            "as": "worker_info"
        }},
        {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
        {"$unwind": {"path": "$worker_info", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "user_name": "$user_info.name",
            "assigned_worker_name": "$worker_info.name",
            "assigned_worker_phone": "$worker_info.phone"
        }},
        {"$sort": {"created_at": -1}}
    ]))

    # Statistics
    total = db.complaints.count_documents({"department": department})
    pending = db.complaints.count_documents({"department": department, "status": "Pending"})
    in_progress = db.complaints.count_documents({"department": department, "status": "In Progress"})
    resolved = db.complaints.count_documents({"department": department, "status": "Resolved"})

    # Fetch workers for this department with complaint counts
    workers = list(db.workers.aggregate([
        {"$match": {"department": department}},
        {"$lookup": {
            "from": "complaints",
            "let": {"worker_id_str": {"$toString": "$_id"}},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$assigned_worker_id", "$$worker_id_str"]}}}
            ],
            "as": "complaints"
        }},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "complaint_count": {"$size": "$complaints"}
        }},
        {"$project": {"complaints": 0}},
        {"$sort": {"name": 1}}
    ]))

    # Monthly trend data (simplified - last 6 months)
    trend_data_raw = list(db.complaints.aggregate([
        {"$match": {"department": department}},
        {"$group": {
            "_id": {"$substr": ["$created_at", 0, 7]},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}},
        {"$limit": 6}
    ]))
    
    trend_labels = [d["_id"] for d in trend_data_raw]
    trend_data = [d["count"] for d in trend_data_raw]

    # Format timestamps
    for c in complaints:
        if isinstance(c.get("created_at"), datetime):
            c["created_at"] = c["created_at"].strftime("%Y-%m-%d %H:%M")

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

    db = get_db()
    
    if remarks:
        db.complaints.update_one(
            {"_id": ObjectId(complaint_id)},
            {"$set": {"status": status, "remarks": remarks}}
        )
    else:
        db.complaints.update_one(
            {"_id": ObjectId(complaint_id)},
            {"$set": {"status": new_status}}
        )

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

    db = get_db()
    db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"admin_image": filename}}
    )

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

    db = get_db()

    # Insert new worker
    result = db.workers.insert_one({
        "name": name,
        "phone": phone,
        "department": department,
        "created_at": datetime.now().isoformat()
    })
    worker_id = str(result.inserted_id)

    # Assign worker to complaint
    db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {
            "assigned_worker_id": worker_id,
            "assigned_worker_name": name,
            "assigned_worker_phone": phone
        }}
    )

    flash("Worker assigned successfully!", "success")
    return redirect(url_for('dept_admin_dashboard'))


# ---- DEPARTMENT ADMIN: FEEDBACK ----
@app.route("/dept_admin/feedback", methods=["GET", "POST"], endpoint="dept_admin_feedback")
def dept_admin_feedback():
    if "dept_admin_id" not in session or session.get("role") != "dept_admin":
        return redirect(url_for("dept_admin_login"))

    department = session.get("department")
    
    db = get_db()

    # Handle reply
    if request.method == "POST":
        feedback_id = request.form["feedback_id"]
        reply_msg = request.form["reply"].strip()

        db.feedback.update_one(
            {"_id": ObjectId(feedback_id)},
            {"$set": {
                "admin_reply": reply_msg,
                "replied_at": datetime.now().isoformat()
            }}
        )
        flash("Reply sent successfully!", "success")

    # Fetch feedbacks related to this department's complaints
    feedbacks = list(db.feedback.aggregate([
        {"$lookup": {
            "from": "users",
            "let": {"user_id_str": "$user_id"},
            "pipeline": [
                {"$addFields": {"id_str": {"$toString": "$_id"}}},
                {"$match": {"$expr": {"$eq": ["$id_str", "$$user_id_str"]}}}
            ],
            "as": "user_info"
        }},
        {"$lookup": {
            "from": "complaints",
            "let": {"complaint_id": "$complaint_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$complaint_id"]}}},
                {"$match": {"department": department}}
            ],
            "as": "complaint_info"
        }},
        {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
        {"$unwind": {"path": "$complaint_info", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "user_name": "$user_info.name",
            "complaint_title": "$complaint_info.title"
        }},
        {"$sort": {"created_at": -1}}
    ]))

    return render_template("admin_feedback.html", feedbacks=feedbacks, analytics=None)


# ---- RUN APP ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)