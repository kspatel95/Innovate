# Use the official Python image from the Docker Hub
FROM python:3.8.5

# Set the working directory in the container
WORKDIR /Innovate

# Copy the requirements.txt file into the container
COPY requirements.txt requirements.txt

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables
ENV PORT=8050

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server"]
