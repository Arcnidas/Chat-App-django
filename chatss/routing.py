from django.urls import path, re_path
from . import consumers

ASGI_urlpatterns = [
    path("websocket/<str:id>",consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/group/(?P<group_id>\w+)/$', consumers.GroupChatConsumer.as_asgi()), 


] 