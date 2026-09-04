# Frontend Template Requirements

This document outlines the frontend (HTML template) requirements for the Women Skill Development Recommendation System. It specifies which template files need to be created, their purpose, and the expected content based on the view context.

## Existing Templates

The following templates already exist in `templates/recommender/`:

- `base.html` - Base template with common layout, navigation, and styling
- `home.html` - Landing page
- `register.html` - User registration form
- `login.html` - User login form (Note: requires a login view to be implemented)
- `profile.html` - User profile view and edit form

## Missing Templates to Create

The following templates need to be created to complete the frontend:

### 1. `skill_assessment.html`
**Purpose:** Display the skill assessment form where users evaluate their current competencies.

**View Context (from `skill_assessment` view):**
- `skills`: QuerySet of all active Skill objects
- `user_skills`: Dictionary mapping skill IDs to user's current proficiency and years of experience (for pre-populating form)

**Expected Content:**
- Form that POSTs to the skill assessment URL
- For each skill in `skills`:
  - Skill name and category
  - Dropdown/select for proficiency level (None, Basic, Intermediate, Advanced, Expert)
  - Input for years of experience (numeric)
  - Pre-select values from `user_skills` if available
- Submit button

### 2. `recommendations.html`
**Purpose:** Display a list of all recommendations for the current user.

**View Context (from `view_recommendations` view):**
- `user_profile`: UserProfile object
- `recommendations`: QuerySet of Recommendation objects (filtered by user, active=True, ordered by -created_at)

**Expected Content:**
- Page header showing user's name and "My Recommendations"
- For each recommendation in `recommendations`:
  - Recommendation title
  - Recommendation type (skill_gap, learning_path, career_advice) - display as human-readable
  - Creation date
  - Link to recommendation detail view (using recommendation.id)
  - Brief description (maybe truncated)
- Button/link to generate new recommendations (links to skill assessment or get_recommendations)

### 3. `recommendation_detail.html`
**Purpose:** Display detailed view of a specific recommendation.

**View Context (from `recommendation_detail` view):**
- `recommendation`: Recommendation object
- `recommendation_skills`: QuerySet of RecommendationSkill objects (with related Skill)
- `recommendation_resources`: QuerySet of RecommendationResource objects (with related Resource and Resource's Skill)

**Expected Content:**
- Recommendation title and type
- Description
- Generation info (LLM used, date generated)
- Two sections:
  1. **Recommended Skills:**
     - For each skill in `recommendation_skills`:
       - Skill name, category
       - Priority level (1 = highest)
       - Reasoning/explanation
  2. **Learning Resources:**
     - For each resource in `recommendation_resources`:
       - Resource title
       - Resource type
       - Associated skill name
       - URL (as a link)
       - Relevance score (display as percentage or rating)
- Back link to recommendations list

### 4. `resources.html`
**Purpose:** Display a browsable list of learning resources with filtering capabilities.

**View Context (from `resources` view):**
- `resources`: QuerySet of LearningResource objects (with related Skill)
- `skills`: QuerySet of all active Skill objects (for filter dropdown)
- `resource_types`: List of resource type choices (from LearningResource.RESOURCE_TYPES)
- `selected_skill`: Currently selected skill ID (from GET request, or None)
- `selected_type`: Currently selected resource type (from GET request, or None)

**Expected Content:**
- Page header: "Learning Resources"
- Filter controls:
  - Dropdown to filter by skill (populated from `skills`, with "All Skills" option)
  - Dropdown to filter by resource type (populated from `resource_types`, with "All Types" option)
  - Apply filter button (or auto-submit on change)
- Resources display:
  - For each resource in `resources`:
    - Resource title
    - Resource type (badge or label)
    - Associated skill name
    - Description (truncated)
    - URL (as a link - "Visit Resource")
    - Additional info: rating, duration, cost, free/paid status (if available)
- If no resources match filters, show appropriate message

### 5. `about.html`
**Purpose:** Display information about the application.

**View Context (from `about` view):**
- No additional context beyond the base template context (user, messages, etc.)

**Expected Content:**
- Page header: "About SkillRecommender"
- Information sections:
  - What the application does
  - How it helps women's career development
  - Technologies used
  - AI integration details (Groq LLM)
  - Contact information or support links
- Call-to-action (e.g., "Get Started" button linking to registration)

## Additional Notes

### Login and Logout Views
While not strictly template creation, the following views need to be implemented or configured to use the existing login.html template:

1. **Login View:**
   - Either create a custom login view in `views.py` that uses `login.html`
   - Or use Django's built-in `auth_views.LoginView` with template_name='recommender/login.html'

2. **Logout View:**
   - Implement a logout view (can use Django's built-in `auth_views.LogoutView`)
   - Add a logout link in the navigation base.html
   - After logout, redirect to home or login page

### Navigation Updates
The `base.html` template should be updated to include navigation links for all major sections:
- Home
- Register
- Login
- Profile
- Skill Assessment
- My Recommendations
- Learning Resources
- About
- Logout (when authenticated)

### Styling and Consistency
All templates should extend `base.html` and:
- Use Bootstrap 5 components for consistency
- Follow the same card-based layout pattern used in existing templates
- Include appropriate iconography (Font Awesome)
- Be responsive and mobile-friendly

### Template Organization
All templates must be placed in:
`skill_recommender/templates/recommender/`

### LLM Backend Development Note
The Groq LLM backend integration has been completed and is functioning with proper error handling and fallback mechanisms. Frontend developers should focus on implementing the required templates listed below to complete the user interface. Any future LLM enhancements or model updates will be handled separately in the backend.

### Verification
After creating each template, verify by:
1. Starting the development server: `python manage.py runserver`
2. Navigating to the corresponding URL
3. Checking that the page renders correctly without errors
4. Ensuring all context variables are used appropriately
5. Confirming responsive behavior on different screen sizes

## Implementation Order
Recommended order for implementation:
1. `about.html` (simplest)
2. `skill_assessment.html` (form-based)
3. `resources.html` (with filtering)
4. `recommendations.html` (list view)
5. `recommendation_detail.html` (detailed view)
6. Implement/update login/logout views and navigation

---
*This document serves as a guide for frontend developers to complete the template layer of the application. All templates should follow the existing codebase's styling and patterns.*