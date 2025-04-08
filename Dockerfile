# Use an official lightweight Python image.
FROM python:3.9-slim

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file to the container.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose port 5000 for the Flask app.
EXPOSE 5000

# Set the command to run the Flask app.
CMD ["python", "app.py"]
