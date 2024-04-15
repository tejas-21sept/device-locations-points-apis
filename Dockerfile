# Use the official Python image as base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the working directory
COPY . /code/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run the Django server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "locations_data_apis.wsgi:application"]
