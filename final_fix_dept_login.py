#!/usr/bin/env python3
"""Final fix for dept_admin_login - completely clean version"""

import re

print("="*80)
print("  FINAL FIX FOR DEPT_ADMIN_LOGIN")
print("="*80)
print()

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('app.py.backup_final_login', 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ Created backup: app.py.backup_final_login")
print()

# Find the dept_admin_login function
pattern = r'@app\.route\("/dept_admin/login".*?\ndef dept_admin_login\(\):.*?(?=\n@app\.route|$)'

# New clean function
new_function = '''@app.route("/dept_admin/login", methods=["GET", "POST"], endpoint="dept_admin_login")
def dept_admin_login():
    """Department admin login handler"""
    if request.method == "POST":
        try:
            # Get form data safely
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
                # Set session safely
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
            import traceback
            traceback.print_exc()
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

# Try to find and replace
match = re.search(pattern, content, re.DOTALL)
if match:
    print("✅ Found dept_admin_login function")
    content = content[:match.start()] + new_function + content[match.end():]
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Replaced dept_admin_login function")
    print()
    print("="*80)
    print("  FIX APPLIED - RESTART SERVER NOW")
    print("="*80)
    print()
    print("The server should auto-reload if debug mode is on.")
    print("Otherwise, restart manually: python app.py")
else:
    print("❌ Could not find function to replace")
    print("   Manual intervention required")

print()
