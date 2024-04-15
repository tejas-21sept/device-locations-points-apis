import os
from io import StringIO

import boto3
import pandas as pd

from locations_data_apis.settings import (
    aws_access_key_id,
    aws_secret_access_key,
    bucket_name,
    file_name,
    region_name,
)


def read_csv_from_s3():
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

        obj = s3.get_object(Bucket=bucket_name, Key=file_name)
        data = obj["Body"].read().decode("utf-8")
        return pd.read_csv(StringIO(data))
    except Exception as e:
        print(f"\n S3 Exception - {e}\n")
        return None
