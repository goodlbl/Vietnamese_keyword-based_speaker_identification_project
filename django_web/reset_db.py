import os
import shutil

db_file = "db.sqlite3"
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"✅ Database file deleted: {db_file}")
else:
    print(f"ℹ️ File not found: {db_file}")

print("Scanning and deleting migration files...")
root_dir = os.getcwd()

for root, dirs, files in os.walk(root_dir):
    if 'env' in root or 'venv' in root or '.git' in root:
        continue

    if "migrations" in dirs:
        migrations_path = os.path.join(root, "migrations")
        
        for filename in os.listdir(migrations_path):
            file_path = os.path.join(migrations_path, filename)
            
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    os.remove(file_path)
                    print(f"   🗑️ Deleted: {os.path.relpath(file_path)}")
                except Exception as e:
                    print(f"   ❌ Error deleting {filename}: {e}")
            
            elif filename == "__pycache__":
                shutil.rmtree(file_path)

print("\n DONE! System is clean.")