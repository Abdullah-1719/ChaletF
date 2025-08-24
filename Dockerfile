# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and folders
COPY app.py .
COPY templates/ templates/

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
