FROM tiangolo/meinheld-gunicorn-flask:latest

# Update to the latest PIP
RUN pip3 install --upgrade pip

WORKDIR /app

# Copy requirements file to set up the python environment
COPY requirements.txt ./

# Install the dependencies
RUN pip3 install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the application
COPY src/main.py ./

# Make the necessary working dirs
RUN mkdir -p /app/logs
RUN mkdir -p /app/db
