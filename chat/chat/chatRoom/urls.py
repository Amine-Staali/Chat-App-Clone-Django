from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView, name= 'login'),
    path('register/', views.RegisterView, name= 'register'),
    path('logout/', views.logoutView, name = 'logout'),

    path('Browse_Topics/', views.topicView, name = 'Browse_Topics'),
    path('activities/', views.activityView, name= 'activities'),
    
    path('',views.Home, name = 'home'),
    
    path('Profile/<str:pk>/', views.userProfile, name='userProfile'),
    path('Profile/<str:pk>/Edit/', views.editProfile, name='editProfile'),
    
    path('Room/<str:pk>/', views.Roomchat, name='room'),
    path('Create_room/', views.addRoom, name='add_room'),
    path('Update_room/<str:pk>/', views.updateRoom, name='Update_room'),
    path('delete_room/<str:pk>/', views.deleteRoom, name = 'Delete_room'),
    
    path('delete_message/<str:pk>/', views.deleteMsg, name = 'Delete_msg'),

]
