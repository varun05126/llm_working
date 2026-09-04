import os
import django
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_recommender.settings')
# Setup Django
django.setup()

# Run migrations - important for serverless where tmp directory may be wiped
# Note: In production with external DB, ensure MIGRATIONS_RUN is managed properly
try:
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    # Note: We don't set MIGRATIONS_RUN env var as it doesn't persist between processes
    # Migrations are idempotent and safe to run on each startup in this context
except Exception as e:
    # Log the error but don't break the application
    print(f"Error running migrations: {e}")

application = get_wsgi_application()