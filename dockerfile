# Use an official Python slim image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file to leverage Docker caching
COPY requirements.txt .

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Default command to run Streamlit (configurable later in docker-compose.yml)
CMD ["streamlit", "run", "shooting_statistics/app.py"]
