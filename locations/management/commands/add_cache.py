"""
Command to add latest device location data to Redis cache.

This command retrieves data from a CSV file stored on Amazon S3, processes it to find the latest data for each device ID based on the timestamp, and then adds this latest data to a Redis cache. The data is stored in Redis as a hash, with each device ID as the key and latitude, longitude, and timestamp as fields within the hash.

Attributes:
    help (str): A brief description of the command displayed when using Django's help system.

Methods:
    handle(*args, **options): The method called when the command is executed. It retrieves the data, processes it, and stores the latest device location data in Redis cache. It also handles exceptions and displays appropriate messages.

Raises:
    Exception: An error occurred while retrieving, processing, or storing data. The error message is displayed if an exception occurs.

Usage:
    python manage.py add_location_cache

Example:
    $ python manage.py add_location_cache
"""

import pandas as pd
import redis
from django.core.management.base import BaseCommand

from locations.utils.s3_csv_utils import read_csv_from_s3
from locations_data_apis.settings import redis_instance


class Command(BaseCommand):
    help = "Adding cache to redis."

    def handle(self, *args, **options):

        try:
            # Retrieve data from csv file
            df = read_csv_from_s3()
            # print(f"\n df Data - {df}\n")

            # converting "time_stamp" column into str datatype
            df["time_stamp"] = df["time_stamp"].astype(str)

            # Group data by "device_fk_id" and find the row with latest "time_stamp"
            latest_data = df.loc[df.groupby("device_fk_id")["time_stamp"].idxmax()]

            # adding latest data for each device ID to redis cache
            for _, row in latest_data.iterrows():
                device_id = row["device_fk_id"]
                data = {
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "time_stamp": row["time_stamp"],
                }
                redis_instance.hmset(device_id, data)

            self.stdout.write(
                self.style.SUCCESS(
                    "Latest device location data is stored in redis cache successfully."
                )
            )
        except Exception as e:
            # print(f"\n add cache Exception - {e}\n")
            self.stdout.write(
                self.style.ERROR(f"Error occurred while adding cache to redis - {e}")
            )
