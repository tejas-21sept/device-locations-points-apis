from django.urls import path

from .views import (
    LatestDeviceInfoAPIView,
    LocationPointsAPIView,
    StartEndLocationAPIView,
)

urlpatterns = [
    path(
        "latest-info/<str:device_id>/",
        LatestDeviceInfoAPIView.as_view(),
        name="latest-info",
    ),
    path(
        "start-end-location/<str:device_id>/",
        StartEndLocationAPIView.as_view(),
        name="start-end-location",
    ),
    path(
        "location-points/<str:device_id>/",
        LocationPointsAPIView.as_view(),
        name="location-points",
    ),
]
