# Use an official Python runtime as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock to the working directory
COPY Pipfile Pipfile.lock /app/

# Install Pipenv and the project dependencies
RUN pip3 install --upgrade pipenv && pipenv install --system --deploy 

# Install Flask and its dependencies
RUN pipenv install flask

# Copy the rest of the application code to the working directory
COPY . .

# Set the entrypoint command to run the Python script
ENTRYPOINT ["pipenv", "run", "python3", "main.py"]