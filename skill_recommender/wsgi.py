import os
import django
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_recommender.settings')
# Setup Django
django.setup()

# In ephemeral serverless environments without persistent DB, initialize local SQLite
if not os.environ.get('DATABASE_URL'):
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        from recommender.models import Skill
        if Skill.objects.count() == 0:
            execute_from_command_line(['manage.py', 'seed_data'])
    except Exception as e:
        print(f"Ephemeral database initialization notice: {e}")

application = get_wsgi_application()
app = application