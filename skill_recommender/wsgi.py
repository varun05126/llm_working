import os
import subprocess
import sys
from django.core.wsgi import get_wsgi_application

# Run migrations on startup to ensure tables exist
# This is safe to call multiple times as Django tracks applied migrations
try:
    # Print current directory and Python path for debugging
    print(f"=== DJANGO MIGRATION START ===", file=sys.stdout)
    print(f"Current directory: {os.getcwd()}", file=sys.stdout)
    print(f"Python executable: {sys.executable}", file=sys.stdout)
    print(f"Checking for manage.py: {os.path.exists('manage.py')}", file=sys.stdout)

    # Run migrations
    result = subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'],
                          capture_output=True, text=True, timeout=30)

    if result.returncode == 0:
        print(f"Migrations completed successfully", file=sys.stdout)
        if result.stdout:
            print(f"Migration output: {result.stdout}", file=sys.stdout)
    else:
        print(f"Migration failed with return code {result.returncode}", file=sys.stderr)
        print(f"Migration stdout: {result.stdout}", file=sys.stderr)
        print(f"Migration stderr: {result.stderr}", file=sys.stderr)
        # Don't raise the exception - let the app continue in case tables already exist

except subprocess.TimeoutExpired:
    print(f"Migration timed out after 30 seconds", file=sys.stderr)
except Exception as e:
    print(f"Unexpected error during migration: {e}", file=sys.stderr)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_recommender.settings')
application = get_wsgi_application()
print(f"=== DJANGO APPLICATION INITIALIZED ===", file=sys.stdout)