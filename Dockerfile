
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Flask
RUN pip install flask psutil

# Copy the rest of the application
COPY . .

# Command to run the bot
CMD ["python", "bot.py"]
