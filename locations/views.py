from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from locations.utils.custom_api_response import api_response
from locations_data_apis.settings import redis_instance


class LatestDeviceInfoAPIView(APIView):
    """
    API endpoint that takes a device ID and returns the device's latest information.

    Args:
        device_id (str): The unique identifier of the device.

    Returns:
        Response: A JSON response containing the device's latest information.
    """

    def get(self, request, device_id):
        """
        Retrieve the latest information of a device.

        Args:
            request: HTTP request object.
            device_id (str): The unique identifier of the device.

        Returns:
            Response: A JSON response containing the device's latest information.
        """
        try:
            # Get the device data from redis cache using device_id
            device_data_bytes = redis_instance.hgetall(device_id)

            # Convert bytes value of device_data to string.
            device_data = {
                key.decode(): value.decode() for key, value in device_data_bytes.items()
            }

            if not device_data:
                # Return 404 if device data is not found in cache.
                return Response(
                    api_response(
                        status_code=404,
                        message="Device data not found",
                        data={"error": "Device data not found"},
                    ),
                    status=status.HTTP_404_NOT_FOUND,
                )

            device_data["device_id"] = device_id

            return Response(
                api_response(
                    status_code=200,
                    message="Device data retrieved successfully.",
                    data=device_data,
                ),
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                api_response(
                    status_code=500,
                    message="Internal server error.",
                    data=str(e),
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
