import os
import subprocess
import sys
from django.core.wsgi import get_wsgi_application

def ensure_database_initialized():
    """Ensure database tables exist, running migrations if needed"""
    try:
        # Check if we can query a basic table (like django_migrations)
        # This is safer than just checking if the file exists
        import sqlite3
        db_path = '/tmp/db.sqlite3'

        # If database file doesn't exist, we definitely need to migrate
        if not os.path.exists(db_path):
            print(f"Database file does not exist at {db_path}", file=sys.stdout)
            run_migrations()
            return

        # Check if we can query the database
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Check if django_migrations table exists (created by first migration)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations';")
            if cursor.fetchone() is None:
                print("django_migrations table not found, running migrations", file=sys.stdout)
                run_migrations()
            else:
                # Optionally, we could check if our app tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recommender_userprofile';")
                if cursor.fetchone() is None:
                    print("App tables not found, running migrations", file=sys.stdout)
                    run_migrations()
                else:
                    print("Database already initialized", file=sys.stdout)
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}, running migrations", file=sys.stdout)
            run_migrations()

    except Exception as e:
        print(f"Error in ensure_database_initialized: {e}", file=sys.stdout)
        # Fallback: try to run migrations anyway
        try:
            run_migrations()
        except Exception as e2:
            print(f"Migration also failed: {e2}", file=sys.stdout)

def run_migrations():
    """Run Django migrations"""
    try:
        print("Running Django migrations...", file=sys.stdout)
        result = subprocess.run(
            [sys.executable, 'manage.py', 'migrate', '--noinput'],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("Migrations completed successfully", file=sys.stdout)
            if result.stdout.strip():
                print(f"Migration output: {result.stdout.strip()}", file=sys.stdout)
        else:
            print(f"Migration failed with return code {result.returncode}", file=sys.stderr)
            print(f"Migration stdout: {result.stdout}", file=sys.stderr)
            print(f"Migration stderr: {result.stderr}", file=sys.stderr)
            # Don't raise - let the app continue in case tables partially exist
    except subprocess.TimeoutExpired:
        print("Migration timed out after 30 seconds", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error during migration: {e}", file=sys.stderr)

# Run database initialization
ensure_database_initialized()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_recommender.settings')
application = get_wsgi_application()