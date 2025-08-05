# Use the official Rasa SDK image as base
FROM rasa/rasa-sdk:3.6.2

# Set working directory
WORKDIR /app

# Copy all project files to the container
COPY . /app

# Install Python dependencies with root permissions
USER root
RUN pip install --no-cache-dir -r requirements.txt
USER 1001

# Expose Rasa SDK server port
EXPOSE 5055

# Start Rasa SDK action server
CMD ["start"]

