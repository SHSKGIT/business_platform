from django.shortcuts import render
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def update_purchase_status(request, purchase_id):
    # Assume we update the purchase status here
    status = "completed"  # Example status
    user_id = request.user.id

    # Notify the user via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}", {"type": "purchase_status_update", "status": status}
    )

    return JsonResponse({"status": "success"})
