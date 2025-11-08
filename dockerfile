# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /gym

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables for Flask (not used by Gunicorn but kept for compatibility)
ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Allow build-time injection of application version. Jenkins will pass --build-arg APP_VERSION=<version> during docker build.
ARG APP_VERSION=unknown
ENV APP_VERSION=${APP_VERSION}

# Expose port
EXPOSE 5000

# Run the Flask app using Gunicorn with a single worker to reduce duplicate state issues
# and ensure a lightweight production server. The WSGI app is `app` in `src/app.py`.
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "src.app:app"]
