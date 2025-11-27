"""
Clean version of dept_admin_login function
Copy this into app.py to replace the existing function
"""

CLEAN_FUNCTION = '''
# ---- DEPARTMENT ADMIN LOGIN ----
@app.route("/dept_admin/login", methods=["GET", "POST"], endpoint="dept_admin_login")
def dept_admin_login():
    """Department admin login handler"""
    if request.method == "POST":
        try:
            # Get form data
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            # Validate input
            if not username or not password:
                flash("Please enter both username and password", "danger")
                return redirect(url_for("dept_admin_login"))

            # Get database
            db = get_db()
            
            # Find department admin
            dept_admin = db.dept_admins.find_one({"username": username})

            # Verify credentials
            if dept_admin and check_password_hash(dept_admin["password"], password):
                # Set session
                session["dept_admin_id"] = str(dept_admin.get("id", ""))
                session["dept_admin_name"] = dept_admin.get("name", "")
                session["dept_admin_username"] = dept_admin.get("username", "")
                session["department"] = dept_admin.get("department", "")
                session["role"] = "dept_admin"
                
                flash(f"Welcome {dept_admin.get('name', 'Admin')}!", "success")
                return redirect(url_for("dept_admin_dashboard"))
            else:
                flash("Invalid username or password", "danger")
                return redirect(url_for("dept_admin_login"))
                
        except KeyError as ke:
            print(f"❌ KeyError in dept_admin_login: {ke}")
            flash("Database error. Please contact administrator.", "danger")
            return redirect(url_for("dept_admin_login"))
        except Exception as e:
            print("="*80)
            print(f"❌ DEPARTMENT ADMIN LOGIN ERROR")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error: {e}")
            print("="*80)
            import traceback
            traceback.print_exc()
            print("="*80)
            flash("An error occurred during login. Please try again.", "danger")
            return redirect(url_for("dept_admin_login"))

    return render_template("dept_admin_login.html")
'''

print(CLEAN_FUNCTION)
