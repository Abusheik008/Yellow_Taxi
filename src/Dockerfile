# Base image
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /src

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
