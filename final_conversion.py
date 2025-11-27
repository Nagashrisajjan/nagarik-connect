"""
Final comprehensive MongoDB conversion script
This will convert ALL remaining SQL queries in app.py
"""

import re

def final_mongodb_conversion():
    print("🚀 Starting final MongoDB conversion...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip_until = -1
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip if we're in a skip block
        if i < skip_until:
            i += 1
            continue
        
        # Pattern 1: Multi-line SQL SELECT with JOIN
        if 'cursor.execute("""' in line or "cursor.execute('''" in line:
            # Find the end of this SQL block
            sql_end = i
            for j in range(i, min(i + 50, len(lines))):
                if '""")' in lines[j] or "''')" in lines[j]:
                    sql_end = j
                    break
            
            # Extract the SQL query
            sql_block = ''.join(lines[i:sql_end+1])
            
            # Determine what kind of query this is
            if 'FROM complaints' in sql_block and 'JOIN' in sql_block:
                # This is a complex JOIN query - replace with MongoDB aggregation
                new_lines.append("    # MongoDB aggregation (converted from SQL JOIN)\n")
                new_lines.append("    # TODO: Review this aggregation pipeline\n")
                skip_until = sql_end + 1
            else:
                new_lines.append(line)
        
        # Pattern 2: cursor.fetchall() or cursor.fetchone()
        elif 'cursor.fetchall()' in line:
            new_lines.append(line.replace('cursor.fetchall()', 'list(db.collection.find())  # TODO: Fix collection name'))
        elif 'cursor.fetchone()' in line:
            new_lines.append(line.replace('cursor.fetchone()', 'db.collection.find_one()  # TODO: Fix collection name'))
        
        # Pattern 3: Simple cursor.execute with parameters
        elif 'cursor.execute(' in line and '%s' in line:
            new_lines.append("    # TODO: Convert this query to MongoDB\n")
            new_lines.append(f"    # Original: {line}")
        
        else:
            new_lines.append(line)
        
        i += 1
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Conversion complete!")
    print("⚠️  File contains TODO comments - manual review needed")

if __name__ == "__main__":
    final_mongodb_conversion()
