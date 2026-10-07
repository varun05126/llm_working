from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='recommender/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('skill-assessment/', views.skill_assessment, name='skill_assessment'),
    path('get-recommendations/', views.get_recommendations, name='get_recommendations'),
    path('recommendations/', views.view_recommendations, name='view_recommendations'),
    path('recommendation/<int:rec_id>/', views.recommendation_detail, name='recommendation_detail'),
    path('resources/', views.resources, name='resources'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout_view, name='logout'),
    
    # Real-Time APIs for interactive async operations
    path('api/contact/', views.api_contact, name='api_contact'),
    path('api/recommendations/realtime/', views.realtime_recommendations_api, name='api_realtime_recommendations'),
    path('api/recommendations/toggle-status/', views.toggle_skill_status_api, name='api_toggle_skill_status'),
]
