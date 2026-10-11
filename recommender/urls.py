from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='recommender/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('assess/', views.skill_assessment, name='skill_assessment'),
    path('skill-assessment/', views.skill_assessment, name='skill_assessment_legacy'),
    path('recommendations/', views.view_recommendations, name='view_recommendations'),
    path('recommendation/<int:rec_id>/', views.recommendation_detail, name='recommendation_detail'),
    path('resources/', views.resources, name='resources'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout_view, name='logout'),

    # APIs
    path('api/contact/', views.api_contact, name='api_contact'),
    path('api/milestone/toggle/', views.api_toggle_milestone, name='api_toggle_milestone'),
    path('api/chatbot/', views.api_chatbot, name='api_chatbot'),
]
