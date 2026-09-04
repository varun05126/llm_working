import os
import sys
from django.core.wsgi import get_wsgi_application

print("=== WSGI.PY LOADED - CUSTOM BUILD ===", file=sys.stdout)

# Add the project root to Python path so we can import skill_recommender module
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added {project_root} to Python path", file=sys.stdout)

print(f"Python path: {sys.path[:3]}...", file=sys.stdout)  # Show first 3 entries

# Simple approach: always try to run migrations
# In Vercel serverless, each invocation gets a fresh container
# so we need to ensure tables exist on each startup
try:
    print("=== ATTEMPTING MIGRATIONS ===", file=sys.stdout)
    print(f"Current directory: {os.getcwd()}", file=sys.stdout)
    print(f"manage.py exists: {os.path.exists('manage.py')}", file=sys.stdout)

    # Import Django settings first
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_recommender.settings')

    # Now run migrations
    from django.core.management import execute_from_command_line
    import django
    django.setup()

    print("=== RUNNING MIGRATIONS NOW ===", file=sys.stdout)
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    print("=== MIGRATIONS COMPLETED ===", file=sys.stdout)

except Exception as e:
    print(f"=== MIGRATION ERROR: {e} ===", file=sys.stderr)
    import traceback
    print(f"=== TRACEBACK: {traceback.format_exc()} ===", file=sys.stderr)
    # Don't re-raise - let the app continue in case tables already exist

print("=== INITIALIZING DJANGO APPLICATION ===", file=sys.stdout)
# Change to the skill_recommender directory for the WSGI application
os.chdir(os.path.dirname(os.path.abspath(__file__)))
application = get_wsgi_application()
print("=== DJANGO APPLICATION READY ===", file=sys.stdout)