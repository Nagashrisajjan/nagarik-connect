"""
Comprehensive MongoDB Converter
Converts ALL SQL queries in app.py to MongoDB
"""

import re
from datetime import datetime

def convert_all_sql_to_mongodb():
    print("🚀 Starting comprehensive MongoDB conversion...")
    print("📝 Reading app.py...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    
    # Track conversions
    conversions = []
    
    # Step 1: Remove any remaining cursor/conn references
    print("\n📌 Step 1: Cleaning up cursor/conn references...")
    content = re.sub(r'\s*cursor\.close\(\)', '', content)
    content = re.sub(r'\s*conn\.close\(\)', '', content)
    content = re.sub(r'\s*conn\.commit\(\)', '', content)
    conversions.append("Removed cursor.close(), conn.close(), conn.commit()")
    
    # Step 2: Replace all cursor.execute with db operations
    print("📌 Step 2: Converting cursor.execute statements...")
    
    # Pattern: cursor.execute("SELECT COUNT(*) AS X FROM complaints WHERE ...")
    def replace_count_query(match):
        full_match = match.group(0)
        
        # Extract what we're counting
        if 'AS total' in full_match:
            result_key = 'total'
        elif 'AS pending' in full_match:
            result_key = 'pending'
        elif 'AS resolved' in full_match:
            result_key = 'resolved'
        elif 'AS in_progress' in full_match:
            result_key = 'in_progress'
        elif 'AS solved' in full_match:
            result_key = 'solved'
        else:
            result_key = 'count'
        
        # Build MongoDB query
        if 'WHERE' not in full_match:
            return f'{result_key} = db.complaints.count_documents({{}})'
        elif "status='Pending'" in full_match or 'status="Pending"' in full_match:
            if 'user_id' in full_match:
                return f'{result_key} = db.complaints.count_documents({{"user_id": session["user_id"], "status": "Pending"}})'
            else:
                return f'{result_key} = db.complaints.count_documents({{"status": "Pending"}})'
        elif "status='Resolved'" in full_match or 'status="Resolved"' in full_match:
            if 'user_id' in full_match:
                return f'{result_key} = db.complaints.count_documents({{"user_id": session["user_id"], "status": "Resolved"}})'
            else:
                return f'{result_key} = db.complaints.count_documents({{"status": "Resolved"}})'
        elif "status='In Progress'" in full_match or 'status="In Progress"' in full_match:
            if 'user_id' in full_match:
                return f'{result_key} = db.complaints.count_documents({{"user_id": session["user_id"], "status": "In Progress"}})'
            else:
                return f'{result_key} = db.complaints.count_documents({{"status": "In Progress"}})'
        elif 'in progress' in full_match.lower():
            if 'user_id' in full_match:
                return f'{result_key} = db.complaints.count_documents({{"user_id": session["user_id"], "status": {{"$regex": "in progress", "$options": "i"}}}}'
            else:
                return f'{result_key} = db.complaints.count_documents({{"status": {{"$regex": "in progress", "$options": "i"}}}}'
        elif 'department' in full_match:
            return f'{result_key} = db.complaints.count_documents({{"department": dept_name}})'
        else:
            return f'{result_key} = db.complaints.count_documents({{}})  # TODO: Add filter'
    
    # Replace COUNT queries
    content = re.sub(
        r'cursor\.execute\(["\']SELECT COUNT\(\*\).*?["\'].*?\)\s*\n\s*\w+\s*=\s*cursor\.fetchone\(\)\[["\'](\w+)["\']\]',
        replace_count_query,
        content,
        flags=re.DOTALL | re.IGNORECASE
    )
    conversions.append("Converted COUNT queries")
    
    # Step 3: Mark complex queries for manual review
    print("📌 Step 3: Marking complex queries...")
    
    # Find all remaining cursor.execute with multi-line SQL
    complex_pattern = r'cursor\.execute\(["\'\s]*SELECT.*?["\'\s]*\)'
    matches = list(re.finditer(complex_pattern, content, re.DOTALL | re.IGNORECASE))
    
    print(f"   Found {len(matches)} complex queries to mark")
    
    for match in reversed(matches):  # Reverse to maintain positions
        start, end = match.span()
        # Add TODO comment before the query
        content = content[:start] + '# TODO: Convert this SQL query to MongoDB\n    ' + content[start:end] + '  # NEEDS CONVERSION' + content[end:]
    
    conversions.append(f"Marked {len(matches)} complex queries for manual review")
    
    # Step 4: Save
    print("\n💾 Saving converted file...")
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content)
    
    print("\n✅ Conversion complete!")
    print(f"\n📊 Statistics:")
    print(f"   Original size: {original_length} characters")
    print(f"   New size: {new_length} characters")
    print(f"   Difference: {new_length - original_length:+d} characters")
    print(f"\n🔄 Conversions made:")
    for i, conv in enumerate(conversions, 1):
        print(f"   {i}. {conv}")
    
    print("\n⚠️  Next steps:")
    print("   1. Search for 'TODO: Convert' in app.py")
    print("   2. Manually convert complex JOIN queries")
    print("   3. Test each route")
    print("   4. Remove TODO comments when done")
    
    return True

if __name__ == "__main__":
    try:
        convert_all_sql_to_mongodb()
        print("\n🎉 Automated conversion successful!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
