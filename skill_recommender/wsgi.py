import os
import subprocess
import sys
from django.core.wsgi import get_wsgi_application

# Run migrations on startup to ensure tables exist
# This is safe to call multiple times as Django tracks applied migrations
try:
    subprocess.check_call([sys.executable, 'manage.py', 'migrate', '--noinput'])
except subprocess.CalledProcessError as e:
    # Log the error but don't fail - the app might still work if tables already exist
    print(f"Warning: Migration failed: {e}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_recommender.settings')
application = get_wsgi_application()