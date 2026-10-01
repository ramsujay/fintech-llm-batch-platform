# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies (ignoring pip warnings)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project codebase into the container
COPY . .

# Set environment variables (API keys will be passed at runtime)
ENV GROQ_API_KEY=""

# Command to run the batch processor when the container starts
CMD ["python", "batch_processor.py"]