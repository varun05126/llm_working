from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('skill-assessment/', views.skill_assessment, name='skill_assessment'),
    path('get-recommendations/', views.get_recommendations, name='get_recommendations'),
    path('recommendations/', views.view_recommendations, name='view_recommendations'),
    path('recommendation/<int:rec_id>/', views.recommendation_detail, name='recommendation_detail'),
    path('resources/', views.resources, name='resources'),
    path('about/', views.about, name='about'),
]