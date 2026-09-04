# Women Skill Development Recommender

An AI-powered skill development recommendation system specifically designed for women's career growth. Built with Django and integrated with Groq API for personalized recommendations.

## Features

- User registration and profile management
- Skill assessment across various categories (technical, soft skills, leadership, etc.)
- AI-powered skill gap analysis using Groq LLM
- Personalized learning path recommendations
- Career development advice tailored for women professionals
- Learning resources database with filtering capabilities
- Responsive design with Bootstrap

## Tech Stack

- **Backend**: Django 6.1.1
- **Frontend**: HTML5, CSS3, Bootstrap 5.3.0
- **AI Integration**: Groq API (using Mixtral 8x7B model)
- **Database**: SQLite (for development), can be switched to PostgreSQL/MySQL
- **Environment Variables**: Python-dotenv for configuration

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd skill_recommender
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=your_django_secret_key_here
   DEBUG=True
   ```

5. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Visit** `http://127.0.0.1:8000/` in your browser.

## Project Structure

- `skill_recommender/` - Django project settings
- `recommender/` - Main application containing models, views, templates
- `templates/recommender/` - HTML templates
- `static/` - Static files (CSS, JavaScript, images) - to be added

## Usage

1. Register a new account or log in
2. Complete your profile information
3. Take the skill assessment to evaluate your current competencies
4. Get personalized recommendations including:
   - Skill gap analysis
   - 3-month learning path
   - Career development advice
5. Explore learning resources by skill type or resource type

## Customization

- To change the AI model, modify the `groq_model_used` field in the `Recommendation` model or update the view logic.
- To add more skill categories, update the `CATEGORY_CHOICES` in the `Skill` model.
- To adjust the recommendation logic, modify the `get_recommendations` view in `recommender/views.py`.

## Acknowledgments

- Built with ❤️ for women's career advancement
- Powered by Groq's fast LLM inference
- Inspired by the need for personalized skill development guidance

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions or support, please open an issue on this repository.

```

Note: This README is a template and should be adjusted as per the actual project requirements.