from django.urls import path

from .views import LatestDeviceInfoAPIView

urlpatterns = [
    path(
        "latest-info/<str:device_id>/",
        LatestDeviceInfoAPIView.as_view(),
        name="latest-info",
    ),
]
