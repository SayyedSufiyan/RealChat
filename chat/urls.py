
from django.urls import path
from . import views
from .views import register_view  # ✅ Add this line
from .views import all_users_view
from .views import profile_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    
    path('', views.chat_room, name='chat_home'), 
    path('chat/<int:user_id>/', views.chat_room, name='chat_room'),
    path('register/', register_view, name='register'),
    path('all-users/', all_users_view, name='all_users'),
    path('profile/', profile_view, name='profile'),
    path('all-users/', views.all_users, name='all_users'),
    path('send-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('notifications/', views.notifications, name='notifications'),
    path('accept/<int:req_id>/', views.accept_request, name='accept_request'),
    

]