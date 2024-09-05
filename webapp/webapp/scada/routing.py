from django.urls import re_path
from .consumer import PurchaseConsumer


websocket_urlpatterns = [
    re_path(
        r"ws/purchase/(?P<user_id>\d+)/$", PurchaseConsumer.as_asgi(), name="purchase"
    ),
]
