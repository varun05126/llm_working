import os
import django
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_recommender.settings')
# Setup Django
django.setup()

# Run migrations and auto-seed if needed (essential for serverless where /tmp is initialized fresh)
try:
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    from recommender.models import Skill
    if Skill.objects.count() == 0:
        execute_from_command_line(['manage.py', 'seed_data'])
except Exception as e:
    # Log the error but don't break the application
    print(f"Database initialization notice: {e}")

application = get_wsgi_application()
app = application