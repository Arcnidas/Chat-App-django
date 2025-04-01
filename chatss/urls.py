from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('profile-update/', views.Update_Profile, name='Update_Profile'),
    path('profile-info/<str:pk>', views.Profile_info, name='Profile_details'),
    
    path('logout/', views.logout, name='logout'),
    path('send-friend-request/', views.send_friend_request, name='send-friend-request'),


    path('friend-request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend-request/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('load-friend-requests/', views.load_friend_requests, name='load_friend_requests'),
    path('load-group-requests/', views.received_group_requests, name='received_group_requests'),
    path('display-friends/', views.display_friends, name='display_friend'),

    path('chat-person/<int:id>', views.Chat_to_Person, name="chat_person"),
    path('api/home/', views.home_api, name='home_api'),
    path('test/chat/<int:id>', views.chat_to_person_api, name='chat_to_person_api'),
    path('create-group/', views.create_group, name='create_group'),
    path("group-request/send/", views.send_group_request, name="send_group_request"),
    path("group-request/<int:request_id>/<str:action>/", views.handle_group_request, name="handle_group_request"),
    path("all-groups/", views.display_groups, name="display_groups"),
    path('chat-group/<int:group_id>', views.group_chat_api, name='group_chat_api'),





]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)