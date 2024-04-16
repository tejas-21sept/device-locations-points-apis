import csv
from datetime import datetime
from io import StringIO

import boto3
import pandas as pd
import redis
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from locations.utils.custom_api_response import api_response
from locations.utils.s3_csv_utils import read_csv_from_s3
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


class StartEndLocationAPIView(APIView):
    """
    API endpoint that takes a device ID and returns the start and end locations for that device.

    Args:
        device_id (str): The unique identifier of the device.

    Returns:
        Response: A JSON response containing the start and end locations for the device.
    """

    def get(self, request, device_id):
        """
        Retrieve the start and end locations of a device.

        Args:
            request: HTTP request object.
            device_id (str): The unique identifier of the device.

        Returns:
            Response: A JSON response containing the start and end locations for the device.
        """
        try:
            # Check if start location is available in cache
            start_location = redis_instance.hget(device_id, "start_location")

            if start_location is None:
                # Start location not found in cache, fetch data from DataFrame
                df = read_csv_from_s3()
                device_data = (
                    df[df["device_fk_id"] == int(device_id)]
                    .sort_values(by="time_stamp")
                    .iloc[0]
                )

                # Calculate start location from fetched data
                start_location = {
                    "latitude": device_data["latitude"],
                    "longitude": device_data["longitude"],
                }

            # Logic to query end location from the raw data
            end_location_bytes = redis_instance.hgetall(device_id)

            end_location_dict = {
                key.decode(): value.decode()
                for key, value in end_location_bytes.items()
            }

            # Construct end_location dictionary
            end_location = {
                "latitude": float(end_location_dict["latitude"]),
                "longitude": float(end_location_dict["longitude"]),
            }

            # Construct data dictionary
            data = {
                "device_id": device_id,
                "start_location": start_location,
                "end_location": end_location,
            }

            return Response(
                api_response(
                    status_code=200,
                    message="Start and end locations retrieved successfully.",
                    data=data,
                ),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            # Return a 500 response with the error message
            return Response(
                api_response(
                    status_code=500, message="Internal server error.", data=str(e)
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LocationPointsAPIView(APIView):
    """
    API endpoint to retrieve location points data within a specified time range for a device.

    Parameters:
    - request: HTTP request object.
    - device_id: ID of the device for which to retrieve location points data.

    Returns:
    - Response: JSON response containing location points data or an error message.

    Raises:
    - HTTP 400 Bad Request: If required fields are missing in the request.
    - HTTP 500 Internal Server Error: If there's an unexpected server error.
    """

    def post(self, request, device_id):
        """
        Retrieve location points data within a specified time range for a device.

        Args:
        - request: HTTP request object.
        - device_id: ID of the device for which to retrieve location points data.

        Returns:
        - Response: JSON response containing location points data or an error message.

        Raises:
        - HTTP 400 Bad Request: If required fields are missing in the request.
        - HTTP 500 Internal Server Error: If there's an unexpected server error.
        """
        try:
            return self.get_location_points_data(request, device_id)
        except KeyError as e:
            missing_field = e.args[0]
            return Response(
                api_response(
                    status_code=400,
                    message=f"Field '{missing_field}' is required.",
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            # Return a 500 response with the error message
            return Response(
                api_response(
                    status_code=500, message="Internal server error.", data=str(e)
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_location_points_data(self, request, device_id):
        # Extract start_date, start_time, end_date, and end_time from the request body
        start_date = (
            request.data["start_date"] if "start_date" in request.data else None
        )
        start_time = (
            request.data["start_time"] if "start_time" in request.data else None
        )
        end_date = request.data["end_date"] if "end_date" in request.data else None
        end_time = request.data["end_time"] if "end_time" in request.data else None

        missing_fields = []

        # Check for missing fields
        if not start_date:
            missing_fields.append("start_date")
        if not start_time:
            missing_fields.append("start_time")
        if not end_date:
            missing_fields.append("end_date")
        if not end_time:
            missing_fields.append("end_time")

        # If any required field is missing, return a 400 response
        if missing_fields:
            return Response(
                api_response(
                    status_code=200,
                    message=f"Missing required fields: {', '.join(missing_fields)}",
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Read CSV file
        df = read_csv_from_s3()

        # Concatenate date and time strings to form ISO 8601 datetime strings
        start_datetime_str = f"{start_date}T{start_time}Z"
        end_datetime_str = f"{end_date}T{end_time}Z"

        # Convert start_time and end_time strings to datetime objects
        start_time = datetime.strptime(start_datetime_str, "%Y-%m-%dT%H:%M:%SZ")
        end_time = datetime.strptime(end_datetime_str, "%Y-%m-%dT%H:%M:%SZ")

        # Filter the DataFrame based on the datetime value
        filtered_df1 = df[df["time_stamp"] == start_datetime_str]

        # Filter the DataFrame based on device_id and time range
        filtered_df = df[
            (df["device_fk_id"] == int(device_id))
            & (df["time_stamp"] >= start_datetime_str)
            & (df["time_stamp"] <= end_datetime_str)
        ]

        # Convert the filtered DataFrame to a list of dictionaries
        location_points = filtered_df.to_dict(orient="records")

        # Extract latitude, longitude, and time_stamp from each dictionary
        result = [
            {
                "latitude": point["latitude"],
                "longitude": point["longitude"],
                "time_stamp": point["time_stamp"],
            }
            for point in location_points
        ]

        return Response(
            api_response(
                status_code=200,
                message="Location points data is retrieved successfully.",
                data=result,
            ),
            status=status.HTTP_200_OK,
        )
