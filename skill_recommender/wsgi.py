import os
import django
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_recommender.settings')
# Setup Django
django.setup()

# Run migrations once per container
if not os.environ.get('MIGRATIONS_RUN'):
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        os.environ['MIGRATIONS_RUN'] = 'true'
    except Exception as e:
        # Log the error but don't break the application
        print(f"Error running migrations: {e}")

application = get_wsgi_application()